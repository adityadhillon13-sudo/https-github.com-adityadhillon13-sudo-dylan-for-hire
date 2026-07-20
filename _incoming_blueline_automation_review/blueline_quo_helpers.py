"""
BlueLine Staffing -- Shared Quo (OpenPhone) API Helpers
====================================================
Version: 1.0 | 2026-07-09

SINGLE SOURCE OF TRUTH for talking to Quo's /contacts, /conversations, and
/messages endpoints. Written after root-causing a real production bug: two
separate scripts (an ad hoc Franklin-center check and
master_candidate_file_consolidator.py's get_quo_sms_history_text()) each had
their own hand-rolled copy of the /messages call, and both were missing the
required `phoneNumberId` parameter -- one crashed outright (400 on every
candidate), the other silently returned empty SMS history with no error at
all. Real OpenPhone error body confirmed the requirement:
"/phoneNumberId: Expected required property". Root cause diffed against
master_daily_agent.py's own proven-working get_messages_for_phone(), which
has always included it.

Every NEW script that needs Quo contacts/conversations/messages should
import from HERE instead of writing its own requests.get() calls. One bug
fixed here fixes it everywhere it's reused, instead of needing the same fix
applied N times in N places (which is exactly how this bug happened twice).

Deliberately dependency-free of master_daily_agent.py (which validates all
env keys and can abort at import time -- an unsafe side effect to inherit
just to reuse HTTP helpers).
"""

import os
import time
import logging
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/Downloads/.env"))

log = logging.getLogger("blueline.quo_helpers")

QUO_API_KEY  = os.getenv("QUO_API_KEY")
QUO_PHONE_ID = os.getenv("QUO_PHONE_NUMBER_ID")
QUO_BASE     = "https://api.openphone.com/v1"
QUO_TIMEOUT  = 30

if not QUO_API_KEY:
    log.warning("QUO_API_KEY not set in ~/Downloads/.env -- Quo calls will fail")
if not QUO_PHONE_ID:
    log.warning("QUO_PHONE_NUMBER_ID not set in ~/Downloads/.env -- /messages and "
                "/conversations calls will fail with a 400 (phoneNumberId is required)")

HEADERS = {"Authorization": QUO_API_KEY or "", "Content-Type": "application/json"}


def _get_with_retry(path, params=None):
    """3 attempts, retries on timeout/connection error AND 429, with backoff.
    Raises on final failure -- callers decide how loud to be about it."""
    for attempt in range(1, 4):
        try:
            r = requests.get(f"{QUO_BASE}{path}", headers=HEADERS,
                              params=params or {}, timeout=QUO_TIMEOUT)
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
            log.warning(f"  Quo GET {path} attempt {attempt}/3 failed: {e}")
            if attempt == 3:
                raise
            time.sleep(3 * attempt)
            continue
        if r.status_code == 429 and attempt < 3:
            log.warning(f"  Quo GET {path} attempt {attempt}/3 rate limited (429)")
            time.sleep(5 * attempt)
            continue
        r.raise_for_status()
        return r
    raise RuntimeError(f"Exhausted retries on {path}")


def get_all_contacts():
    """Paginated fetch of every Quo contact. Returns list of raw contact
    dicts (defaultFields-nested shape, per OpenPhone's real API)."""
    contacts, page_token = [], None
    while True:
        params = {"pageSize": 100}
        if page_token:
            params["pageToken"] = page_token
        r = _get_with_retry("/contacts", params)
        data = r.json()
        contacts.extend(data.get("data", []))
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return contacts


def get_recent_conversations(days=15):
    """Conversations with activity in the last N days. REQUIRES
    phoneNumberId (matches master_daily_agent.py's proven-working pattern)."""
    if not QUO_PHONE_ID:
        raise RuntimeError("QUO_PHONE_NUMBER_ID not set -- cannot call /conversations")
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).timestamp()
    convos, page_token = [], None
    while True:
        params = {"phoneNumberId": QUO_PHONE_ID, "pageSize": 100}
        if page_token:
            params["pageToken"] = page_token
        r = _get_with_retry("/conversations", params)
        data = r.json()
        for c in data.get("data", []):
            try:
                ts = datetime.fromisoformat(
                    (c.get("lastActivityAt") or "").replace("Z", "+00:00")
                ).timestamp()
            except Exception:
                ts = 0.0
            if ts >= cutoff:
                convos.append(c)
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return convos


def get_messages_for_phone(phone, days=60):
    """Full-ish SMS history for one phone number. REQUIRES phoneNumberId --
    the actual root cause of the earlier consolidator/Franklin-script bugs."""
    if not QUO_PHONE_ID:
        raise RuntimeError("QUO_PHONE_NUMBER_ID not set -- cannot call /messages")
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).timestamp()
    msgs, page_token = [], None
    while True:
        params = [("phoneNumberId", QUO_PHONE_ID), ("participants[]", phone), ("pageSize", "50")]
        if page_token:
            params.append(("pageToken", page_token))
        r = _get_with_retry("/messages", params)
        data = r.json()
        for m in data.get("data", []):
            try:
                ts = datetime.fromisoformat(
                    (m.get("createdAt") or "").replace("Z", "+00:00")
                ).timestamp()
            except Exception:
                ts = 0.0
            if ts >= cutoff:
                msgs.append(m)
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return msgs


def contact_full_name(contact):
    df = contact.get("defaultFields", {}) or {}
    first = (df.get("firstName") or "").strip()
    last  = (df.get("lastName") or "").strip()
    return f"{first} {last}".strip()


def contact_phones(contact):
    df = contact.get("defaultFields", {}) or {}
    return [(p.get("value") or "").strip() for p in (df.get("phoneNumbers") or []) if p.get("value")]


def contact_role_field(contact):
    df = contact.get("defaultFields", {}) or {}
    return (df.get("role") or "").strip()
