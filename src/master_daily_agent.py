#!/usr/bin/env python3
"""
BlueLine Staffing — Master Daily Agent
Version: 2.6 | Date: 2026-07-02  # [FIXED 2026-07-04] was stale at 2.5; runtime log already said v2.6 since Round 11
=====================================================================================
RECONCILIATION + HARDENING NOTICE (v2.4→v2.5, 2026-07-02, Round 7) — READ FIRST
=====================================================================================
v2.5 adds three hardening fixes on top of the v2.4 reconciliation below, made at
Aditya's explicit request for "maximum compliance, no duplication of messages,
opt-out ironclad" before this file is deployed to replace the real cron script:
  - [HARDENED] Process lock (LOCK_PATH, acquire_lock()/release_lock()) — closes a
    real double-send risk that existed even after the v2.4 reconciliation: if cron
    fires twice, or a manual run overlaps the scheduled one, two processes could
    both read the same "no existing contact yet" snapshot and both create a
    contact + send an intro SMS to the same candidate. Per-message dedup logic
    can't catch this because it happens before either process has any in-memory
    state to dedup against. Now only one process can hold the lock at a time.
  - [HARDENED] send_sms() hard opt-out guard — every send, from every caller, is
    now re-checked against STATE_OPTOUTS/BLOCKED_NUMBERS at send time, read fresh
    from disk, independent of the calling step's own pre-check. Defense-in-depth:
    no current or future code path can physically send to an opted-out number
    even if its own opt-out logic has a bug.
  - [HARDENED] step2_new_leads() no longer silently loses a candidate whose Quo
    contact was created but whose intro SMS failed to send — previously they'd be
    silently skipped as a "duplicate" on every future run since the contact now
    exists, and no one would ever find out they were never actually messaged. Now
    flagged to master_needs_human_review.txt.
See DYLAN_AUDIT_2026-07-01_FULL.md Round 7 (hardening addendum) for the full
write-up and the tests added for each of these three fixes.
=====================================================================================
RECONCILIATION NOTICE (v2.4, 2026-07-02, Round 7) — READ THIS BEFORE TRUSTING BUG NUMBERS
=====================================================================================
This project's src/ copy of this file and the actually-deployed copy at
~/Downloads/BlueLine/master_daily_agent.py (the one Aditya's cron job really runs)
diverged for several days into two separate fix histories that were never
reconciled — discovered 2026-07-02 when this project was given real read/write
access to ~/Downloads for the first time and the two files were diffed directly.
Both histories independently used the label "BUG-15" for two COMPLETELY DIFFERENT
bugs (see below) — do not trust a bare "BUG-15" reference anywhere in this
project's docs without checking which lineage it means. This version merges both
histories into one file. See DYLAN_AUDIT_2026-07-01_FULL.md Round 7 for the full
write-up, and 00_INDEX.md Rule 0E for the process change this triggered (verify
the REAL deployed file, not just this project's src/, before claiming this
project's docs describe production accurately).

Fixes carried in from the real deployed v2.3 (~/Downloads/BlueLine, dated
2026-06-30) that this project's src/ was missing until this reconciliation:
  - [DEPLOYED-BUG-14] step3 handled_ids was only updated on disk (append_to_set),
             not in the in-memory set already loaded for this run — the same
             msg_id could be processed twice in one run if a contact appeared in
             multiple conversations. Root cause of the "Whitaker duplicate-message
             incident." Fixed: handled_ids.add(msg_id) added to all four branches.
  - [DEPLOYED-BUG-15] INTEREST_KEYWORDS was too broad ("ok","okay","send","info",
             "ready","i am","i'm") — caused the document checklist to re-fire on
             any casual reply from candidates already deep in the pipeline. Root
             cause of the "Joyelette Miller repeat-blast incident" (4x) and "Torri
             Allen" repeat-send, both referenced in this project's own master
             context doc Bug Fix Sync section. Fixed: (a) INTEREST_KEYWORDS
             tightened back down, (b) DOCS_SENT_KEYWORDS added — routes to human
             review instead of re-sending, (c) UPDATE_REQUEST_KEYWORDS added —
             same, (d) STATE_CHECKLIST_SENT (master_checklist_sent.txt) added —
             gates the checklist send so it only ever fires once per phone.
  - [DEPLOYED-CHANGE] BOROUGH_ABBREV added — Step 2 stores an abbreviated borough
             in the Quo contact lastName for OpenPhone-UI readability. Ported
             faithfully including its known pre-existing minor inconsistency
             with extract_role_borough_from_contact() (see inline comment at the
             fix site) — not silently "improved" as a side effect of reconciling.

Fixes already in this project's src/ that the deployed v2.3 file does NOT have —
confirmed by the same diff, meaning these are LIVE GAPS in the code Aditya's cron
actually runs today, not just documentation gaps:
  - DYLAN_INTRO has no "Reply STOP to opt out." in the deployed version — a live
    TCPA compliance gap on every first-contact SMS sent today.
  - OPTOUT_KEYWORDS in the deployed version is missing "please stop", "take me
    off", "wrong number", "leave me alone", "dont text"/"do not text" — those
    phrases are NOT auto-processed as opt-outs on the live system today.
  - DOCUMENT_CHECKLIST_MSG in the deployed version still contains emoji.
  This project's src/ is NOT yet deployed back to ~/Downloads/BlueLine — see
  09_GO_LIVE_READINESS.md for the explicit decision needed before that happens.

[PRE-RECONCILIATION HISTORY — this project's src/ lineage only, before the
above merge. "BUG-15" through "BUG-18" below refer to THIS lineage, not the
deployed-file "DEPLOYED-BUG-14/15" above — same number, different bugs.]
Fixes in v2.2 (found during full doc+code audit, 2026-07-01):
  - [BUG-15] DYLAN_INTRO had no "Reply STOP to opt out." despite 07_COMPLIANCE.md stating
             every first-contact message includes it. Added.
  - [BUG-16] OPTOUT_KEYWORDS was missing "please stop", "take me off", "wrong number",
             "leave me alone", "dont text"/"do not text", "dont contact" — all already
             documented in 07_COMPLIANCE.md/05_PIPELINE_REFERENCE.md as auto-handled.
             Widened to match.
  - [BUG-17] INTEREST_KEYWORDS widened to match 05_PIPELINE_REFERENCE.md's documented set
             (added yup, "i am/i'm interested", "of course", "open"/"open to it",
             "sign me up", "count me in", "let's/lets do it", "i'm in"/"im in", "send info",
             "tell me more" — previously only a narrower subset was recognized).
             [SUPERSEDED 2026-07-02 — see DEPLOYED-BUG-15 above; this widening
             reintroduced the exact bug the deployed file had already fixed a day
             earlier. INTEREST_KEYWORDS is now re-tightened to the deployed set.]
  - [BUG-18] DOCUMENT_CHECKLIST_MSG contained emoji, violating 06_COMMUNICATIONS.md's own
             Ground Rule #3 ("No emojis in SMS"). Removed.
Fixes in v2.1 (2026-06-29):
  - [BUG-01] CSV license column: was reading "License" (YES/NO boolean), now reads "Role" (RN/LPN/CNA)
  - [BUG-02] Participant structure: conversation participants are strings not dicts
  - [BUG-03] Timestamp parsing: lastActivityAt is ISO string not int ms; parse correctly
  - [BUG-04] Message timestamps: createdAt is ISO string; parse before comparison
  - [BUG-05] Wrong messages endpoint: /conversations/{id}/messages returns 404;
             use /messages?phoneNumberId=...&participants[]=... instead
  - [BUG-06] Message text field: field is "text" not "body"/"content"
  - [BUG-07] Step 3 interest handler: upgrade1 could SKIP an interested candidate;
             interested candidates always get DOCUMENT_CHECKLIST_MSG, no upgrade1 gate
  - [BUG-08] Step 1 dead Claude call: generated msg_text then discarded it; removed
  - [BUG-09] Step 3 opt-out rename: convo.get("contactId") always None; use phone lookup
  - [BUG-10] Step 3 role/borough: convo.get("lastName") doesn't exist; now looks up contact
  - [BUG-11] Step 1 role/borough: participant.get("lastName") always fails; now looks up contact
  - [BUG-12] upgrade1 get_quo_history wrong endpoint: /conversations?phoneNumber= returns 404
             Fixed in upgrade1_context_aware_messaging.py
  - [BUG-13] upgrade1 message field: was "body"/"content"; fixed to "text"

Run order (as of v2.6, Round 11): Step 1 (re-engage, 72h stall window) →
DEDUP → Step 2 (new leads, unlimited/run). Step 3 (SMS replies) is no longer
part of the automatic sequence — it runs exclusively, continuously, inside
master_sms_poll_service.py, because "reply instantly" is now a hard
requirement that a once/day (or even every-30-min) cron cannot satisfy, and
running it in two places at once created a duplicate-response race. Pass
--include-step3 to main() to run it here anyway, for manual debugging only.
"""

