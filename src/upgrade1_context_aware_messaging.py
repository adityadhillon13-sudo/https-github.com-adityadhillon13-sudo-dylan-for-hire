"""
================================================================================
UPGRADE 1 — CONTEXT-AWARE MESSAGING
BlueLine Staffing | Dylan AI Agent
Version: 1.1 | 2026-06-29
Fixes:
  - [BUG-12] get_quo_history used wrong endpoint (/conversations?phoneNumber= → 404)
             Now uses /messages?phoneNumberId=...&participants[]=+1xxx (correct)
  - [BUG-13] Message text field was "body"/"content"; correct field is "text"
  - [BUG-04] createdAt is ISO string; parse before filtering by cutoff date
================================================================================

PURPOSE:
    Before any outbound SMS (Steps 1, 2, 3), this module:
      1. Pulls last 4 days of Quo SMS history for the candidate
      2. Pulls last 4 days of Gmail threads matching the candidate's name
      3a. If history found → Claude decides: skip or write contextual SMS
      3b. If no history found → returns approved re-engagement SMS

INTEGRATION: See bottom of file — two lines replace every SMS send call.

COST PROFILE:
    Quo:    1 GET per candidate (4-day window, paginated)
    Gmail:  1 search + up to 5 message fetches per candidate
    Claude: 1 call per candidate, ~800–1,200 input tokens typical
================================================================================
"""

import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import requests
import anthropic

try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build as gmail_build
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False


# ================================================================================
# SECTION 1: CONFIGURATION
# ================================================================================

from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=Path.home() / "Downloads" / ".env")

QUO_API_KEY         = os.getenv("QUO_API_KEY")
QUO_PHONE_NUMBER_ID = os.getenv("QUO_PHONE_NUMBER_ID")
CLAUDE_API_KEY      = os.getenv("CLAUDE_API_KEY")
QUO_BASE_URL        = "https://api.openphone.com/v1"

HISTORY_DAYS  = 4        # Days of history to pull (Quo + Gmail)
SMS_MAX_CHARS = 160      # Hard ceiling on outbound SMS length
SKIP_SIGNAL   = "DYLAN_SKIP"

GMAIL_TOKEN_PATH       = os.path.expanduser("~/Downloads/gmail_token.json")
# [FIX 2026-07-01] Was os.path.join(_BASE_DIR, "gmail_token.json") — resolved to
# ~/Downloads/BlueLine/gmail_token.json (this script's own folder). But
# master_gmail_setup.py and master_gmail_reviewer.py both write/read the real
# token at ~/Downloads/gmail_token.json (one level up). That mismatch meant
# get_gmail_history() below has been silently failing every single call since
# this file was introduced — Gmail context was NEVER reaching the SMS
# re-engagement decision, only Quo history was (post the 2026-06-29 URL fix).
# Verify after this fix: `ls ~/Downloads/gmail_token.json` should exist.
GMAIL_SCOPES           = ["https://www.googleapis.com/auth/gmail.readonly"]

logger = logging.getLogger(__name__)


# ================================================================================
# SECTION 2: QUO — PULL SMS HISTORY (4 DAYS)
# ================================================================================

