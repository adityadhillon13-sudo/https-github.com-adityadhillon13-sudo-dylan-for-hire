# DYLAN FOR HIRE — SETUP GUIDE
**Version:** 2.0 | **Last Updated:** 2026-07-01
**Purpose:** Zero-to-live setup instructions. Follow in order. Every step is required.
**What's new in v2.0:** Steps 1–10 below are the original once-a-day cron setup —
still accurate, still required as your foundation. Step 11 (new) adds the 24/7
real-time layer (Gmail push notifications + continuous SMS reply checking) that
Dylan for Hire needs to legitimately claim "always-on." Do Steps 1–10 first;
Step 11 is additive, not a replacement — the daily cron still runs Steps 1/2/DEDUP.

---

## OVERVIEW

Total setup time: 45–90 minutes (most of it is waiting for installs and OAuth flows)

**Checklist:**
- [ ] 1. Prerequisites confirmed
- [ ] 2. Repository / files in place
- [ ] 3. Python dependencies installed
- [ ] 4. Environment variables configured
- [ ] 5. Gmail OAuth setup
- [ ] 6. Application PDFs in place
- [ ] 7. Candidate CSV in place
- [ ] 8. Test run (manual)
- [ ] 9. Cron automation configured

---

## STEP 1 — PREREQUISITES

Before starting, confirm you have:

| Requirement | How to verify |
|-------------|--------------|
| macOS (any recent version) | `uname -s` → should print `Darwin` |
| Python 3.11 | `python3.11 --version` → should print `Python 3.11.x` |
| Anthropic API key | Available at console.anthropic.com |
| OpenPhone (Quo) account with SMS number | Dashboard at openphone.com |
| OpenPhone API key | Settings → Integrations → API |
| OpenPhone Phone Number ID | Settings → Phone Numbers → click your number → ID in URL |
| Gmail account for info@bluelinestaffing.com | Credentials from Google Cloud Console |
| ElevenLabs API key (for pitch/arch doc audio only) | platform.elevenlabs.io (stored in WV pipeline .env, not here) |

**Install Python 3.11 if not present:**
```bash
# Using Homebrew (recommended)
brew install python@3.11

# Verify
python3.11 --version
```

---

## STEP 2 — FILES IN PLACE

All source files must be in `~/Downloads/BlueLine/`:

```bash
# Create directory if it doesn't exist
mkdir -p ~/Downloads/BlueLine

# Copy all source files there. The core files are:
# master_daily_agent.py
# master_gmail_reviewer.py
# master_gmail_setup.py
# upgrade1_context_aware_messaging.py
# master_requirements.txt

ls ~/Downloads/BlueLine/
# Should list all the above files
```

---

## STEP 3 — PYTHON DEPENDENCIES

```bash
cd ~/Downloads/BlueLine
pip3.11 install -r master_requirements.txt --break-system-packages
```

**Expected packages (from master_requirements.txt):**
- `anthropic` — Claude API client
- `requests` — Quo/OpenPhone API calls
- `python-dotenv` — loads .env files
- `google-auth-oauthlib` — Gmail OAuth2
- `google-api-python-client` — Gmail read/compose

**If you see permission errors:**
```bash
pip3.11 install -r master_requirements.txt --user
```

**Verify install:**
```bash
python3.11 -c "import anthropic, requests, dotenv, google.auth; print('All OK')"
```

---

## STEP 4 — ENVIRONMENT VARIABLES

Create the `.env` file at `~/Downloads/.env` (NOT inside BlueLine/ — the agent looks one level up):

```bash
# Create or edit the file
nano ~/Downloads/.env
```

Paste exactly:
```env
CLAUDE_API_KEY=sk-ant-YOUR_KEY_HERE
QUO_API_KEY=YOUR_OPENPHONE_API_KEY_HERE
QUO_PHONE_NUMBER_ID=PNWtLBsgMe
```

> **Replace the placeholder values with your real credentials.**  
> `QUO_PHONE_NUMBER_ID` is the ID of your OpenPhone number, not the phone number itself.  
> For BlueLine, this value is `PNWtLBsgMe` (the +15512506678 number).