import sys
import os
import re
import csv
import time
import hashlib
import logging
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path
import requests
from dotenv import load_dotenv
import anthropic
from upgrade1_context_aware_messaging import get_context_aware_sms  # UPGRADE 1

# ── Environment ────────────────────────────────────────────────────────────────
load_dotenv(dotenv_path=Path.home() / "Downloads" / ".env")

QUO_API_KEY    = os.environ["QUO_API_KEY"]
QUO_PHONE_ID   = os.environ["QUO_PHONE_NUMBER_ID"]
CLAUDE_API_KEY = os.environ["CLAUDE_API_KEY"]

QUO_BASE    = "https://api.openphone.com/v1"
QUO_HEADERS = {"Authorization": QUO_API_KEY, "Content-Type": "application/json"}

client          = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
BLOCKED_NUMBERS = {'+13473572031'}  # Vanessa Ratcliff — opted out
DOWNLOADS       = Path.home() / "Downloads"
STATE_PROCESSED       = DOWNLOADS / "master_processed_contacts.txt"
STATE_OPTOUTS         = DOWNLOADS / "master_permanent_optouts.txt"
STATE_INTERESTS       = DOWNLOADS / "master_handled_interest_replies.txt"
STATE_REVIEW          = DOWNLOADS / "master_needs_human_review.txt"
STATE_TIMESTAMP       = DOWNLOADS / "master_last_run_timestamp.txt"
# [RECONCILED 2026-07-02, Round 7] Ported from the real deployed v2.3 script at
# ~/Downloads/BlueLine/master_daily_agent.py, which had drifted ahead of this
# project's src/ on this specific fix — tracks phones that already received the
# docs checklist so a casual follow-up reply doesn't re-blast it. See BUG-15
# note at INTEREST_KEYWORDS below and DYLAN_AUDIT_2026-07-01_FULL.md Round 7.
STATE_CHECKLIST_SENT  = DOWNLOADS / "master_checklist_sent.txt"
# [ADDED 2026-07-02, Round 12 — explicit rule from Aditya: "for no reason should
# duplicate messages or emails be sent — ever — develop a check for this"] Records
# a timestamped fingerprint of every successful SMS send (phone + exact message
# text). send_sms() checks this BEFORE sending — see DUPLICATE_SEND_COOLDOWN_HOURS
# below — so no caller, current or future, can physically send the same message
# to the same phone twice within the cooldown window. This is defense-in-depth on
# top of (not a replacement for) each step's own per-message dedup logic, the same
# pattern already proven for the opt-out guard on send_sms().
STATE_SMS_FINGERPRINTS = DOWNLOADS / "master_sms_dedup_fingerprints.txt"
DUPLICATE_SEND_COOLDOWN_HOURS = 24
# [ADDED 2026-07-02, Round 12 — explicit rule from Aditya: "hard max limit of 75
# new candidates a day... consider previous 24 hours, not last 30 min"] Records a
# timestamp for every successful NEW_LEAD_SENT in step2_new_leads(). This is a
# genuine rolling 24-hour window (re-checked from this log on every run), not a
# calendar-day counter — closing the exact bug that made the old 30/day cap
# re-grant a fresh budget on every same-day rerun. Applies regardless of which
# client is using Dylan — a universal safety default, not BlueLine-specific.
STATE_NEW_LEAD_SEND_LOG = DOWNLOADS / "master_new_lead_send_timestamps.txt"
NEW_LEAD_ROLLING_CAP        = 75
NEW_LEAD_CAP_WINDOW_HOURS   = 24
CSV_PATH        = DOWNLOADS / "BlueLine" / "CONFIDENTIAL_candidates.csv"
LOG_PATH        = DOWNLOADS / f"master_run_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
# [HARDENED 2026-07-02, Round 7] Process lock — if cron fires twice, or a manual
# run overlaps the scheduled one, two processes reading the same "existing
# contacts" snapshot could both decide a candidate is new and both send an
# intro SMS: a real double-message risk that isn't caught by any per-message
# dedup logic below, because it happens BEFORE either process's in-memory state
# exists. This file-lock closes that at the process level. See LOCK_STALE_SECONDS.
LOCK_PATH             = DOWNLOADS / "master_daily_agent.lock"
LOCK_STALE_SECONDS    = 6 * 3600  # a lock older than this is assumed to be a crashed run, not a live one

# [REMOVED 2026-07-02, Round 11] DAILY_NEW_LEADS / CATCHUP_MAX (formerly 30 and
# 150) — Step 2 no longer caps new-lead outreach; see step2_new_leads().

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("blueline")

run_log: list[dict] = []