def get_quo_history(phone_number: str) -> str:
    """
    [v1.1 FIX] Fetches last HISTORY_DAYS of SMS messages for this candidate.

    Correct endpoint: GET /messages?phoneNumberId=...&participants[]=+1xxx
    Message object fields: {id, to, from, text, direction, createdAt, ...}
    - "text"      is the message body (NOT "body"/"content")
    - "direction" is "incoming" or "outgoing"
    - "createdAt" is ISO 8601 string (NOT ms epoch)

    phone_number: E.164 format — "+13478889999"
    """
    if not QUO_API_KEY or not QUO_PHONE_NUMBER_ID:
        logger.warning("QUO_API_KEY or QUO_PHONE_NUMBER_ID not set — skipping Quo history")
        return ""

    headers    = {"Authorization": QUO_API_KEY, "Content-Type": "application/json"}
    cutoff_ts  = (datetime.now(timezone.utc) - timedelta(days=HISTORY_DAYS)).timestamp()
    lines      = []
    page_token = None

    try:
        while True:
            # [FIX BUG-12] Correct endpoint: /messages with phoneNumberId + participants[]
            params = [
                ("phoneNumberId", QUO_PHONE_NUMBER_ID),
                ("participants[]", phone_number),
                ("pageSize", "50"),
            ]
            if page_token:
                params.append(("pageToken", page_token))

            resp = requests.get(
                f"{QUO_BASE_URL}/messages",
                headers=headers,
                params=params,
                timeout=15
            )

            if not resp.ok:
                logger.warning(f"Quo /messages {resp.status_code} for {phone_number}: {resp.text[:100]}")
                return ""

            data = resp.json()
            messages = data.get("data", [])

            for msg in messages:
                # [FIX BUG-04] createdAt is ISO string — parse before comparison
                created_str = msg.get("createdAt", "")
                try:
                    msg_ts = datetime.fromisoformat(created_str.replace("Z", "+00:00")).timestamp()
                except Exception:
                    msg_ts = 0.0

                if msg_ts < cutoff_ts:
                    continue  # Outside our history window

                direction = "Dylan →" if msg.get("direction") == "outgoing" else "Candidate →"
                # [FIX BUG-13] Field is "text" not "body"/"content"
                body = (msg.get("text") or "").strip()
                if body:
                    lines.append(f"[{created_str}] {direction} {body}")

            page_token = data.get("nextPageToken")
            if not page_token:
                break

    except Exception as e:
        logger.warning(f"Quo unexpected error for {phone_number}: {e}")
        return ""

    lines.sort()
    return "\n".join(lines)


# ================================================================================
# SECTION 3: GMAIL — PULL EMAIL THREADS BY CANDIDATE NAME (4 DAYS)
# ================================================================================

def get_gmail_history(candidate_name: str) -> str:
    """
    Searches Gmail for threads mentioning the candidate's name in last HISTORY_DAYS days.
    Returns formatted email previews string, or "" if none found / unavailable.
    Reuses existing gmail_token.json — no new auth setup needed.
    """
    if not GMAIL_AVAILABLE:
        logger.warning("Google libraries not installed — skipping Gmail history")
        return ""
    if not os.path.exists(GMAIL_TOKEN_PATH):
        logger.warning("gmail_token.json missing — skipping Gmail history")
        return ""

    try:
        creds      = Credentials.from_authorized_user_file(GMAIL_TOKEN_PATH, GMAIL_SCOPES)
        service    = gmail_build("gmail", "v1", credentials=creds)
        cutoff_str = (datetime.now() - timedelta(days=HISTORY_DAYS)).strftime("%Y/%m/%d")

        name_parts = candidate_name.strip().split()
        name_q     = f'"{candidate_name}"' if len(name_parts) >= 2 else candidate_name
        query      = f"{name_q} after:{cutoff_str}"

        results  = service.users().messages().list(
            userId="me", q=query, maxResults=5
        ).execute()

        refs = results.get("messages", [])
        if not refs:
            return ""

        previews = []
        for ref in refs:
            msg = service.users().messages().get(
                userId="me",
                id=ref["id"],
                format="metadata",
                metadataHeaders=["From", "To", "Subject", "Date"]
            ).execute()

            h       = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
            previews.append(
                f"[{h.get('Date', '?')}] FROM: {h.get('From', '?')} | "
                f"SUBJECT: {h.get('Subject', '(no subject)')}\n"
                f"PREVIEW: {msg.get('snippet', '').strip()}"
            )

        return "\n\n".join(previews)

    except Exception as e:
        logger.warning(f"Gmail history error for '{candidate_name}': {e}")
        return ""


# ================================================================================
# SECTION 4: CLAUDE — DECISION ENGINE
# ================================================================================

