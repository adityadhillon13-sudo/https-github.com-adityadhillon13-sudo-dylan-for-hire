"""
BlueLine Staffing — Candidate File Consolidator
====================================================
Version: 1.0 | 2026-07-02
STATUS: WRITTEN, NOT YET RUN against real data. This is new code — test it on
ONE real "ready for submission" candidate before trusting it on the full list.
See 09_GO_LIVE_READINESS.md before relying on this in production.

PURPOSE
  For every candidate whose Quo pipeline stage (see master_gmail_reviewer.py
  v1.2, `role` field on their Quo contact) is
  PIPELINE:ONBOARD_RETURNED_READY_FOR_SUBMISSION:
  [FIXED 2026-07-02 — this tag originally contained a literal "|", which
  corrupted Quo's pipe-delimited contact rows for any reader, including the
  Pipeline Dashboard. Underscore-only now; see master_gmail_reviewer.py's
  STAGE_* constants for the authoritative values — don't hardcode this
  string elsewhere, import the constant instead.]

    1. Pull every email attachment that candidate has ever sent to
       info@bluelinestaffing.com (reuses master_gmail_reviewer.get_all_attachments)
    2. Classify each attachment individually (MEDICAL / RESUME / ONBOARDING / OTHER)
       via one small Claude call per file — the existing aggregate Vision call
       in master_gmail_reviewer.py never tagged WHICH file was which, only
       whether categories existed somewhere in the pile.
    3. Merge same-category files into three named PDFs:
         {FullName}-{License}-Medical.pdf
         {FullName}-{License}-Resume.pdf
         {FullName}-{License}-Onboarding.pdf
       saved to ~/Downloads/BlueLine/CandidateFiles/
    4. Read the candidate's Quo SMS history and ask Claude which centers (from
       BLUELINE_CENTER_DIRECTORY.md) match what the candidate actually said
       they can commute to. This is BEST-EFFORT — candidates state boroughs in
       free text ("Manhattan and the Bronx"), not a structured center field.
       Always show Aditya which centers were picked and why before he sends.
    5. Compose ONE Gmail DRAFT per matched center (never sent — same
       draft-only invariant as every other script in this project) with the
       three PDFs attached via the real Gmail API (which — unlike the Cowork
       MCP Gmail connector used by the live dashboard — DOES support
       attachments; this is exactly why this step lives here and not in the
       Cowork artifact).
    6. Pushes PIPELINE:SUBMISSION_DRAFTS_READY:<ISO date> to the candidate's
       Quo `role` field — NOT "SUBMITTED". Nothing in this codebase can
       claim a submission happened until Aditya actually clicks Send in
       Gmail. Whether that ever gets auto-detected (e.g. scanning Sent Mail)
       is an open gap — see bottom of this file.

RUN MANUALLY, ON DEMAND — this is not wired into the daily cron. Candidate
document sets and center assignments are exactly the kind of thing that
deserves a human glance before any draft goes near a real facility inbox.

  cd ~/Downloads/BlueLine
  python3.11 master_candidate_file_consolidator.py                 # all ready candidates
  python3.11 master_candidate_file_consolidator.py --email a@b.com  # just one, for testing

DEPENDENCIES (add to master_requirements.txt):
  pypdf       — merging existing PDF attachments + wrapping generated pages
  Pillow      — converting image attachments (jpg/png/tiff) into PDF pages
"""

import json
import logging
import argparse
import requests
from io import BytesIO
from pathlib import Path
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from PIL import Image
from pypdf import PdfWriter, PdfReader

from master_gmail_reviewer import (
    get_gmail_service, get_claude_client, get_all_messages_from_sender,
    get_all_attachments, save_as_draft, BLUELINE_EMAIL,
    QUO_API_KEY, QUO_BASE_URL, STAGE_READY_FOR_SUBMISSION,
)
# [CLEANED 2026-07-02, Round 14 audit] Removed unused `os`, `sys`, and the
# unused `extract_email_address` / `is_system_or_non_candidate_email` imports
# from master_gmail_reviewer — confirmed dead via grep (`\bos\.|\bsys\.`
# returned nothing; neither function name appears as a call site anywhere in
# this file) before removing, per the no-falsify-audit mandate.

log = logging.getLogger("master.consolidator")

