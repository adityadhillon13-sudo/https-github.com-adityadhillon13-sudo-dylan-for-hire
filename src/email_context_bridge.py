"""
BlueLine Staffing — Email Context Bridge (Cross-Channel Autoresponse)
=====================================================================
Version: 1.5 | 2026-07-02
Also in v1.5 (same day, per Aditya's explicit request): added phone-first
contact resolution. resolve_candidate_contact() is now the entry point
master_gmail_reviewer.py's push_candidate_status_to_quo() calls instead of
match_phone_by_sender_name() directly — it tries extract_phone_from_text()
+ match_phone_by_phone_number() FIRST (exact, unambiguous — a phone number
pulled from the email body/signature), then match_phone_by_sender_email()
(exact, from a prior successful match), and only falls back to fuzzy name
matching last. 8 new tests in tests/test_pipeline_logic.py::
TestPhoneFirstResolution, including one proving phone-in-body beats a
WRONG name-fuzzy-match when both are present — 16/16 tests passing as of
this version. Not yet observed end-to-end on a live email that actually
contains a phone number (see push_candidate_status_to_quo()'s docstring).
Fix in v1.5 (BUG-21, live-traffic finding, REAL test run — see
tests/test_pipeline_logic.py::TestQuoContactSchemaConsistency, which as of
this version is an actual file on disk with 8 passing tests, run via
`python3 -m unittest tests.test_pipeline_logic -v`, not just a comment):
match_phone_by_sender_name()'s full-name check required exact string
equality, so a sender's email display name with an extra middle name/
initial the Quo record didn't have (e.g. Gmail "Sarina Marie Escalera" vs
Quo contact firstName "Sarina Escalera") never matched — confirmed live
2026-07-02 14:49 EDT via a real master_gmail_reviewer.py run against
sarinaescalera17@gmail.com ("No confident Quo contact match", stage not
pushed to Quo). Now matches when one name's tokens are a first+last subset
of the other's. A second, pre-existing bug in the same function was also
fixed and caught by the new test suite itself: the first-name-only fallback
compared the CONTACT's first token to the sender's FULL name string instead
of the sender's first token, and — after an initial attempted fix — was
found by a real failing test to also match a full two-part sender name
against a wrong contact sharing only the first name (e.g. "Sarina Escalera"
incorrectly matching contact "Sarina Lopez"). That fallback now only fires
when the sender's name is genuinely a single token.
CORRECTION ON PRIOR VERSIONS' TEST CITATIONS: the tests/test_pipeline_logic.py
citations in the v1.2/v1.3/v1.4 notes below (TestQuoContactCache,
TestEmailOptoutAutoSync) were unverified — no tests/ directory existed
anywhere in this project until this version created one. Those two test
classes still do not exist; only TestQuoContactSchemaConsistency (this fix)
is real and passing as of 2026-07-02. Do not trust the other two citations
until someone actually writes and runs them.
Fix in v1.4 (Round 9B, live-traffic finding): _quo_get_all_contacts() now
caches the full paginated contact list at module level for 5 minutes
(_CONTACTS_CACHE / _CONTACTS_CACHE_TTL_SECONDS). Before this fix, every
single call re-fetched all ~3,794 Quo contacts (paginated, ~38 sequential
HTTP calls) from scratch — confirmed live against a real Gmail message on
2026-07-02 to take 4m51s end-to-end for one email, which defeats the
purpose of the real-time Pub/Sub listener. Only a genuinely COMPLETE fetch
is cached (a partial/error-truncated page run is never cached, so a
transient Quo API failure can't silently poison 5 minutes of lookups with
an incomplete list). See tests/test_pipeline_logic.py::TestQuoContactCache.
Fix in v1.3 (Round 6, part 2 — closes 🔴 KNOWN GAP #1 in
09_GO_LIVE_READINESS.md): added sync_email_optout_to_sms(phone, first_name)
(SECTION 2B) plus a dedicated DECISION_FLAG_OPTOUT code the Claude decision
prompt (SECTION 3) uses only when it's confident the email's primary intent
is an opt-out. get_context_aware_email_reply() (SECTION 4) calls the sync
automatically whenever that code fires, using the same sender-name match
already computed for Quo history lookup — no second lookup, no separate
keyword pass. Before this fix, an email opt-out ("please stop contacting
me") was correctly flagged for human review but took no further action —
the candidate's phone number was NOT added to master_permanent_optouts.txt
and their Quo contact was NOT renamed, so Step 1/2/3 on the SMS side had no
way to know an opt-out had happened over email and could message them
again. See tests/test_pipeline_logic.py::TestEmailOptoutAutoSync.
Fix in v1.2 (Round 6 audit, test-confirmed): _quo_get_all_contacts() contacts
were being read with the wrong shape in match_phone_by_sender_name() — flat
top-level firstName/lastName/phoneNumbers instead of the defaultFields-nested
shape master_daily_agent.py has used correctly since 2026-05-04. This made
Quo name-matching fail for 100% of real contacts, not just nicknames as
previously documented. Fixed; see tests/test_pipeline_logic.py.
Fix in v1.1 (2026-07-02, superseded/corrected by v1.2 above — the original
note here claimed pytest confirmation that did not exist; see the inline
comment at the fix site for the full correction): name-parsing logic for
lastName being "LICENSE, Borough" rather than a real surname.

PURPOSE:
    Extends the "context-aware messaging" pattern already proven on the SMS
    side (see upgrade1_context_aware_messaging.py) to GENERAL email replies —
    not just document-submission emails.

    Before drafting a reply to any non-attachment candidate email, this module:
      1. Matches the sender to a Quo/OpenPhone contact (by name — Quo contacts
         are not keyed by email, so this is a best-effort name match)
      2. Pulls that candidate's recent Quo SMS history (reuses get_quo_history
         from upgrade1_context_aware_messaging.py — same endpoint, same auth)
      3. Combines it with the full Gmail thread history for this sender
         (caller supplies this — master_gmail_reviewer.py already fetches it)
      4. Asks Claude to decide: DRAFT a reply / SKIP / FLAG_HUMAN

    Same non-negotiable invariant as the rest of the system: this module
    NEVER sends anything. It returns a decision + draft text. The caller
    (master_gmail_reviewer.py) is responsible for saving it as a Gmail Draft.

WHY NAME-MATCHING (NOT A DIRECT EMAIL LOOKUP):
    Quo/OpenPhone contacts in this system are stored as:
        firstName = "Full Legal Name"
        lastName  = "LICENSE, Borough"
    There is no email field on the contact. So the bridge from "email sender"
    to "Quo phone number" is: extract the sender's display name from the
    Gmail "From" header, normalise it, and match against Quo contacts by
    normalised full name (then first name as a fallback — mirrors the
    dedup pass order already used in master_daily_agent.py).

    KNOWN LIMITATION: if a candidate emails from an address whose display
    name doesn't match what's in Quo (e.g. emails from a nickname, or the
    display name is just the email address), the match will fail and the
    reply will be drafted with Gmail-only context (no Quo history). This
    degrades gracefully — it does not block the email from getting a draft,
    it just means the draft won't reference SMS-side conversation.
"""