_SYSTEM_PROMPT = """You are Dylan, AI recruiting assistant for BlueLine Staffing (CNAs, LPNs, RNs — NYC).

Review the candidate's SMS + email history and decide the single best next action.

═══ SKIP — do not send anything if ANY of these apply ═══
- Opted out / said STOP or UNSUBSCRIBE → SKIP, always, no exceptions
- Messaged within last 24 hours → SKIP
- Mid-process: documents submitted, interview scheduled, or awaiting Aditya review → SKIP
- Active email thread in progress → SKIP (email is handling it — don't double-contact)
- Candidate just replied YES or expressed interest → SKIP (they receive DOCUMENT_CHECKLIST_MSG separately; do not send a duplicate)

═══ SEND — only when none of the above apply ═══
- Conversation stalled 2–4 days after prior positive engagement → warm, brief, specific follow-up
- Intro sent with no reply in 4+ days → soft check-in that references the specific prior message sent
- Candidate re-applied on Indeed after prior history → acknowledge the re-application; pick up exactly from where things stood

═══ VOICE & TONE — Dylan persona ═══
- Warm, direct, professional. Never desperate, never pushy, never lengthy.
- Always reference what was actually said or sent — never generic if history exists.
- Don't repeat information already sent in full (e.g. don't re-send the full document list).
- No emojis. No exclamation spam. No jargon. No hollow filler ("I hope this message finds you well").
- If the candidate mentioned something specific — a question, a concern, partial docs sent — acknowledge it directly.
- Soft, low-pressure CTA: "Reply YES anytime." / "Let me know if you're still open." / "Happy to pick this back up when you're ready."
- Sign off as Dylan — no last name, no title.
- Examples of the right register:
    "Hi Jane, just checking back — did you get a chance to send over the BLS card? Happy to follow up once it's in."
    "Hi Marcus, following up from last week. Still looking to place LPNs in Queens if you're available — reply YES and we'll get moving."
    "Hi Priya, noticed you re-applied. Let's continue from where we left off — still need the physical and PPD. Let me know when those are ready."

OUTPUT — respond with EXACTLY one of the following. Nothing else. No explanation.

SKIP

OR

SMS: [message under 160 chars, written as Dylan, specific to this candidate's actual history]"""


def claude_decide_message(
    candidate_name: str,
    phone_number: str,
    role: str,
    borough: str,
    quo_history: str,
    gmail_history: str
) -> str:
    """
    Sends candidate context to Claude. Returns SKIP_SIGNAL or a ready-to-send SMS string.
    """
    if not CLAUDE_API_KEY:
        logger.error("CLAUDE_API_KEY not set — defaulting to SKIP")
        return SKIP_SIGNAL

    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

    user_prompt = (
        f"CANDIDATE:\n"
        f"Name:    {candidate_name}\n"
        f"Phone:   {phone_number}\n"
        f"Role:    {role}\n"
        f"Borough: {borough}\n\n"
        f"── SMS HISTORY (last {HISTORY_DAYS} days) ──────────────────\n"
        f"{quo_history.strip() or 'None'}\n\n"
        f"── EMAIL HISTORY (last {HISTORY_DAYS} days) ────────────────\n"
        f"{gmail_history.strip() or 'None'}\n\n"
        f"Make your decision now."
    )

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}]
        )

        raw = response.content[0].text.strip()

        if raw.upper().startswith("SKIP"):
            logger.info(f"[UPGRADE1] SKIP  → {candidate_name} ({phone_number})")
            return SKIP_SIGNAL

        if raw.upper().startswith("SMS:"):
            sms = raw[4:].strip()
            if len(sms) > SMS_MAX_CHARS:
                sms = sms[:SMS_MAX_CHARS]
            logger.info(f"[UPGRADE1] SEND  → {candidate_name} | '{sms}'")
            return sms

        logger.warning(f"[UPGRADE1] Unexpected Claude output for {candidate_name}: '{raw}' — defaulting SKIP")
        return SKIP_SIGNAL

    except Exception as e:
        logger.error(f"[UPGRADE1] Claude API error for {candidate_name}: {e}")
        return SKIP_SIGNAL


# ================================================================================
# SECTION 5: RE-ENGAGEMENT FALLBACK (ZERO HISTORY — APPROVED 2026-05-04)
# ================================================================================