def log_action(step: str, contact: str, action: str, detail: str = ""):
    entry = {"timestamp": datetime.now().isoformat(), "step": step,
             "contact": contact, "action": action, "detail": detail}
    run_log.append(entry)
    log.info(f"[{step}] {contact} | {action} | {detail}")

def save_run_log():
    if not run_log:
        return
    with open(LOG_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["timestamp","step","contact","action","detail"])
        w.writeheader()
        w.writerows(run_log)
    log.info(f"Run log saved: {LOG_PATH}")

# ── Process lock (Round 7 hardening) ────────────────────────────────────────────
def acquire_lock() -> bool:
    """Atomically claim LOCK_PATH so only one run of this script can be sending
    messages at a time. Uses O_CREAT|O_EXCL (atomic create-if-absent at the OS
    level) rather than an 'if path.exists()' check, which would itself have a
    race window between the check and the write. Returns True if this process
    now holds the lock and should proceed; False if another live run already
    holds it and this run should exit immediately without sending anything.
    A lock older than LOCK_STALE_SECONDS is treated as an abandoned lock from a
    crashed run (a hard crash could leave the file behind) and is reclaimed —
    reclaiming is itself done through the same atomic path, so two processes
    racing to reclaim a stale lock still can't both win."""
    try:
        fd = os.open(str(LOCK_PATH), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, f"{os.getpid()} {datetime.now().isoformat()}".encode())
        os.close(fd)
        return True
    except FileExistsError:
        try:
            age_seconds = time.time() - LOCK_PATH.stat().st_mtime
        except Exception:
            age_seconds = 0
        if age_seconds > LOCK_STALE_SECONDS:
            log.warning(f"  Lock is {age_seconds/3600:.1f}h old — treating as a crashed prior run, reclaiming.")
            try:
                LOCK_PATH.unlink()
            except FileNotFoundError:
                pass  # another process already reclaimed it first — let it win, we back off
            else:
                return acquire_lock()  # retry once, still through the atomic path
            return False
        return False

def release_lock():
    try:
        LOCK_PATH.unlink()
    except FileNotFoundError:
        pass

# ── State file helpers ──────────────────────────────────────────────────────────
def load_set(path: Path) -> set:
    if path.exists():
        return set(path.read_text(encoding="utf-8").splitlines())
    return set()

def append_to_set(path: Path, value: str):
    with open(path, "a", encoding="utf-8") as f:
        f.write(value + "\n")

def append_to_review(entry: str):
    with open(STATE_REVIEW, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} | {entry}\n")

# ── Round 12: hard duplicate-send guard (send_sms() calls these) ───────────────
def _sms_fingerprint(phone: str, text: str) -> str:
    """Identifies 'this exact message to this exact phone' — NOT just the
    phone, so legitimately different messages to the same candidate (intro,
    then later a rate sheet) are never confused with a duplicate."""
    raw = f"{normalise_phone(phone)}|{text}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def _was_recently_sent(fingerprint: str) -> bool:
    """Reads STATE_SMS_FINGERPRINTS, prunes entries older than 2x the cooldown
    (keeps the file bounded without needing a separate cleanup job), rewrites
    the pruned file, and returns whether `fingerprint` was sent within the
    cooldown window. Pruning at 2x the cooldown (not exactly 1x) leaves a
    little headroom so a fingerprint doesn't get pruned right as it would
    still legitimately block a near-boundary resend."""
    if not STATE_SMS_FINGERPRINTS.exists():
        return False
    now = datetime.now().timestamp()
    retain_cutoff  = now - (DUPLICATE_SEND_COOLDOWN_HOURS * 2 * 3600)
    cooldown_cutoff = now - (DUPLICATE_SEND_COOLDOWN_HOURS * 3600)
    kept_lines = []
    seen_recently = False
    for line in STATE_SMS_FINGERPRINTS.read_text(encoding="utf-8").splitlines():
        if "|" not in line:
            continue
        ts_str, fp = line.split("|", 1)
        ts = parse_iso_ts(ts_str)
        if ts < retain_cutoff:
            continue  # old enough to drop entirely
        kept_lines.append(line)
        if fp == fingerprint and ts >= cooldown_cutoff:
            seen_recently = True
    STATE_SMS_FINGERPRINTS.write_text("\n".join(kept_lines) + ("\n" if kept_lines else ""), encoding="utf-8")
    return seen_recently

def _record_sent_fingerprint(fingerprint: str):
    with open(STATE_SMS_FINGERPRINTS, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()}|{fingerprint}\n")

# ── Round 12: rolling 24h new-lead cap (step2_new_leads() calls these) ─────────
def new_leads_sent_in_window() -> int:
    """Genuine rolling window, re-derived from the log on every call — not a
    calendar-day counter. Also prunes entries older than the window so the
    file doesn't grow forever."""
    if not STATE_NEW_LEAD_SEND_LOG.exists():
        return 0
    cutoff = datetime.now().timestamp() - (NEW_LEAD_CAP_WINDOW_HOURS * 3600)
    kept = []
    for line in STATE_NEW_LEAD_SEND_LOG.read_text(encoding="utf-8").splitlines():
        ts = parse_iso_ts(line)
        if ts >= cutoff:
            kept.append(line)
    STATE_NEW_LEAD_SEND_LOG.write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")
    return len(kept)

def record_new_lead_sent():
    with open(STATE_NEW_LEAD_SEND_LOG, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()}\n")

# ── Timestamp helpers ───────────────────────────────────────────────────────────
def parse_iso_ts(s) -> float:
    """Parse ISO 8601 string or int/float epoch to UTC timestamp (seconds). Returns 0 on failure."""
    if not s:
        return 0.0
    if isinstance(s, (int, float)):
        # Handle milliseconds (> year 2001 in seconds = 978307200)
        return s / 1000.0 if s > 1e10 else float(s)
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()
    except Exception:
        return 0.0

def seven_days_ago_ts() -> float:
    return (datetime.now(timezone.utc) - timedelta(days=7)).timestamp()

# [FIX 2026-07-02, Round 11 — explicit rule from Aditya] Stall window for
# Step 1 re-engagement lowered from 96h to 72h. Kept as a single named
# constant (not a magic number inline) so it's a one-line change if this
# ever needs adjusting again.
STALL_WINDOW_HOURS = 72

def stall_cutoff_ts() -> float:
    return (datetime.now(timezone.utc) - timedelta(hours=STALL_WINDOW_HOURS)).timestamp()