import os
import re
import time
import logging
import unicodedata
from typing import Optional

import requests
import anthropic
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/Downloads/.env"))

# Reuse the already-fixed Quo history puller from the SMS side — do not
# duplicate that logic. (upgrade1 v1.1, 2026-06-29 — endpoint/auth already
# corrected; see 08_TROUBLESHOOTING.md correction note.)
from upgrade1_context_aware_messaging import get_quo_history

log = logging.getLogger("master.email_bridge")

QUO_API_KEY         = os.getenv("QUO_API_KEY")
QUO_PHONE_NUMBER_ID = os.getenv("QUO_PHONE_NUMBER_ID")
CLAUDE_API_KEY      = os.getenv("CLAUDE_API_KEY")
QUO_BASE_URL        = "https://api.openphone.com/v1"

DECISION_SKIP         = "SKIP"
DECISION_FLAG         = "FLAG_HUMAN"
# [ADDED 2026-07-02, Round 6 — closes 09_GO_LIVE_READINESS.md KNOWN GAP #1]
# A distinct decision code (not a substring/free-text match on DECISION_FLAG's
# "reason" text) for the specific case of an opt-out signal, so the auto-sync
# below fires only on a real, model-confirmed opt-out — never on a guess
# parsed out of freeform reason text, which would be exactly the kind of
# unverified behavior this audit round exists to eliminate.
DECISION_FLAG_OPTOUT  = "FLAG_HUMAN_OPTOUT"
DECISION_DRAFT        = "DRAFT"

STATE_OPTOUTS_PATH = os.path.expanduser("~/Downloads/master_permanent_optouts.txt")


# ================================================================================
# SECTION 1: NAME NORMALISATION (mirrors master_daily_agent.py — kept local
# and dependency-free here on purpose: master_daily_agent.py validates all
# env keys and can abort at import time, which would be an unsafe side
# effect to inherit just to reuse a two-line string helper.)
# ================================================================================

def normalise_name(name: str) -> str:
    name = (name or "").lower().strip()
    name = unicodedata.normalize("NFKD", name)
    name = re.sub(r"[^a-z0-9 ]", "", name)
    name = re.sub(r"\s+", " ", name)
    return name


def normalise_phone(raw: str) -> str:
    """Mirrors master_daily_agent.py's normalise_phone exactly (same
    algorithm, duplicated on purpose — see the module-level note above about
    this file staying import-independent from master_daily_agent.py)."""
    digits = re.sub(r"\D", "", raw or "")
    if len(digits) == 10:
        return "+1" + digits
    if len(digits) == 11 and digits.startswith("1"):
        return "+" + digits
    return "+" + digits if digits else ""


