"""
Dylan for Hire — Nightly Candidate Index
====================================================
Version: 1.0 | 2026-07-09
STATUS: NEW, UNTESTED against a real Quo/OpenPhone account (logic-level tests
only, mocked HTTP — see tests/test_vacancy_matcher.py). Run manually once
against real data before trusting it, same posture as
master_candidate_file_consolidator.py.

PURPOSE
  Vacancy Matcher needs, for every active candidate: which centers/boroughs
  they've mentioned in SMS/email history, their real paperwork/pipeline
  stage, and whether they're opted out. Doing that by live-scanning Quo on
  every vacancy request means hitting /contacts and /messages for
  potentially thousands of candidates per query — that's what caused the
  429/timeout errors flagged when this feature was requested. This module
  walks every ACTIVE candidate ONCE (nightly, on a cron you add by hand — see
  bottom of this file) and writes one local JSON file. Vacancy Matcher then
  reads that file — instant, and Quo only gets hit once a day, not once per
  vacancy.

WHY "ACTIVE ONLY", NOT EVERY CONTACT EVER
  Quo's /conversations endpoint returns lastActivityAt per phone number in
  ONE cheap paginated call (mirrors master_daily_agent.py's
  get_recent_conversations). Only candidates active within the window get a
  /messages history fetch — this is what keeps a nightly run from being
  thousands of individual API calls just to find the ~dozens of people who
  said anything recently.

RATE-LIMIT HANDLING (the actual fix for the 429s)
  _quo_get() below respects a 429's Retry-After header if present, otherwise
  backs off exponentially (min(60s, 2**attempt) — same pattern already used
  in master_sms_poll_service.py / master_gmail_pubsub_listener.py), and
  sleeps briefly between paginated calls so a nightly run doesn't burst
  requests. This did not exist in any of the ad hoc Quo wrapper functions
  this project had before today (master_daily_agent.py's quo_get_raw(),
  master_candidate_file_consolidator.py's get_all_quo_contacts()) — verified
  by grep, neither checks for status 429 specifically.

DRAFT-ONLY INVARIANT
  This module only READS from Quo and WRITES a local JSON file. It never
  calls send-message or anything that reaches a candidate. Outreach drafting
  is a separate module (outreach_drafts.py) and is itself draft-only too.

CLIENT-AGNOSTIC BY DESIGN
  Every function takes a ClientConfig (client_config.py). Nothing here is
  hardcoded to BlueLine's env var names or file paths.
"""

import argparse
import json
import logging
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

from client_config import ClientConfig, BLUELINE_CONFIG, get_quo_api_key, get_quo_phone_id
from center_alias import load_centers, build_alias_index, resolve_center_query

# STAGE_* constants: imported, not duplicated — this project's own house rule
# (see master_candidate_file_consolidator.py's top-of-file comment: "don't
# hardcode this string elsewhere, import the constant instead"), because a
# duplicated pipeline-tag string is exactly the class of bug (BUG-15-style)
# this codebase has been burned by before.
from master_gmail_reviewer import (
    STAGE_NEW, STAGE_DOCS_INCOMPLETE, STAGE_DOCS_COMPLETE_SENT,
    STAGE_READY_FOR_SUBMISSION, STAGE_SUBMITTED_PREFIX,
)
from master_candidate_file_consolidator import STAGE_DRAFTS_READY_PREFIX

log = logging.getLogger("master.candidate_index")

MAX_RETRIES = 5
INTER_REQUEST_SLEEP_SECONDS = 0.15


# ── Rate-limit-safe Quo HTTP wrapper (the actual fix for the 429s) ──────────

def _quo_get(config: ClientConfig, path: str, params=None) -> requests.Response:
    """GET against Quo/OpenPhone with 429/backoff handling. This is the
    piece that was genuinely missing everywhere else in this codebase —
    quo_get_raw() (master_daily_agent.py) and get_all_quo_contacts()
    (master_candidate_file_consolidator.py) both just check resp.ok with no
    429-specific retry."""
    api_key = get_quo_api_key(config)
    headers = {"Authorization": api_key, "Content-Type": "application/json"}
    url = f"{config.quo_base_url}{path}"

    last_resp = None
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(url, headers=headers, params=params or {}, timeout=15)
        except requests.exceptions.RequestException as e:
            wait = min(60, 2 ** attempt)
            log.warning(f"  Quo GET {path} network error (attempt {attempt + 1}/{MAX_RETRIES}): {e} — retrying in {wait}s")
            time.sleep(wait)
            continue

        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After")
            wait = float(retry_after) if retry_after and retry_after.isdigit() else min(60, 2 ** attempt)
            log.warning(f"  Quo GET {path} rate-limited (429), attempt {attempt + 1}/{MAX_RETRIES} — waiting {wait}s")
            time.sleep(wait)
            last_resp = resp
            continue

        return resp

    log.error(f"  Quo GET {path} exhausted {MAX_RETRIES} retries — giving up for this call")
    return last_resp


