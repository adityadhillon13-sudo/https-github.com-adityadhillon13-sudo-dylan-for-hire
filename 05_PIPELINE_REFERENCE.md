# DYLAN FOR HIRE — PIPELINE REFERENCE
**Version:** 2.1 | **Last Updated:** 2026-07-02
**Purpose:** Exact logic, conditions, and decision trees for every pipeline step.
**Source:** master_daily_agent.py v2.1, master_gmail_reviewer.py v1.2,
email_context_bridge.py, master_gmail_pubsub_listener.py, master_sms_poll_service.py,
master_candidate_file_consolidator.py v1.0 (NEW 2026-07-02) — all verified line by
line, 2026-07-02, EXCEPT the two new v1.2/v1.0 additions (STEP 6 and STEP 7 below),
which are written and unit-checked (syntax valid, imports resolve, PDF-merge logic
tested against synthetic files) but NOT YET RUN against real Gmail/Quo data. See
09_GO_LIVE_READINESS.md before trusting their output in production.

## LIVE DASHBOARDS (Cowork artifacts — read-only views over this pipeline's data)

Two persistent Cowork artifacts exist and pull live data from Quo + Gmail on
every open/reload — neither writes anything without an explicit human click:

1. **BlueLine Live Dashboard** (id: `blueline-live-dashboard`) — inbox monitor.
   Shows unanswered Quo SMS and Gmail threads needing a reply, with an
   AI-drafted response per item, plus a running activity log and an
   "Automated Notices" bucket for non-candidate mail. Send (Quo) / Create Gmail
   Draft / Approve & Send All buttons, each behind a confirmation dialog.
   This is also what the "Blueline live monitor" scheduled task (runs every 15
   min, Mon–Fri) mirrors into chat — that scheduled task NEVER sends anything;
   only this dashboard's own buttons do.

2. **BlueLine Pipeline Dashboard** (id: `blueline-pipeline-dashboard`, NEW
   2026-07-02) — funnel metrics. Total leads in system, new leads (this
   month / 30d / 7d, by first-message-date proxy since Quo doesn't expose a
   contact creation date in bulk), active conversations (7d), no-response,
   needs-follow-up (mirrors STEP 1's stalled/never-replied split below), and
   — critically — Hot Files / Submission-Ready / Drafts-Prepared-For-Centers
   counts read directly from each Quo contact's `role` field (see STEP 6).
   Has a fast "Quick Refresh" (contacts + stage tags only) and a slower "Deep
   Scan" (full per-contact message history, needed for the activity/new-lead/
   follow-up numbers). Until STEP 6/7 below have run at least once on real
   mail, its Document & Onboarding Stage section will correctly show zero.

---

## PIPELINE OVERVIEW

```
master_daily_agent.py::main()  — DAILY CRON, 9am EST, unchanged

  step3_sms_reply_handler()      ← ALL inbound SMS replies
  step1_reengage_stalled()        ← ALL contacts silent 96+ hrs
  merge_duplicate_contacts()      ← DEDUP before new outreach
  step2_new_leads()               ← NEW intro SMS to CSV leads
```

`master_sms_poll_service.py` (NEW, v2.0 — 24/7 companion):
```
  step3_sms_reply_handler()      ← same function, called every ~90 sec, all day
                                     (imported unmodified from master_daily_agent.py)
```

`master_gmail_reviewer.py` v1.1 (batch mode — can still run standalone on demand):
```
  get_unread_messages_all()       ← ALL unread candidate emails (was: attachment-only)
  process_sender() branches to:
    → doc-review flow (attachments present) — Claude Vision, unchanged
    → email_context_bridge flow (no attachments) — NEW, see STEP 5 below
```

`master_gmail_pubsub_listener.py` (NEW, v2.0 — 24/7 real-time):
```
  Gmail watch() + Pub/Sub pull → process_new_message_by_id() per new message
  (calls the SAME process_sender() logic above — no separate code path)
```