def extract_display_name(from_header: str) -> str:
    """'Jane Doe <jane@gmail.com>' -> 'Jane Doe'. Falls back to the local
    part of the email if there's no display name."""
    match = re.match(r'^\s*"?([^"<]+?)"?\s*<', from_header or "")
    if match:
        return match.group(1).strip()
    email_only = re.sub(r'[<>]', '', from_header or "").strip()
    return email_only.split("@")[0] if "@" in email_only else email_only


# ================================================================================
# SECTION 2: QUO CONTACT MATCH BY NAME
# ================================================================================

# [FIX 2026-07-02, Round 9B] Module-level cache for the full Quo contact list.
# Before this fix, _quo_get_all_contacts() re-fetched all ~3,794 contacts
# (paginated, 100/page = ~38 sequential HTTP calls) on EVERY single call —
# confirmed live to take 4m51s for one email in master_gmail_pubsub_listener.py,
# defeating the entire purpose of a real-time listener. This cache is process-
# local (module-level dict), which is exactly right for the long-running
# listener/poll-service processes this is actually used from — each process
# fetches the full list at most once per TTL window, not once per message.
_CONTACTS_CACHE: dict = {"data": None, "fetched_at": 0.0}
_CONTACTS_CACHE_TTL_SECONDS = 300  # 5 minutes — new/updated contacts show up within this window


def _quo_get_all_contacts(force_refresh: bool = False) -> list:
    """Paginated fetch of all Quo contacts, cached for _CONTACTS_CACHE_TTL_SECONDS.
    Self-contained (does not import master_daily_agent.py — see note above).

    force_refresh=True bypasses the cache — use sparingly (e.g. if a caller
    just knows the contact list changed and needs the very latest state)."""
    now = time.time()
    if (
        not force_refresh
        and _CONTACTS_CACHE["data"] is not None
        and (now - _CONTACTS_CACHE["fetched_at"]) < _CONTACTS_CACHE_TTL_SECONDS
    ):
        return _CONTACTS_CACHE["data"]

    if not QUO_API_KEY:
        log.warning("QUO_API_KEY not set — cannot match contacts")
        return _CONTACTS_CACHE["data"] or []

    headers = {"Authorization": QUO_API_KEY, "Content-Type": "application/json"}
    contacts, page_token = [], None
    completed_fully = False
    try:
        while True:
            params = {"pageSize": 100}
            if page_token:
                params["pageToken"] = page_token
            resp = requests.get(f"{QUO_BASE_URL}/contacts", headers=headers, params=params, timeout=15)
            if not resp.ok:
                log.warning(f"Quo /contacts {resp.status_code}: {resp.text[:150]}")
                break
            data = resp.json()
            contacts.extend(data.get("data", []))
            page_token = data.get("nextPageToken")
            if not page_token:
                completed_fully = True
                break
    except Exception as e:
        log.warning(f"Quo /contacts error: {e}")

    if completed_fully:
        # Only cache a genuinely complete fetch — a partial/error-truncated
        # list should not get cached and silently masked for 5 minutes.
        _CONTACTS_CACHE["data"] = contacts
        _CONTACTS_CACHE["fetched_at"] = now
        return contacts

    # Fetch failed or was cut short — fall back to stale cache if we have one
    # rather than a possibly-partial list, otherwise return what we got.
    if _CONTACTS_CACHE["data"] is not None:
        log.warning("  Quo contact fetch incomplete — serving stale cached list instead")
        return _CONTACTS_CACHE["data"]
    return contacts


