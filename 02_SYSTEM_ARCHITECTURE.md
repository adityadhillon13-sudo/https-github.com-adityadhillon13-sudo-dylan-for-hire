# DYLAN FOR HIRE — SYSTEM ARCHITECTURE
**Version:** 2.0 | **Last Updated:** 2026-07-01
**Source of truth:** master_daily_agent.py v2.1 (615 lines), master_gmail_reviewer.py v1.1,
upgrade1_context_aware_messaging.py v1.1 (bug-fixed 2026-07-01), email_context_bridge.py (new),
master_gmail_pubsub_listener.py (new), master_sms_poll_service.py (new)

**What's new in v2.0:** §12 corrected (the Quo URL bug it described was already fixed — see
08_TROUBLESHOOTING.md BUG history). New §13 covers the real-time layer and the new
email cross-channel bridge, which is the architectural answer to "does email check
Quo history the way SMS does" — before v2.0, it didn't; now it does.

---

## 1. HIGH-LEVEL DATA FLOW

```
CANDIDATE SOURCES
  ├── CONFIDENTIAL_candidates.csv  (CSV leads)
  ├── Indeed employer portal       (manual download → Claude reads)
  └── info@bluelinestaffing.com   (inbound email with attachments)
         │
         ▼
  ┌─────────────────────────────────────────────┐
  │         master_daily_agent.py (v2.1)        │
  │                                             │
  │  Step 3: SMS Reply Handler                  │
  │  Step 1: Re-engage Stalled Contacts         │
  │  DEDUP:  Merge Duplicate Contacts           │
  │  Step 2: New Lead Intro SMS                 │
  └─────────────────────────────────────────────┘
         │
         ▼
  ┌─────────────────────────────────────────────┐
  │   master_gmail_reviewer.py (SEPARATE)       │
  │   Step 4: Document Review                   │
  └─────────────────────────────────────────────┘
         │
         ▼
  OUTPUTS
  ├── SMS via Quo/OpenPhone API (+15512506678)
  ├── Gmail Drafts (never auto-send)
  ├── Human review queue (master_needs_human_review.txt)
  └── Run log CSV (master_run_log_YYYYMMDD_HHMMSS.csv)
```

---

## 2. CODE EXECUTION ORDER (ACTUAL)

**CRITICAL:** The technical execution order in `master_daily_agent.py::main()` is NOT the same as the logical recruitment funnel order used in presentations.

```python
# Verified from main() — actual code order:
step3_sms_reply_handler()       # inbound replies first
step1_reengage_stalled()         # then re-engage
merge_duplicate_contacts()       # dedup before new sends
step2_new_leads()                # new outreach last
```

**Why this order makes sense:**
- Handle inbound before sending outbound (avoids sending to someone who just replied)
- Re-engage before new leads (existing relationships first)
- Dedup before new leads (prevents creating duplicates on this run)
- New leads last (lowest priority — never at risk of duplicating active conversations)

**Note:** Gmail document review (`master_gmail_reviewer.py`) runs as a completely separate script. It is NOT called from `main()`. Run it separately, on demand, when email volume warrants.

---

## 3. FILE STRUCTURE — EVERY FILE, WHAT IT DOES, AND WHERE IT LIVES