---

## STEP 3 — SMS REPLY HANDLER

**Trigger:** Runs at start of every main() call  
**Function:** `step3_sms_reply_handler()`  
**What it reads:** All Quo conversations with inbound activity in last 7 days (performance-optimised — not all conversations, only recently active ones)

### Decision Tree

```
For each active conversation:
  ├── Fetch all messages in conversation
  ├── Find the latest INBOUND message
  ├── Check if message ID is in master_handled_interest_replies.txt
  │     └── If YES → SKIP (already handled this run or a previous run)
  │
  ├── Normalise message text (lowercase, strip punctuation)
  │
  ├── Check against OPTOUT_KEYWORDS
  │   {"stop","unsubscribe","remove","opt out","optout","dont text","do not text",
  │    "dont contact","do not contact","wrong number","take me off"}
  │   └── If match → OPT-OUT FLOW:
  │         1. Rename Quo contact: firstName = "DO NOT MESSAGE - {original_name}"
  │         2. Clear contact lastName
  │         3. Delete Quo conversation
  │         4. Add phone to master_permanent_optouts.txt
  │         5. Log action
  │
  ├── Check against INTEREST_KEYWORDS
  │   {"yes","interested","asap","available","open","ready","sure","absolutely",
  │    "definitely","of course","sign me up","count me in","let's do it",
  │    "lets do it","i'm in","im in","send me","send info"}
  │   └── If match → INTEREST FLOW:
  │         1. Detect license from contact's lastName field (e.g. "RN, Queens" → "RN")
  │         2. Send DOCUMENT_CHECKLIST_MSG (full document list + pay rates)
  │         3. Wait 2 seconds
  │         4. Add message ID to master_handled_interest_replies.txt
  │         5. Log action
  │         (Confirmed 2026-07-01: no ADD_ON_STUFF_MESSAGE constant or send call
  │          exists anywhere in current code — that legacy step is gone, not
  │          just undocumented. Removed from this decision tree.)
  │
  └── If no keyword match → UNKNOWN FLOW:
        1. Append to master_needs_human_review.txt with full context
        2. Log action as "FLAGGED_FOR_REVIEW"
```

### Opt-out Keywords (full list from v2.1 code)
```python
OPTOUT_KEYWORDS = {
    'stop', 'unsubscribe', 'remove', 'opt out', 'optout',
    'dont text', 'do not text', 'dont contact', 'do not contact',
    'wrong number', 'take me off', 'please stop', 'no thanks',
    'not interested', 'leave me alone'
}
```

### Interest Keywords (full list from v2.1 code)
```python
INTEREST_KEYWORDS = {
    'yes', 'yep', 'yeah', 'yup', 'sure', 'ok', 'okay',
    'interested', 'i am interested', 'i\'m interested',
    'available', 'open', 'open to it', 'ready',
    'asap', 'immediately', 'right away',
    'absolutely', 'definitely', 'of course',
    'sign me up', 'count me in', 'let\'s do it', 'lets do it',
    'i\'m in', 'im in', 'send me', 'send info', 'tell me more'
}
```

---

## STEP 1 — RE-ENGAGE STALLED CONTACTS

**Trigger:** Runs after Step 3, before DEDUP  
**Function:** `step1_reengage_stalled()`  
**What it targets:** All Quo contacts where the last outbound message was 96+ hours ago AND no inbound reply has been received

### Decision Tree