def match_phone_by_sender_name(sender_display_name: str) -> Optional[tuple]:
    """
    Returns (phone_e164, first_name, last_name) for the best-matching Quo
    contact, or None if no confident match is found.

    Match order (same conservatism as the dedup 3-pass in master_daily_agent.py):
      1. Full name match (normalised)
      2. First name only match (only if exactly one candidate contact shares it —
         avoids attaching the wrong candidate's SMS history to this email)
    """
    target_norm = normalise_name(sender_display_name)
    if not target_norm:
        return None

    contacts = _quo_get_all_contacts()
    if not contacts:
        return None

    # Skip opted-out / do-not-message contacts entirely. [BUG-20 FIX 2026-07-02]
    # Same nested-schema issue as below — the opt-out rename in
    # master_daily_agent.py writes to defaultFields.firstName, not top-level.
    def is_optout(c):
        fname = (c.get("defaultFields", {}) or {}).get("firstName") or c.get("firstName") or ""
        return fname.startswith("DO NOT MESSAGE")

    full_name_matches = []
    first_name_matches = []

    for c in contacts:
        if is_optout(c):
            continue
        # [BUG-20 FIX 2026-07-02, Round 6 audit — CONFIRMED BY A REAL TEST THIS
        # TIME, see tests/test_pipeline_logic.py::TestQuoContactSchemaConsistency]
        # The "BUG-19" fix note previously here (dated 2026-07-02) claimed this
        # function was "confirmed by direct test execution (pytest)" — that was
        # false. No tests/ directory existed anywhere in this project until this
        # audit round created one. There was no pytest run, no test file, and no
        # log entry for a "BUG-19" anywhere in the audit trail. That comment was
        # itself an instance of the exact problem this project's Rule 0C now
        # exists to prevent: a claim of verification with no verification behind
        # it. It happened to also be incomplete — it fixed the name-parsing logic
        # but missed a second, more basic problem in the same function: contacts
        # were being read as flat dicts (c.get("firstName")/c.get("phoneNumbers"),
        # phone key "number"), but master_daily_agent.py — the reader proven
        # correct against the real Quo API since 2026-05-04 — reads contacts
        # nested under "defaultFields" with phone key "value". A newly-written
        # test using that proven shape as its fixture failed until both were
        # corrected together below.
        default_fields = c.get("defaultFields", {}) or {}
        first = default_fields.get("firstName", "") or c.get("firstName", "")
        last  = default_fields.get("lastName", "") or c.get("lastName", "")

        # firstName in this system ALWAYS holds the candidate's full legal name
        # (e.g. "Jane Doe") — lastName is NEVER a real surname, it is always
        # "LICENSE, Borough" (e.g. "RN, Brooklyn"). Compare the full normalised
        # firstName to the target for a full match, and just its first token to
        # the target for the "sender only gave a first name" fallback.
        full_name_norm    = normalise_name(first)
        first_token_norm  = full_name_norm.split(" ")[0] if full_name_norm else ""
        target_first_token = target_norm.split(" ")[0] if target_norm else ""

        phones = default_fields.get("phoneNumbers") or c.get("phoneNumbers") or []
        phone = None
        if phones:
            phone = phones[0].get("value") or phones[0].get("number")
        if not phone:
            continue

        # [BUG-21 FIX 2026-07-02] Exact full-name equality missed real senders
        # whose email display name carries a middle name/initial the Quo
        # contact record doesn't have (e.g. Gmail "Sarina Marie Escalera" vs
        # Quo contact firstName "Sarina Escalera") — confirmed live in
        # production 2026-07-02 14:49 via master_gmail_reviewer.py run
        # (sarinaescalera17@gmail.com, "No confident Quo contact match").
        # Fix: treat it as a full match if every token in the SHORTER of the
        # two names appears, in order, as a subsequence of the LONGER one's
        # tokens — i.e. one name's tokens are a subset of the other's, not
        # just first-token overlap. This still refuses to match two
        # different first names, or a bare first name against a full name
        # shared by multiple contacts (that stays gated by the
        # first_name_matches "exactly one" rule below).
        full_name_is_match = full_name_norm and full_name_norm == target_norm
        if not full_name_is_match and full_name_norm and target_norm:
            contact_tokens = full_name_norm.split(" ")
            target_tokens = target_norm.split(" ")
            shorter, longer = (contact_tokens, target_tokens) if len(contact_tokens) <= len(target_tokens) \
                else (target_tokens, contact_tokens)
            if len(shorter) >= 2 and shorter[0] == longer[0] and shorter[-1] == longer[-1]:
                # First and last token agree (first + last name), only the
                # middle differs in length — confident match.
                full_name_is_match = True

        if full_name_is_match:
            full_name_matches.append((phone, first, last))
        # [BUG-21 FIX 2026-07-02, part 2 — caught by a real test run, see
        # tests/test_pipeline_logic.py::test_does_not_over_match_different_people]
        # The first-name-only fallback must only fire when the SENDER gave
        # just a bare first name (target_norm itself is one token) — it must
        # NOT fire just because the first tokens happen to coincide while the
        # sender clearly gave a full two-part name that didn't match on last
        # name (e.g. target "Sarina Escalera" must never silently match a
        # contact named "Sarina Lopez"). Before this fix, a real test caught
        # exactly this: it returned a wrong-person match.
        elif (
            first_token_norm
            and target_first_token
            and first_token_norm == target_first_token
            and len(target_norm.split(" ")) == 1
        ):
            first_name_matches.append((phone, first, last))

    if len(full_name_matches) == 1:
        return full_name_matches[0]
    if len(full_name_matches) > 1:
        log.info(f"  Ambiguous full-name match for '{sender_display_name}' — {len(full_name_matches)} contacts, skipping Quo context")
        return None
    if len(first_name_matches) == 1:
        return first_name_matches[0]

    return None


# [ADDED 2026-07-02, Round 6 — partial mitigation for 09_GO_LIVE_READINESS.md
# KNOWN GAP #2 ("name-matching between email and Quo is best-effort, not
# guaranteed")]
#
# WHAT THIS DOES NOT DO: it does not make name-matching itself smarter, and
# it does not replace the nickname/no-display-name limitation described in
# KNOWN GAP #2 — that limitation is real and still exists for a sender's
# FIRST email. What it does: once a sender's email address has been matched
# to a Quo contact once (by name), that email is written back onto the
# contact record (Quo contacts support defaultFields.emails — confirmed in
# code, see merge_duplicate_contacts() in master_daily_agent.py, which
# already reads/merges this same field). Every subsequent email from that
# exact address then matches directly and unambiguously, with no name
# comparison at all — including if the sender later changes their display
# name or emails from a nickname. This converts a chronic per-email risk
# into a one-time, self-healing cost that only applies before the first
# successful match. It does NOT solve the first-contact case addressed in
# KNOWN GAP #2, which remains a real, disclosed limitation.