```
RUNTIME DIRECTORY: ~/Downloads/BlueLine/
├── master_daily_agent.py               ← MAIN ORCHESTRATOR (v2.1, 615 lines)
│   • Runs Steps 3→1→DEDUP→2
│   • Module-level constants: all SMS templates, BLOCKED_NUMBERS, keyword sets
│   • Validates all 3 env keys at startup — aborts if any missing
│
├── master_gmail_reviewer.py            ← GMAIL DOC REVIEW (Step 4, separate)
│   • OAuth2 Gmail access via google-auth-oauthlib
│   • Claude Vision (claude-opus-4-5) reads attachments as base64
│   • Validates against 9 doc categories + NYS date windows
│   • Creates Gmail Draft — never sends
│
├── master_gmail_setup.py               ← ONE-TIME OAUTH SETUP
│   • Run once to generate gmail_token.json
│   • Opens browser for Google authorization
│
├── upgrade1_context_aware_messaging.py ← CONTEXT-AWARE SMS (imported by Steps 1 & 3)
│   • Calls Quo API to fetch last 4 days of SMS history
│   • Calls Gmail API to fetch last 4 days of email threads
│   • Passes to claude-haiku-4-5 for re-engagement message generation
│   • Returns None if context says skip (mid-process, active email, etc.)
│   ✅ CORRECTED 2026-07-01: already uses https://api.openphone.com/v1 with no
│      Bearer prefix (fixed v1.1, 2026-06-29) — see §12 below. The real bug found
│      here was a Gmail token path mismatch, not the URL — see 08_TROUBLESHOOTING.md BUG-14.
│
├── master_requirements.txt             ← PIP DEPENDENCIES
│   anthropic, requests, python-dotenv, google-auth-oauthlib, google-api-python-client
│
├── CONFIDENTIAL_candidates.csv         ← LEAD LIST [NEVER COMMIT]
│   • Columns: name, phone + license/location/experience fields
│   • UTF-8 BOM encoding (loaded with utf-8-sig)
│   • 344+ candidates as of 2026-06-30
│
├── gmail_credentials.json              ← GOOGLE OAUTH2 CLIENT CREDS [NEVER COMMIT]
├── gmail_token.json                    ← GOOGLE OAUTH2 ACCESS TOKEN [NEVER COMMIT, auto-refreshes]
├── .env                                ← API KEYS [NEVER COMMIT]
│   • CLAUDE_API_KEY=sk-ant-...
│   • QUO_API_KEY=...
│   • QUO_PHONE_NUMBER_ID=PNWtLBsgMe
│   ⚠️ LOADED FROM: ~/Downloads/.env (NOT ~/Downloads/BlueLine/.env)
│      Code calls: load_dotenv(Path.home() / "Downloads" / ".env")
│
├── cron_output.log                     ← CRON EXECUTION LOG (append-mode)
├── CLAUDE.md                           ← Agent context for Claude
└── BLUELINE_*.md                       ← Operational documentation (6 files)

STATE FILES DIRECTORY: ~/Downloads/  (auto-generated, persist across runs)
├── master_processed_contacts.txt       ← Phone numbers sent intro SMS (dedup guard)
├── master_permanent_optouts.txt        ← PERMANENT opt-outs [NEVER DELETE — TCPA]
├── master_last_run_timestamp.txt       ← ISO timestamp — drives catchup logic
├── master_handled_interest_replies.txt ← Quo message IDs already responded to
├── master_needs_human_review.txt       ← Unrecognised replies → Aditya reviews
├── master_processed_email_ids.txt      ← Gmail message IDs already reviewed
└── master_run_log_YYYYMMDD_HHMMSS.csv ← Per-run action log (new file each run)

APPLICATION PDFs: ~/Desktop/aditya/  (must exist for Gmail doc review to work)
├── Editable Onboarding Blueline RN .pdf
├── Editable Onboarding Blueline LPN .pdf
└── Editable Onboarding Blueline CNA .pdf
```

---

## 4. API INTEGRATIONS

### 4A. Quo / OpenPhone API

