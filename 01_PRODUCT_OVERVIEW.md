# DYLAN FOR HIRE — PRODUCT OVERVIEW
**Version:** 2.0 | **Last Updated:** 2026-07-01
**What changed:** Dylan moved from a once-daily batch to continuous (24/7)
checking of both SMS and email, and email replies now cover general
inquiries (not just document submissions) with the same cross-channel
history check SMS already had. See §1A for exactly what "24/7" does and
doesn't mean here — accurate framing matters for a sales conversation.

---

## 1. WHAT IT IS

Dylan for Hire is an AI-powered healthcare recruiting agent that runs
continuously and handles the entire early-funnel recruiting workflow:

1. Finds new nurse candidates and sends personalised first-contact messages (daily)
2. Reads every SMS reply and responds intelligently within ~90 seconds, all day
3. Reads every inbound email — document submission or general inquiry — within
   seconds of arrival, all day, checking both Gmail and SMS history first
4. Follows up on candidates who go silent — with context-aware, personalised messages (daily)
5. Reviews credential documents submitted by email and prepares compliance checklists

**What it replaces:** 6–8 hours of daily manual recruiter work (outreach, follow-up, document review)
**What it costs:** Re-measure after one week of 24/7 operation — see §5, the
old $18,000/year estimate was built on once-a-day batch economics
**What it runs on:** Python 3.11, macOS. New-lead outreach and re-engagement
stay on a 9:00 AM EST daily cron (deliberately — see §1A); inbound SMS and
email are now handled by two always-on background services, not cron.

## 1A. WHAT "24/7" MEANS HERE (READ BEFORE PITCHING THIS)

**True of the system today:** inbound SMS and inbound email are both
checked continuously (not once a day), and every reply — SMS or email —
is generated only after checking that candidate's history across BOTH
channels. Nothing sits unanswered until the next morning anymore.

**Also true, and this is a feature, not a limitation:** anything sensitive
still waits for a human. Email replies are always drafts, never sent
automatically. Both SMS and email flag anything ambiguous, legal-sounding,
price-related, or opt-out-adjacent for Aditya (or your customer) to handle
directly, rather than guessing. This is what makes running 24/7 safe under
TCPA and under a small agency owner's actual risk tolerance — sell it as
"always watching, always ready, human approves anything that matters," not
as a fully unsupervised agent. The latter framing is both inaccurate and a
harder sell to a compliance-conscious buyer anyway.

---

## 2. THE BUSINESS CONTEXT (BLUELINE STAFFING)

| Field | Value |
|-------|-------|
| Agency name | BlueLine Staffing |
| Location | Allendale, NJ |
| Owner | Aditya (operates EST hours from Gurugram, India) |
| Outbound persona | **Dylan** — all SMS and email signed as Dylan |
| Agency email | info@bluelinestaffing.com |
| Agency SMS number | +15512506678 |
| Roles placed | CNA, LPN, RN, RNS, HHA |
| Service area | NYC — Bronx, Brooklyn, Manhattan, Queens (34+ facilities) |

---

## 3. THE PIPELINE (LOGICAL RECRUITMENT FUNNEL)

```
STEP 1 — New Lead Intro (daily, 9am cron)
  Every morning: 30 new nurses receive a personalised first contact SMS
  Source: CONFIDENTIAL_candidates.csv
  Logic: deduplicated, license-aware, borough-aware
  Effect: fills the top of the funnel daily

STEP 2 — SMS Reply Handler (continuous, ~90 second checks, all day — NEW cadence)
  Handles every inbound reply to an outbound SMS
  YES → sends full document checklist + pay rates instantly (< 10 seconds
        after the poll cycle that catches it)
  STOP/UNSUBSCRIBE → permanent opt-out, contact renamed, never messaged again
  Unknown → flagged for Aditya to handle manually

STEP 3 — Re-engage Stalled Contacts (daily, 9am cron)
  Targets every candidate silent for 96+ hours
  Reads 4 days of SMS + email history before sending anything
  Sends a contextually relevant follow-up — or skips if mid-process
  Never sends a generic blast to someone who is already engaged

STEP 4 — Document Review (continuous, real-time via Gmail push — NEW cadence)
  Monitors info@bluelinestaffing.com for attachments from candidates
  Claude Vision reads: nursing license, physical, titers, TB, BLS, I-9
  Validates each against NYS date windows and compliance requirements
  Generates a ✓/✗ checklist reply — saved as Gmail Draft, never auto-sent

STEP 5 — General Email Inquiry (continuous, real-time via Gmail push — NEW)
  Any unread email WITHOUT attachments (a question, a follow-up, a comment)
  Checks the sender's full Gmail thread history AND their Quo SMS history
  (name-matched — see 02_SYSTEM_ARCHITECTURE.md §13A for match logic/limits)
  Drafts a reply, skips if nothing is needed, or flags for human review if
  the email is sensitive (opt-out, legal, pricing, client-originated, or
  anything Claude isn't confident about) — see 07_COMPLIANCE.md
```

**Note on technical execution order:** The daily-cron code still runs in the
order Step 2 (SMS replies) → re-engage → DEDUP → Step 1 (new leads) — Steps
2/4/5 above are ALSO checked continuously by the two new background
services, independent of the cron's own Step-2 pass. This is by design:
inbound responses get handled the moment they arrive, not just once a day.

---

## 4. WHAT MAKES IT DIFFERENT FROM OTHER SMS AUTOMATION

