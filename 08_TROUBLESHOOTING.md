# DYLAN FOR HIRE — TROUBLESHOOTING GUIDE
**Version:** 2.0 | **Last Updated:** 2026-07-01
**Source:** Known bugs in v2.1/v2.2, all error patterns seen in production, 18 bugs fixed (BUG-14 through BUG-18 new — found during full doc+code audit, 2026-07-01).
**Correction in this version:** the "known ongoing bug" section below (Quo URL/Bearer) was
stale — it was already fixed as of 2026-06-29 and this doc hadn't caught up. See BUG-14 for
the real bug that was found in its place.

---

## QUICK DIAGNOSIS

**Agent didn't run at 9 AM:**
```bash
crontab -l              # is the cron entry still there?
cat ~/Downloads/BlueLine/cron_output.log   # what happened?
```

**SMS not sending:**
```bash
python3.11 -c "
from dotenv import load_dotenv; from pathlib import Path; import os
load_dotenv(Path.home() / 'Downloads' / '.env')
print(os.environ.get('QUO_PHONE_NUMBER_ID', 'MISSING'))
"
```

**No Gmail drafts appearing:**
```bash
ls ~/Downloads/gmail_token.json   # exists? (corrected 2026-07-01 — NOT the BlueLine/ subfolder, see BUG-14)
# If missing: python3.11 master_gmail_setup.py
```

**Something weird happened to contacts:**
```bash
python3.11 -c "
from master_daily_agent import merge_duplicate_contacts
merge_duplicate_contacts()
"
```

---

## KNOWN ISSUES — ALL 13 BUGS FIXED IN V2.1

These were identified and patched. Documented here so you know the history and can verify they haven't regressed.

### BUG-01 — .env path mismatch
**Symptom:** `KeyError: CLAUDE_API_KEY` even though .env exists in BlueLine/  
**Root cause:** Code calls `load_dotenv(Path.home() / "Downloads" / ".env")` but .env was at `~/Downloads/BlueLine/.env`  
**Fix (v2.1):** .env moved to `~/Downloads/.env`. The code path is correct — the file location was wrong.  
**Verify:** `ls ~/Downloads/.env && cat ~/Downloads/.env | head -3`

### BUG-02 — QUO_PHONE_NUMBER_ID missing from .env
**Symptom:** `KeyError: QUO_PHONE_NUMBER_ID` at startup  
**Root cause:** Key was missing from .env; value only existed in `.envls` (accidental shell artifact)  
**Fix (v2.1):** Added `QUO_PHONE_NUMBER_ID=PNWtLBsgMe` to .env  
**Verify:** `cat ~/Downloads/.env | grep QUO_PHONE_NUMBER_ID`

### BUG-03 — CSV encoding error on UTF-8 BOM files
**Symptom:** First candidate name had a `ï»¿` prefix (e.g. "ï»¿Jane Doe")  
**Root cause:** CSV saved with UTF-8 BOM, loaded with `utf-8` encoding instead of `utf-8-sig`  
**Fix (v2.1):** CSV loaded with `encoding='utf-8-sig'`  
**Verify:** First row name in CSV should not have BOM characters when printed

### BUG-04 — Phone normalisation dropping area codes
**Symptom:** Phone numbers stored as 10-digit strings failing E.164 format check  
**Root cause:** normalise_phone() wasn't prepending +1 for US numbers  
**Fix (v2.1):** normalise_phone() now always produces +1XXXXXXXXXX format  
**Verify:** Run `python3.11 -c "from master_daily_agent import normalise_phone; print(normalise_phone('7185551234'))"`

### BUG-05 — Duplicate contact creation despite dedup
**Symptom:** Same candidate had 2+ Quo contacts  
**Root cause:** Dedup only checked phone; first-name match wasn't run  
**Fix (v2.1):** 3-pass dedup (phone, full name, first name) now runs before every new contact creation  
**Verify:** `merge_duplicate_contacts()` should return 0 merges on a clean system

