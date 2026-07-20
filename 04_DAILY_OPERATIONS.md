# DYLAN FOR HIRE — DAILY OPERATIONS
**Version:** 2.1 | **Last Updated:** 2026-07-02
**Purpose:** Everything Aditya does every morning. In order. With exact commands.
**What's new:** Part 0 below — with the two new 24/7 services, your first
check every morning is no longer "did the 9am job run," it's "have both
background services been running all night without crashing." Part 3C (new,
2026-07-02) — two live Cowork dashboards now exist for a faster daily glance
than reading CSVs and log files, plus a new on-demand script for consolidating
a ready candidate's files and drafting their submission to centers.

---

## THE DAILY ROUTINE (20–35 MINUTES)

The daily batch (Steps 1/2/DEDUP) still runs automatically at 9:00 AM EST via
cron. The two new services (SMS reply checking, Gmail real-time review) run
continuously and should never have "finished" — if they show as stopped,
that's the first thing to fix, since it means candidates have been going
unanswered.

---

## PART 0 — (NEW) CONFIRM BOTH 24/7 SERVICES ARE STILL RUNNING

```bash
launchctl list | grep blueline
# Expect two lines: com.blueline.gmaillistener and com.blueline.smspoll
# Both should show a PID (a number) — not "-" — and exit code 0

tail -30 ~/Downloads/gmail_listener.log
tail -30 ~/Downloads/sms_poll.log
```

**If either is missing or shows a crash exit code:** see
`08_TROUBLESHOOTING.md` "24/7 SERVICE TROUBLESHOOTING" before doing
anything else — every hour these are down is an hour of candidate
messages/emails not being checked at all.

---

## PART 1 — CONFIRM THE AGENT RAN

```bash
# Check that cron fired and the agent completed
tail -50 ~/Downloads/BlueLine/cron_output.log
```

**What you want to see:**
```
═══ BlueLine Master Agent v2.1 ═══
...
Run log saved: ~/Downloads/master_run_log_YYYYMMDD_HHMMSS.csv
```

**What you don't want to see:**
- `ModuleNotFoundError` → dependencies issue
- `KeyError` → .env issue
- Python traceback without "Run log saved" → agent crashed mid-run
- Empty file → cron didn't run (Full Disk Access? crontab still set?)

**If the agent didn't run:**
```bash
# Check crontab is still active
crontab -l

# Manual run
cd ~/Downloads/BlueLine
python3.11 master_daily_agent.py
```

---

## PART 2 — READ THE RUN LOG

```bash
# Open the most recent run log
cat ~/Downloads/master_run_log_$(date +%Y%m%d)*.csv

# Or: open in spreadsheet
open ~/Downloads/master_run_log_$(date +%Y%m%d)*.csv
```

**CSV columns:** `timestamp, candidate_name, phone, action, result, notes`

**What to look for:**
- Total new leads contacted (Step 2 sends)
- Any failed sends (non-200 responses) — these will retry tomorrow automatically
- Interest replies handled (Step 3 actions)
- Re-engagement messages sent (Step 1 actions)
- Any errors or unexpected actions

**Healthy run example:**
```
2026-06-30 09:00:12, Jane Doe, +17185551234, INTRO_SMS, SENT, "New lead, RN Queens"
2026-06-30 09:00:15, Maria Santos, +17185555678, INTEREST_REPLY, SENT_CHECKLIST, "Sent document list"
2026-06-30 09:00:22, John Smith, +19175559876, REENGAGE, SENT, "Context-aware follow-up"
```

---

## PART 3 — REVIEW GMAIL DRAFTS (MOST IMPORTANT)

Go to: **mail.google.com → Drafts**

Or:
```bash
open "https://mail.google.com/mail/#drafts"
```

The Gmail document reviewer creates a draft for every candidate who submitted credentials. Each draft contains:
- A ✓/✗ checklist of all documents submitted vs. required
- The appropriate onboarding PDF attached (RN, LPN, or CNA)
- A professional reply written as Dylan

**For each draft:**
1. Read the checklist — confirm it looks correct
2. Add your Gmail signature at the bottom
3. Click **Send**

**What can go wrong:**
- If a draft is missing for a candidate who emailed → check `master_processed_email_ids.txt` (maybe already processed)
- If the checklist looks wrong → the attachment may have been unreadable; override and send manually