def fetch_active_conversations(config: ClientConfig, days: int) -> list:
    """One cheap paginated call for 'who has been active in the last N
    days', mirroring master_daily_agent.py's get_recent_conversations() but
    generic over ClientConfig instead of hardcoded module constants."""
    phone_id = get_quo_phone_id(config)
    cutoff_ts = (datetime.now(timezone.utc) - timedelta(days=days)).timestamp()
    conversations, cursor = [], None
    while True:
        params = {"phoneNumberId": phone_id, "pageSize": 100}
        if cursor:
            params["pageToken"] = cursor
        resp = _quo_get(config, "/conversations", params)
        if resp is None or not resp.ok:
            log.warning(f"  /conversations fetch stopped early: {getattr(resp, 'status_code', 'no response')}")
            break
        data = resp.json()
        batch = data.get("data", [])
        for convo in batch:
            last_ts = _parse_iso_ts(convo.get("lastActivityAt"))
            if last_ts >= cutoff_ts:
                conversations.append(convo)
        if batch and _parse_iso_ts(batch[-1].get("lastActivityAt")) < cutoff_ts:
            break
        cursor = data.get("nextPageToken")
        if not cursor:
            break
        time.sleep(INTER_REQUEST_SLEEP_SECONDS)
    return conversations


def fetch_all_contacts(config: ClientConfig) -> list:
    """One full paginated contact fetch. Called once per index build — not
    cached across calls the way email_context_bridge.py's
    _quo_get_all_contacts() is, because this module only calls it once per
    run anyway."""
    contacts, cursor = [], None
    while True:
        params = {"pageSize": 100}
        if cursor:
            params["pageToken"] = cursor
        resp = _quo_get(config, "/contacts", params)
        if resp is None or not resp.ok:
            log.warning(f"  /contacts fetch stopped early: {getattr(resp, 'status_code', 'no response')}")
            break
        data = resp.json()
        contacts.extend(data.get("data", []))
        cursor = data.get("nextPageToken")
        if not cursor:
            break
        time.sleep(INTER_REQUEST_SLEEP_SECONDS)
    return contacts


def fetch_message_text(config: ClientConfig, phone: str, days: int = 90) -> str:
    """INCOMING-only SMS history text for one phone, for center/borough
    mention scanning.

    [FIXED 2026-07-10, Round 18 reconciliation] Two real bugs found by
    directly comparing this function against BlueLine Automation's
    independently-built blueline_quo_helpers.py (see DYLAN_AUDIT_2026-07-01_
    FULL.md Round 18 for the full comparison):

    1. This call was missing the REQUIRED `phoneNumberId` parameter on
       /messages. BlueLine Automation's module docstring documents the real
       root cause directly: OpenPhone's own error body is literally
       "/phoneNumberId: Expected required property" — and WITHOUT it, this
       endpoint doesn't always error loudly; it can silently return an empty
       result with no error at all, meaning this function would have quietly
       returned "" for every candidate, so centers_mentioned/boroughs_mentioned
       would have always come back empty despite the whole pipeline "running
       successfully" with zero visible errors. This is the same missing
       parameter master_candidate_file_consolidator.py's own
       get_quo_sms_history_text() also has (confirmed by direct comparison,
       2026-07-10) — that pre-existing bug is OUT of this round's scope to
       fix (not part of today's request) but is flagged here rather than
       silently ignored now that it's been found.
    2. This function used to join ALL message text regardless of direction
       into the scan blob — meaning Dylan's own automated outbound replies
       (e.g. the document-checklist template, which itself contains city/
       facility-adjacent words) could get misattributed as something the
       CANDIDATE said. BlueLine Automation's index builder filters to
       `direction == "incoming"` before scanning for center mentions — a
       real, meaningful correctness improvement, now adopted here too.
    """
    phone_id = get_quo_phone_id(config)
    cutoff_ts = (datetime.now(timezone.utc) - timedelta(days=days)).timestamp()
    lines, cursor = [], None
    while True:
        params = [("phoneNumberId", phone_id), ("participants[]", phone), ("pageSize", "50")]
        if cursor:
            params.append(("pageToken", cursor))
        resp = _quo_get(config, "/messages", params)
        if resp is None or not resp.ok:
            break
        data = resp.json()
        for msg in data.get("data", []):
            ts = _parse_iso_ts(msg.get("createdAt"))
            if ts < cutoff_ts:
                continue
            if msg.get("direction") == "outgoing":
                continue  # only the candidate's own words count as a stated preference
            text = (msg.get("text") or "").strip()
            if text:
                lines.append(text)
        cursor = data.get("nextPageToken")
        if not cursor:
            break
        time.sleep(INTER_REQUEST_SLEEP_SECONDS)
    return "\n".join(lines)