# ── Quo API helpers ─────────────────────────────────────────────────────────────
# [FIX 2026-07-02, Round 10 — found live while diagnosing an apparent SMS poll
# service hang] None of requests.get/post/patch/delete calls in this file set a
# timeout. Python's requests library defaults to timeout=None ("wait forever")
# when omitted — so a single stalled Quo connection (network stall, slow
# response, proxy hiccup) freezes the entire step3_sms_reply_handler() loop,
# and therefore the whole 24/7 SMS poll service, indefinitely with zero error
# output. This is inconsistent with email_context_bridge.py, which already
# sets timeout=15 on its Quo calls. QUO_REQUEST_TIMEOUT_SECONDS applied to
# every Quo HTTP call in this file below — turns a silent infinite hang into a
# bounded failure that the poll service's own retry/backoff loop can catch.
QUO_REQUEST_TIMEOUT_SECONDS = 20

def quo_get(path: str, params=None) -> dict:
    r = requests.get(f"{QUO_BASE}{path}", headers=QUO_HEADERS, params=params or {},
                      timeout=QUO_REQUEST_TIMEOUT_SECONDS)
    r.raise_for_status()
    return r.json()

def quo_post(path: str, body: dict) -> dict:
    r = requests.post(f"{QUO_BASE}{path}", headers=QUO_HEADERS, json=body,
                       timeout=QUO_REQUEST_TIMEOUT_SECONDS)
    if not r.ok:
        log.error(f"API {r.status_code} on POST {path} | {r.text[:200]}")
    r.raise_for_status()
    return r.json()

def quo_get_raw(path: str, params=None) -> requests.Response:
    return requests.get(f"{QUO_BASE}{path}", headers=QUO_HEADERS, params=params or {},
                         timeout=QUO_REQUEST_TIMEOUT_SECONDS)

def send_sms(to: str, text: str) -> str:
    """Send SMS; returns message ID or '' on failure.
    [HARDENED 2026-07-02, Round 7] Hard opt-out guard: every send, from every
    caller in this file, is checked against STATE_OPTOUTS and BLOCKED_NUMBERS
    read fresh from disk at send time — not relying on whatever pre-check the
    calling step already did. This is defense-in-depth: it means no future
    code path, bug, or new step added to this file can ever physically place
    an SMS to a number that has opted out, even if that path's own opt-out
    check is missing or wrong. If this guard trips, something upstream has a
    real bug and needs investigating — it should never legitimately fire."""
    norm_to = normalise_phone(to)
    if norm_to in BLOCKED_NUMBERS or norm_to in load_set(STATE_OPTOUTS):
        log.error(f"  REFUSED TO SEND: {norm_to} is opted-out/blocked. This should be unreachable — "
                  f"the calling step's own opt-out check should have skipped this number already. "
                  f"Investigate the caller, do not remove this guard.")
        return ""

    # [HARDENED 2026-07-02, Round 12] Hard duplicate-send guard, same pattern
    # and same rationale as the opt-out guard above: every caller, from every
    # step, current or future, is checked here — not relying on each step's
    # own per-message dedup logic, which has to be correct in every branch to
    # actually work. Blocks the exact same message text to the exact same
    # phone within DUPLICATE_SEND_COOLDOWN_HOURS. See _sms_fingerprint().
    fingerprint = _sms_fingerprint(to, text)
    if _was_recently_sent(fingerprint):
        log.error(f"  REFUSED TO SEND: identical message already sent to {norm_to} within the last "
                  f"{DUPLICATE_SEND_COOLDOWN_HOURS}h. This should be unreachable under normal "
                  f"operation — investigate the caller, do not remove this guard.")
        return ""

    body = {"content": text, "from": QUO_PHONE_ID, "to": [to]}
    try:
        resp = quo_post("/messages", body)
        msg_id = resp.get("data", {}).get("id", "")
        if msg_id:
            _record_sent_fingerprint(fingerprint)
        return msg_id
    except Exception as e:
        if "Opted Out" in str(e) or "0201400" in str(e) or "400 Client Error" in str(e):
            log.warning(f"Skipping {to} — opted out at carrier")
            return ""
        raise

def get_all_contacts() -> list[dict]:
    """Fetch all Quo contacts (paginated)."""
    contacts, cursor = [], None
    while True:
        params = {"pageSize": 100}
        if cursor:
            params["pageToken"] = cursor
        data = quo_get("/contacts", params)
        contacts.extend(data.get("data", []))
        cursor = data.get("nextPageToken")
        if not cursor:
            break
    return contacts

def get_contact_by_phone(phone: str) -> dict | None:
    """Look up a single Quo contact by phone number. Returns contact dict or None."""
    contacts = get_all_contacts()
    norm = normalise_phone(phone)
    for c in contacts:
        for p in (c.get("defaultFields", {}).get("phoneNumbers") or []):
            if normalise_phone(p.get("value", "")) == norm:
                return c
    return None

def get_messages_for_phone(phone: str, days: int = 7) -> list[dict]:
    """
    [FIX BUG-05] Fetch messages for a specific participant using the correct endpoint.
    /messages?phoneNumberId=...&participants[]=+1xxx
    Message object: {id, to, from, text, direction, createdAt, ...}
    """
    params = [
        ("phoneNumberId", QUO_PHONE_ID),
        ("participants[]", phone),
        ("pageSize", "50"),
    ]
    try:
        r = quo_get_raw("/messages", params)
        if not r.ok:
            return []
        return r.json().get("data", [])
    except Exception:
        return []

def get_recent_conversations(days: int = 7) -> list[dict]:
    """
    Fetch conversations with activity in the last N days.
    Participants field is a list of phone number strings.
    """
    cutoff_ts = (datetime.now(timezone.utc) - timedelta(days=days)).timestamp()
    conversations, cursor = [], None
    while True:
        params = {"phoneNumberId": QUO_PHONE_ID, "pageSize": 100}
        if cursor:
            params["pageToken"] = cursor
        data = quo_get("/conversations", params)
        batch = data.get("data", [])
        for convo in batch:
            last_ts = parse_iso_ts(convo.get("lastActivityAt"))
            if last_ts >= cutoff_ts:
                conversations.append(convo)
        # Stop if oldest in batch is before our window
        if batch and parse_iso_ts(batch[-1].get("lastActivityAt")) < cutoff_ts:
            break
        cursor = data.get("nextPageToken")
        if not cursor:
            break
    return conversations

# ── Phone normalisation ─────────────────────────────────────────────────────────
def normalise_phone(raw: str) -> str:
    digits = re.sub(r"\D", "", raw or "")
    if len(digits) == 10:
        return "+1" + digits
    if len(digits) == 11 and digits.startswith("1"):
        return "+" + digits
    return "+" + digits if digits else ""

def normalise_name(name: str) -> str:
    name = name.lower().strip()
    name = unicodedata.normalize("NFD", name)
    name = "".join(c for c in name if unicodedata.category(c) != "Mn")
    name = re.sub(r"[^a-z0-9 ]", "", name)
    return re.sub(r"\s+", " ", name).strip()