def build_reengagement_sms(candidate_name: str, role: str, borough: str) -> str:
    """
    Returns the prescribed default re-engagement SMS for candidates with
    no Quo or Gmail activity in the last 4 days.

    Prescribed template (BLUELINE_COMMS_PLAYBOOK §1D / BLUELINE_MASTER_OPS Step 1):
    "Hi {first}, just checking in from BlueLine Staffing.
     Still open to nursing shifts in NYC? Reply YES anytime."

    Note: role and borough params retained for signature compatibility but not used
    in the prescribed fallback template.
    """
    first = candidate_name.strip().split()[0] if candidate_name.strip() else "there"
    msg = (
        f"Hi {first}, just checking in from BlueLine Staffing. "
        f"Still open to nursing shifts in NYC? Reply YES anytime."
    )
    return msg[:SMS_MAX_CHARS]


# ================================================================================
# SECTION 6: MAIN ENTRY POINT
# ================================================================================

def get_context_aware_sms(
    candidate_name: str,
    phone_number: str,
    role: str,
    borough: str
) -> Optional[str]:
    """
    THE ONE FUNCTION TO CALL from master_daily_agent.py
    before every outbound SMS in Steps 1, 2, and 3.

    Returns:
        None  → skip this candidate (do not send anything)
        str   → exact SMS text to send; pass directly to your Quo send function

    Args:
        candidate_name : full name     e.g. "Jane Doe"
        phone_number   : E.164 format  e.g. "+13478889999"
        role           : license type  e.g. "CNA", "LPN", "RN"
        borough        : detected      e.g. "Brooklyn"
    """
    logger.info(f"[UPGRADE1] Evaluating → {candidate_name} ({phone_number})")

    quo_history   = get_quo_history(phone_number)
    gmail_history = get_gmail_history(candidate_name)
    has_history   = bool(quo_history.strip() or gmail_history.strip())

    if has_history:
        decision = claude_decide_message(
            candidate_name=candidate_name,
            phone_number=phone_number,
            role=role,
            borough=borough,
            quo_history=quo_history,
            gmail_history=gmail_history
        )
        return None if decision == SKIP_SIGNAL else decision

    else:
        sms = build_reengagement_sms(candidate_name, role, borough)
        logger.info(f"[UPGRADE1] NO HISTORY → RE-ENGAGE | {candidate_name} | '{sms}'")
        return sms


# ================================================================================
# HOW TO INTEGRATE INTO master_daily_agent.py
# ================================================================================
#
#  STEP 1 — Add ONE import at the top of master_daily_agent.py:
#
#      from upgrade1_context_aware_messaging import get_context_aware_sms
#
#
#  STEP 2 — In Steps 1, 2, and 3, wrap EVERY send_sms() call like this:
#
#      BEFORE:
#          send_sms(phone_number, message_text)
#
#      AFTER:
#          sms = get_context_aware_sms(
#              candidate_name = contact_name,     # full name string
#              phone_number   = phone_number,     # E.164 string
#              role           = contact_role,     # "CNA", "LPN", or "RN"
#              borough        = contact_borough   # e.g. "Brooklyn"
#          )
#          if sms:
#              send_sms(phone_number, sms)
#          else:
#              logger.info(f"[UPGRADE1] Skipped: {contact_name}")
#
#
#  STEP 3 — Repeat Step 2 in each of the three steps. That's the full integration.
#
#
#  STEP 4 — TEST ON ONE CANDIDATE FIRST (before full cron run):
#
#      cd ~/Downloads/BlueLine
#      python3.11 -c "
#      from upgrade1_context_aware_messaging import get_context_aware_sms
#      result = get_context_aware_sms('Jane Doe', '+13471234567', 'CNA', 'Brooklyn')
#      print('RESULT:', result if result else 'SKIP')
#      "
#
#  If result prints a message → integration working, Claude decided to send.
#  If result prints SKIP → integration working, Claude decided to hold.
#  If you get an import error → check the file is in ~/Downloads/BlueLine/
#
# ================================================================================