### BUG-06 — Opt-out file not checked before re-engagement
**Symptom:** Opted-out candidate received a re-engagement message  
**Root cause:** Step 1 checked BLOCKED_NUMBERS but not master_permanent_optouts.txt  
**Fix (v2.1):** Step 1 now reads optouts file and checks every phone before sending  
**Verify:** Add a test phone to optouts.txt, confirm Step 1 skips it

### BUG-07 — Interest reply triggered on already-handled message
**Symptom:** Candidate received duplicate document checklist SMS  
**Root cause:** master_handled_interest_replies.txt not checked before responding  
**Fix (v2.1):** Message ID check runs before every interest response  
**Verify:** `cat ~/Downloads/master_handled_interest_replies.txt` — should grow each time a YES is handled

### BUG-08 — Context-aware messaging skipping all contacts
**Symptom:** Step 1 sent no re-engagement messages even for clearly stalled contacts  
**Root cause:** upgrade1 was returning None for all contacts because Quo API calls were failing silently (wrong base URL)  
**Fix (v2.1):** Step 1 falls back to GENERIC_FOLLOWUP when upgrade1 returns None  
**Remaining bug:** upgrade1 still has wrong URL (`api.quo.com` should be `api.openphone.com`) and wrong auth header (adds Bearer prefix). Needs a separate fix in upgrade1_context_aware_messaging.py.

### BUG-09 — Daily catchup cap not applied correctly
**Symptom:** After 5 missed days, agent tried to send 150+ messages, hitting API rate limits  
**Root cause:** `days_missed * DAILY_CAP` was not capped at MAX_CATCHUP  
**Fix (v2.1):** `sends_today = min(DAILY_CAP * days_missed, MAX_CATCHUP)` — hard cap at 150

### BUG-10 — Borough detection failing for Staten Island candidates
**Symptom:** Staten Island candidates getting borough "NY" (default)  
**Root cause:** "Staten Island" wasn't in the keyword map (two-word name, split detection)  
**Fix (v2.1):** Borough detection now handles multi-word borough names

### BUG-11 — Gmail reviewer not aggregating attachments
**Symptom:** Checklist showed documents as missing even though candidate emailed them in a previous email  
**Root cause:** Reviewer only read the triggering email's attachments, not the sender's full history  
**Fix (v2.1):** Gmail reviewer now fetches ALL historical emails from sender and aggregates all attachments

### BUG-12 — Onboarding PDF not found (path case sensitivity)
**Symptom:** Gmail draft created but PDF not attached; error: "File not found"  
**Root cause:** PDF filename had `aditya` (lowercase) but directory was `Aditya` (capital A)  
**Fix (v2.1):** PDF paths in code updated to use `~/Desktop/aditya/` (lowercase)  
**Note:** Verify your actual directory name matches — macOS is case-insensitive for most paths but this can still cause issues in some contexts

### BUG-13 — Cron not running due to missing Full Disk Access
**Symptom:** cron_output.log empty; no daily runs happening  
**Root cause:** macOS requiring Full Disk Access for cron to read files in ~/Downloads/  
**Fix:** System Settings → Privacy & Security → Full Disk Access → enable `/usr/sbin/cron`

---

## RESOLVED — UPGRADE1 API URL (previously listed here as "not yet fixed" — corrected 2026-07-01)

**File:** `upgrade1_context_aware_messaging.py`
**This doc previously said** `QUO_BASE_URL` still pointed at the old
`api.quo.com` domain with a `Bearer` prefix. **That was wrong.** A direct
read of the actual file (2026-07-01) shows `QUO_BASE_URL = "https://api.openphone.com/v1"`
and `"Authorization": QUO_API_KEY` (no Bearer) — already correct, dated
v1.1 / 2026-06-29. This doc was simply a revision behind the code.
**Lesson:** re-verify bug status against the actual `.py` file before
repeating a "known bug" claim — don't propagate a stale troubleshooting
entry forward.

### BUG-14 — Gmail token path mismatch in upgrade1 (found + fixed 2026-07-01)