# ── Borough detection ───────────────────────────────────────────────────────────
BOROUGH_KEYWORDS = {
    "Manhattan": ["manhattan", "new york, ny", "new york ny", "10001","10002","10003",
                  "10004","10005","10006","10007","10009","10010","10011","10012",
                  "10013","10014","10016","10017","10018","10019","10020","10021",
                  "10022","10023","10024","10025","10026","10027","10028","10029",
                  "10030","10031","10032","10033","10034","10035","10036","10037",
                  "10038","10039","10040","10044","10065","10069","10075","10128"],
    "Brooklyn":  ["brooklyn","11201","11203","11204","11205","11206","11207","11208",
                  "11209","11210","11211","11212","11213","11214","11215","11216",
                  "11217","11218","11219","11220","11221","11222","11223","11224",
                  "11225","11226","11228","11229","11230","11231","11232","11233",
                  "11234","11235","11236","11237","11238","11239"],
    "Queens":    ["queens","astoria","flushing","jamaica","11354","11355","11356",
                  "11357","11358","11360","11361","11362","11363","11364","11365",
                  "11366","11367","11368","11369","11370","11371","11372","11373",
                  "11374","11375","11377","11378","11379","11385","11411","11412",
                  "11413","11414","11415","11416","11417","11418","11419","11420",
                  "11421","11422","11423","11424","11425","11426","11427","11428",
                  "11429","11430","11432","11433","11434","11435","11436"],
    "Bronx":     ["bronx","10451","10452","10453","10454","10455","10456","10457",
                  "10458","10459","10460","10461","10462","10463","10464","10465",
                  "10466","10467","10468","10469","10470","10471","10472","10473",
                  "10474","10475"],
    "Staten Island": ["staten island","10301","10302","10303","10304","10305",
                      "10306","10307","10308","10309","10310","10312","10314"],
}

def detect_borough(text: str) -> str:
    t = (text or "").lower()
    for borough, keywords in BOROUGH_KEYWORDS.items():
        if any(kw in t for kw in keywords):
            return borough
    return "NY"

# [RECONCILED 2026-07-02, Round 7] Ported from the real deployed v2.3 script —
# abbreviated borough form stored in the Quo contact lastName for readability
# in the OpenPhone UI (e.g. "CNA, Bklyn" instead of "CNA, Brooklyn").
BOROUGH_ABBREV = {
    "Manhattan":   "Mhtn",
    "Brooklyn":    "Bklyn",
    "Queens":      "Qns",
    "Bronx":       "Bx",
    "Staten Island": "SI",
    "NY":          "NY",
}

VALID_ROLES = {"RN", "LPN", "CNA", "HHA", "RNS", "MA", "CMA"}

def extract_role_borough_from_contact(contact: dict) -> tuple[str, str]:
    """
    Parse role + borough from contact defaultFields.lastName.
    Standard format: 'RN, Queens'. Handles legacy malformed formats gracefully.
    """
    last = (contact.get("defaultFields", {}).get("lastName") or "").strip()
    if "," in last:
        parts = last.split(",", 1)
        role_candidate = parts[0].strip().upper()
        if role_candidate in VALID_ROLES:
            return role_candidate, parts[1].strip().rstrip(")")
    # Fallback: scan the full string for known role tokens
    last_upper = last.upper()
    for role in ("RN", "LPN", "CNA", "HHA", "RNS"):
        if role in last_upper:
            return role, "NY"
    return "CNA", "NY"

# ── Message templates ───────────────────────────────────────────────────────────
# [FIX 2026-07-01] Added "Reply STOP to opt out." — 07_COMPLIANCE.md states this is a
# non-negotiable requirement on every first-contact message and had documented it as
# already present. It was not. This closes that TCPA gap.
DYLAN_INTRO = (
    "Hi {first_name}, this is Dylan from BlueLine Staffing. "
    "We place CNAs, LPNs, and RNs at facilities across NYC. "
    "Are you currently open to {license_type} shifts? "
    "Reply YES and I'll send you shift details and rates right away. "
    "Reply STOP to opt out."
)

# [FIX 2026-07-01] Removed emoji (📋/📍/📧) — violated 06_COMMUNICATIONS.md Ground Rule #3
# ("No emojis in SMS") which this exact template was supposed to already follow.
DOCUMENT_CHECKLIST_MSG = (
    "Great! Here's what we need to get you started:\n\n"
    "REQUIRED DOCUMENTS:\n"
    "1. Physical (within 1 year)\n"
    "2. Immunization titers (MMR, Varicella, Hep B)\n"
    "3. Government-issued photo ID\n"
    "4. Nursing license (active, NYS)\n"
    "5. Chest X-ray OR 2-step PPD (within 1 year)\n"
    "6. COVID vaccination card OR test results\n"
    "7. BLS/CPR card (within 2 years)\n\n"
    "OUR RATES:\n"
    "CNA: $22–$26/hr | LPN: $34–$40/hr | RN: $48–$58/hr\n"
    "AM (7a–3p) | PM (3p–11p) | NOC (11p–7a)\n\n"
    "Email your documents to: info@bluelinestaffing.com\n"
    "What shifts work best for you? (AM / PM / NOC / Flexible)"
)

# [RECONCILED 2026-07-02, Round 7 — SUPERSEDES the 2026-07-01 "BUG-17 widened"
# version of this set below.] The real deployed v2.3 script at
# ~/Downloads/BlueLine/master_daily_agent.py had ALREADY tightened this set on
# 2026-06-30, one day before this project's own "BUG-17" widened it back out —
# the two changes moved in opposite directions on the same line of code because
# they happened in two diverged copies of this file that never got reconciled.
# The deployed tightening was a real production fix, not a stylistic choice:
# generic tokens ("ok","okay","send","i am","i'm") caused the document
# checklist to re-fire on casual replies from candidates already deep in the
# pipeline — the "Joyelette Miller repeat-blast incident" (4x) and "Torri
# Allen" repeat-send referenced in this project's own master context doc
# Bug Fix Sync section. This project's src/ never had that incident's fix
# until now. Re-tightened to match the deployed, incident-tested set.
INTEREST_KEYWORDS = {"yes","yep","yeah","sure","interested",
                     "definitely","absolutely","asap","available",
                     "tell me more","let me know","consent","proceed"}

# [RECONCILED 2026-07-02, Round 7 — ported from deployed v2.3, part of the same
# BUG-15 fix above.] Candidate signals they already sent documents — must NOT
# be treated as new interest (would re-send the checklist); route to human
# review instead so Aditya can check the inbox.
DOCS_SENT_KEYWORDS = {"i sent","i emailed","already sent","already emailed",
                      "sent everything","sent all","i submitted","did you get",
                      "did you receive","have you received","i attached","i forwarded",
                      "check your email","i uploaded"}