**Verify the keys load correctly:**
```bash
python3.11 -c "
from dotenv import load_dotenv
from pathlib import Path
import os
load_dotenv(Path.home() / 'Downloads' / '.env')
print('CLAUDE_API_KEY:', os.environ.get('CLAUDE_API_KEY','MISSING')[:20])
print('QUO_API_KEY:', os.environ.get('QUO_API_KEY','MISSING')[:15])
print('QUO_PHONE_NUMBER_ID:', os.environ.get('QUO_PHONE_NUMBER_ID','MISSING'))
"
```

Expected output:
```
CLAUDE_API_KEY: sk-ant-...
QUO_API_KEY: ...
QUO_PHONE_NUMBER_ID: PNWtLBsgMe
```

---

## STEP 5 — GMAIL OAUTH SETUP

This is a one-time setup to authorise the Gmail agent to access `info@bluelinestaffing.com`.

**Prerequisites:**
- You must have a Google Cloud project with the Gmail API enabled
- `gmail_credentials.json` must be in `~/Downloads/` (NOT `~/Downloads/BlueLine/` —
  corrected in v2.0: the actual code in master_gmail_setup.py and
  master_gmail_reviewer.py both read/write one level up from the BlueLine folder.
  The earlier version of this doc said BlueLine/ — that was wrong and, combined
  with a matching bug in upgrade1_context_aware_messaging.py, meant Gmail history
  was silently never reaching the SMS re-engagement decision. Both are now fixed —
  see 08_TROUBLESHOOTING.md BUG-14.)

**Run the setup:**
```bash
cd ~/Downloads/BlueLine
python3.11 master_gmail_setup.py
```

This will:
1. Open a browser window with a Google login prompt
2. Log in as the info@bluelinestaffing.com account
3. Approve the requested permissions (read email + create drafts)
4. A file `gmail_token.json` will appear in `~/Downloads/` (top level, not BlueLine/)

**Verify setup:**
```bash
ls ~/Downloads/gmail_token.json
# File should exist and be non-empty
```

**Token refresh:** The token auto-refreshes when it expires. If you see auth errors weeks later, re-run `master_gmail_setup.py` and re-authorise.

---

## STEP 6 — APPLICATION PDFs

The Gmail document reviewer attaches the correct onboarding PDF to each checklist reply. All three PDFs must exist at `~/Desktop/aditya/` with EXACT filenames:

```
~/Desktop/aditya/Editable Onboarding Blueline RN .pdf
~/Desktop/aditya/Editable Onboarding Blueline LPN .pdf
~/Desktop/aditya/Editable Onboarding Blueline CNA .pdf
```

Note the trailing space before `.pdf` in each filename — this is intentional and must match exactly.

**Verify:**
```bash
ls ~/Desktop/aditya/ | grep "Onboarding"
# Should list all 3 files
```

---

## STEP 7 — CANDIDATE CSV

The CSV lead list must be at:
```
~/Downloads/BlueLine/CONFIDENTIAL_candidates.csv
```

**Required columns:**
- `name` — candidate's full name (first last)
- `phone` — candidate's phone number

**Additional columns** (optional but improve accuracy):
- Any field containing license type text (e.g. "Registered Nurse", "LPN", "CNA")
- Any field containing borough or zip code

**Format:**
- UTF-8 or UTF-8 BOM encoding (both are handled)
- First row is headers
- One candidate per row

**Verify:**
```bash
head -5 ~/Downloads/BlueLine/CONFIDENTIAL_candidates.csv
```

---

## STEP 8 — FIRST TEST RUN (MANUAL)

Run the agent manually for the first time to verify everything works:

```bash
cd ~/Downloads/BlueLine
python3.11 master_daily_agent.py
```

