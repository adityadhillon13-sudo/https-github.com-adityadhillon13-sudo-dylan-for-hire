# SAAS PROJECT — HEALTHCARE RECRUITMENT
## Master Context Document · Dylan for Hire
### Carry this into every new session. Last updated: July 1, 2026. Version 3.0.

---

## RULE 0 — DYLAN WORK HAPPENS IN THIS PROJECT, NOWHERE ELSE

This project folder ("Dylan for Hire- Saas Product Healthcare recruitment")
is the single source of truth for Dylan/BlueLine automation. If you are an
assistant session working anywhere else and Aditya brings up Dylan, SMS
automation, candidate pipelines, or BlueLine's Gmail/Quo integration —
flag it immediately and redirect back to this project before doing any
build work. See `00_INDEX.md` Rule 0 for the full statement and reasoning.
This is not a formality: the doc set in this project has already drifted
from the real code more than once (corrected in v3.0 — see §13 below), and
splitting Dylan work across projects during a 2-week launch push is how
that gets worse.

**[ADDED 2026-07-02, Round 13 — Rule 0 governs CONVERSATION locus, this
paragraph governs CODE source-of-truth, and the two are not the same thing.]**
Aditya runs concurrent sessions — this Cowork project AND at least one
Claude Code session, both able to touch `~/Downloads/BlueLine/`. Neither
session has live visibility into the other's in-progress work; the only
shared truth is the files actually on disk, and on 2026-07-02 that caused
real confusion (untested code landed in the live BlueLine deployment from a
session neither aware of nor verified against this project's test suite).
Resolution:
- **`~/Downloads/BlueLine/` is the source of truth for pipeline engineering
  code** (bug fixes, safety guards, performance) — it's the actual
  cron/launchd deployment, so it's the only place a fix is genuinely proven.
  This project's `src/` is a synced reference copy, not an independent
  place to invent pipeline logic.
- **This project is still the source of truth for product strategy, the
  eventual multi-tenant architecture, docs, and business planning** — that
  hasn't changed. Rule 0 stands for that.
- **Both folders are now git repos** (secrets/PII/logs gitignored, never
  committed). Run `scripts/sync_check.sh` (in this project) at the start of
  any session touching the shared pipeline files — it reports drift and can
  auto-sync BlueLine → `src/` for the files where that direction is
  unambiguous. See `DYLAN_AUDIT_2026-07-01_FULL.md` Round 13 for the full
  incident writeup.

---

## 0. GOVERNING DOCUMENTS

All work across ALL projects is governed by this hierarchy. Higher layers override lower layers on any conflict.

### Universal (all projects)
| Priority | Document | Location | Authority |
|----------|----------|----------|-----------|
| 0 | WORKING_PROTOCOL.md | ~/Desktop/Aditya/CLAUDE/ | HOW work is done — Plan→Align→Execute. Mandatory pre-flight plan before any build. |
| 1 | Claude Operational Bible .md | ~/Desktop/Aditya/CLAUDE/ | Universal quality, strategy, decision framework, automation mandate, cross-project rules. Overrides everything. |

**Quality floor (from Bible — non-negotiable):** All Tier 1 output (client-facing, revenue-generating, public-facing) must meet the 95th percentile standard. This is the operating floor, not an aspiration.

### BlueLine / SaaS-specific
| Priority | Document | Location |
|----------|----------|----------|
| 1 | CLAUDE.md | ~/Downloads/BlueLine/ |
| 2 | BLUELINE_MASTER_OPS.md | ~/Downloads/BlueLine/ |
| 3 | BLUELINE_CANDIDATE_PIPELINE.md | ~/Downloads/BlueLine/ |
| 4 | BLUELINE_COMMS_PLAYBOOK.md | ~/Downloads/BlueLine/ |
| 5 | BLUELINE_TECH_CONFIG.md | ~/Downloads/BlueLine/ |
| 6 | BLUELINE_CENTER_DIRECTORY.md | ~/Downloads/BlueLine/ (34 centers, contacts, rates) |
| 7 | This file, plus `00_INDEX.md` through `10_CLIENT_INTAKE_AND_ADAPTER_SPEC.md` | This project folder |

---

## 1. WHO I AM

**Name:** Aditya (goes by Adi)
**Location:** Gurugram, Haryana, India
**Primary income business:** BlueLine Staffing (Allendale, NJ) — NYC-area healthcare staffing agency. Owners: Gagan Sehgal + Rakesh Khettry (hands-off). Aditya runs it independently.
**Working hours:** BlueLine 6:30pm–3:00am IST = 9:00am–5:00pm EST. (This is Aditya's own working hours — it is NOT Dylan's uptime. Dylan's own operating hours are covered in §2 below and are being changed to 24/7 as of v3.0.)
**Communication style:** All caps, abbreviated, fast. Wants execution over planning. Build first, explain after.

---

## 2. THE PRODUCT — DYLAN FOR HIRE

### What it is
A productized AI staffing automation service sold to small US nurse staffing agencies (2–50 employees). Built on **Dylan** — the AI agent originally built for BlueLine Staffing's internal operations. BlueLine is the live proof of concept.

### The offer
| Tier | Price | Notes |
|---|---|---|
| DIY Template | $497 one-time | Template bundle, self-setup, no support |
| **Pro Retainer** ✓ PRIMARY | $1,500 setup + $750/month | Full custom build, $750 deposit to start |
| Enterprise | Custom quote | Multi-state, white-label, dedicated SLA |

**Revenue target:** 7 clients = $5,250/month MRR by Month 4

### What Dylan actually does today (verified against source code, 2026-07-01)

**Was (through 2026-06-30):** one batch run per day at 9:00 AM EST. Everything
else — including all Gmail review — was manual/on-demand.

**Is (as of v3.0, once Aditya completes `03_SETUP_GUIDE.md` Step 11):**

1. **Candidate Applies** — Web / SMS / email capture
2. **Intake Captured** — Automated form processing
3. **Inbound SMS handled continuously** — `master_sms_poll_service.py` checks
   Quo every ~90 seconds, all day, instead of once at 9am (interest → document
   checklist in seconds; opt-out → permanent removal; unrecognised → flagged)
4. **Inbound email handled continuously** — `master_gmail_pubsub_listener.py`
   reacts within seconds of a new email via Gmail push notifications. Covers
   BOTH document submissions (existing Claude Vision review) AND general
   inquiries (new — checks Gmail thread history AND Quo SMS history before
   drafting, skipping, or flagging for human review)
5. **Documents Audited** — 8 required + 3 recommended (non-blocking) = 11 tracked
   categories (Claude Vision, zero human review of the audit itself).
   **Corrected 2026-07-01 (Round 2 audit):** this was previously documented as
   "11-point" (implying 11 mandatory items) — verified directly against
   `validate_documents()` and corrected to "9-category" at the time.
   **Updated 2026-07-01 (Round 4 — Aditya's product decision):** Hepatitis B
   and annual flu vaccine were added to the automated check as **recommended,
   not mandatory** (same non-blocking treatment as BLS/CPR), because both allow
   a signed declination as a compliant alternative to vaccination and the system
   can't yet tell "non-compliant" apart from "validly declined." Required (8):
   resume, nursing license, I-9/ID documents, physical, MMR titers, varicella
   titers, chest X-ray/PPD/Quantiferon, COVID vaccine. Recommended (3): BLS/CPR,
   Hepatitis B, annual flu vaccine. **Do not shorthand this as "11-point check"
   without stating the 8/3 split — that exact collapse is what caused the
   original inaccurate claim this file spent two audit rounds correcting.**
   NYS CHRC background-check/fingerprinting remains unbuilt and undecided —
   deliberately not folded into this decision because there's usually no
   declination alternative for it, making it a higher-liability, different kind
   of gap. See `09_GO_LIVE_READINESS.md` 🔴 KNOWN GAPS #6. **Verification status:**
   the Hep B/flu code change was made this session and has not yet been tested
   against a real document — do not repeat "11 tracked categories" to a prospect
   until that test passes (see `09_GO_LIVE_READINESS.md` 🟡 list).
6. **Shift Matched** — AM/PM/overnight by borough & role
7. **Client Alerted** — In under 4 minutes from submission
8. **Daily batch:** re-engage stalled contacts (72hr+ silence, cross-channel
   context-aware), dedup, new lead intro (unlimited — every eligible lead each run).
   Reply handling (instant) is a separate, permanent 24/7 service — see §12A.

**Only manual step in the entire funnel: the sales call, plus reviewing
and sending anything Dylan drafts or flags — see §7 below and
`07_COMPLIANCE.md`. That review step is a deliberate design choice, not a
gap — see the honest positioning note in §2A.**

### 2A. HONEST POSITIONING — WHAT "24/7 AUTONOMOUS" ACTUALLY MEANS HERE

Aditya's go-to-market goal is to sell this as a 24/7 running agent. That's
now accurate for the *checking and drafting* work — Dylan is watching both
channels continuously and cross-references history before acting. It is
**not**, and should never be marketed as, an agent that sends things without
a human in the loop for anything sensitive. The system draft-only gate for
email and the FLAG_HUMAN decision for both channels are real, deliberate,
load-bearing product features — they are what makes 24/7 operation safe
under TCPA and under a small agency owner's risk tolerance. When pitching
this: "always watching, always ready, never sends anything sensitive
without you" is the honest and, based on Aditya's own risk read, the more
sellable framing than "fully autonomous."

### Proven results at BlueLine Staffing NYC
- 37 active nurses managed (22 CNAs · 9 LPNs · 6 RNs)
- 19 Full-Time · 16 Part-Time · 2 Per Diem
- Monthly payroll generated: $30–35K
- Monthly client billing: $42–48K
- 83% intake time reduction
- 8 required + 3 recommended (11 tracked) document audit categories — zero
  human review of the audit step (see correction note in §2 above — do not
  quote "11-point" without the required/recommended split, and do not quote
  the Hep B/flu additions to a prospect at all until live-tested)
- Candidate to placement alert: < 4 minutes
- 1 person now runs what needed 3

**Verification note (see `09_GO_LIVE_READINESS.md`):** the numbers above are
business-reported (from Quo / Google Sheets / actual billing), not something
derivable from source code. Re-verify them before quoting to a prospect —
they should reflect the current week, not a snapshot from launch.

---

## 3. THE TECH STACK

| Tool | Function | Cost |
|---|---|---|
| Phantombuster | LinkedIn sourcing — 15 connections/day automated | $56/mo |
| Make.com | 4 automation scenarios (see below) | Existing |
| Claude API | Proposal drafting + document audit + email/SMS decision intelligence | Pay-as-go |
| Google Cloud Pub/Sub | **New (v3.0)** — real-time Gmail push notifications | ~$0–5/mo at this volume |
| Calendly | Discovery calls booked automatically | Free/Pro |
| Stripe | Invoice generation + payment link on proposal sign | % fee |
| Google Sheets | Live pipeline dashboard — source of truth | Free |
| Carrd | One-page offer site | Existing |
| Loom | 15-20min Dylan walkthrough video (primary sales asset) | Existing |

### The 4 Make.com Sales-Funnel Scenarios (separate from the product itself)
1. **Loom follow-up** → triggered 48hrs after LinkedIn connection, sends Loom link
2. **Call booking handler** → triggered when Calendly booking confirmed, adds to Sheets
3. **Proposal draft** → triggered after call, Claude API generates 400-word personalised proposal
4. **Invoice + onboarding** → triggered when proposal approved, Stripe link sent + onboarding sequence starts

---

## 4. THE SALES FUNNEL (end to end)

```
Phantombuster (15 connections/day)
  → LinkedIn connection accepted
  → Make.com Scenario 1: Loom drop at 48hrs
  → Prospect books via Calendly (book.dylanforhire.com)
  → Make.com Scenario 2: Sheets pipeline updated, you're alerted
  → Sales call (30 min, only manual step)
  → Make.com Scenario 3: Claude API drafts proposal within 60 seconds
  → You approve + send
  → Prospect pays $750 deposit via Stripe
  → Make.com Scenario 4: Onboarding sequence fires
  → 10-day build
  → Go live
  → $750/month recurring begins
```

---

## 5. THE OUTREACH SYSTEM

### LinkedIn sequence (5 messages)
- **Day 0:** Connection note (300 chars, peer-to-peer, no pitch)
- **Day 2:** Loom drop — "Built this for my own agency, thought you'd find it relevant"
- **Day 5:** Soft bump — one question about their current intake process
- **Day 10:** Price + booking link — direct, confident
- **Day 17:** Clean breakup message

### Target ICP (Ideal Client Profile)
- 2–50 employee nurse staffing agency
- Places CNAs / LPNs / RNs (per diem or contract)
- US-based, operating in 1–5 states
- Owner-operator or small founding team
- Tracking candidates in spreadsheets today
- No dedicated tech or ops hire
- Wants to scale without adding headcount

### Verified outreach targets (first 10)
1. KIND Staffing Group — Rockford, IL — CNA/LPN · LTC · 50-state
2. SmithLife Staffing — Rockville, MD — CNA/LPN/CMT · DC metro
3. Caring Staff Nursing Agency — Pennsylvania — CNA/LPN/RN · per diem
4. ANR Staffing Solutions — New York, NY — NY DOH · TA013
5. Adaptive Workforce Solutions — New York, NY — NY DOH · TA022
6. Allcare Medical Services — New York, NY — NY DOH · TA038
7. Advanced Care Staffing — New York, NY — NY DOH · TA026
8. Amare Medical Staffing — New York, NY — NY DOH · TA043
9. Capital Staffing Solutions — New York, NY — NY DOH · TA075
10. Clover Health Services — New York, NY — NY DOH · TA085

*+ 10 more from NJ/IL/TX/FL/PA/MD DOH registries*

---

## 6. REVENUE PATH TO $5K/MONTH

| Month | Clients | What Dylan enables | Your revenue |
|---|---|---|---|
| Month 1 | 2 | First 2 agencies onboarded + live | $3K setup fees |
| Month 2 | 4 | 2 more live, outreach engine running | $3K/mo MRR |
| Month 3 | 6 | Referrals kick in | $4.5K/mo MRR |
| Month 4+ | 7 | $5K goal hit ✓ | $5.3K/mo MRR |

---

## 6A. PHASE 1 COSTS BY MONTH

### Fixed Monthly Tool Stack

| Tool | Monthly Cost | Purpose |
|---|---|---|
| Phantombuster | $56 | LinkedIn sourcing — 15 connections/day automated |
| Make.com (Core) | $29 | 4 automation scenarios |
| Claude API | ~$30–45 | Proposal drafting + doc audit + (new) continuous email/SMS decisions — likely higher than the old ~$30 estimate once 24/7 polling is live; re-measure after week 1 |
| Google Cloud Pub/Sub | ~$0–5 | Real-time Gmail notifications — free tier covers this volume |
| Calendly (Standard) | $12 | Discovery call booking + intake questions |
| Carrd (Pro) | $4 | One-page offer site (dylanforhire.com) |
| Domain | $1 | dylanforhire.com (~$12/yr) |
| **Total Fixed (revised estimate)** | **~$135–145/mo** | |

**Variable:** Stripe 2.9% + $0.30/transaction — charged only on revenue, zero upfront.

**Action before quoting a customer:** measure actual Claude API spend for one
full week of 24/7 operation (email listener + SMS poll service both running)
before finalizing the per-client cost basis in any pricing conversation —
the old $18K/yr subscription-cost assumption in `01_PRODUCT_OVERVIEW.md`
was built on once-a-day batch economics, not continuous polling.

### Phase 1 Summary (M0–M3)

| Metric | Value |
|--------|-------|
| Total setup fee revenue | $9,000 |
| Total MRR at end of M3 | $3,000/mo |
| Payback period | Month 1 (first client covers tool costs many times over) |
| Break-even | Day 1 of M1 — $1,500 setup fee vs ~$140 monthly tools |

---

## 7. WEB PRESENCE

| URL | Purpose | Status |
|---|---|---|
| dylanforhire.com | One-page sales site (Carrd) | Build needed |
| book.dylanforhire.com | Calendly redirect | Setup guide delivered |
| hello@dylanforhire.com | Contact / Calendly sender | Gmail setup guide delivered |

### Website structure (5 sections, nothing else)
1. **Hero** — "Your Nurse Staffing Agency. Fully Automated." + CTA button → Calendly
2. **The Problem** — 3 pain stats + 1 punchline
3. **How Dylan Works** — 4-step flow visual
4. **Proof** — BlueLine numbers + quote
5. **Pricing** — 3 tiers + "Start with $750 →" Stripe link

---

## 8. CALENDLY SETUP (not yet live — guide delivered)

| Setting | Value |
|---|---|
| Account name | Adi Dylan |
| Email | hello.dylanforhire@gmail.com (forwards to aditya.dhillon13@gmail.com) |
| Phone | 551-250-6678 |
| Availability | Mon–Fri 9am–6pm EST |
| Call type | Free 30-Min Dylan Demo |
| Duration | 30 minutes |
| Buffer before | 10 minutes |
| Buffer after | 15 minutes |
| Max/day | 4 calls |
| Min notice | 4 hours |
| URL | calendly.com/adi-dylan/dylan-demo |

### Pre-call intake questions (required)
1. Agency name
2. State(s) you operate in
3. Nurses on your bench (dropdown: <10 / 10–25 / 26–50 / 50+)
4. What are you currently using to manage candidate intake?

---

## 9. THE PITCH DECK

**Current version: V8 FINAL** (`Dylan_for_Hire_Pitch_Deck_V8_FINAL.pptx`)
**Built with:** Node.js + pptxgenjs · Source: `dylan_pitch_v8.js`

**Before your next demo:** update the "How Dylan Works" and "Features" slides
to mention continuous (not once-daily) checking — this is now true and it's
a stronger claim than what V8 currently says. Do not touch the numbers on
the Proof slide without re-verifying them first (see `09_GO_LIVE_READINESS.md`).

**⚠️ Separate HTML pitch/architecture assets — build script mismatch (found
2026-07-01, Round 2 audit, verified directly in code):** `pitch/build_pitch_deck.py`
and `pitch/build_arch_doc_v2.py` both hardcode their output path to
`~/Downloads/BlueLine/blueline_pitch_deck.html` /
`~/Downloads/BlueLine/blueline_architecture_doc.html`. The actual finished,
audio-embedded assets sitting in this project's `pitch/` folder are named
`dylan_for_hire_pitch_deck.html` / `dylan_for_hire_architecture.html`. Running
either script today would NOT update the real files in place — it would
create differently-named BlueLine-branded files in a different folder. The
scripts' own embedded content is also stale (hardcoded "v2.1", "13 bugs
fixed" — both are now v3.0 / 18 bugs fixed). See `09_GO_LIVE_READINESS.md`
🔴 KNOWN GAPS.

### Design system
- **Background:** `#04080E` (near-black navy)
- **Primary accent:** Teal `#00BAC8`
- **Money/gain:** Green `#00E676` (bright) / `#00C27A` (primary)
- **Cost/problem:** Coral `#F04040`
- **Revenue:** Gold `#EFB01F`
- **Font:** Calibri throughout
- **One idea per slide. Max 15 words per content element.**

---

## 10. DOCUMENTS DELIVERED (all in outputs)

| File | Purpose |
|------|---------|
| `Dylan_for_Hire_Pitch_Deck_V8_FINAL.pptx` | Current deck — use this, update per §9 note above |
| `Dylan_for_Hire_LinkedIn_Outreach_Sequence.md` | 5-message sequence + Make.com logic |
| `Dylan_for_Hire_Discovery_Call_Script.md` | 30-min word-for-word call script + objection handlers |
| `Dylan_for_Hire_Proposal_AutoDraft_System.md` | Make.com → Claude API proposal system |
| `11_CUSTOMER_FACING_PRODUCT_OVERVIEW.md` | **Replaces** the uploaded `Dylan_for_Hire_Product_Overview.md` (2026-07-01) — sanitized, prospect-safe overview. Credential table corrected from a false "11-point" claim to the verified 9-category schema; 24/7 claim deliberately omitted until verified live (see `09_GO_LIVE_READINESS.md`) |
| `12_SCHEDULING_SETUP_GUIDE.md` | **Supersedes** `Dylan_for_Hire_Calendly_Setup_Guide.md` (this project folder never actually had that file — only referenced it). Step-by-step Calendly + Gmail setup; live account values live in §8 above, not duplicated in that file |

**Note (2026-07-01):** the four `.pptx`/`.md` files above other than the two `11_`/`12_` entries were not
found in this project folder as of the Round 3 audit — they may exist only in Aditya's local outputs
folder outside this synced project. Not treated as a discrepancy requiring action, but flagged so this
table isn't read as a guarantee those files are retrievable from here.

---

## 11. WHAT STILL NEEDS TO BE DONE

### Aditya must do these personally (cannot be automated or delegated)
- [ ] **Complete `03_SETUP_GUIDE.md` Step 11** (Pub/Sub + launchd) on the real
  Mac — this cannot be verified or completed from a synced project folder;
  it requires your Google Cloud Console and your actual machine
- [ ] **Record the Loom walkthrough** (15–20 min), updated to show real-time
  behavior, not just the daily batch
- [ ] **Complete Stripe verification** — non-US account has processing delay
- [ ] **Point `book.dylanforhire.com`** → Calendly URL
- [ ] **Build Carrd site** — `dylanforhire.com`
- [ ] **Re-verify all Proof-slide numbers** before the first customer demo

### Next to build in this project
- [ ] Carrd site (one-page, 5 sections — copy ready, needs design build)
- [ ] Make.com Scenarios 1–4 (sales funnel automation, separate from the product itself)
- [ ] Full launch checklist — see `09_GO_LIVE_READINESS.md`

---

## 12. KEY RULES FOR THIS PROJECT

- **Rule 0 stands above all of these — see top of this document.**
- **Automation-first.** Every repeatable step gets automated. Human time = sales calls + reviewing drafts/flags. Target: no more than 20–25 hrs/week managing any business.
- **BlueLine is the credibility anchor.** Real numbers. Real nurses. Real billing. Never invent stats.
- **Never send automatically.** Email and SMS both retain human-in-loop gates for anything sensitive — this is a permanent product feature, not a temporary limitation. See `07_COMPLIANCE.md`.
- **Design system is locked.** Teal / green / coral / gold palette. Calibri. McKinsey top-accent-bar on all KPI cards.
- **ICP is locked:** 2–50 staff nurse staffing agencies, US-based, spreadsheet-trackers.
- **Pricing is locked:** $497 DIY / $1,500+$750/mo Pro / Enterprise custom.
- **95th percentile quality floor.** All client-facing output meets the standard of the top 5% of comparable work. No exceptions.
- **Before repeating any claim about what the system does, verify it against the actual source code in `src/`, not just the docs.** The docs have been wrong before (see §13).
- **MANDATORY — this doc set is a living contract, not a snapshot.** Every session that touches this project must: (1) read this file plus `00_INDEX.md` before doing anything else; (2) if a claim in any doc is repeated to Aditya or a customer, verify it against `src/` first — do not assume a prior session's fix is still true; (3) if drift, a stale claim, or a bug is found, fix it in the doc(s) in the SAME session, not "next time"; (4) log what was found and fixed as a new dated section in `DYLAN_AUDIT_2026-07-01_FULL.md` (append, don't overwrite prior rounds). This is not optional housekeeping — it is how this project avoids the exact failure mode documented in §13 from recurring. See `00_INDEX.md` for the full continuous-audit procedure.

---

## 12A. BLUELINE TECHNICAL REFERENCE (proof of concept — production system)

### Pipeline Architecture (verified from source, 2026-07-01)

```
DAILY CRON (schedule at Aditya's discretion — v2.6+ no longer includes Step 3):
  master_daily_agent.py main():
    Step 1 → Re-engage stalled contacts (72hr inactivity threshold)
    DEDUP  → Live deduplication against Quo contacts
    Step 2 → New lead intro SMS (unlimited — every eligible CSV row each run, no cap)

24/7 SERVICES (v3.0 — see 03_SETUP_GUIDE.md Step 11):
  master_sms_poll_service.py     ← Step 3 (SMS replies), EXCLUSIVE owner, every
                                     ~90 seconds, all day — "reply instantly" is a
                                     hard requirement, so this must run permanently
                                     (launchd), not just in a manual terminal.
  master_gmail_pubsub_listener.py ← Email (doc + general inquiry), real-time
```

> **[FIXED 2026-07-02, Round 11]** Step 3 used to run from BOTH the daily cron
> (inside `main()`) AND the 24/7 poll service — that redundancy was a real
> duplicate-response race, not just wasted API calls, because
> `acquire_lock()`/`release_lock()` in `master_daily_agent.py` only guards against
> two overlapping runs of `main()` itself; it does nothing to stop the poll
> service's direct `step3_sms_reply_handler()` call from overlapping with a
> cron-triggered run. `main()` no longer calls Step 3 by default (opt-in via
> `--include-step3`, manual/debug only). Separately, the old 30/day new-lead cap
> in Step 2 had a live bug (its "days missed" math was `0` for any same-day
> rerun, so any cron cadence faster than once/day silently re-granted a fresh
> 30-lead budget every run) — removed entirely per Aditya's explicit rule that
> new-lead outreach should be unlimited, gated only by real dedup checks. See
> `DYLAN_AUDIT_2026-07-01_FULL.md` Round 11 for the full write-up and
> `tests/test_pipeline_logic.py::TestRound11PipelineRules` for the tests.

### Quo Contact Naming Convention (CRITICAL — never deviate)

```
firstName  = "Full Legal Name"          e.g. "Jane Doe"
lastName   = "LICENSE, Borough"         e.g. "RN, Brooklyn" | "CNA, Bronx"

Opt-out:
firstName  = "DO NOT MESSAGE - {name}"
lastName   = ""  (cleared)
```

**License codes:** RN · RNS · LPN · CNA · HHA
**Borough codes:** Bronx · Brooklyn · Manhattan · Queens · Staten Island · NY (default)

### Environment Variables

```env
CLAUDE_API_KEY=sk-ant-...
QUO_API_KEY=...
QUO_PHONE_NUMBER_ID=PNWtLBsgMe
GCP_PROJECT_ID=...                    # new, v3.0 — required for real-time email
GMAIL_PUBSUB_TOPIC=gmail-dylan-notify           # new, v3.0
GMAIL_PUBSUB_SUBSCRIPTION=gmail-dylan-notify-sub  # new, v3.0
```

Loaded from `~/Downloads/.env` (confirmed correct in code as of v3.0 — this
matches what the docs say, unlike the Gmail token path, which didn't; see §13).

### Key Invariants (unchanged, extended to email in v3.0)

- Nothing auto-sends — email replies are always drafts; SMS auto-sends only
  for the two hardcoded, pre-approved flows (intro, document checklist on
  YES) that existed before this project began; anything else is either a
  draft or a flag
- Opt-outs are permanent — phone added to optouts file AND Quo contact renamed
- Deduplication runs against live Quo contacts before every intro SMS
- Gmail reviewer is cumulative — reads ALL attachments AND all prior email
  from sender's full history; email general-inquiry replies also check
  Quo SMS history (new, v3.0)

---

## 13. WHAT WAS WRONG IN THE OLD DOCS (v1.0–v2.1) — CORRECTED IN v3.0

Recorded here so this doesn't happen silently again. Both were found by
reading the actual `.py` source files directly rather than trusting the
prior doc set:

1. **`08_TROUBLESHOOTING.md` and `02_SYSTEM_ARCHITECTURE.md` said the Quo
   API URL bug in `upgrade1_context_aware_messaging.py` was still open.**
   It was already fixed as of 2026-06-29 (v1.1). The docs were a full doc
   revision behind the code.
2. **The Gmail token path was inconsistent across files** —
   `master_gmail_reviewer.py` and `master_gmail_setup.py` both correctly
   used `~/Downloads/gmail_token.json`, but `upgrade1_context_aware_messaging.py`
   computed a different path (`~/Downloads/BlueLine/gmail_token.json`) —
   meaning Gmail history had been silently absent from every SMS
   re-engagement decision. Neither the old docs nor the code caught this
   until this audit. Fixed 2026-07-01.

**Standing instruction:** before telling a customer or Aditya what the
system does, check the source in `src/`, not just this doc set.

---

## 14. OTHER ACTIVE PROJECTS (context only — separate projects, separate chats)

- **BlueLine Staffing** — ongoing ops. Navy/teal palette. Calibri. Compliance, regulatory, biz dev.
- **Wealth Velocity** — YouTube channel. Personal finance. Navy/gold palette. Montserrat.
- **Peak Protocol** — Health/longevity YouTube. Obsidian/teal. Inter.
- **Godrej Emerald** — 2BHK property sale, Thane West. Active listing.
- **Indian Stock Portfolio** — Shelved per Aditya's instruction.

**Per Rule 0: none of these projects should touch Dylan/BlueLine automation
work. If a conversation in one of them drifts into Dylan territory, redirect
to this project.**

---

*This document is the single source of truth for the Dylan for Hire / SaaS Project Healthcare Recruitment work. Start every new session by referencing this. See `09_GO_LIVE_READINESS.md` for the active 2-week launch push.*