# [RECONCILED 2026-07-02, Round 7 — ported from deployed v2.3, same BUG-15
# fix.] Candidate asking for a status update — route to human review, not
# treated as new interest.
UPDATE_REQUEST_KEYWORDS = {"update","any news","heard back","how long",
                           "when will","still waiting","any response","any word",
                           "following up","check in","checking in","looking for a",
                           "have you submitted","been submitted","any update"}

# [FIX 2026-07-01] Widened to match what 07_COMPLIANCE.md and 05_PIPELINE_REFERENCE.md
# already documented (and promised to candidates/regulators) as auto-handled opt-out
# phrases. Previously "please stop", "take me off", "wrong number", "leave me alone",
# "dont text"/"do not text" were NOT in this set — those messages were silently falling
# through to the human-review queue instead of being auto-processed as opt-outs.
OPTOUT_KEYWORDS   = {"stop","unsubscribe","remove","opt out","optout",
                     "dont text","do not text","dont contact","do not contact",
                     "don't contact","wrong number","take me off","please stop",
                     "no thanks","not interested","leave me alone"}

# ── STEP 3: SMS Reply Handler ───────────────────────────────────────────────────
def step3_sms_reply_handler():
    log.info("═══ STEP 3: SMS Reply Handler ═══")
    handled_ids = load_set(STATE_INTERESTS)
    optouts     = load_set(STATE_OPTOUTS)
    cutoff_ts   = seven_days_ago_ts()

    conversations = get_recent_conversations(days=7)
    log.info(f"  Conversations with recent activity: {len(conversations)}")

    for convo in conversations:
        # [FIX BUG-02] participants is a list of phone strings, not dicts
        participants = convo.get("participants", [])
        if not participants:
            continue
        phone = normalise_phone(participants[0])
        name  = convo.get("name") or phone

        if not phone or phone in optouts or phone in BLOCKED_NUMBERS:
            continue

        # [FIX BUG-05] Use correct messages endpoint
        messages = get_messages_for_phone(phone, days=7)
        inbound_recent = [
            m for m in messages
            if m.get("direction") == "incoming"
            # [FIX BUG-04] parse ISO timestamp before comparing
            and parse_iso_ts(m.get("createdAt")) >= cutoff_ts
        ]

        for msg in inbound_recent:
            msg_id = msg.get("id", "")
            if msg_id in handled_ids:
                continue

            # [FIX BUG-06] field is "text" not "body"/"content"
            text = (msg.get("text") or "").strip().lower()

            # Opt-out
            if any(kw in text for kw in OPTOUT_KEYWORDS):
                # [FIX BUG-09] Look up contact by phone to rename
                contact = get_contact_by_phone(phone)
                if contact:
                    try:
                        requests.patch(
                            f"{QUO_BASE}/contacts/{contact['id']}",
                            headers=QUO_HEADERS,
                            json={"defaultFields": {
                                "firstName": f"DO NOT MESSAGE - {contact.get('defaultFields', {}).get('firstName', phone)}",
                                "lastName": ""
                            }},
                            timeout=QUO_REQUEST_TIMEOUT_SECONDS,
                        )
                    except Exception as e:
                        log.warning(f"  Could not rename opt-out contact {phone}: {e}")
                append_to_set(STATE_OPTOUTS, phone)
                append_to_set(STATE_INTERESTS, msg_id)
                handled_ids.add(msg_id)  # [RECONCILED 2026-07-02, Round 7 — ported real BUG-14] update
                # in-memory set immediately, not just the on-disk file — otherwise the same msg_id
                # could be processed twice in one run if a contact appeared in multiple conversations
                # (e.g. after a dedup failure). Root cause of the "Whitaker duplicate-message incident"
                # per the deployed v2.3 script's fix history. Applied to all three branches below too.
                log_action("STEP3", name, "OPT_OUT", phone)

            # [RECONCILED 2026-07-02, Round 7 — ported from deployed v2.3, part of the real BUG-15
            # fix] Candidate says they already sent docs — must NOT be treated as new interest
            # (would re-send the checklist). Route to human review instead.
            elif any(kw in text for kw in DOCS_SENT_KEYWORDS):
                append_to_review(f"STEP3 | {name} | {phone} | DOCS SENT — check inbox: {text[:120]}")
                append_to_set(STATE_INTERESTS, msg_id)
                handled_ids.add(msg_id)
                log_action("STEP3", name, "DOCS_SENT_FLAGGED_FOR_REVIEW", text[:80])

            # [RECONCILED 2026-07-02, Round 7 — ported from deployed v2.3, same BUG-15 fix]
            # Candidate asking for a status update — route to human review, not treated as interest.
            elif any(kw in text for kw in UPDATE_REQUEST_KEYWORDS):
                append_to_review(f"STEP3 | {name} | {phone} | UPDATE REQUEST: {text[:120]}")
                append_to_set(STATE_INTERESTS, msg_id)
                handled_ids.add(msg_id)
                log_action("STEP3", name, "UPDATE_REQUEST_FLAGGED_FOR_REVIEW", text[:80])

            # [FIX BUG-07] Interest — send DOCUMENT_CHECKLIST_MSG only if not already sent to this phone.
            # [RECONCILED 2026-07-02, Round 7 — ported real BUG-15 fix from deployed v2.3] Previously
            # (and still, until this reconciliation) this branch always sent the checklist on any
            # INTEREST_KEYWORDS match, with no memory of whether it had already been sent — the exact
            # cause of the Joyelette Miller (4x) and Torri Allen repeat-blast incidents documented in
            # this project's master context doc Bug Fix Sync section. Now gated on STATE_CHECKLIST_SENT.
            elif any(kw in text for kw in INTEREST_KEYWORDS):
                checklist_sent_phones = load_set(STATE_CHECKLIST_SENT)
                if phone in checklist_sent_phones:
                    # Checklist already sent — this is a follow-up, not new consent; a human should see it.
                    append_to_review(f"STEP3 | {name} | {phone} | RE-INTEREST (checklist already sent): {text[:120]}")
                    append_to_set(STATE_INTERESTS, msg_id)
                    handled_ids.add(msg_id)
                    log_action("STEP3", name, "RE_INTEREST_FLAGGED_FOR_REVIEW", text[:80])
                else:
                    send_sms(phone, DOCUMENT_CHECKLIST_MSG)
                    append_to_set(STATE_CHECKLIST_SENT, phone)
                    append_to_set(STATE_INTERESTS, msg_id)
                    handled_ids.add(msg_id)
                    log_action("STEP3", name, "INTEREST_REPLY_SENT", text[:80])

            # Unrecognised — flag for human review
            else:
                append_to_review(f"STEP3 | {name} | {phone} | UNRECOGNISED: {text[:120]}")
                append_to_set(STATE_INTERESTS, msg_id)
                handled_ids.add(msg_id)
                log_action("STEP3", name, "FLAGGED_FOR_REVIEW", text[:80])