**Expected output pattern:**
```
═══ BlueLine Master Agent v2.1 ═══
Loaded env from: /Users/Aditya/Downloads/.env
CLAUDE_API_KEY: ✓
QUO_API_KEY: ✓
QUO_PHONE_NUMBER_ID: ✓

═══ STEP 3: SMS Reply Handler ═══
  Scanning conversations...
  Conversations with recent activity: N
  [details of any inbound replies handled]

═══ STEP 1: Re-engage Stalled Contacts ═══
  [details of any re-engagement messages sent]

═══ DEDUP: Merging duplicate contacts ═══
  Total contacts fetched: N
  [details of any merges]

═══ STEP 2: New Lead Intro SMS ═══
  Sending to N new leads...
  [details of each intro SMS]

Run log saved: ~/Downloads/master_run_log_YYYYMMDD_HHMMSS.csv
```

**Common first-run errors:**

| Error | Cause | Fix |
|-------|-------|-----|
| `KeyError: CLAUDE_API_KEY` | .env not found at correct path | Verify ~/.env location vs ~/Downloads/.env |
| `ModuleNotFoundError: anthropic` | Dependencies not installed | Run pip3.11 install command in Step 3 |
| `401 Unauthorized` from Quo API | Wrong QUO_API_KEY | Verify key at openphone.com → Settings → API |
| `400 Bad Request` from Quo send | Wrong QUO_PHONE_NUMBER_ID | Verify number ID in OpenPhone dashboard |
| CSV read error | Wrong filename or encoding | Check exact filename and UTF-8 encoding |

---

## STEP 9 — CRON AUTOMATION

**[CHANGED 2026-07-02]** Schedule updated to every 30 minutes, 9:00 AM–5:00 PM EST, Monday–Friday
only.