| Capability | Generic SMS tools | Dylan for Hire |
|-----------|------------------|----------------|
| Personalised first message | Template blast | License + borough aware |
| Response to YES | Manual or delayed | < 10 seconds, automatic |
| Follow-up logic | Scheduled drip | Reads SMS + email history first |
| Duplicate protection | None / weak | 3-pass dedup (phone, full name, first name) |
| Document review | Not included | Full NYS credential validation via AI Vision |
| TCPA compliance | Opt-out list (basic) | Permanent file, hardcoded blocklist, human-in-loop for email |
| Skip logic | None | Skips if mid-process, active email thread, or messaged recently |
| Catchup logic | Not included | Detects missed days, sends up to 150 on catch-up |
| Audit trail | None | Timestamped CSV log of every action |

---

## 5. THE COST CASE

### True Annual Cost: Human Recruiter vs. Dylan

| Component | Human Recruiter | Dylan for Hire |
|-----------|----------------|----------------|
| Base salary + benefits + payroll | $62,640 | — |
| Paid unproductive time (37 days/yr) | $8,910 | — |
| Missed placements (37 down-days × 30 leads × 5% rate × $1,800 avg margin) | $99,000 | — |
| System subscription | — | $18,000/yr |
| **Total true annual cost** | **$161,640** | **$18,000** |
| **Net advantage** | | **$143,640/yr** |

### Year-One ROI at 8 Placements/Month (Default Assumptions)

| Value Stream | Amount |
|-------------|--------|
| Revenue from +25% placement lift | +$33,197 |
| Downtime coverage (37 days × 30 leads × 5% × per-placement margin) | +$99,000 |
| Recruiter time freed (750 hrs/yr at $30/hr effective) | +$22,500 |
| BlueLine annual subscription | −$18,000 |
| **Net year-one advantage** | **~$136,700** |

**Payback period:** < 2 months

---

## 6. THE CANDIDATE JOURNEY (WHAT A NURSE EXPERIENCES)

```
Day 0:  Receives SMS from Dylan — "Hi Sarah, this is Dylan from BlueLine..."
        [If YES] → Receives document checklist + pay rates in < 10 seconds

Day 1–3: If no reply → system waits (re-engage window is 72 hours, lowered
          from 96h on 2026-07-02 per Aditya's explicit rule — see
          `STALL_WINDOW_HOURS` in master_daily_agent.py)
          System reads email + SMS history before deciding to follow up

Day 3:  Context-aware re-engagement if silent — references actual situation
        (e.g. "Hi Sarah, just checking — did the document list come through okay?")

Ongoing: Candidate submits documents to info@bluelinestaffing.com
          Gmail agent reads every attachment → drafts checklist reply
          Aditya reviews draft → sends → candidate knows what's missing
```

---

## 7. WHAT THE OPERATOR DOES DAILY (Aditya's Morning Routine)

**Total time required:** 15–30 minutes

1. Open Gmail Drafts → review document checklist replies → add signature → send
2. Check `master_needs_human_review.txt` → manually reply to unrecognised SMS
3. Skim `master_run_log_YYYYMMDD.csv` → confirm numbers look right
4. Check `cron_output.log` → confirm no errors

Everything else runs automatically.

---

## 8. WHITE-LABEL PARAMETERS

This system is fully white-labelable. To deploy for another agency, change:

| Parameter | Where to change | Example |
|-----------|----------------|---------|
| Recruiter persona name | DYLAN_INTRO template in `master_daily_agent.py` | "Dylan" → "Marcus" |
| Agency name | DYLAN_INTRO template | "BlueLine Staffing" → "Apex Care Staffing" |
| Agency email | `master_gmail_reviewer.py` monitored inbox | info@bluelinestaffing.com → info@apexcare.com |
| Agency SMS number | `.env` QUO_PHONE_NUMBER_ID | PNWtLBsgMe → new number ID |
| Pay rates | DOCUMENT_CHECKLIST_MSG template | CNA $22–26 → whatever agency pays |
| Facility list | DOCUMENT_CHECKLIST_MSG template | Update as needed |
| Blocked numbers | BLOCKED_NUMBERS set in `master_daily_agent.py` | Add/remove numbers |

---

## 9. SYSTEM REQUIREMENTS SUMMARY

| Requirement | Value |
|-------------|-------|
| Language | Python 3.11 |
| OS | macOS (cron-based scheduling) |
| SMS platform | Any OpenPhone-compatible or Twilio/EZTexting (see API docs) |
| Email | Gmail (OAuth2) — or any IMAP with modification |
| AI engine | Anthropic Claude (API key required) |
| Scheduler | macOS cron (launchd also supported) |
| Internet | Required at run time |
| Storage | ~100MB (logs, state files, audio assets) |

---

## 10. CURRENT LIVE METRICS

**As documented 2026-06-30 (business-reported — re-verify before any customer
call, see `09_GO_LIVE_READINESS.md`):**

| Metric | Value |
|--------|-------|
| Total candidates contacted | 344+ |
| Active conversations (this week) | 41 |
| New contacts per morning | 30 |
| Boroughs covered | 5 (all NYC boroughs) |

**System version, as verified from source 2026-07-01:**

| Metric | Value |
|--------|-------|
| Version | 3.0 |
| Known bugs | 0 (14 bugs fixed — BUG-14 found and fixed 2026-07-01, see 08_TROUBLESHOOTING.md) |
| Emails auto-sent | 0 (all drafts, human reviews before sending — unchanged, permanent design) |
| SMS/email checked | Continuously (was: once daily as of 2026-06-30) |
| Real-time services live on Aditya's Mac | **Unverified from this project folder** — requires `launchctl list \| grep blueline` run on the actual machine. Do not claim this to a customer until confirmed. |