```
Fetch ALL Quo contacts (paginated)

For each contact:
  ├── Check firstName against "DO NOT MESSAGE" prefix → SKIP
  ├── Check phone against BLOCKED_NUMBERS → SKIP
  ├── Check phone against master_permanent_optouts.txt → SKIP
  ├── Check if contact was handled in this run's Step 3 (interest/optout) → SKIP
  │
  ├── Calculate hours since last outbound message
  │   └── If < 72 hours → SKIP (not stalled yet)
  │       [UPDATED 2026-07-02, Round 14 — lowered from 96h to 72h
  │       (STALL_WINDOW_HOURS) per Aditya's explicit rule]
  │
  └── For every contact past the stall window (no never_replied/stalled
      split anymore — that classification was retired when upgrade1 was
      introduced; [CORRECTED 2026-07-02, Round 14 audit] this whole branch
      was stale — confirmed via grep across all of src/ that
      NO_RESPONSE_FINAL, GENERIC_FOLLOWUP, and never_replied do not exist
      anywhere in the current codebase):
      ├── Call get_context_aware_sms(name, phone, role, borough)
      │   ├── Returns personalised message string → SEND it, log REENGAGE_SENT
      │   └── Returns None → SKIP entirely (mid-process, active email,
      │       interview scheduled, etc.), log REENGAGE_SKIPPED
      │
      └── There is no separate hardcoded fallback template sent directly
          from step1_reengage_stalled() itself — see
          upgrade1_context_aware_messaging.py for how get_context_aware_sms
          handles its own internal Claude-call failures.
```

### Context-Aware Messaging Logic (upgrade1)

```
get_context_aware_sms(phone, name, license_type):
  1. GET Quo conversation for phone → fetch last 4 days of messages
     (If API call fails: use empty history)
  
  2. GET Gmail threads matching candidate name → fetch last 4 days
     (If API call fails: use empty history)
  
  3. Call claude-haiku-4-5-20251001 with:
     - SMS history (4 days)
     - Email history (4 days)
     - Candidate name + license type
     - Instruction: write a personalised re-engagement SMS (< 160 chars, no emoji)
       OR return the exact string "SKIP" if candidate is mid-process
  
  4. If Claude returns "SKIP" → return None
  5. If Claude returns a message → return that message
  6. If Claude fails → return None (do not fall through to generic)
```

### Skip Conditions for Context-Aware Messaging