**[CORRECTION 2026-07-02]** This doc previously said the prior schedule was "once daily at
9:00 AM EST" — that was the intended setup, not what was actually deployed. Verified directly
against `crontab -l` on Aditya's Mac: the real prior line was `9 * * * * cd ... && set -a &&
source .env && set +a && python3.11 master_daily_agent.py ...` — every hour at minute 9, every
day including weekends. Also found and fixed: the `TZ` line had a stray leading character
(`iTZ=America/New_York`), so `TZ` was never actually set and the schedule ran in the Mac's system
timezone, not confirmed EST. Both are fixed as of this update. The deployed line also sources
`.env` (`set -a && source .env && set +a`) before running — preserved below, not previously
documented here.

This is safe to run every 30 min: `step3_sms_reply_handler()`
and `step1_reengage_stalled()` both rescan a fixed 7-day conversation window on every run (not an
incremental "since last run" window), and every send path is gated by persistent dedup state
(`master_processed_contacts.txt`, `master_handled_interest_replies.txt`, `master_checklist_sent.txt`,
etc.) — so nothing gets double-sent by running more frequently. `step2_new_leads()`'s catch-up math
(`days_missed` in `STATE_TIMESTAMP`) is day-granularity, so running multiple times a day doesn't
inflate the new-lead send quota either.

This also answers the "does the first morning run cover overnight activity" question directly:
since step1/step3 always look back 7 full days regardless of when the agent last ran, the 16-hour
gap between the last run at 5:00 PM and the first run at 9:00 AM the next day is automatically
inside that window — no separate overnight catch-up logic is needed.

Open a terminal and run:

```bash
crontab -e
```

In the editor, add these five lines (replace any existing single `0 9 * * *` line from an older
setup — do not keep both, or the agent will run twice at 9:00 AM). The safest way to set all five
at once, avoiding `vi`/`crontab -e` entirely, is the heredoc replacement pattern below — run it
directly in Terminal (not inside an editor):
```bash
cat <<'EOF' | crontab -
TZ=America/New_York
0,30 9-16 * * 1-5 cd /Users/Aditya/Downloads/BlueLine && set -a && source .env && set +a && /usr/local/bin/python3.11 master_daily_agent.py >> /Users/Aditya/Downloads/BlueLine/cron_output.log 2>&1
0 17 * * 1-5 cd /Users/Aditya/Downloads/BlueLine && set -a && source .env && set +a && /usr/local/bin/python3.11 master_daily_agent.py >> /Users/Aditya/Downloads/BlueLine/cron_output.log 2>&1
5 9-16 * * 1-5 cd /Users/Aditya/Downloads/BlueLine && set -a && source .env && set +a && /usr/local/bin/python3.11 master_gmail_reviewer.py >> /Users/Aditya/Downloads/BlueLine/cron_output.log 2>&1
5 17 * * 1-5 cd /Users/Aditya/Downloads/BlueLine && set -a && source .env && set +a && /usr/local/bin/python3.11 master_gmail_reviewer.py >> /Users/Aditya/Downloads/BlueLine/cron_output.log 2>&1
EOF
```
(Verified live via `crontab -l` on Aditya's Mac — daily-agent lines confirmed 2026-07-02,
gmail-reviewer lines added and confirmed via a second live `crontab -l` paste the same day,
~14:53 EDT. This is exactly what's currently deployed.)

Read as: `master_daily_agent.py` fires on the hour and half-hour from 9:00 AM through 4:30 PM plus
once more at 5:00 PM, Monday–Friday (`1-5` = Mon-Fri, cron's day-of-week field, where 0/7=Sunday) —
17 runs/day. `master_gmail_reviewer.py` runs the same pattern offset 5 minutes later (9:05 AM
through 4:35 PM plus 5:05 PM) so the two scripts don't hit the Quo API in the same window — also
17 runs/day. Nothing runs overnight or on weekends for either. Note: the reviewer only scans
*unread* Gmail — already-read candidate threads with pending docs won't be picked up by cron; run
it manually on demand to clear backlog.

Save and exit if using `crontab -e` (Ctrl+X in nano, `:wq` in vi) — not needed with the heredoc
command above, which applies immediately.

**Verify the crontab was saved:**
```bash
crontab -l
# Should show the TZ line + all four schedule lines above
```

**macOS Full Disk Access (required for cron to work):**
1. Open System Settings → Privacy & Security → Full Disk Access
2. Click + and navigate to `/usr/sbin/cron`
3. Enable it

**Verify cron is running (check partway through the first business day):**
```bash
cat ~/Downloads/BlueLine/cron_output.log
# Should show multiple agent runs, roughly 30 minutes apart, starting at 9:00 AM EST
```

---

## STEP 10 — (OPTIONAL) PITCH DECK AND ARCHITECTURE DOC

**⚠️ Known mismatch (found 2026-07-01, verified directly in code) — read
before running this step:** `build_pitch_deck.py` and `build_arch_doc_v2.py`
write to `blueline_pitch_deck.html` / `blueline_architecture_doc.html` in
`~/Downloads/BlueLine/`. The actual, currently-presented, audio-embedded
assets are named `dylan_for_hire_pitch_deck.html` /
`dylan_for_hire_architecture.html` and live in this project's `pitch/`
folder. Running the commands below as written will NOT update those files —
it will create new, differently-named, old-branding (v2.1-era) HTML files
somewhere else. Do not run this step expecting it to refresh the live deck
until the `OUT` path in both scripts is repointed to the real filenames (or
the scripts are retired in favor of hand-editing the current HTML). See
`09_GO_LIVE_READINESS.md` 🔴 KNOWN GAPS #7.

To rebuild the HTML presentations with fresh audio:

```bash
cd ~/Downloads/BlueLine

# 1. Build HTML files (no audio yet)
python3.11 build_pitch_deck.py
python3.11 build_arch_doc_v2.py

# 2. Generate ElevenLabs audio (requires WV pipeline .env with ELEVENLABS_API_KEY)
# Note: ElevenLabs key is in ~/Downloads/WV/pipeline/.env, NOT BlueLine .env
# gen_all_audio.py has the key hardcoded — verify it's current before running
python3.11 gen_all_audio.py

# 3. Embed audio into HTML files
python3.11 embed_audio.py