| Detail | Value |
|--------|-------|
| Base URL | `https://api.openphone.com/v1` |
| Auth header | `Authorization: {QUO_API_KEY}` (NO "Bearer" prefix — this is OpenPhone's format) |
| Content-Type | `application/json` |
| Outbound SMS number | `+15512506678` |
| Phone number ID | `PNWtLBsgMe` (from env: QUO_PHONE_NUMBER_ID) |

**Endpoints used:**

```
POST /messages
  Body: { "from": "+15512506678", "to": "+1XXXXXXXXXX",
          "content": "...", "phoneNumberId": "PNWtLBsgMe" }
  Returns: 200 OK on success; non-200 = do not mark as processed

GET /contacts?pageSize=100&pageToken={token}
  Returns paginated list; iterate nextPageToken

POST /contacts
  Body: { "firstName": "Full Name", "lastName": "LICENSE, Borough",
          "phoneNumbers": [{"number": "+1XXXXXXXXXX"}] }

PATCH /contacts/{contactId}
  Used to rename opt-out contacts to "DO NOT MESSAGE - {name}"

GET /conversations?phoneNumberId=PNWtLBsgMe&pageSize=50
  Returns conversations with recent activity

GET /conversations/{conversationId}/messages?pageSize=50
  Returns messages in conversation; used to read inbound replies
```

**Pagination pattern:**
```python
pageToken = None
while True:
    params = {"pageSize": 100}
    if pageToken:
        params["pageToken"] = pageToken
    resp = requests.get(url, headers=headers, params=params)
    data = resp.json()
    items.extend(data.get("data", []))
    pageToken = data.get("nextPageToken")
    if not pageToken:
        break
```

### 4B. Anthropic Claude API

| Usage | Model | Where |
|-------|-------|-------|
| Gmail document review (Step 4) | `claude-opus-4-5` | master_gmail_reviewer.py |
| Context-aware re-engagement (Steps 1 & 3) | `claude-haiku-4-5-20251001` | upgrade1_context_aware_messaging.py |

**Vision call pattern (Step 4):**
```python
client.messages.create(
    model="claude-opus-4-5",
    max_tokens=2000,
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": system_prompt},
            {"type": "image", "source": {"type": "base64",
             "media_type": "application/pdf", "data": base64_content}}
        ]
    }]
)
```

**Re-engagement call pattern (Step 1):**
```python
client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=160,
    messages=[{"role": "user", "content": reengagement_prompt}]
)
```

### 4C. Gmail API (Google OAuth2)

| Detail | Value |
|--------|-------|
| Monitored inbox | `info@bluelinestaffing.com` |
| Scope | `gmail.readonly` + `gmail.compose` (draft creation) |
| Token refresh | Automatic via google-auth-oauthlib |
| Credentials file | `~/Downloads/gmail_credentials.json` (NOT the BlueLine/ subfolder — corrected 2026-07-01, see BUG-14) |
| Token file | `~/Downloads/gmail_token.json` (NOT the BlueLine/ subfolder — corrected 2026-07-01, see BUG-14) |
| Email window | Last 15 days of unread emails with attachments |
| Attachment aggregation | ALL attachments from sender's full email history (cumulative) |

---

## 5. CONTACT NAMING CONVENTION (CRITICAL INVARIANT)

This convention is used throughout ALL code. Never deviate.

```
Quo Contact.firstName  = "Full Legal Name"        e.g. "Jane Doe"
Quo Contact.lastName   = "LICENSE, Borough"        e.g. "RN, Brooklyn"

Opt-out:
Quo Contact.firstName  = "DO NOT MESSAGE - {name}" e.g. "DO NOT MESSAGE - Jane Doe"
Quo Contact.lastName   = ""                        (cleared)
```

**License codes:** RN, RNS, LPN, CNA, HHA  
**Borough codes:** Bronx, Brooklyn, Manhattan, Queens, Staten Island, NY (default)

---

## 6. BLOCKED AND EXCLUDED NUMBERS

**Hardcoded in master_daily_agent.py:**
```python
BLOCKED_NUMBERS = {'+13473572031'}   # Vanessa Ratcliff — never contact
```

**State file (permanent, never delete):**
```
~/Downloads/master_permanent_optouts.txt
```
One phone number per line (+1XXXXXXXXXX format). Read at startup, checked before every send.

---

## 7. DAILY CAP AND CATCHUP LOGIC

```python
DAILY_CAP = 30        # normal daily new leads
MAX_CATCHUP = 150     # maximum if multiple days were missed

# Logic:
days_missed = (now - last_run_timestamp).days
daily_sends = min(DAILY_CAP * max(1, days_missed), MAX_CATCHUP)
```

---

## 8. DEDUPLICATION — 3-PASS ALGORITHM

Runs before Step 2 (new leads) via `merge_duplicate_contacts()`:

**Pass 1 — Phone number match**  
Normalise all phones to E.164 (+1XXXXXXXXXX). If new lead's phone matches any existing Quo contact's phone → skip.

**Pass 2 — Full name match**  
Normalise both names (lowercase, strip accents, strip punctuation). If lead's full name matches any existing contact → skip.

**Pass 3 — First name match**  
If lead's first name alone matches any existing contact's first name → skip (conservative dedup).

Contacts that pass all 3 passes are treated as new leads.

---

## 9. BOROUGH DETECTION

From CSV fields (Step 2), the system scans all CSV columns for borough keywords and ZIP codes:

```python
BOROUGH_MAP = {
    "bronx":         "Bronx",
    "brooklyn":      "Brooklyn",
    "manhattan":     "Manhattan",
    "queens":        "Queens",
    "staten island": "Staten Island",
    # ZIP code ranges also mapped:
    # 10001-10282 → Manhattan, 10451-10475 → Bronx
    # 11201-11256 → Brooklyn, 11354-11697 → Queens
    # 10301-10314 → Staten Island
}
DEFAULT_BOROUGH = "NY"   # if no borough detected
```

---

## 10. CRON AUTOMATION

**Schedule [CHANGED 2026-07-02]:** every 30 minutes, 9:00 AM–5:00 PM EST, Monday–Friday
(DST-aware via TZ=America/New_York). See rationale below.

**[CORRECTION 2026-07-02]** This doc previously stated the prior schedule was "9:00 AM EST
daily" (`0 9 * * *`). That was wrong — it described the intended setup, not what was actually
running. Verified directly against `crontab -l` on Aditya's Mac during this change: the real
prior line was `9 * * * * cd ... && set -a && source .env && set +a && python3.11
master_daily_agent.py ...` — i.e. **every hour, at minute 9, every day of the week including
weekends**, not once a day. Also found and fixed in the same session: the `TZ` environment line
had a stray leading character (`iTZ=America/New_York` instead of `TZ=America/New_York`), so cron
never actually received a `TZ` variable — the real schedule was running in whatever timezone the
Mac's system clock was set to, not confirmed EST. Both issues are resolved as of this crontab
update; also note the deployed line sources `.env` explicitly (`set -a && source .env && set +a`)
before running the script, which is preserved in the new schedule below and was not previously
documented here.

**Why running every 30 min is safe:** `step3_sms_reply_handler()` and `step1_reengage_stalled()`
both scan a fixed, unconditional 7-day conversation window every single run — not an incremental
"since last run" window — and every send action is gated by persistent dedup state on disk
(`master_processed_contacts.txt`, `master_handled_interest_replies.txt`,
`master_checklist_sent.txt`, etc.), so re-scanning the same conversations on the next run can't
cause a duplicate send. `step2_new_leads()`'s catch-up multiplier (`days_missed`, computed from
`STATE_TIMESTAMP`) is day-granularity, so multiple runs within the same day don't inflate the
new-lead SMS quota either. Net effect: this schedule change increases API call volume (Quo +
Claude) roughly 17x versus the old once-daily run, but does not change send behavior/dedup logic
at all — it's a frequency change only, not a rewrite.