DOWNLOADS_DIR      = Path.home() / "Downloads"
OUTPUT_DIR         = DOWNLOADS_DIR / "BlueLine" / "CandidateFiles"
CENTER_DIRECTORY   = DOWNLOADS_DIR / "BlueLine" / "BLUELINE_CENTER_DIRECTORY.md"
STAGE_DRAFTS_READY_PREFIX = "PIPELINE:SUBMISSION_DRAFTS_READY:"


# ── Quo contact lookup (mirrors master_daily_agent.py's get_all_contacts) ──────

def get_all_quo_contacts() -> list:
    if not QUO_API_KEY:
        log.error("QUO_API_KEY not set")
        return []
    headers = {"Authorization": QUO_API_KEY, "Content-Type": "application/json"}
    contacts, page_token = [], None
    while True:
        params = {"pageSize": 100}
        if page_token:
            params["pageToken"] = page_token
        resp = requests.get(f"{QUO_BASE_URL}/contacts", headers=headers, params=params, timeout=15)
        if not resp.ok:
            log.error(f"Quo /contacts {resp.status_code}: {resp.text[:200]}")
            break
        data = resp.json()
        contacts.extend(data.get("data", []))
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return contacts


def find_ready_candidates() -> list:
    """Returns Quo contacts whose role field marks them READY_FOR_SUBMISSION."""
    contacts = get_all_quo_contacts()
    ready = []
    for c in contacts:
        df = c.get("defaultFields", {}) or {}
        if (df.get("role") or "") == STAGE_READY_FOR_SUBMISSION:
            ready.append(c)
    return ready


def get_quo_sms_history_text(phone: str, days: int = 60) -> str:
    """Full-ish SMS history for center-matching (longer window than the
    4-day re-engagement context — we want the borough/shift answers even
    if they were given weeks ago)."""
    if not QUO_API_KEY:
        return ""
    from datetime import datetime, timedelta, timezone
    headers = {"Authorization": QUO_API_KEY, "Content-Type": "application/json"}
    cutoff_ts = (datetime.now(timezone.utc) - timedelta(days=days)).timestamp()
    lines, page_token = [], None
    try:
        while True:
            params = [("participants[]", phone), ("pageSize", "50")]
            if page_token:
                params.append(("pageToken", page_token))
            resp = requests.get(f"{QUO_BASE_URL}/messages", headers=headers, params=params, timeout=15)
            if not resp.ok:
                break
            data = resp.json()
            for msg in data.get("data", []):
                try:
                    ts = datetime.fromisoformat(msg.get("createdAt", "").replace("Z", "+00:00")).timestamp()
                except Exception:
                    ts = 0.0
                if ts < cutoff_ts:
                    continue
                direction = "Dylan" if msg.get("direction") == "outgoing" else "Candidate"
                text = (msg.get("text") or "").strip()
                if text:
                    lines.append(f"{direction}: {text}")
            page_token = data.get("nextPageToken")
            if not page_token:
                break
    except Exception as e:
        log.warning(f"SMS history fetch failed for {phone}: {e}")
    return "\n".join(lines)


# ── Per-attachment classification (NEW — the aggregate Vision call in
#    master_gmail_reviewer.py never told us WHICH file was which) ─────────────