The Claude haiku prompt instructs it to return "SKIP" if:
- Candidate submitted documents in the last 4 days (don't interrupt mid-process)
- Candidate is in an active email thread within last 24 hours
- Candidate has an interview or appointment scheduled
- Last outreach was within 24 hours (regardless of the 72-hour window)

---

## DEDUP — MERGE DUPLICATE CONTACTS

**Trigger:** Runs after Step 1, before Step 2  
**Function:** `merge_duplicate_contacts()`  
**Purpose:** Clean up any duplicate Quo contacts before sending new intros

### Algorithm

```
1. Fetch ALL Quo contacts (paginated, 100/page)
2. Build index:
   - phone_map: normalised_phone → contact
   - name_map: normalised_full_name → contact
   - firstname_map: normalised_first_name → contact

3. For each pair of contacts:
   ├── If same normalised phone → MERGE
   ├── If same normalised full name → MERGE
   └── If same normalised first name AND similar lastName → MERGE

4. Merge procedure:
   ├── Keep the contact with the most complete data (non-empty fields)
   ├── Delete the duplicate via DELETE /contacts/{id}
   └── Log merge action

5. Update master_processed_contacts.txt to remove duplicate phone numbers
```

### Name Normalisation

```python
def normalise_name(name):
    name = name.lower().strip()
    name = unicodedata.normalize('NFKD', name)  # strip accents
    name = re.sub(r'[^a-z0-9 ]', '', name)       # strip punctuation
    name = re.sub(r'\s+', ' ', name)               # collapse spaces
    return name
```

---

## STEP 2 — NEW LEAD INTRO SMS

**Trigger:** Runs last in main()  
**Function:** `step2_new_leads()`  
**Source:** `~/Downloads/BlueLine/CONFIDENTIAL_candidates.csv`

### Decision Tree

```
Read CONFIDENTIAL_candidates.csv (utf-8-sig encoding)
Calculate sends_today based on daily cap and catchup logic

For each row in CSV (up to sends_today):
  ├── Skip if phone already in master_processed_contacts.txt
  │   (already sent intro SMS in a previous run)
  │
  ├── Skip if phone in master_permanent_optouts.txt
  │
  ├── Skip if phone in BLOCKED_NUMBERS
  │
  ├── Normalise phone to E.164 format (+1XXXXXXXXXX)
  │
  ├── Run 3-pass dedup against live Quo contacts:
  │   ├── Pass 1: phone match → SKIP if found
  │   ├── Pass 2: full name match → SKIP if found
  │   └── Pass 3: first name match → SKIP if found
  │
  ├── Detect license type — reads the `Role` column specifically (row.get("Role")
  │   or row.get("role")), NOT a free-text scan of all fields. Value is upper-cased
  │   and used as-is; if the column is absent or empty, silently defaults to "CNA"
  │   with no warning. (Corrected 2026-07-01 — this was previously documented as
  │   scanning all CSV fields, which is not how the code works.)
  │
  ├── Detect NYC borough — reads the `Location` column specifically
  │   (row.get("Location") or row.get("location")) and runs it through
  │   detect_borough() (keyword + zip map). If the column is absent or empty,
  │   silently defaults to "NY". (Corrected 2026-07-01 — same fix as above;
  │   this is not a scan of every CSV column.)
  │
  │   ⚠️ Practical implication: a CSV prepared without columns literally named
  │   `Role` and `Location` will silently produce CNA/NY for every candidate —
  │   no error, no log warning. Confirm actual column names before onboarding
  │   any new client's lead list.
  │
  ├── Create Quo contact:
  │   firstName = "Full Name"
  │   lastName = "LICENSE, Borough"
  │   phoneNumbers = [{"number": "+1XXXXXXXXXX"}]
  │
  ├── Send DYLAN_INTRO SMS:
  │   POST /messages
  │   {from: "+15512506678", to: "+1XXXXXXXXXX",
  │    content: DYLAN_INTRO.format(first_name=..., license_type=...),
  │    phoneNumberId: "PNWtLBsgMe"}
  │
  ├── If HTTP 200 → add phone to master_processed_contacts.txt
  │   (ONLY on confirmed success — failed sends retry next run)
  │
  └── If non-200 → log error, do NOT add to processed list
      (will be retried on next run)
```

### Daily Cap / Catchup Logic

```python
DAILY_CAP = 30
MAX_CATCHUP = 150

last_run = read_timestamp()   # ~/Downloads/master_last_run_timestamp.txt
days_missed = max(1, (now - last_run).days)
sends_today = min(DAILY_CAP * days_missed, MAX_CATCHUP)
# Result: 30 normal, up to 150 if 5+ days missed
```

---

## STEP 4 — GMAIL DOCUMENT REVIEW (SEPARATE SCRIPT)

**Script:** `master_gmail_reviewer.py`  
**Trigger:** Run separately, on demand  
**What it monitors:** Unread emails at `info@bluelinestaffing.com` with attachments (last 15 days)

### Decision Tree

```
Authenticate to Gmail (OAuth2 token)
Query: unread emails with attachments, from last 15 days

For each qualifying email thread:
  ├── Check if thread ID in master_processed_email_ids.txt → SKIP
  │
  ├── Get sender email and name
  │
  ├── CUMULATIVE MODE: Fetch ALL past emails from this sender (not just this one)
  │   Purpose: gather full document set — candidate may have submitted across multiple emails
  │
  ├── Collect all attachments across full email history
  │
  ├── For each attachment:
  │   ├── Decode base64 → raw bytes
  │   ├── Send to claude-opus-4-5 as base64 PDF/image
  │   ├── Receive structured JSON:
  │   │   {
  │   │     "nursing_license": {"found": bool, "state": "NY", "expiry": "date", "valid": bool},
  │   │     "physical_exam": {"found": bool, "date": "date", "within_12_months": bool},
  │   │     "mmr_titers": {"found": bool, "date": "date", "immune": bool, "within_5_years": bool},
  │   │     "varicella_titers": {"found": bool, "date": "date", "immune": bool},
  │   │     "tb_test": {"found": bool, "type": "PPD|CXR|Quantiferon", "date": "date", "within_9_months": bool},
  │   │     "covid_vaccine": {"found": bool, "complete": bool},
  │   │     "bls_cpr": {"found": bool, "expiry": "date", "valid": bool},
  │   │     "i9_documents": {"list_a": bool, "list_b": bool, "list_c": bool, "compliant": bool},
  │   │     "resume": {"found": bool}
  │   │   }
  │   └── Aggregate results across all attachments
  │
  ├── Validate aggregated results:
  │   ├── Physical: must be within 12 months of today
  │   ├── MMR titers: within 5 years, must show immunity
  │   ├── Varicella titers: within 5 years, must show immunity
  │   ├── TB test (PPD OR Chest X-Ray OR Quantiferon): within 9 months
  │   ├── Nursing license: must be New York State, must not be expired
  │   ├── BLS/CPR: must not be expired
  │   └── I-9 documents: List A alone, OR List B + List C together
  │
  ├── Detect license type from parsed nursing_license field
  │   → Select correct PDF: RN .pdf, LPN .pdf, or CNA .pdf
  │
  ├── Compose reply email:
  │   Subject: "Re: [original subject]"
  │   Body: Professional Dylan-persona reply with ✓/✗ checklist
  │         ✓ = document found and valid
  │         ✗ = document missing, expired, or invalid (with reason)
  │         Attach: correct onboarding PDF from ~/Desktop/aditya/
  │
  ├── SAVE AS GMAIL DRAFT (never send automatically)
  │
  └── Add thread ID to master_processed_email_ids.txt
```

### NYS Document Validation Rules

| Document | Required? | Date Window | Validity Criteria |
|----------|-----------|-------------|-------------------|
| Nursing license | Yes | Must not be expired | New York State only |
| Physical exam | Yes | ≤ 12 months old | Recent physician signature |
| MMR titers | Yes | ≤ 5 years old | Must show immunity (not just vaccination) |
| Varicella titers | Yes | ≤ 5 years old | Must show immunity |
| TB test (PPD or CXR or Quantiferon) | Yes | ≤ 9 months old | Any one is sufficient |
| COVID vaccine card | Yes | n/a | Complete series |
| I-9 documents | Yes | n/a | List A alone OR List B + List C |
| Resume | Yes | n/a | For candidate profile |
| BLS/CPR card | Recommended | Must not be expired if submitted | Marked `optional: True` — noted, not blocking |
| Hepatitis B vaccine | Recommended | n/a | Vaccine card, titer, **or signed declination** — `optional: True` |
| Annual flu vaccine | Recommended | Current season | Vaccine card **or signed declination** — `optional: True` |

**8 required + 3 recommended = 11 total tracked categories.** Do not shorthand this as
"11-point check" without the required/recommended split — that exact shorthand is what
caused the original inaccurate "11-point" marketing claim this project spent two audit
rounds correcting. If asked what's required vs. nice-to-have, the answer is the 8-row
"Yes" list above; the 3 "Recommended" rows are tracked and shown to the candidate/operator
but never block the "documents complete" email.

**Corrected 2026-07-01:** this table previously listed BLS/CPR as required and
Resume/COVID as "Recommended" (optional). A direct read of `validate_documents()`
in `master_gmail_reviewer.py` shows the opposite for BLS/CPR: it's marked
`"optional": True`, so it never blocks the "documents complete" email.
Resume and COVID carry no optional flag and are therefore treated as required.

**Re-verified 2026-07-01 (Round 2 audit):** confirmed the table was exactly 9 categories
at that point, matching `validate_documents()` exactly.

**Updated 2026-07-01 (Round 4 — Aditya's product decision):** Hepatitis B and annual flu
vaccine added to `validate_documents()` and the Vision JSON schema, both as
`optional: True` (recommended, not blocking) — matching the BLS/CPR pattern, not the
required-category pattern. Rationale: both OSHA (Hepatitis B) and standard flu-vaccine
policy allow a signed declination as a legitimate alternative to vaccination. The system
cannot yet distinguish "no vaccine, not compliant" from "no vaccine, validly declined" —
making either one a blocking requirement today would incorrectly flag candidates who
already did the compliant thing by declining on paper. Non-blocking is the technically
correct choice given that limitation, not just a lighter-touch compromise.
**Status: built, not yet verified against a real document (see `09_GO_LIVE_READINESS.md`
🟡 list) — do not repeat "11 categories tracked" to a prospect until at least one real
test document confirms Claude Vision extracts these two fields correctly.** NYS
background-check/fingerprint clearance remains unbuilt and undecided — see
`09_GO_LIVE_READINESS.md` 🔴 KNOWN GAPS #6.

### Application PDF Selection Logic

```python
license_to_pdf = {
    "RN":  "~/Desktop/aditya/Editable Onboarding Blueline RN .pdf",
    "RNS": "~/Desktop/aditya/Editable Onboarding Blueline RN .pdf",
    "LPN": "~/Desktop/aditya/Editable Onboarding Blueline LPN .pdf",
    "CNA": "~/Desktop/aditya/Editable Onboarding Blueline CNA .pdf",
    "HHA": "~/Desktop/aditya/Editable Onboarding Blueline CNA .pdf",  # default to CNA
}
```

---

## STEP 5 — GENERAL EMAIL INQUIRY (NEW, v2.0)

**Module:** `email_context_bridge.py`, called from `master_gmail_reviewer.py::process_sender()`
**Trigger:** Any unread email from a non-filtered sender with NO document attachments
**Runs:** Continuously (real-time listener) or on-demand (batch mode) — same logic either way

### Decision Tree

```
For each unread, non-attachment email from a candidate:
  ├── Extract sender display name from "From" header
  │
  ├── match_phone_by_sender_name(sender_name):
  │     ├── Fetch all Quo contacts (skip any "DO NOT MESSAGE" prefixed ones)
  │     ├── Full-name match (normalised) → use if exactly one match
  │     ├── Else first-name match → use only if exactly one candidate has it
  │     └── Ambiguous or no match → proceed with Gmail-only context (no block)
  │
  ├── If matched → get_quo_history(phone) [reused from upgrade1_context_aware_messaging.py,
  │     same 4-day window, same endpoint — not reimplemented]
  │
  ├── Build full Gmail thread history text (all prior emails from this sender,
  │     excluding the new inbound one, which is passed separately)
  │
  ├── Send to claude-opus-4-5: sender info + new inbound email + Gmail history +
  │     Quo SMS history (or "None / no Quo match")
  │
  └── Claude returns exactly one of:
        FLAG_HUMAN: <reason>   → append to master_needs_human_review_email.txt, no draft
        SKIP: <reason>         → no action (duplicate, automated notice, nothing to answer)
        DRAFT: <full reply>    → compose_general_reply_email() → save_as_draft() (never sent)
```

### FLAG_HUMAN triggers (always wins — see full list in the module's system prompt)
- Any opt-out / removal / "stop contacting me" signal in an email (email opt-outs
  are NOT currently written to `master_permanent_optouts.txt` automatically — that
  file is phone-keyed; an email opt-out requires you to also stop SMS manually if
  the same person has a Quo record — see 07_COMPLIANCE.md)
- Legal, complaint, discrimination, regulatory-body language
- Pricing/contract/rate negotiation — commits the agency to specific terms
- Client/facility-originated email (not a candidate) — scheduling, billing, a placed nurse
- Anything Claude isn't confident it understands, or where the email contradicts
  what's already on file

### Known limitation — name-matching, not a guaranteed lookup
Quo contacts don't store an email address, so matching an inbound email to a
Quo phone number is a best-effort display-name match. If a candidate emails
from an address whose display name doesn't match what's in Quo (a nickname,
a shared family email, or just the raw email address with no display name),
the match fails gracefully — the reply still gets drafted, just without SMS
context. This degrades quality, not safety — the FLAG_HUMAN gate is
unaffected either way.

---

## STEP 6 — PIPELINE STAGE TRACKING (NEW, v1.2, 2026-07-02)

**Module:** `master_gmail_reviewer.py` (same doc-review flow as STEP 4, extended)
**Trigger:** Every time a doc-review reply draft is composed (i.e. every time
STEP 4's Claude Vision analysis runs for a sender)
**Why this exists:** Before v1.2, "docs complete" / "onboarding sent" only
ever existed as prose inside a Gmail draft — no dashboard or script could
read it without re-running Vision analysis. This closes that gap by writing
one of four stage tags to the candidate's Quo contact `role` field (chosen
because it's already exposed, unused, and both readable and writable by
every tool this project already uses — no new API, no new credentials).

### Decision Tree

```
After validate_documents() produces validation_results for a sender:
  ├── compute_pipeline_stage(validation_results):
  │     medical_complete = all 8 required medical categories are "ok"
  │       (resume, nursing_license, id_documents, physical, mmr_titers,
  │        varicella_titers, chest_tb, covid_vaccine — same 8 that gate
  │        compose_reply_email's "documents complete" branch in STEP 4)
  │     onboarding_returned = employment_application.ok
  │       (NEW tracked category — see below)
  │
  │     ├── NOT medical_complete            → PIPELINE:DOCS_INCOMPLETE
  │     ├── medical_complete, NOT returned   → PIPELINE:DOCS_COMPLETE_ONBOARD_SENT   ("hot file")
  │     └── medical_complete AND returned    → PIPELINE:ONBOARD_RETURNED_READY_FOR_SUBMISSION
  │
  │     [FIXED 2026-07-02] These tags originally contained a literal "|"
  │     (e.g. "DOCS_COMPLETE|ONBOARD_SENT"). Quo's own list-contacts renders
  │     contacts as pipe-delimited text without escaping "|" inside field
  │     values, so a role containing "|" shifted every column after it
  │     (email, phone) out of alignment — this broke the Pipeline
  │     Dashboard's parsing the moment a real stage got pushed. Underscore-
  │     only from here on; the dashboard's parser was also hardened to
  │     recover gracefully if it ever encounters the old corrupted format.
  │
  ├── match_phone_by_sender_name(candidate_name) — same best-effort match as STEP 5
  │     └── No confident match → log a warning, do NOT push (dashboard will
  │           undercount this candidate until the match improves or Aditya
  │           adds their email to the Quo contact manually)
  │
  └── PATCH /contacts/{id} {defaultFields: {role: <stage>}} via the real
        OpenPhone API (same auth/base URL as master_daily_agent.py)
```

### New tracked category: `employment_application`

Added to the Claude Vision extraction schema in STEP 4 specifically to
distinguish "candidate returned their signed onboarding form" from "candidate
sent yet another random document." `found` = the form is present somewhere in
their attachments; `signed` = a signature/initials are visible on it. Marked
`optional: True` in `validate_documents()` — it never blocks the medical
"documents complete" email (that gate is unchanged from STEP 4), it only
feeds STEP 6's stage computation above.

### What this does NOT do
- Never sets `PIPELINE:SUBMITTED` — only `master_candidate_file_consolidator.py`
  (STEP 7) can move a candidate past `READY_FOR_SUBMISSION`, and even it only
  reaches `SUBMISSION_DRAFTS_READY`, never a confirmed-sent state (see STEP 7).
- Never sends anything, never modifies the Gmail draft flow — this is a pure
  side-effect addition to the existing STEP 4 doc-review pass.
- **STATUS: written 2026-07-02, NOT YET RUN against a real candidate.**
  Test with one real doc-review pass before trusting the Pipeline Dashboard's
  Hot Files / Submission-Ready counts.

---

## STEP 7 — CANDIDATE FILE CONSOLIDATION & CENTER SUBMISSION (NEW, v1.0, 2026-07-02)

**Script:** `master_candidate_file_consolidator.py` — standalone, run on demand,
NOT wired into the daily cron
**Trigger:** Manual (`python3.11 master_candidate_file_consolidator.py` or
`--email a@b.com` for a single candidate)
**Precondition:** Candidate's Quo `role` = `PIPELINE:ONBOARD_RETURNED_READY_FOR_SUBMISSION`

### Why this is a separate script, not folded into master_gmail_reviewer.py
The Cowork MCP Gmail connector used by the Pipeline Dashboard (and available
in Cowork chat generally) cannot download attachment bytes from any email and
its own `create_draft` tool explicitly states attachments aren't supported —
confirmed by inspecting both tool schemas directly, 2026-07-02. The REAL
Gmail API that `master_gmail_reviewer.py` already authenticates against on
your Mac has neither limitation, so file consolidation had to live there, as
a script you run locally — it cannot be built as a Cowork artifact today.

### Decision Tree

```
For each candidate with role == READY_FOR_SUBMISSION (or one --email target):
  ├── Pull every attachment across their full email history (reuses STEP 4's
  │     get_all_attachments — same 10-attachment cap per sender)
  │
  ├── Classify EACH attachment individually as MEDICAL / RESUME / ONBOARDING /
  │     OTHER via one small Claude call per file (NEW — STEP 4's aggregate
  │     Vision call never tagged which specific file was which, only whether
  │     categories existed somewhere in the pile)
  │
  ├── Merge same-category files into three PDFs (pypdf for existing PDFs,
  │     Pillow to convert images to PDF pages first):
  │       {FullName}-{License}-Medical.pdf
  │       {FullName}-{License}-Resume.pdf
  │       {FullName}-{License}-Onboarding.pdf
  │     saved to ~/Downloads/BlueLine/CandidateFiles/
  │
  ├── Read the candidate's Quo SMS history (60-day window) and ask Claude
  │     which centers in BLUELINE_CENTER_DIRECTORY.md match what they
  │     actually said (borough/shift/named center) — BEST-EFFORT, candidates
  │     state boroughs in free text, not a structured field. Always review
  │     before sending.
  │
  ├── Compose ONE Gmail DRAFT per matched center, three PDFs attached via the
  │     real Gmail API — DRAFT MODE, same invariant as every other script in
  │     this project. Nothing is ever sent automatically.
  │
  └── PATCH role → PIPELINE:SUBMISSION_DRAFTS_READY:<ISO date>
        (never PIPELINE:SUBMITTED — see Known Gaps below)
```

### Known Gaps (full detail in the script's own docstring/footer)
1. **Untested end to end** — written 2026-07-02. Run `--email` on one real
   candidate first; check PDFs open, drafts show 3 attachments, Quo role updates.
2. **Center directory parsing is unverified** — `BLUELINE_CENTER_DIRECTORY.md`
   lives only on your Mac, not in this Cowork session. The script hands Claude
   the raw file text rather than a brittle regex parser, but if most of the 34
   centers don't actually have emails listed in that file, most candidates
   will hit "no centers matched." Confirm before relying on this broadly.
3. **No confirmed-sent tracking.** Moving a candidate from
   `SUBMISSION_DRAFTS_READY` to a true "submitted" state is a manual step
   today (or an open feature: scanning Sent Mail after the fact).
4. **Per-attachment classification cost** — one Haiku call per file, per
   candidate, every run. Fine for the small "ready for submission" list this
   targets; would need caching if ever run repeatedly over the full base.