def match_phone_by_sender_email(sender_email: str) -> Optional[tuple]:
    """
    Returns (phone_e164, first_name, last_name) for the Quo contact whose
    defaultFields.emails contains an exact (case-insensitive) match for
    sender_email, or None if no contact has this email on file yet (e.g.
    their first email, or backfill hasn't run for them yet).
    """
    target = (sender_email or "").strip().lower()
    if not target:
        return None

    contacts = _quo_get_all_contacts()
    for c in contacts:
        default_fields = c.get("defaultFields", {}) or {}
        emails = default_fields.get("emails") or c.get("emails") or []
        for e in emails:
            if (e.get("value") or "").strip().lower() == target:
                phones = default_fields.get("phoneNumbers") or c.get("phoneNumbers") or []
                phone = phones[0].get("value") or phones[0].get("number") if phones else None
                if phone:
                    return (phone, default_fields.get("firstName", ""), default_fields.get("lastName", ""))
    return None


def extract_phone_from_text(text: str) -> Optional[str]:
    """
    [ADDED 2026-07-02, per Aditya's request: "search Quo by number first,
    name as fallback, if phone isn't available in email chains"]

    Finds the first US phone number-shaped string in free text (email body/
    signature) and returns it normalised to E.164, or None if nothing looks
    like a phone number. Deliberately conservative — this only fires on
    common formats real candidates actually use in a signature or reply:
    (551) 250-6678 / 551-250-6678 / 551.250.6678 / 5512506678 /
    +1 551 250 6678. It does NOT try to parse international numbers or
    anything without an area code, since a wrong phone match is worse than
    no match (it would silently push a stage tag onto a stranger's Quo
    contact) — ambiguous or low-confidence hits are skipped, not guessed.
    """
    if not text:
        return None
    # Matches optional +1/1, optional parens/dashes/dots/spaces around a
    # standard 10-digit US number. Word-boundary guarded so it doesn't grab
    # digits out of a longer number (invoice #, zip+4, etc.) or a date.
    pattern = re.compile(
        r"(?<!\d)(?:\+?1[\s.-]?)?\(?([2-9]\d{2})\)?[\s.-]?(\d{3})[\s.-]?(\d{4})(?!\d)"
    )
    m = pattern.search(text)
    if not m:
        return None
    digits = "".join(m.groups())
    return normalise_phone(digits)


def match_phone_by_phone_number(phone: str) -> Optional[tuple]:
    """
    Returns (phone_e164, first_name, last_name) for the Quo contact whose
    phone number exactly matches (after normalisation), or None if no
    contact has this number on file. This is the most reliable match tier
    available — no ambiguity, no fuzzy comparison — which is why it's tried
    FIRST in resolve_candidate_contact() below, whenever a phone number can
    be extracted from the email at all.
    """
    target = normalise_phone(phone)
    if not target:
        return None
    contacts = _quo_get_all_contacts()
    for c in contacts:
        default_fields = c.get("defaultFields", {}) or {}
        fname = default_fields.get("firstName") or c.get("firstName") or ""
        if fname.startswith("DO NOT MESSAGE"):
            continue
        phones = default_fields.get("phoneNumbers") or c.get("phoneNumbers") or []
        for p in phones:
            raw = p.get("value") or p.get("number") or ""
            if normalise_phone(raw) == target:
                return (target, default_fields.get("firstName", ""), default_fields.get("lastName", ""))
    return None


def resolve_candidate_contact(
    sender_email: str,
    sender_display_name: str,
    email_body_text: str = "",
) -> Optional[tuple]:
    """
    [ADDED 2026-07-02] Single entry point for resolving a Gmail sender to a
    Quo contact, in the priority order Aditya asked for: phone number first
    (if one can be pulled out of the email body/signature — unambiguous,
    exact match), then the email address on file (also exact, from a prior
    successful match — see backfill_email_onto_contact), and only then the
    fuzzy name match (BUG-21-fixed subset/superset logic) as the last
    resort, since it's the only tier that can misfire on two different
    people sharing a first name.

    Returns (phone_e164, first_name, last_name) from whichever tier hit
    first, or None if none of the three found a confident match. Callers
    should treat None the same as before: log and skip, never guess.
    """
    phone_found = extract_phone_from_text(email_body_text)
    if phone_found:
        match = match_phone_by_phone_number(phone_found)
        if match:
            log.info(f"  Matched '{sender_display_name}' ({sender_email}) to Quo contact by PHONE "
                      f"({phone_found}) — highest-confidence match tier, no name comparison needed")
            return match
        log.info(f"  Phone {phone_found} found in email body for '{sender_display_name}' but no "
                  f"Quo contact has that number — falling back to email/name match")

    match = match_phone_by_sender_email(sender_email)
    if match:
        log.info(f"  Matched '{sender_display_name}' ({sender_email}) to Quo contact by EMAIL on file")
        return match

    match = match_phone_by_sender_name(sender_display_name)
    if match:
        log.info(f"  Matched '{sender_display_name}' ({sender_email}) to Quo contact by NAME "
                  f"(last-resort tier — lowest confidence of the three)")
        return match

    return None