def _parse_iso_ts(s) -> float:
    if not s:
        return 0.0
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()
    except (ValueError, TypeError):
        return 0.0


# ── Contact field parsing (duplicated from master_daily_agent.py ON PURPOSE —
#    see center_alias.py's BOROUGH_KEYWORDS comment for why: this module must
#    stay importable/testable without QUO_API_KEY/CLAUDE_API_KEY/GCP_PROJECT_ID
#    already set in the environment, which importing master_daily_agent.py
#    would require (os.environ["..."], not os.getenv). Cross-checked for drift
#    in tests/test_vacancy_matcher.py::TestExtractRoleBoroughStaysInSync.) ────

def extract_role_borough(contact: dict, valid_roles) -> tuple:
    last = (contact.get("defaultFields", {}).get("lastName") or "").strip()
    if "," in last:
        parts = last.split(",", 1)
        role_candidate = parts[0].strip().upper()
        if role_candidate in valid_roles:
            return role_candidate, parts[1].strip().rstrip(")")
    last_upper = last.upper()
    for role in ("RN", "LPN", "CNA", "HHA", "RNS"):
        if role in last_upper:
            return role, "NY"
    return "CNA", "NY"


def is_opted_out(contact: dict, phone: str, optouts_set: set) -> bool:
    first_name = (contact.get("defaultFields", {}).get("firstName") or "")
    if first_name.strip().upper().startswith("DO NOT MESSAGE"):
        return True
    return phone in optouts_set


def _load_optouts(config: ClientConfig) -> set:
    path = Path(config.optouts_path)
    if not path.exists():
        return set()
    return {line.strip() for line in path.read_text().splitlines() if line.strip()}


def readiness_bucket(pipeline_stage: str) -> str:
    """Classifies a raw PIPELINE:* tag into a readiness bucket for ranking.

    PRODUCT DECISION, NOT A BUG — flagging per this project's own convention
    for open judgment calls (see 05_PIPELINE_REFERENCE.md-style flags
    elsewhere): a candidate already at DRAFTS_READY or SUBMITTED is mid-
    process for a SPECIFIC center, not necessarily unavailable for a
    DIFFERENT vacancy. This buckets them below submission_ready/hot_file but
    still shows them (never silently hides), so Aditya sees them and can
    judge case by case rather than the tool guessing. Adjust the ordering in
    vacancy_matcher.py's RANK_ORDER if this default doesn't match how you
    actually want to work vacancies.
    """
    stage = pipeline_stage or ""
    if stage == STAGE_READY_FOR_SUBMISSION:
        return "submission_ready"
    if stage == STAGE_DOCS_COMPLETE_SENT:
        return "hot_file"
    if stage.startswith(STAGE_DRAFTS_READY_PREFIX) or stage.startswith(STAGE_SUBMITTED_PREFIX):
        return "drafts_or_submitted"
    if stage == STAGE_DOCS_INCOMPLETE:
        return "docs_incomplete"
    if stage == STAGE_NEW or not stage:
        return "unscreened"
    return "unscreened"


# ── Index build ──────────────────────────────────────────────────────────────