def classify_attachment(att: dict, client) -> str:
    """Returns one of: MEDICAL, RESUME, ONBOARDING, OTHER"""
    ext = Path(att["filename"]).suffix.lower()
    if ext in {".jpg", ".jpeg"}:
        media_type = "image/jpeg"
    elif ext == ".png":
        media_type = "image/png"
    elif ext in {".tiff", ".tif"}:
        media_type = "image/tiff"
    elif ext == ".pdf":
        media_type = "application/pdf"
    else:
        return "OTHER"

    import base64 as b64
    data_b64 = b64.standard_b64encode(att["data"]).decode("utf-8")
    block = ({"type": "document", "source": {"type": "base64", "media_type": media_type, "data": data_b64}}
             if media_type == "application/pdf" else
             {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": data_b64}})

    prompt = (
        "Classify this single document into EXACTLY one category. Reply with "
        "only the category word, nothing else.\n\n"
        "MEDICAL — physical exam, titers/immunization records, chest x-ray, PPD/Quantiferon, "
        "COVID card, BLS/CPR card, nursing license, government ID, Social Security card\n"
        "RESUME — a candidate's professional resume/CV\n"
        "ONBOARDING — BlueLine's own employment/onboarding application form, filled in and "
        "signed by the candidate\n"
        "OTHER — anything that doesn't clearly fit the above"
    )
    try:
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001", max_tokens=10,
            messages=[{"role": "user", "content": [block, {"type": "text", "text": prompt}]}],
        )
        raw = resp.content[0].text.strip().upper()
        for cat in ("MEDICAL", "RESUME", "ONBOARDING", "OTHER"):
            if cat in raw:
                return cat
        return "OTHER"
    except Exception as e:
        log.warning(f"  Classification failed for {att['filename']}: {e}")
        return "OTHER"


# ── PDF assembly ────────────────────────────────────────────────────────────

def attachments_to_pdf_bytes(attachments: list) -> bytes:
    """Merges a list of attachments (mixed PDF/image) into ONE PDF, in the
    order given. Images become single-page PDFs first (via Pillow), then
    everything is merged with pypdf."""
    writer = PdfWriter()
    for att in attachments:
        ext = Path(att["filename"]).suffix.lower()
        if ext == ".pdf":
            reader = PdfReader(BytesIO(att["data"]))
            for page in reader.pages:
                writer.add_page(page)
        elif ext in {".jpg", ".jpeg", ".png", ".tiff", ".tif"}:
            img = Image.open(BytesIO(att["data"])).convert("RGB")
            page_bytes = BytesIO()
            img.save(page_bytes, format="PDF")
            page_bytes.seek(0)
            reader = PdfReader(page_bytes)
            for page in reader.pages:
                writer.add_page(page)
        else:
            log.warning(f"  Skipping unsupported file type in PDF merge: {att['filename']}")

    out = BytesIO()
    writer.write(out)
    return out.getvalue()


def safe_filename_part(s: str) -> str:
    return re_sub_filename(s).strip("-") or "Unknown"


def re_sub_filename(s: str) -> str:
    import re
    return re.sub(r"[^A-Za-z0-9]+", "-", s or "")


# ── Center directory + matching (BEST-EFFORT — see module docstring) ──────────

def load_center_directory() -> str:
    """Raw text of BLUELINE_CENTER_DIRECTORY.md. NOT parsed into a structured
    format here on purpose — its real layout hasn't been verified from this
    session (that file lives only on Aditya's Mac). Handing Claude the raw
    text and asking it to extract name+email pairs is more robust to whatever
    the actual formatting turns out to be than a brittle regex parser would
    be, but VERIFY the emails it picks match the real file before sending
    anything for real."""
    if not CENTER_DIRECTORY.exists():
        log.error(f"Center directory not found at {CENTER_DIRECTORY} — cannot match centers")
        return ""
    return CENTER_DIRECTORY.read_text(encoding="utf-8", errors="replace")


def match_centers(candidate_name: str, sms_history: str, directory_text: str, client) -> list:
    """Returns a list of {"name": str, "email": str, "reason": str} — best-effort,
    always show this to Aditya before trusting it."""
    if not directory_text.strip() or not sms_history.strip():
        return []
    prompt = (
        f"Candidate: {candidate_name}\n\n"
        f"Their SMS conversation (look for which boroughs/centers they said they can work at):\n"
        f"{sms_history[:4000]}\n\n"
        f"Center directory (name, address, email if listed):\n{directory_text[:8000]}\n\n"
        "Return ONLY a JSON array of the centers this candidate is a plausible match for, "
        "based on what they actually said (borough, shift, or a named center). Each item: "
        '{"name": "...", "email": "... or null if not listed in the directory", '
        '"reason": "short phrase quoting what the candidate said"}. '
        "If nothing in their history indicates a borough/center preference, return []."
    )
    try:
        resp = client.messages.create(
            model="claude-opus-4-5", max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = resp.content[0].text.strip()
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(raw)
    except Exception as e:
        log.warning(f"  Center matching failed for {candidate_name}: {e}")
        return []


# ── Quo status push (reuses the exact PATCH pattern from master_gmail_reviewer) ─

def push_drafts_ready_status(contact_id: str) -> bool:
    if not QUO_API_KEY:
        return False
    headers = {"Authorization": QUO_API_KEY, "Content-Type": "application/json"}
    stage = STAGE_DRAFTS_READY_PREFIX + date.today().isoformat()
    try:
        resp = requests.patch(
            f"{QUO_BASE_URL}/contacts/{contact_id}",
            headers=headers, json={"defaultFields": {"role": stage}}, timeout=15,
        )
        return resp.ok
    except Exception as e:
        log.warning(f"  Could not push drafts-ready status: {e}")
        return False


# ── Draft composition (real attachments — real Gmail API, not the Cowork connector) ─

def compose_center_draft(center_email: str, candidate_name: str, license_type: str,
                          reason: str, pdf_files: list) -> MIMEMultipart:
    msg = MIMEMultipart()
    msg["To"] = center_email
    msg["From"] = BLUELINE_EMAIL
    msg["Subject"] = f"New Candidate Submission — {candidate_name} ({license_type or 'License TBD'})"
    body = (
        f"Hi,\n\n"
        f"Submitting {candidate_name} ({license_type or 'license type pending confirmation'}) "
        f"for your consideration.\n\n"
        f"Match reason: {reason or 'candidate indicated availability for your facility/borough'}\n\n"
        f"Documents attached: medical file, resume, signed onboarding application.\n\n"
        f"DRAFT — this has not been sent. Please review before sending.\n\n"
        f"Thanks,\nDylan\nBlueLine Staffing\ninfo@bluelinestaffing.com"
    )
    msg.attach(MIMEText(body, "plain"))
    for filepath, filename in pdf_files:
        with open(filepath, "rb") as f:
            part = MIMEBase("application", "pdf")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
            msg.attach(part)
    return msg


# ── Main per-candidate flow ─────────────────────────────────────────────────

def process_candidate(contact: dict, service, client, directory_text: str) -> dict:
    df = contact.get("defaultFields", {}) or {}
    full_name = (df.get("firstName") or "").strip() or "Unknown Candidate"
    last_name_field = (df.get("lastName") or "").strip()
    license_type = last_name_field.split(",")[0].strip().upper() if "," in last_name_field else ""
    emails = df.get("emails") or []
    sender_email = (emails[0].get("value") if emails else "").strip()
    phones = df.get("phoneNumbers") or []
    phone = (phones[0].get("value") if phones else "").strip()

    if not sender_email:
        log.warning(f"  {full_name}: no email on file — cannot gather attachments, skipping")
        return {"name": full_name, "outcome": "no_email"}

    log.info(f"Processing {full_name} <{sender_email}> ({license_type or 'license unknown'})")

    all_messages = get_all_messages_from_sender(service, sender_email)
    attachments = get_all_attachments(service, all_messages)
    if not attachments:
        log.warning(f"  {full_name}: no attachments found on Gmail — skipping")
        return {"name": full_name, "outcome": "no_attachments"}

    buckets = {"MEDICAL": [], "RESUME": [], "ONBOARDING": [], "OTHER": []}
    for att in attachments:
        cat = classify_attachment(att, client)
        buckets[cat].append(att)
        log.info(f"    {att['filename']} -> {cat}")

    name_part = safe_filename_part(full_name)
    lic_part = safe_filename_part(license_type or "License")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    written = {}
    for cat, suffix in (("MEDICAL", "Medical"), ("RESUME", "Resume"), ("ONBOARDING", "Onboarding")):
        files = buckets[cat]
        if not files:
            log.warning(f"    No {cat} document found for {full_name} — {suffix}.pdf not created")
            continue
        pdf_bytes = attachments_to_pdf_bytes(files)
        out_name = f"{name_part}-{lic_part}-{suffix}.pdf"
        out_path = OUTPUT_DIR / out_name
        out_path.write_bytes(pdf_bytes)
        written[suffix] = (str(out_path), out_name)
        log.info(f"    Wrote {out_path} ({len(files)} source file(s))")

    if len(written) < 3:
        log.warning(f"  {full_name}: only {len(written)}/3 file groups produced — "
                    f"drafting to centers anyway with what exists, but flag this for manual check")

    sms_history = get_quo_sms_history_text(phone) if phone else ""
    centers = match_centers(full_name, sms_history, directory_text, client)
    if not centers:
        log.warning(f"  {full_name}: no centers matched — nothing drafted. "
                    f"Check {CENTER_DIRECTORY} exists and candidate's SMS history mentions a borough.")
        return {"name": full_name, "outcome": "no_centers_matched", "files_written": list(written.keys())}

    pdf_file_list = [v for v in written.values()]
    drafted = []
    for center in centers:
        center_email = center.get("email")
        if not center_email:
            log.warning(f"    Skipping '{center.get('name')}' — no email on file in directory")
            continue
        draft_msg = compose_center_draft(
            center_email, full_name, license_type, center.get("reason", ""), pdf_file_list
        )
        try:
            draft_id = save_as_draft(service, draft_msg, thread_id="")
            log.info(f"    DRAFT created for center '{center.get('name')}' <{center_email}> (id={draft_id})")
            drafted.append({"center": center.get("name"), "email": center_email, "draft_id": draft_id})
        except Exception as e:
            log.error(f"    Failed to create draft for '{center.get('name')}': {e}")

    if drafted:
        push_drafts_ready_status(contact.get("id"))

    return {
        "name": full_name, "outcome": "drafts_created" if drafted else "draft_failures",
        "files_written": list(written.keys()), "centers_drafted": drafted,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", help="Process only this one candidate email (for testing)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    log.info("=== CANDIDATE FILE CONSOLIDATOR: Starting (DRAFT MODE — nothing will be sent) ===")

    service = get_gmail_service()
    client = get_claude_client()
    directory_text = load_center_directory()
    if not directory_text:
        log.error("Aborting — no center directory available. Cannot safely guess facility emails.")
        return

    if args.email:
        contacts = [c for c in get_all_quo_contacts()
                    if any((e.get("value") or "").lower() == args.email.lower()
                           for e in (c.get("defaultFields", {}).get("emails") or []))]
        if not contacts:
            log.error(f"No Quo contact found with email {args.email}")
            return
    else:
        contacts = find_ready_candidates()

    log.info(f"  {len(contacts)} candidate(s) to process")
    results = [process_candidate(c, service, client, directory_text) for c in contacts]

    ready = sum(1 for r in results if r["outcome"] == "drafts_created")
    log.info(f"=== DONE — {ready}/{len(results)} candidate(s) got center draft(s) created ===")
    for r in results:
        log.info(f"    {r['name']}: {r['outcome']}")


if __name__ == "__main__":
    main()


# ================================================================================
# KNOWN GAPS — read before relying on this in production
# ================================================================================
# 1. UNTESTED END TO END. Written 2026-07-02. Run with --email on ONE real
#    candidate first. Check: PDFs open correctly, file names are right,
#    drafts appear in Gmail with 3 attachments, Quo role field updates.
#
# 2. save_as_draft() here is called with thread_id="" (a fresh draft, not a
#    reply) since a center submission is a NEW conversation, not a reply to
#    the candidate's thread. Confirm the real Gmail API accepts an empty
#    threadId in the draft body (it should create a standalone draft) —
#    this differs from every other save_as_draft() call in this project,
#    which are always replies. Verify on first real run.
#
# 3. Center directory parsing is 100% delegated to Claude reading the raw
#    .md text — no structured schema enforced. If BLUELINE_CENTER_DIRECTORY.md
#    doesn't actually contain email addresses for most/all of the 34 centers
#    (only a handful are confirmed in SAAS_PROJECT_HEALTHCARE_RECRUITMENT_
#    MASTER_CONTEXT.md's "Known discrepancies" notes), most candidates will
#    hit "no_centers_matched" or drafts with missing emails. Confirm the
#    real file has emails for the centers you actually place at before
#    expecting this to work broadly.
#
# 4. "SUBMITTED" (vs. "SUBMISSION_DRAFTS_READY") is never set automatically.
#    Detecting that Aditya actually clicked Send on a draft would require
#    scanning Sent Mail for a matching subject/recipient after the fact —
#    not built here. Today, moving a candidate from drafts-ready to
#    submitted is a manual status update (until/unless that's built).
#
# 5. Per-attachment classification (classify_attachment) adds one Claude
#    Haiku call per file, per candidate, every run — cheap individually but
#    not free at scale. Fine for on-demand runs over "ready for submission"
#    candidates (should be a small list at any given time); would need
#    caching if this were ever run over the full candidate base repeatedly.
# ================================================================================