# Final files:
# blueline_pitch_deck.html (~11MB with embedded audio)
# blueline_architecture_doc.html (~6MB with embedded audio)
```

**To present:**
```bash
open ~/Downloads/BlueLine/blueline_pitch_deck.html
open ~/Downloads/BlueLine/blueline_architecture_doc.html
```

---

## STEP 11 — (NEW, v2.0) REAL-TIME 24/7 LAYER

Everything above gives you one check per day at 9:00 AM. This step adds
continuous checking — new emails handled within seconds, new SMS replies
handled within ~90 seconds, all day, every day — using two new background
services: `master_gmail_pubsub_listener.py` and `master_sms_poll_service.py`.

This is the step that makes "24/7 running agent" an accurate claim rather
than marketing language. Budget ~25 minutes for the Google Cloud part
(one-time) plus ~10 minutes to set up the two background services.

### 11A — Install the new dependency

```bash
cd ~/Downloads/BlueLine
pip3.11 install google-cloud-pubsub --break-system-packages
```

### 11B — Create a Google Cloud Pub/Sub topic (one-time, ~10 min)

You need the SAME Google Cloud project you used for Gmail API in Step 5.

1. Go to https://console.cloud.google.com/cloudpubsub/topic/list (make sure
   the project selector at the top shows your Dylan/BlueLine project)
2. Click **CREATE TOPIC**
3. Topic ID: type exactly `gmail-dylan-notify`
4. Leave all other settings default. Click **CREATE**
5. You'll land on the topic's page. Click the **PERMISSIONS** tab
6. Click **ADD PRINCIPAL**
7. New principals: paste exactly `gmail-api-push@system.gserviceaccount.com`
8. Role: search for and select **Pub/Sub Publisher**
9. Click **SAVE**

   *(Why: this is Google's own Gmail service account. Granting it Publisher
   rights on your topic is what lets Gmail notify Pub/Sub when new mail
   arrives. Without this exact step, Gmail's `watch()` call in Step 11D
   will fail with a permissions error.)*

### 11C — Create a Pub/Sub pull subscription (one-time, ~3 min)

1. Still on the topic page, click **CREATE SUBSCRIPTION**
2. Subscription ID: type exactly `gmail-dylan-notify-sub`
3. Delivery type: leave as **Pull** (do NOT choose Push — Push requires a
   public HTTPS server, which you don't have; Pull is what
   `master_gmail_pubsub_listener.py` uses)
4. Leave other settings default. Click **CREATE**

### 11D — Add the two new environment variables

```bash
nano ~/Downloads/.env
```

Add these two lines (find your Project ID at the top of any Google Cloud
Console page, next to the project name dropdown):

```env
GCP_PROJECT_ID=your-project-id-here
GMAIL_PUBSUB_TOPIC=gmail-dylan-notify
GMAIL_PUBSUB_SUBSCRIPTION=gmail-dylan-notify-sub
```

### 11E — Authenticate this Mac to Google Cloud (one-time)

The Pub/Sub pull client needs its own credentials — separate from the
Gmail OAuth token you already set up.

```bash
# Install the Google Cloud CLI if you don't have it
brew install --cask google-cloud-sdk

# Log in — opens a browser
gcloud auth application-default login

# Set the active project to match GCP_PROJECT_ID above
gcloud config set project your-project-id-here
```

### 11F — Test both services manually BEFORE making them permanent

```bash
cd ~/Downloads/BlueLine

# Terminal window 1 — Gmail real-time listener
python3.11 master_gmail_pubsub_listener.py
# Expected: "Gmail watch() active. Expires: ..." then it goes quiet and waits.
# Send a test email to info@bluelinestaffing.com from another address and
# confirm you see it picked up within ~20 seconds and a log line printed.