# ── STEP 1: Re-engage Stalled Contacts ─────────────────────────────────────────
def step1_reengage_stalled():
    log.info("═══ STEP 1: Re-engage Stalled Contacts ═══")
    processed     = load_set(STATE_PROCESSED)
    optouts       = load_set(STATE_OPTOUTS)
    stale_cutoff  = stall_cutoff_ts()

    conversations = get_recent_conversations(days=7)

    for convo in conversations:
        # [FIX BUG-02] participants is a list of phone strings
        participants = convo.get("participants", [])
        if not participants:
            continue
        phone = normalise_phone(participants[0])
        name  = convo.get("name") or phone

        if not phone:
            continue
        if phone in optouts or phone in BLOCKED_NUMBERS:
            continue
        if phone not in processed:
            continue  # Not yet messaged via CSV — Step 2 handles new

        # [FIX BUG-03] Parse ISO timestamp correctly
        last_ts = parse_iso_ts(convo.get("lastActivityAt"))
        if last_ts >= stale_cutoff:
            continue  # Recent activity — not stalled

        # [FIX BUG-08] Removed dead Claude call — upgrade1 handles message generation
        # [FIX BUG-10/11] Look up contact to get correct role + borough for upgrade1
        role, borough = "CNA", "NY"
        contact = get_contact_by_phone(phone)
        if contact:
            role, borough = extract_role_borough_from_contact(contact)

        sms = get_context_aware_sms(name, phone, role, borough)
        if sms:
            send_sms(phone, sms)
            log_action("STEP1", name, "REENGAGE_SENT", sms[:80])
        else:
            log_action("STEP1", name, "REENGAGE_SKIPPED", "upgrade1: context skip")

# ── DUPLICATE MERGER ───────────────────────────────────────────────────────────
def merge_duplicate_contacts():
    log.info("═══ DEDUP: Merging duplicate contacts ═══")
    contacts = get_all_contacts()
    log.info(f"  Total contacts fetched: {len(contacts)}")

    groups: dict[tuple, list] = {}
    for c in contacts:
        df        = c.get("defaultFields", {})
        first     = (df.get("firstName") or "").strip()
        norm_name = normalise_name(first)

        phones   = df.get("phoneNumbers") or []
        norm_ph  = normalise_phone(phones[0].get("value", "")) if phones else ""

        if not norm_name or not norm_ph:
            continue

        key = (norm_name, norm_ph)
        groups.setdefault(key, []).append(c)

    merged_count = 0
    for key, group in groups.items():
        if len(group) < 2:
            continue

        def completeness(c):
            df = c.get("defaultFields", {})
            fields = [df.get("firstName"), df.get("lastName"),
                      df.get("emails"), df.get("phoneNumbers")]
            return sum(1 for f in fields if f)

        group.sort(key=completeness, reverse=True)
        winner, dupes = group[0], group[1:]

        winner_emails = {e.get("value") for e in (winner.get("defaultFields", {}).get("emails") or [])}
        extra_emails  = []
        for d in dupes:
            for e in (d.get("defaultFields", {}).get("emails") or []):
                if e.get("value") not in winner_emails:
                    extra_emails.append(e)
                    winner_emails.add(e.get("value"))

        if extra_emails:
            merged_emails = (winner.get("defaultFields", {}).get("emails") or []) + extra_emails
            try:
                requests.patch(
                    f"{QUO_BASE}/contacts/{winner['id']}",
                    headers=QUO_HEADERS,
                    json={"defaultFields": {"emails": merged_emails}},
                    timeout=QUO_REQUEST_TIMEOUT_SECONDS,
                )
            except Exception as e:
                log.warning(f"  Could not patch winner {winner['id']}: {e}")

        for d in dupes:
            try:
                requests.delete(f"{QUO_BASE}/contacts/{d['id']}", headers=QUO_HEADERS,
                                 timeout=QUO_REQUEST_TIMEOUT_SECONDS)
                log_action("DEDUP", key[0], "DELETED_DUPLICATE", d["id"])
                merged_count += 1
            except Exception as e:
                log.warning(f"  Could not delete dupe {d['id']}: {e}")

    log.info(f"  Duplicates removed: {merged_count}")