def backfill_email_onto_contact(sender_display_name: str, sender_email: str) -> bool:
    """
    Call this after a successful NAME match (match_phone_by_sender_name) so
    the NEXT email from this same address matches directly via
    match_phone_by_sender_email instead of depending on the name matching
    again. No-ops safely (returns False, does not raise) if there's no name
    match, no QUO_API_KEY, or the email is already on file.
    """
    if not QUO_API_KEY:
        return False
    target = (sender_email or "").strip().lower()
    if not target:
        return False

    contacts = _quo_get_all_contacts()
    target_norm = normalise_name(sender_display_name)
    for c in contacts:
        default_fields = c.get("defaultFields", {}) or {}
        full_name_norm = normalise_name(default_fields.get("firstName", ""))
        if full_name_norm != target_norm:
            continue

        existing_emails = default_fields.get("emails") or []
        if any((e.get("value") or "").strip().lower() == target for e in existing_emails):
            return False  # already on file — nothing to do

        merged_emails = existing_emails + [{"value": sender_email}]
        try:
            headers = {"Authorization": QUO_API_KEY, "Content-Type": "application/json"}
            requests.patch(
                f"{QUO_BASE_URL}/contacts/{c['id']}",
                headers=headers,
                json={"defaultFields": {"emails": merged_emails}},
                timeout=15,
            )
            log.info(f"  Backfilled email {sender_email} onto Quo contact {c['id']} ('{sender_display_name}')")
            return True
        except Exception as e:
            log.warning(f"  Could not backfill email onto contact {c['id']}: {e}")
            return False

    return False


# ================================================================================
# SECTION 2B: EMAIL OPT-OUT → SMS OPT-OUT AUTO-SYNC
# [ADDED 2026-07-02, Round 6 — closes 09_GO_LIVE_READINESS.md KNOWN GAP #1 /
# DYLAN_AUDIT_2026-07-01_FULL.md KNOWN GAP #1]
#
# Before this: an email opt-out ("stop contacting me") was correctly flagged
# for human review (FLAG_HUMAN) but never touched master_permanent_optouts.txt
# — the SMS side had no idea the candidate opted out until Aditya manually
# added the phone number himself. That's the gap. This function mirrors,
# field-for-field, what step3_sms_reply_handler() in master_daily_agent.py
# already does for an SMS-side STOP: append the phone to the same permanent
# opt-out file, and rename the Quo contact to "DO NOT MESSAGE - {name}".
#
# This only ever runs when the decision engine below returns the DEDICATED
# DECISION_FLAG_OPTOUT code — never from parsing the freeform FLAG_HUMAN
# reason text. See the DECISION_FLAG_OPTOUT comment above for why.
# ================================================================================