# Terminal window 2 — SMS reply service
python3.11 master_sms_poll_service.py
# Expected: "SMS REPLY SERVICE: starting — checking Quo every 90s"
# Text the BlueLine number YES from a test phone and confirm a reply
# arrives within ~90 seconds instead of waiting for tomorrow's 9am run.
```

If either fails, do not proceed to 11G — see 08_TROUBLESHOOTING.md first.
**Do not skip this manual test.** Turning a broken script into a
permanent background service just means it fails silently, forever,
instead of failing loudly, once.

### 11G — Make both services permanent with launchd

Cron is the wrong tool here — cron runs something once and exits; these
two scripts need to stay running. macOS's `launchd` is the equivalent of
"keep this alive, restart it if it crashes, start it on login."

Create the first service file:
```bash
nano ~/Library/LaunchAgents/com.blueline.gmaillistener.plist
```
Paste:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.blueline.gmaillistener</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3.11</string>
        <string>/Users/aditya/Downloads/BlueLine/master_gmail_pubsub_listener.py</string>
    </array>
    <key>WorkingDirectory</key><string>/Users/aditya/Downloads/BlueLine</string>
    <key>RunAtLoad</key><true/>
    <key>KeepAlive</key><true/>
    <key>StandardOutPath</key><string>/Users/aditya/Downloads/gmail_listener.log</string>
    <key>StandardErrorPath</key><string>/Users/aditya/Downloads/gmail_listener_error.log</string>
</dict>
</plist>
```

Create the second:
```bash
nano ~/Library/LaunchAgents/com.blueline.smspoll.plist
```
Paste the same structure, changing only the label, script filename, and log names:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.blueline.smspoll</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3.11</string>
        <string>/Users/aditya/Downloads/BlueLine/master_sms_poll_service.py</string>
    </array>
    <key>WorkingDirectory</key><string>/Users/aditya/Downloads/BlueLine</string>
    <key>RunAtLoad</key><true/>
    <key>KeepAlive</key><true/>
    <key>StandardOutPath</key><string>/Users/aditya/Downloads/sms_poll.log</string>
    <key>StandardErrorPath</key><string>/Users/aditya/Downloads/sms_poll_error.log</string>
</dict>
</plist>
```

Load both (starts them immediately, and on every future login/reboot):
```bash
launchctl load ~/Library/LaunchAgents/com.blueline.gmaillistener.plist
launchctl load ~/Library/LaunchAgents/com.blueline.smspoll.plist
```

**Verify both are running:**
```bash
launchctl list | grep blueline
# Should show both labels with a PID and exit code 0

tail -f ~/Downloads/gmail_listener.log
tail -f ~/Downloads/sms_poll.log
```

**To stop a service** (e.g. for maintenance):
```bash
launchctl unload ~/Library/LaunchAgents/com.blueline.gmaillistener.plist
```
**To restart after editing code:**
```bash
launchctl unload ~/Library/LaunchAgents/com.blueline.gmaillistener.plist
launchctl load ~/Library/LaunchAgents/com.blueline.gmaillistener.plist
```

### 11H — What still runs on the old daily cron (unchanged)

Steps 1 (re-engage stalled), 2 (new leads), and DEDUP stay on the 9:00 AM
cron from Step 9 above. Nothing about that changes. Only Step 3 (SMS
replies) and Gmail document/inquiry review moved to continuous services.

---

## SETUP COMPLETE CHECKLIST

| Item | Status |
|------|--------|
| Python 3.11 installed | ☐ |
| All source files in ~/Downloads/BlueLine/ | ☐ |
| pip dependencies installed | ☐ |
| ~/Downloads/.env with 3 keys | ☐ |
| gmail_token.json generated | ☐ |
| 3 onboarding PDFs in ~/Desktop/aditya/ | ☐ |
| CONFIDENTIAL_candidates.csv in place | ☐ |
| Manual test run succeeded | ☐ |
| Crontab configured | ☐ |
| macOS Full Disk Access granted to cron | ☐ |
| **(v2.0) Pub/Sub topic + subscription created** | ☐ |
| **(v2.0) gmail-api-push@system.gserviceaccount.com granted Publisher** | ☐ |
| **(v2.0) GCP_PROJECT_ID + topic/sub vars in .env** | ☐ |
| **(v2.0) gcloud auth application-default login done** | ☐ |
| **(v2.0) Both services manually tested (11F) before going permanent** | ☐ |
| **(v2.0) Both launchd services loaded and confirmed running** | ☐ |