def build_candidate_index(config: ClientConfig = BLUELINE_CONFIG, active_days: int = None) -> dict:
    active_days = active_days or config.default_active_window_days
    log.info(f"=== CANDIDATE INDEX: building for client '{config.client_id}', "
              f"active window {active_days}d ===")

    centers = load_centers(config)
    alias_index = build_alias_index(centers)
    optouts_set = _load_optouts(config)

    conversations = fetch_active_conversations(config, active_days)
    active_phones = {c.get("participants", [None])[0] or c.get("phoneNumber")
                     for c in conversations}
    active_phones.discard(None)
    active_last_ts = {}
    for c in conversations:
        phone = c.get("participants", [None])[0] or c.get("phoneNumber")
        if phone:
            active_last_ts[phone] = c.get("lastActivityAt")

    log.info(f"  {len(active_phones)} phone(s) active in the last {active_days} day(s)")

    all_contacts = fetch_all_contacts(config)
    contacts_by_phone = {}
    for contact in all_contacts:
        for p in (contact.get("defaultFields", {}).get("phoneNumbers") or []):
            phone = (p.get("value") or "").strip()
            if phone:
                contacts_by_phone[phone] = contact

    candidates = []
    for phone in active_phones:
        contact = contacts_by_phone.get(phone)
        if not contact:
            log.info(f"  {phone}: active conversation but no matching Quo contact — skipping")
            continue

        if is_opted_out(contact, phone, optouts_set):
            continue  # never index opted-out candidates, period

        df = contact.get("defaultFields", {}) or {}
        name = (df.get("firstName") or "").strip() or "Unknown"
        license_type, home_borough = extract_role_borough(contact, config.valid_roles)
        pipeline_stage = (df.get("role") or "").strip()

        message_text = fetch_message_text(config, phone)
        boroughs_mentioned, centers_mentioned = set(), set()
        for line in message_text.splitlines():
            match = resolve_center_query(line, alias_index, centers)
            if match.matched_center:
                centers_mentioned.add(match.matched_center)
            if match.matched_borough:
                boroughs_mentioned.add(match.matched_borough)

        candidates.append({
            "phone": phone,
            "name": name,
            "license_type": license_type,
            "home_borough": home_borough,
            "boroughs_mentioned": sorted(boroughs_mentioned),
            "centers_mentioned": sorted(centers_mentioned),
            "pipeline_stage": pipeline_stage,
            "readiness_bucket": readiness_bucket(pipeline_stage),
            "last_active_iso": active_last_ts.get(phone),
            "opted_out": False,
        })

    index = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "client_id": config.client_id,
        "active_window_days": active_days,
        "candidates": candidates,
    }

    out_path = Path(config.candidate_index_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.with_suffix(out_path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
    tmp_path.replace(out_path)  # atomic on the same filesystem

    log.info(f"  Wrote {len(candidates)} candidate(s) to {out_path}")
    return index


def load_candidate_index(config: ClientConfig = BLUELINE_CONFIG) -> dict:
    path = Path(config.candidate_index_path)
    if not path.exists():
        log.warning(f"No candidate index at {path} — run candidate_index.py once first.")
        return {"generated_at": None, "client_id": config.client_id,
                "active_window_days": None, "candidates": []}
    return json.loads(path.read_text(encoding="utf-8"))


def query_index(index: dict, *, license_type: str = None, center: str = None,
                 borough: str = None) -> list:
    """Shared filter used by both vacancy_matcher.py and pipeline_depth.py.
    `center` and `borough` are already-RESOLVED canonical values (from
    center_alias.resolve_center_query) — this function does no text matching
    of its own, on purpose, so there's exactly one place alias resolution
    happens rather than two copies that could drift."""
    results = []
    for c in index.get("candidates", []):
        if license_type and c.get("license_type") != license_type:
            continue
        if center and center not in (c.get("centers_mentioned") or []):
            continue
        if borough and borough != c.get("home_borough") and borough not in (c.get("boroughs_mentioned") or []):
            continue
        results.append(c)
    return results


def main():
    parser = argparse.ArgumentParser(description="Build the nightly candidate index")
    parser.add_argument("--client", default="blueline", choices=["blueline"],
                         help="Which ClientConfig to use (only 'blueline' exists today)")
    parser.add_argument("--days", type=int, default=None,
                         help="Active-window override (default: config.default_active_window_days)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    config = BLUELINE_CONFIG  # only real client today; --client is future-proofing
    build_candidate_index(config, active_days=args.days)


if __name__ == "__main__":
    main()


# ================================================================================
# CRON — NOT wired in automatically. Add this by hand, same convention this
# project already uses for every schedule change (see 00_INDEX.md Rule 0F —
# state the exact absolute directory in every command):
#
#   0 3 * * * cd /Users/Aditya/Downloads/BlueLine && set -a && source .env && \
#     set +a && /usr/local/bin/python3.11 candidate_index.py >> \
#     /Users/Aditya/Downloads/BlueLine/cron_output.log 2>&1
#
# Picked 3am ET as a placeholder (quiet hours, before the 9am daily agent
# run) — adjust to whatever time makes sense once this has run manually a
# few times and you trust its duration/output.
# ================================================================================