**Symptom:** No symptom visible in logs — this failed silently. Context-aware
SMS re-engagement worked (Quo history was reaching Claude), but Gmail history
never was, and nothing errored to indicate it.
**Root cause:** `master_gmail_setup.py` and `master_gmail_reviewer.py` both
read/write the OAuth token at `~/Downloads/gmail_token.json`. But
`upgrade1_context_aware_messaging.py` computed
`GMAIL_TOKEN_PATH = os.path.join(_BASE_DIR, "gmail_token.json")` — resolving
to `~/Downloads/BlueLine/gmail_token.json` (the script's own folder), a file
that never existed. `get_gmail_history()` checked `os.path.exists(GMAIL_TOKEN_PATH)`,
found nothing, and returned `""` every time — no exception, no log warning
beyond a low-visibility `logger.warning` line.
**Fix (2026-07-01):** `GMAIL_TOKEN_PATH` now hardcoded to
`os.path.expanduser("~/Downloads/gmail_token.json")`, matching the other two files.
**Verify:** `ls ~/Downloads/gmail_token.json` should exist and be non-empty.
Also worth re-running a context-aware re-engagement test candidate with a
known recent email thread and confirming the drafted SMS now references it.

### BUG-15 — `master_sms_poll_service.py` called a function that doesn't exist (found + fixed 2026-07-01)

**Symptom:** Would not have shown up until first launch — `AttributeError:
module 'master_daily_agent' has no attribute 'step3_handle_sms_replies'`,
immediately, every poll cycle. This is the entire 24/7 SMS reply service;
until fixed, it could not run at all.
**Root cause:** The actual function in `master_daily_agent.py` is named
`step3_sms_reply_handler()`. Every doc (`00_INDEX.md`, `02_SYSTEM_ARCHITECTURE.md`,
`05_PIPELINE_REFERENCE.md`) and the new poll service itself referred to it as
`step3_handle_sms_replies()` — a name that was never defined anywhere in the
codebase. Likely renamed at some point in `master_daily_agent.py` without the
rename propagating to the new v2.0 files/docs that reference it.
**Fix (2026-07-01):** Corrected the call in `master_sms_poll_service.py` and
all doc references to the real name, `step3_sms_reply_handler()`.
**Verify:** `python3.11 -c "import master_daily_agent as m; print(m.step3_sms_reply_handler)"`
should print the function object, not raise `AttributeError`.

### BUG-16 — DYLAN_INTRO had no opt-out language despite compliance doc claiming it did (found + fixed 2026-07-01)

**Symptom:** No error — this was a silent compliance gap, not a crash.
**Root cause:** `07_COMPLIANCE.md` states as a non-negotiable rule that every
first-contact message includes an opt-out instruction, and that "the
DYLAN_INTRO template already includes all three [required elements]." The
live `DYLAN_INTRO` constant in `master_daily_agent.py` did not contain any
STOP/opt-out language.
**Fix (2026-07-01):** Added `"Reply STOP to opt out."` to the end of
`DYLAN_INTRO`.
**Verify:** `python3.11 -c "from master_daily_agent import DYLAN_INTRO; print(DYLAN_INTRO)"`
should show the STOP line.

### BUG-17 — OPTOUT_KEYWORDS/INTEREST_KEYWORDS narrower in code than documented (found + fixed 2026-07-01)

**Symptom:** No error — candidates texting phrases like "please stop," "take
me off," or "wrong number" were routed to `master_needs_human_review.txt`
instead of being auto-opted-out, even though `07_COMPLIANCE.md` and
`05_PIPELINE_REFERENCE.md` both documented these phrases as auto-handled.
**Root cause:** `OPTOUT_KEYWORDS`/`INTEREST_KEYWORDS` in `master_daily_agent.py`
were a narrower set than what the compliance/pipeline docs described as
already implemented.
**Fix (2026-07-01):** Widened both keyword sets in code to match what the
docs already promised (see docstring at top of `master_daily_agent.py` v2.2).
**Verify:** `python3.11 -c "from master_daily_agent import OPTOUT_KEYWORDS; print('please stop' in ' '.join(OPTOUT_KEYWORDS) or any('please stop' in k for k in OPTOUT_KEYWORDS))"`

### BUG-18 — DOCUMENT_CHECKLIST_MSG contained emoji, violating its own ground rule (found + fixed 2026-07-01)

**Symptom:** No error — a tone/consistency issue, not a functional one.
**Root cause:** `06_COMMUNICATIONS.md` Ground Rule #3 states "No emojis in
SMS." The live `DOCUMENT_CHECKLIST_MSG` constant contained three emoji
(📋/📍/📧).
**Fix (2026-07-01):** Removed all emoji from the constant.

---

## ERROR REFERENCE

### Startup Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `KeyError: 'CLAUDE_API_KEY'` | .env not found at ~/Downloads/.env | Move .env to ~/Downloads/ (not BlueLine subfolder) |
| `KeyError: 'QUO_API_KEY'` | Same as above | Same fix |
| `KeyError: 'QUO_PHONE_NUMBER_ID'` | Key missing from .env | Add: `QUO_PHONE_NUMBER_ID=PNWtLBsgMe` to ~/Downloads/.env |
| `ModuleNotFoundError: anthropic` | Deps not installed | `pip3.11 install -r master_requirements.txt --break-system-packages` |
| `ModuleNotFoundError: upgrade1_context_aware_messaging` | File missing | Confirm file exists in ~/Downloads/BlueLine/ |

### Quo API Errors

| Error | Cause | Fix |
|-------|-------|-----|
| HTTP 401 Unauthorized | Wrong QUO_API_KEY | Verify key at openphone.com → Settings → API |
| HTTP 400 Bad Request (send) | Wrong QUO_PHONE_NUMBER_ID | Verify number ID in OpenPhone dashboard |
| HTTP 400 "Opted Out" | Carrier-level opt-out | Handled automatically — added to optouts file |
| HTTP 429 Rate Limited | Too many API calls | Wait 60s; agent will retry unprocessed leads next run |
| HTTP 404 on contact | Contact was deleted externally | DEDUP will clean up; skip this contact |

### Gmail API Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `google.auth.exceptions.RefreshError` | Token expired | Run `python3.11 master_gmail_setup.py` |
| `File not found: gmail_token.json` | OAuth never set up | Run `python3.11 master_gmail_setup.py` |
| `File not found: gmail_credentials.json` | Client creds missing | Re-download from Google Cloud Console |
| `No drafts created` | No unread emails with attachments | Normal — no new submissions from candidates |

### Claude API Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `anthropic.AuthenticationError` | Wrong CLAUDE_API_KEY | Verify at console.anthropic.com → API Keys |
| `anthropic.RateLimitError` | Too many requests | Wait; agent will retry on next run |
| `anthropic.APITimeoutError` | Response took too long | Step 1 falls back to generic template; Step 0 re-run manually |

### State File Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Same candidate receives multiple intros | processed_contacts.txt missing a phone | Add phone manually to the file |
| Opted-out candidate re-contacted | optouts.txt was cleared or phone missing | Add phone; verify file; investigate how it got cleared |
| Duplicate Quo contacts | Dedup missed edge case | Run `merge_duplicate_contacts()` manually |
| Old emails being re-reviewed | processed_email_ids.txt corrupted | Backup, clear, accept re-drafting as tolerable |

---

## DIAGNOSTIC COMMANDS

```bash
# Check all 3 env keys load correctly
python3.11 -c "
from dotenv import load_dotenv; from pathlib import Path; import os
load_dotenv(Path.home() / 'Downloads' / '.env')
for k in ['CLAUDE_API_KEY','QUO_API_KEY','QUO_PHONE_NUMBER_ID']:
    v = os.environ.get(k,'MISSING')
    print(f'{k}: {v[:10] if v != \"MISSING\" else \"MISSING\"}...')
"

# Test Quo API connectivity
python3.11 -c "
from dotenv import load_dotenv; from pathlib import Path; import os, requests
load_dotenv(Path.home() / 'Downloads' / '.env')
r = requests.get('https://api.openphone.com/v1/phone-numbers',
                  headers={'Authorization': os.environ['QUO_API_KEY']})
print('Status:', r.status_code)
print('Response:', r.text[:200])
"

# Test Claude API connectivity
python3.11 -c "
from dotenv import load_dotenv; from pathlib import Path; import os, anthropic
load_dotenv(Path.home() / 'Downloads' / '.env')
c = anthropic.Anthropic(api_key=os.environ['CLAUDE_API_KEY'])
r = c.messages.create(model='claude-haiku-4-5-20251001', max_tokens=10,
                       messages=[{'role':'user','content':'ping'}])
print('Claude OK:', r.content[0].text)
"

# Check state file sizes
wc -l ~/Downloads/master_processed_contacts.txt
wc -l ~/Downloads/master_permanent_optouts.txt
wc -l ~/Downloads/master_needs_human_review.txt

# Check cron is active
crontab -l

# Check last successful run time
cat ~/Downloads/master_last_run_timestamp.txt

# Find all run logs from today
ls ~/Downloads/master_run_log_$(date +%Y%m%d)*.csv

# Check if onboarding PDFs are in place
ls -la ~/Desktop/aditya/*.pdf
```

---

## NEW (v2.0) — 24/7 SERVICE TROUBLESHOOTING

### Gmail listener won't start: "GCP_PROJECT_ID not set"
Add `GCP_PROJECT_ID`, `GMAIL_PUBSUB_TOPIC`, `GMAIL_PUBSUB_SUBSCRIPTION` to
`~/Downloads/.env` — see `03_SETUP_GUIDE.md` Step 11D.

### Gmail listener: `watch()` fails with a permissions/403 error
The Pub/Sub topic is missing the Gmail push service account grant. Redo
`03_SETUP_GUIDE.md` Step 11B — the principal must be exactly
`gmail-api-push@system.gserviceaccount.com` with role **Pub/Sub Publisher**.

### Gmail listener runs but nothing happens when you send a test email
1. Check `launchctl list | grep blueline` — is it actually running?
2. Check `~/Downloads/gmail_listener_error.log` for exceptions
3. Confirm the subscription exists and matches `GMAIL_PUBSUB_SUBSCRIPTION`:
   `gcloud pubsub subscriptions list`
4. Check `~/Downloads/master_last_gmail_history_id.txt` — if it's very old,
   Gmail may have expired the history window (only ~7 days retained); the
   listener will detect the 404 and resync forward automatically (no
   backfill of missed messages in that case — process any backlog manually
   via `python3.11 master_gmail_reviewer.py` once)

### SMS poll service: replies still take until 9am
Check `launchctl list | grep blueline` — if `com.blueline.smspoll` isn't
listed, the plist never loaded. Re-run:
```bash
launchctl load ~/Library/LaunchAgents/com.blueline.smspoll.plist
```

### Either service crashes repeatedly (visible in launchd exit codes)
Both scripts have internal exponential backoff and will keep retrying
rather than exit — if launchd shows a nonzero exit code repeatedly, the
process is crashing outside the retry loop (e.g. import error, missing
dependency). Run manually in a terminal first (`03_SETUP_GUIDE.md` Step
11F) to see the real traceback before re-loading as a service.

### Claude API costs higher than expected after enabling 24/7 mode
Expected — continuous polling means more Claude calls than one batch a
day. Check `console.anthropic.com` → Usage after the first full week and
update the cost line in the master context doc (§6A) with the real number
before quoting a customer.

---

## WHEN TO ESCALATE

Things you cannot fix by editing .env or running a command:

1. **OpenPhone account suspended** — contact OpenPhone support; agent cannot run until restored
2. **Google Cloud project disabled** — rebuild Gmail credentials from Google Cloud Console
3. **Anthropic API key permanently revoked** — create a new key at console.anthropic.com
4. **TCPA complaint filed** — legal matter; document everything; do not delete any logs or state files

For 1-3, the fix is always: get new credentials → update .env → test run.