**Overnight/weekend gap coverage:** because step1/step3 always look back a full 7 days regardless
of when the agent last ran, the ~16-hour gap between the last run at 5:00 PM and the first run at
9:00 AM the next business day is automatically inside that 7-day window — the first morning run
needs no special "catch up since 5pm yesterday" logic; it already rescans everything from the
last 7 days, which trivially includes the prior evening.

**Crontab entry (verified live via `crontab -l` on Aditya's Mac, 2026-07-02 — updated same day to
add master_gmail_reviewer.py, confirmed via a second live `crontab -l` paste at 2026-07-02
~14:53 EDT):**
```
TZ=America/New_York
0,30 9-16 * * 1-5 cd /Users/Aditya/Downloads/BlueLine && set -a && source .env && set +a && /usr/local/bin/python3.11 master_daily_agent.py >> /Users/Aditya/Downloads/BlueLine/cron_output.log 2>&1
0 17 * * 1-5 cd /Users/Aditya/Downloads/BlueLine && set -a && source .env && set +a && /usr/local/bin/python3.11 master_daily_agent.py >> /Users/Aditya/Downloads/BlueLine/cron_output.log 2>&1
5 9-16 * * 1-5 cd /Users/Aditya/Downloads/BlueLine && set -a && source .env && set +a && /usr/local/bin/python3.11 master_gmail_reviewer.py >> /Users/Aditya/Downloads/BlueLine/cron_output.log 2>&1
5 17 * * 1-5 cd /Users/Aditya/Downloads/BlueLine && set -a && source .env && set +a && /usr/local/bin/python3.11 master_gmail_reviewer.py >> /Users/Aditya/Downloads/BlueLine/cron_output.log 2>&1
```
Lines 1–2: `master_daily_agent.py` fires on the hour and half-hour, 9:00 AM through 4:30 PM, plus
once more at exactly 5:00 PM, Mon–Fri. 17 runs/day.
Lines 3–4 (**added 2026-07-02**): `master_gmail_reviewer.py` fires at 5 minutes past the hour,
9:05 AM through 4:35 PM, plus once more at 5:05 PM, Mon–Fri — offset 5 minutes after the daily
agent so the two scripts don't contend for the same Quo API rate-limit window. Draft-only (never
auto-sends); writes `PIPELINE:*` stage tags to Quo contacts' `role` field when it can confidently
match the sender to a contact (see `email_context_bridge.py` v1.5 — name-matching only, not
guaranteed on a candidate's first-ever email; see BUG-21 note in that file). 17 runs/day.
**Known gap:** the reviewer only scans *unread* Gmail — already-read candidate threads with
pending docs are not picked up by cron; a manual backlog pass is still needed periodically.
Nothing overnight or on weekends for either script.

**Setup:**
```bash
crontab -e    # opens nano or vi — paste the three lines above (replace any old "0 9 * * *" line, don't keep both)
```

**macOS requirement:** Grant cron Full Disk Access:  
System Settings → Privacy & Security → Full Disk Access → enable `/usr/sbin/cron`

---

## 11. PRESENTATION ASSETS ARCHITECTURE

The pitch deck and architecture doc are standalone HTML files with embedded audio:

```
build_pitch_deck.py      → generates blueline_pitch_deck.html (without audio)
build_arch_doc_v2.py     → generates blueline_architecture_doc.html (without audio)
gen_all_audio.py         → calls ElevenLabs API → writes 31 MP3s to audio2/
embed_audio.py           → base64-encodes all 31 MP3s → injects into both HTML files
```

**ElevenLabs configuration:**
```python
API_KEY     = "<redacted — see ~/Downloads/WV/pipeline/.env>"  # [REDACTED 2026-07-02, Round 14 audit — a real ElevenLabs key was committed here in plaintext at baseline commit 3e936f5. Redacting the working copy does NOT remove it from git history; flagging to Aditya as a DECISION NEEDED item rather than silently rewriting history.]
VOICE_ID    = "VFWoJnruwuOotFvMLmcM"   # BlueLine narration voice
MODEL       = "eleven_multilingual_v2"
VOICE_SETTINGS = {
    "stability": 0.45,
    "similarity_boost": 0.82,
    "style": 0.15,
    "use_speaker_boost": True,
}
```

⚠️ **NEVER use voice `45br5910UE5negDJYWTM`** — that is Aditya's personal cloned voice.  
⚠️ **ElevenLabs API key is in `~/Downloads/WV/pipeline/.env`**, NOT the BlueLine .env.

**Audio segments:**
- Pitch deck: `audio2/pitch_s01.mp3` through `pitch_s12.mp3` (12 slides)
- Architecture doc: `audio2/arch_s01.mp3` through `arch_s18.mp3` + `arch_s03b.mp3` (19 segments)

**Playback mechanism:** All MP3s are base64-encoded and embedded as `data:audio/mpeg;base64,...` strings in the HTML. Files are fully self-contained — no external dependencies at presentation time.

---

## 12. UPGRADE1 — CONTEXT-AWARE MESSAGING MODULE

`upgrade1_context_aware_messaging.py` is imported by both Step 1 and Step 3:

```python
from upgrade1_context_aware_messaging import get_context_aware_sms
```

**What it does:**
1. Fetches last 4 days of Quo SMS conversation for the candidate's phone
2. Fetches last 4 days of Gmail threads mentioning the candidate's name
3. Sends both to Claude (`claude-haiku-4-5-20251001`) with a prompt to:
   - Write a contextually appropriate re-engagement message (< 160 chars, no emoji)
   - OR return `None` if the candidate is mid-process and should be skipped

**Failure behavior:**
- If Quo API call fails → falls back to hardcoded generic template
- If Gmail API call fails → proceeds with SMS-only context
- If Claude returns `None` → message is skipped entirely (contact left for next run)

**✅ CORRECTED 2026-07-01:** This section previously said the Quo URL/Bearer bug
was still open. It was not — `upgrade1_context_aware_messaging.py` already used
the correct `https://api.openphone.com/v1` base URL and the correct no-Bearer
auth header as of v1.1 (2026-06-29). The doc set was one revision behind the
code. **A different, previously-undocumented bug was found instead:** the
Gmail token path in this same file didn't match where the token actually gets
created (`master_gmail_setup.py` / `master_gmail_reviewer.py` both use
`~/Downloads/gmail_token.json`; upgrade1 was computing
`~/Downloads/BlueLine/gmail_token.json`). That meant `get_gmail_history()` has
been silently failing on every call since this module was built — Gmail
context never reached the SMS re-engagement decision, only Quo history did.
Fixed 2026-07-01 — see 08_TROUBLESHOOTING.md BUG-14.

---

## 13. NEW IN v2.0 — REAL-TIME LAYER + EMAIL CROSS-CHANNEL BRIDGE

### 13A. email_context_bridge.py — the email-side twin of upgrade1

Before v2.0, `master_gmail_reviewer.py` only ever fired on unread emails
WITH document attachments, and when it drafted a reply it only used that
sender's own Gmail history — it never touched Quo. So a candidate emailing
a plain question ("what are your rates?") got no automated response of any
kind, and even document-review replies didn't know if the same candidate
had an active SMS conversation.

`email_context_bridge.py` closes this gap with the same pattern already
proven in `upgrade1_context_aware_messaging.py`:

```
get_context_aware_email_reply(sender_name, sender_email, subject, inbound_body, gmail_thread_history):
  1. match_phone_by_sender_name() — best-effort name match against live Quo
     contacts (Quo has no email field, so this is a name match, not a direct
     lookup — see file docstring for match order and known limitation)
  2. If matched → get_quo_history(phone) [reused from upgrade1, not duplicated]
  3. Sends: inbound email + full Gmail thread history + Quo SMS history (if any)
     to claude-opus-4-5
  4. Claude returns exactly one of:
       DRAFT: <reply text>       → caller saves as Gmail Draft (never sent)
       SKIP: <reason>            → no action
       FLAG_HUMAN: <reason>      → appended to master_needs_human_review_email.txt
```

`FLAG_HUMAN` is deliberately the default for anything opt-out-like, legal,
pricing/contract, client-facility-originated, or ambiguous — see
`07_COMPLIANCE.md` for the full FLAG_HUMAN trigger list. This mirrors the
non-negotiable "never auto-send" rule; the only thing that changed is that
email inquiries now get triaged instead of silently sitting unread.

### 13B. master_gmail_reviewer.py v1.1 — widened scope

- `get_unread_messages_all()` replaces `get_unread_messages_with_attachments()`
  as the batch entry point — same filtering (system/non-candidate senders
  excluded), just no longer requires an attachment to qualify
- `process_sender()` is the shared per-sender handler used by both batch mode
  and the real-time listener — branches to the existing Claude Vision
  doc-review flow if attachments exist, or the new `email_context_bridge.py`
  flow if not
- `process_new_message_by_id()` is the entry point the real-time listener
  calls per newly-arrived message (via Gmail history delta, not a full
  unread re-scan)

### 13C. master_gmail_pubsub_listener.py — 24/7 email (new)

Uses Gmail's `watch()` API + a Google Cloud Pub/Sub **pull** subscription
(not push — no public webhook required, fits a local-Mac deployment).
Within seconds of new mail arriving, Gmail notifies Pub/Sub → this script
pulls the notification → fetches the history delta → calls
`process_new_message_by_id()` for each new message. Renews the Gmail
`watch()` automatically before its 7-day expiry. Full setup:
`03_SETUP_GUIDE.md` Step 11.

### 13D. master_sms_poll_service.py — near-real-time SMS (new)

Calls the existing, unmodified `step3_sms_reply_handler()` from
`master_daily_agent.py` every ~90 seconds, running independently 24/7 —
NOT part of the cron-triggered run at all. `master_daily_agent.py`'s own
`main()` no longer calls Step 3 by default (v2.6+); `--include-step3` exists
only for manual debugging and must never run while this poll service is
also running (duplicate-response race). Steps 1/2/DEDUP remain on the cron
(currently every 30 min, 9am–4:30pm EST, Mon–Fri — see crontab below).
[UPDATED 2026-07-02, Round 14 audit — this paragraph was stale: the actual
current values are a 72-hour stall window (`STALL_WINDOW_HOURS`, lowered
from 96h per Aditya's explicit rule) and no fixed daily cap on new leads —
replaced by a rolling 75-messages/trailing-24h safety cap
(`NEW_LEAD_ROLLING_CAP`) with a notification when it's hit, not a hard
30/day ceiling. See `master_daily_agent.py` and
`SAAS_PROJECT_HEALTHCARE_RECRUITMENT_MASTER_CONTEXT.md` for the current
rules; this doc previously described the pre-Round-11 model.]