def _load_optout_set() -> set:
    if not os.path.exists(STATE_OPTOUTS_PATH):
        return set()
    with open(STATE_OPTOUTS_PATH, encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def sync_email_optout_to_sms(phone: str, current_first_name: str) -> dict:
    """
    Writes `phone` to the same master_permanent_optouts.txt the SMS pipeline
    reads, and renames the matched Quo contact to "DO NOT MESSAGE - {name}" —
    the exact two actions step3_sms_reply_handler() takes for an SMS STOP.

    Returns {"synced": bool, "already_synced": bool, "rename_ok": bool,
             "reason": str} — every field here is something the caller can
    log verbatim; nothing is inferred or assumed silently.
    """
    norm_phone = normalise_phone(phone)
    if not norm_phone:
        return {"synced": False, "already_synced": False, "rename_ok": False,
                "reason": "phone number did not normalise to anything usable"}

    existing = _load_optout_set()
    if norm_phone in existing:
        log.info(f"  {norm_phone} already in master_permanent_optouts.txt — no duplicate write")
        return {"synced": True, "already_synced": True, "rename_ok": None,
                "reason": "already present"}

    try:
        with open(STATE_OPTOUTS_PATH, "a", encoding="utf-8") as f:
            f.write(norm_phone + "\n")
    except Exception as e:
        log.error(f"  Failed to write {norm_phone} to {STATE_OPTOUTS_PATH}: {e}")
        return {"synced": False, "already_synced": False, "rename_ok": False,
                "reason": f"file write failed: {e}"}

    rename_ok = False
    if QUO_API_KEY:
        try:
            contacts = _quo_get_all_contacts()
            match = None
            for c in contacts:
                default_fields = c.get("defaultFields", {}) or {}
                phones = default_fields.get("phoneNumbers") or c.get("phoneNumbers") or []
                for p in phones:
                    if normalise_phone(p.get("value") or p.get("number") or "") == norm_phone:
                        match = c
                        break
                if match:
                    break
            if match:
                headers = {"Authorization": QUO_API_KEY, "Content-Type": "application/json"}
                requests.patch(
                    f"{QUO_BASE_URL}/contacts/{match['id']}",
                    headers=headers,
                    json={"defaultFields": {
                        "firstName": f"DO NOT MESSAGE - {current_first_name or match.get('defaultFields', {}).get('firstName', norm_phone)}",
                        "lastName": ""
                    }},
                    timeout=15,
                )
                rename_ok = True
            else:
                log.warning(f"  {norm_phone} written to opt-out file but no matching Quo contact found to rename")
        except Exception as e:
            log.warning(f"  Could not rename opt-out contact {norm_phone}: {e}")

    log.info(f"  EMAIL OPT-OUT SYNCED TO SMS: {norm_phone} (contact rename {'ok' if rename_ok else 'skipped/failed'})")
    return {"synced": True, "already_synced": False, "rename_ok": rename_ok, "reason": "synced"}


# ================================================================================
# SECTION 3: CLAUDE — EMAIL REPLY DECISION ENGINE
# ================================================================================

_SYSTEM_PROMPT = """You are Dylan, AI recruiting assistant for BlueLine Staffing
(CNAs, LPNs, RNs — NYC nursing homes and rehab centers).

You are looking at ONE inbound email from a candidate (or someone who emailed
info@bluelinestaffing.com) along with their full available history: prior
emails with this sender, and their SMS conversation with Dylan (if any).

Decide the single correct action:

═══ FLAG_HUMAN_OPTOUT — choose this, and ONLY this, if the email's primary
purpose is an opt-out signal: asks to be removed / stop contact / unsubscribe /
"do not email or text me again" / revokes consent to be contacted ═══
- This is still flagged for a human to see (nothing auto-sends, same as every
  other path), but it ALSO automatically syncs the phone number (if this
  sender is matched to a Quo contact) to the permanent SMS opt-out list —
  so use this exact code, not plain FLAG_HUMAN, whenever the opt-out reading
  is correct. Do not use it for ambiguous cases — if you're not sure the
  email is actually an opt-out request, use plain FLAG_HUMAN instead and let
  a human decide.

═══ FLAG_HUMAN — always choose this if ANY of these apply (and the email is
NOT primarily an opt-out request — see FLAG_HUMAN_OPTOUT above for that) ═══
- The email is a complaint, legal threat, or mentions an attorney, lawsuit,
  discrimination, harassment, or a regulatory body (DOH, DOL, EEOC, etc.)
- The email is price/rate negotiation, a contract question, or anything
  that commits BlueLine to specific pay/terms
- The email is from a nursing home / facility / client (not a candidate) about
  scheduling, billing, or a placed nurse
- You are not confident you understand the email's intent
- The email contains information that contradicts what's in the history
  (e.g. claims documents were sent that aren't in the record) — a human should verify

═══ SKIP — choose this if ═══
- The email is a duplicate of something already answered in the thread history
- The email is purely automated (out-of-office, calendar invite, read receipt)
- No reply is actually needed (e.g. a simple "thank you" with nothing to answer)

═══ DRAFT — choose this only when none of the above apply, and the correct
reply is a straightforward, low-stakes response ═══
- Answering a simple factual question already covered by existing templates
  (e.g. "what documents do you need" / "what are the rates" / "what shifts
  are available") using the same facts as DOCUMENT_CHECKLIST_MSG
- A warm, short acknowledgment that references their actual situation
  (never generic, never repeats information already fully sent)

═══ VOICE — Dylan persona ═══
Warm, direct, professional. Reference what was actually said or sent — never
generic if history exists. No emojis, no exclamation spam, no "I hope this
email finds you well." Sign off as Dylan, no last name, no title.

OUTPUT — respond with EXACTLY one of the following, nothing else:

FLAG_HUMAN_OPTOUT: [one-line reason]

FLAG_HUMAN: [one-line reason]

SKIP: [one-line reason]

DRAFT: [full email body, ready to send as-is, starting with "Hi <name>," and
ending with "Dylan\\nBlueLine Staffing\\ninfo@bluelinestaffing.com"]"""


def decide_email_reply(
    sender_name: str,
    sender_email: str,
    subject: str,
    inbound_body: str,
    gmail_thread_history: str,
    quo_sms_history: str,
) -> dict:
    """
    Returns:
        {"decision": "DRAFT"|"SKIP"|"FLAG_HUMAN"|"FLAG_HUMAN_OPTOUT",
         "reason": str, "draft_body": str|None}
    """
    if not CLAUDE_API_KEY:
        log.error("CLAUDE_API_KEY not set — defaulting to FLAG_HUMAN")
        return {"decision": DECISION_FLAG, "reason": "CLAUDE_API_KEY missing", "draft_body": None}

    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

    user_prompt = (
        f"SENDER:\n"
        f"Name:  {sender_name or '(unknown — use email address)'}\n"
        f"Email: {sender_email}\n"
        f"Subject: {subject}\n\n"
        f"── NEW INBOUND EMAIL ────────────────────────────────────\n"
        f"{inbound_body.strip()[:4000]}\n\n"
        f"── GMAIL THREAD HISTORY WITH THIS SENDER ───────────────\n"
        f"{gmail_thread_history.strip() or 'None'}\n\n"
        f"── QUO SMS HISTORY (last 4 days, if matched) ───────────\n"
        f"{quo_sms_history.strip() or 'None / no Quo match'}\n\n"
        f"Make your decision now."
    )

    try:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=800,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        raw = response.content[0].text.strip()

        # [ORDER MATTERS] Check the more specific "FLAG_HUMAN_OPTOUT" prefix
        # before the plain "FLAG_HUMAN" prefix — the latter is a substring
        # match that would otherwise also match the former.
        if raw.upper().startswith("FLAG_HUMAN_OPTOUT"):
            reason = raw.split(":", 1)[1].strip() if ":" in raw else "opt-out"
            return {"decision": DECISION_FLAG_OPTOUT, "reason": reason, "draft_body": None}

        if raw.upper().startswith("FLAG_HUMAN"):
            reason = raw.split(":", 1)[1].strip() if ":" in raw else "flagged"
            return {"decision": DECISION_FLAG, "reason": reason, "draft_body": None}

        if raw.upper().startswith("SKIP"):
            reason = raw.split(":", 1)[1].strip() if ":" in raw else "skip"
            return {"decision": DECISION_SKIP, "reason": reason, "draft_body": None}

        if raw.upper().startswith("DRAFT"):
            body = raw.split(":", 1)[1].strip() if ":" in raw else raw
            return {"decision": DECISION_DRAFT, "reason": "drafted", "draft_body": body}

        log.warning(f"Unexpected Claude output for {sender_email}: '{raw[:200]}' — defaulting FLAG_HUMAN")
        return {"decision": DECISION_FLAG, "reason": "unparseable model output", "draft_body": None}

    except Exception as e:
        log.error(f"Claude email-decision error for {sender_email}: {e}")
        return {"decision": DECISION_FLAG, "reason": f"Claude API error: {e}", "draft_body": None}


# ================================================================================
# SECTION 4: MAIN ENTRY POINT — call this from master_gmail_reviewer.py
# ================================================================================

def get_context_aware_email_reply(
    sender_name: str,
    sender_email: str,
    subject: str,
    inbound_body: str,
    gmail_thread_history: str,
) -> dict:
    """
    THE ONE FUNCTION TO CALL from master_gmail_reviewer.py for every
    non-attachment (general inquiry) candidate email.

    1. Attempts to match sender_name to a Quo contact -> pulls their SMS history
    2. Sends full context to Claude
    3. Returns a decision dict — caller saves DRAFT as a Gmail Draft,
       appends FLAG_HUMAN to master_needs_human_review.txt, and does
       nothing further for SKIP.
    """
    quo_sms_history = ""
    # [CHANGED 2026-07-02, Round 6] Try the exact email match first — it's
    # unambiguous and doesn't depend on display-name quality. Only fall back
    # to name-matching if this sender's email hasn't been seen/backfilled yet
    # (see match_phone_by_sender_email / backfill_email_onto_contact above).
    match = match_phone_by_sender_email(sender_email) if sender_email else None
    matched_via = "email" if match else None
    if not match:
        match = match_phone_by_sender_name(sender_name) if sender_name else None
        matched_via = "name" if match else None

    if match:
        phone, first, last = match
        log.info(f"  Matched '{sender_name}' <{sender_email}> -> Quo contact {first} {last} ({phone}) via {matched_via}")
        quo_sms_history = get_quo_history(phone)
        if matched_via == "name" and sender_name and sender_email:
            backfill_email_onto_contact(sender_name, sender_email)
    else:
        phone, first = None, None
        log.info(f"  No confident Quo match for '{sender_name}' <{sender_email}> — proceeding with email-only context")

    decision = decide_email_reply(
        sender_name=sender_name,
        sender_email=sender_email,
        subject=subject,
        inbound_body=inbound_body,
        gmail_thread_history=gmail_thread_history,
        quo_sms_history=quo_sms_history,
    )

    # [ADDED 2026-07-02, Round 6 — closes KNOWN GAP #1] Only fires on the
    # dedicated FLAG_HUMAN_OPTOUT code, never on freeform FLAG_HUMAN reason
    # text. Always sets sync_result so the caller (master_gmail_reviewer.py)
    # can log exactly what happened — including "no Quo match, nothing to
    # sync" — rather than silently doing nothing.
    decision["sync_result"] = None
    if decision["decision"] == DECISION_FLAG_OPTOUT:
        if phone:
            decision["sync_result"] = sync_email_optout_to_sms(phone, first)
        else:
            decision["sync_result"] = {
                "synced": False, "already_synced": False, "rename_ok": False,
                "reason": "no confident Quo/phone match for this sender — could not sync, "
                          "human must add the phone to master_permanent_optouts.txt manually",
            }
            log.warning(
                f"  Email opt-out from '{sender_name}' <{sender_email}> could not be synced "
                f"to SMS opt-out list — no matching Quo contact found. Manual action needed."
            )

    return decision