# ── STEP 2: New Leads from CSV ──────────────────────────────────────────────────
def step2_new_leads():
    log.info("═══ STEP 2: New Leads from CSV ═══")
    processed = load_set(STATE_PROCESSED)
    optouts   = load_set(STATE_OPTOUTS)

    if not CSV_PATH.exists():
        log.warning(f"  CSV not found: {CSV_PATH}")
        return

    # [FIX 2026-07-02, Round 11, SUPERSEDED by Round 12 below] Round 11 removed
    # the old DAILY_NEW_LEADS=30/day cap entirely (its days-missed catchup math
    # re-granted a fresh 30-lead budget on every same-day rerun, so any cron
    # cadence faster than once/day silently over-sent). Aditya's next explicit
    # rule was a real safety ceiling, done correctly this time: "hard max limit
    # of 75 new candidates a day regardless of client... consider previous 24
    # hours, not last 30 min." NEW_LEAD_ROLLING_CAP (75) is checked against a
    # genuine rolling 24h window re-derived from STATE_NEW_LEAD_SEND_LOG on
    # every run (see new_leads_sent_in_window()) — not a calendar-day counter —
    # so it is correct at any cron cadence, closing Round 11's bug at the root
    # instead of just removing the symptom.
    already_sent_in_window = new_leads_sent_in_window()
    remaining_budget = NEW_LEAD_ROLLING_CAP - already_sent_in_window
    log.info(f"  New leads sent in trailing {NEW_LEAD_CAP_WINDOW_HOURS}h: {already_sent_in_window}/"
             f"{NEW_LEAD_ROLLING_CAP} — {max(0, remaining_budget)} of budget remaining this run")
    if remaining_budget <= 0:
        append_to_review(
            f"STEP2 | SAFETY CAP | {NEW_LEAD_ROLLING_CAP}/{NEW_LEAD_ROLLING_CAP} new candidates "
            f"messaged in the trailing {NEW_LEAD_CAP_WINDOW_HOURS}h — pausing new-lead outreach until "
            f"earlier sends roll out of the window. This is expected safety behavior, not an error. "
            f"No manual action needed — outreach resumes automatically as headroom frees up."
        )
        log.warning("  SAFETY CAP REACHED — 0 new leads will be sent this run.")
        return

    existing_contacts = get_all_contacts()
    existing_phones   = {
        normalise_phone(p.get("value", ""))
        for c in existing_contacts
        for p in (c.get("defaultFields", {}).get("phoneNumbers") or [])
    }
    existing_names = {normalise_name(c.get("defaultFields", {}).get("firstName") or "") for c in existing_contacts}

    sent_count   = 0
    cap_notified = False
    with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if sent_count >= remaining_budget:
                if not cap_notified:
                    append_to_review(
                        f"STEP2 | SAFETY CAP | Reached {NEW_LEAD_ROLLING_CAP}/{NEW_LEAD_ROLLING_CAP} new "
                        f"candidates messaged in the trailing {NEW_LEAD_CAP_WINDOW_HOURS}h mid-run — "
                        f"remaining CSV rows will be picked up automatically on a future run as headroom "
                        f"frees up. Expected safety behavior, not an error."
                    )
                    log.warning(f"  SAFETY CAP REACHED mid-run at {sent_count} sent — stopping for this run.")
                    cap_notified = True
                break

            name     = (row.get("Name") or row.get("name") or "").strip()
            phone    = normalise_phone(row.get("Phone") or row.get("phone") or "")
            # [FIX BUG-01] License type is in "Role" column, not "License" (which is YES/NO boolean)
            license_type = (row.get("Role") or row.get("role") or "CNA").strip().upper()
            location     = (row.get("Location") or row.get("location") or "").strip()

            if not name or not phone:
                continue
            if not phone.startswith("+1"):
                log_action("STEP2", name, "SKIPPED_INTERNATIONAL", phone)
                continue
            if phone in optouts or phone in processed or phone in BLOCKED_NUMBERS:
                continue

            norm_ph   = normalise_phone(phone)
            norm_name = normalise_name(name)
            if norm_ph in existing_phones:
                log_action("STEP2", name, "SKIPPED_DUPLICATE_PHONE", phone)
                continue
            if norm_name in existing_names:
                log_action("STEP2", name, "SKIPPED_DUPLICATE_NAME", name)
                continue

            borough      = detect_borough(location) if location else "NY"
            # [RECONCILED 2026-07-02, Round 7 — ported from deployed v2.3] Store the abbreviated
            # borough form for readability in the OpenPhone UI (e.g. "CNA, Bklyn"). Note: this means
            # extract_role_borough_from_contact() will read back the abbreviated form, not the full
            # name detect_borough()/BOROUGH_KEYWORDS use — this inconsistency already exists in the
            # real deployed code today; ported faithfully rather than "fixed" here to avoid changing
            # behavior beyond what's already proven in production. Flagged in
            # DYLAN_AUDIT_2026-07-01_FULL.md Round 7 as a real, pre-existing minor gap worth a
            # deliberate decision later, not silently changed as a side effect of this reconciliation.
            borough_abbr = BOROUGH_ABBREV.get(borough, borough)
            first_name = name.split()[0] if name else "there"

            contact_payload = {
                "defaultFields": {
                    "firstName": name,
                    "lastName":  f"{license_type}, {borough_abbr}",
                },
                "phoneNumbers": [{"phoneNumber": phone, "type": "mobile"}]
            }
            try:
                quo_post("/contacts", contact_payload)
                existing_phones.add(norm_ph)
                existing_names.add(norm_name)
            except Exception as e:
                log.warning(f"  Could not create contact {name}: {e}")
                continue

            intro = DYLAN_INTRO.format(first_name=first_name, license_type=license_type)
            msg_id = send_sms(phone, intro)
            if msg_id:
                append_to_set(STATE_PROCESSED, phone)
                log_action("STEP2", name, "NEW_LEAD_SENT", f"{license_type} | {borough} | {phone}")
                sent_count += 1
            else:
                # [HARDENED 2026-07-02, Round 7] Previously this candidate would be silently
                # lost forever: the Quo contact above was already created, so on every future
                # run they match existing_phones and get SKIPPED_DUPLICATE_PHONE — meaning a
                # send failure here meant no human ever found out this candidate never got
                # messaged. Now flagged for manual review instead of disappearing.
                append_to_review(f"STEP2 | {name} | {phone} | INTRO SMS FAILED TO SEND — Quo contact "
                                  f"was created but no message went out; will be silently skipped as a "
                                  f"'duplicate' on future runs unless handled manually: {license_type} | {borough}")
                log_action("STEP2", name, "SEND_FAILED", phone)
            time.sleep(0.5)

    log.info(f"  New leads messaged this run: {sent_count}")
    STATE_TIMESTAMP.write_text(datetime.now().isoformat())

# ── MAIN ────────────────────────────────────────────────────────────────────────
def main():
    log.info("════════════════════════════════════════")
    log.info("  BlueLine Master Daily Agent v2.6")  # [FIX 2026-07-02, Round 11] Step 3 removed from the automatic sequence; see note below
    log.info(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info("════════════════════════════════════════")

    # [HARDENED 2026-07-02, Round 7] Refuse to run if another instance already holds
    # the lock — see acquire_lock() docstring. This is the fix for the process-level
    # double-send risk (two overlapping runs both deciding a candidate is "new").
    if not acquire_lock():
        log.warning("  Another run is already in progress (lock file present) — "
                     "exiting immediately without sending anything, to prevent duplicate messages.")
        return

    try:
        # [FIX 2026-07-02, Round 11 — explicit rule from Aditya: "replying to
        # candidates instantly is mandatory"] Step 3 (reply handling) is now
        # EXCLUSIVELY the job of master_sms_poll_service.py, which calls
        # step3_sms_reply_handler() directly, continuously, every 90 seconds,
        # 24/7. It used to also run here as part of the daily cron bundle —
        # but acquire_lock()/release_lock() above only protects against two
        # overlapping runs of THIS script (main()); it does nothing to stop
        # this script's Step 3 from overlapping with the poll service's own
        # direct step3_sms_reply_handler() call, since the poll service
        # doesn't go through main() or this lock at all. Running Step 3 from
        # both places at once meant the same inbound reply could be picked
        # up and acted on by two processes at the same time — the same class
        # of failure as the "Whitaker duplicate-message incident" this file
        # already hardened against for in-run duplicates, just triggered
        # across processes instead of within one. Pass --include-step3 on
        # the command line to run it here anyway (manual/debug use only —
        # never do this while the poll service is also running).
        if "--include-step3" in sys.argv:
            try:
                step3_sms_reply_handler()
            except Exception as e:
                log.error(f"STEP 3 failed: {e}", exc_info=True)
        else:
            log.info("  STEP 3 skipped — reply handling is owned exclusively by "
                     "master_sms_poll_service.py. Pass --include-step3 to run it here (debug only).")

        try:
            step1_reengage_stalled()
        except Exception as e:
            log.error(f"STEP 1 failed: {e}", exc_info=True)

        try:
            merge_duplicate_contacts()
        except Exception as e:
            log.error(f"DEDUP failed: {e}", exc_info=True)

        try:
            step2_new_leads()
        except Exception as e:
            log.error(f"STEP 2 failed: {e}", exc_info=True)

        save_run_log()
        log.info("════ Run complete ════")
    finally:
        release_lock()

if __name__ == "__main__":
    main()