**Never let drafts sit unreviewed for more than 24 hours.** Candidates expect a response within one business day.

---

## PART 3B — (NEW) REVIEW EMAIL REPLY DRAFTS FROM GENERAL INQUIRIES

Separate from the document-checklist drafts in Part 3 — these are drafts
written in response to a plain question or comment, not a document
submission. Same place, same review discipline:

Go to: **mail.google.com → Drafts** (same inbox as Part 3, just a different
kind of draft — the subject line usually won't say "Documents Received/Update")

**For each draft:** confirm it correctly references the candidate's actual
situation (it should, since it was written after checking their Gmail +
Quo SMS history — if it reads generic, something didn't match and it's
worth a second look), add your signature, send.

## PART 3C — (NEW, 2026-07-02) CHECK THE LIVE DASHBOARDS

Two Cowork artifacts give you a faster read than digging through logs/CSVs.
Both pull live data on open/reload; neither sends or drafts anything by
itself except via their own explicit buttons:

- **BlueLine Live Dashboard** — unanswered Quo/Gmail threads with drafted
  replies, ready to Send/Create Draft with one click each.
- **BlueLine Pipeline Dashboard** (new) — total leads, new-lead velocity,
  active conversations, no-response/needs-follow-up counts, and — this is
  the one that depends on today's pipeline stage feature actually having
  run — Hot Files (docs complete, onboarding sent) and Submission-Ready
  (onboarding returned) counts, read straight from each Quo contact's `role`
  field. If this section shows all zeros, that's expected until
  `master_gmail_reviewer.py` (v1.2+) has processed at least one real
  candidate's documents — it's not a bug in the dashboard.

**When a candidate shows as Submission-Ready:** run the consolidator to
prep their files and draft the center outreach —

```bash
cd ~/Downloads/BlueLine
python3.11 master_candidate_file_consolidator.py --email candidate@example.com
```

This writes three named PDFs to `~/Downloads/BlueLine/CandidateFiles/` and
creates ONE Gmail draft per matched center with those PDFs attached —
drafts only, never sent. Check `~/Downloads/BlueLine/BLUELINE_CENTER_DIRECTORY.md`
actually has email addresses for the centers you expect before running this
broadly; see 05_PIPELINE_REFERENCE.md STEP 7 for the known gaps (this script
is new and unverified against real data as of 2026-07-02 — test on one
candidate first).

---

## PART 4 — HUMAN REVIEW QUEUE (TWO FILES NOW — SMS AND EMAIL ARE SEPARATE)

```bash
# View all flagged SMS replies
cat ~/Downloads/master_needs_human_review.txt

# View all flagged EMAIL replies (new — kept in a separate file on purpose,
# different format, different context: opt-out-like emails, legal/pricing
# language, client-facility emails, or anything Claude wasn't confident about)
cat ~/Downloads/master_needs_human_review_email.txt
```

**Email flags need a reply from you directly in Gmail** — there's no
auto-generated draft for these (the whole point of flagging instead of
drafting is that Claude wasn't confident enough to write the reply itself).

This file contains SMS replies the system couldn't classify (not clearly YES, not clearly STOP, not a recognisable variant). Each entry shows:
- Candidate name
- Phone number
- The exact text they sent
- Timestamp

**What to do with each:**
- If they're interested → open Quo, reply with the document checklist (or use DOCUMENT_CHECKLIST_MSG from the templates)
- If they're declining → manually add phone to `master_permanent_optouts.txt` and rename Quo contact
- If they're asking a question → reply directly in Quo

**After handling:** You can leave the file as-is (new entries append) or clear it after handling all items:
```bash
# Optional: clear after you've handled everything
> ~/Downloads/master_needs_human_review.txt
```

---

## PART 5 — CHECK INBOX DIRECTLY

Log in to: **info@bluelinestaffing.com**

**What to look for:**
- Any candidate replies to the document checklist emails you sent (from Gmail Drafts)
- Any new email submissions from candidates you haven't yet sent to the Gmail reviewer
- Any client (nursing home) communications about schedules or interviews

**For new attachments you haven't reviewed:**
```bash
cd ~/Downloads/BlueLine
python3.11 master_gmail_reviewer.py
```

Then go back to Gmail Drafts and send the new draft.

---

## PART 6 — 3-DAY FOLLOW-UP CHECK

Every third day (or when time permits), check your sent folder for emails you sent to nursing homes with candidate profiles. If any email hasn't received a reply in 3+ days, send a brief follow-up:

> Hi [contact name], just following up on the CNA/LPN/RN profile I sent over. Let me know if you'd like to move forward or if you need any additional information. Thanks, Dylan

---

## WEEKLY TASKS (MONDAY)

| Task | Where | Action |
|------|-------|--------|
| Archive old run logs | ~/Downloads/ | Move logs older than 7 days to an archive folder |
| Check cron_output.log size | ~/Downloads/BlueLine/ | If > 10MB, clear and start fresh |
| Review total leads remaining in CSV | CONFIDENTIAL_candidates.csv | If < 100 rows remain → source new leads |
| Verify Quo contacts look correct | openphone.com | Spot-check 5–10 contacts for correct naming format |

---

## MONTHLY TASKS

| Task | Action |
|------|--------|
| Verify ElevenLabs API key is still active | Run gen_all_audio.py on one test segment |
| Check Anthropic API usage and costs | console.anthropic.com → Usage |
| Check OpenPhone API usage | openphone.com → Settings → API |
| Review master_permanent_optouts.txt | Confirm it hasn't been accidentally cleared |
| Backup state files | Copy master_*.txt files to secure backup location |

---

## RUNNING THE AGENT MANUALLY

**Any time you need to trigger a run outside of cron:**

```bash
cd ~/Downloads/BlueLine
python3.11 master_daily_agent.py
```

**Running just the Gmail document reviewer (Step 4):**
```bash
cd ~/Downloads/BlueLine
python3.11 master_gmail_reviewer.py
```

**Checking what state files currently contain:**
```bash
wc -l ~/Downloads/master_processed_contacts.txt      # total intros sent
wc -l ~/Downloads/master_permanent_optouts.txt        # total opt-outs
wc -l ~/Downloads/master_needs_human_review.txt       # pending manual replies
tail -10 ~/Downloads/master_handled_interest_replies.txt  # recent interest replies
```

---

## ADDING NEW LEADS TO THE CSV

When you have new leads to add to `CONFIDENTIAL_candidates.csv`:

1. Open the CSV in Numbers or Excel
2. Add new rows at the bottom
3. Ensure the `name` column has the full name and `phone` column has their number
4. Save as CSV (UTF-8 or UTF-8 BOM)
5. The agent will pick them up on the next run automatically

**No restart or reset needed.** The agent reads the CSV fresh every run.

---

## HANDLING INDEED RESUMES (MANUAL WORKFLOW)

When candidates apply via Indeed:

1. Download the resume(s) from Indeed employer portal
2. Put them in a folder: `~/Downloads/Indeed_Leads/`
3. Run Claude to read each resume:
   ```
   Read the resumes in ~/Downloads/Indeed_Leads/ and for each:
   - Extract: name, real phone (NOT @indeedmail.com), personal email, license type, NYC borough
   - Do a Quo dedup check by name and phone
   - If new: create a Quo contact (firstName=name, lastName="LICENSE, Borough")
   - Draft an INDEED_INTRO SMS for approval
   ```
4. Review and approve each draft message before it sends

**Never use Indeed proxy emails** (@indeedmail.com, @indeed.com masking addresses). Only use the candidate's personal email if visible in the resume.

---

## EMERGENCY PROCEDURES

### Agent sent messages to an opted-out number

1. Immediately add the number to `master_permanent_optouts.txt`
2. Rename the Quo contact to "DO NOT MESSAGE - {name}"
3. Send an apology SMS from Quo manually: "Hi, I apologise for the message. You have been removed from our list."
4. Document the incident with timestamp
5. Investigate why the number wasn't in the optouts file

### Duplicate contacts were created

```bash
cd ~/Downloads/BlueLine
python3.11 -c "
from master_daily_agent import merge_duplicate_contacts
merge_duplicate_contacts()
"
```

### Cron hasn't run for multiple days

Check: `~/Downloads/master_last_run_timestamp.txt`  
Run manually: `python3.11 master_daily_agent.py`  
The catchup logic will send up to 150 leads to compensate (capped).

### Gmail auth expired

```bash
cd ~/Downloads/BlueLine
python3.11 master_gmail_setup.py
```
Follow browser prompt to re-authorise. Then re-run the gmail reviewer.
