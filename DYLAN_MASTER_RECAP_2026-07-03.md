
# DYLAN / BLUELINE — MASTER RECAP ACROSS ALL COWORK SESSIONS
### Compiled 2026-07-03 · for splitting into two clean projects: "Dylan" and "BlueLine"

---

## WHY THIS DOCUMENT EXISTS

This project ("Dylan for Hire — SaaS Product Healthcare Recruitment") has been doing double duty: building the **Dylan for Hire SaaS product** (the thing you sell to other agencies) AND actively debugging **BlueLine's own live production system** (the thing Dylan is proof-of-concept'd on). That's the mess you're solving by splitting into two sessions. This doc pulls together the substance from every session across both threads — sampled from 107 local sessions, filtering out the repetitive scheduled-task noise — so you can read this once and hand each new session the right half.

**Read this, then:** open a new Cowork session titled **"Dylan"** for the SaaS-product/sales side, and one titled **"BlueLine"** for the live operational side. The recommended split is in Section 6.

---

## 1. WHERE EVERYTHING PHYSICALLY LIVES RIGHT NOW

| Location | What's there | Status |
|---|---|---|
| `~/Downloads/BlueLine/` | **Source of truth** for the live production agent — `master_daily_agent.py`, `master_gmail_reviewer.py`, `email_context_bridge.py`, `master_gmail_pubsub_listener.py`, `master_sms_poll_service.py`, `master_gmail_setup.py`, cron logs, state files (`master_processed_*.txt`, `master_checklist_sent.txt`, etc.) | **Live, running against real Gmail/Quo** |
| `~/Claude/Projects/Dylan for Hire.../src/` | A **mirrored copy** of BlueLine's pipeline files, kept in sync via `scripts/sync_check.sh` | Reference copy only — never touched directly, always synced FROM BlueLine |
| `~/Downloads/DylanForHire/` | 10 numbered docs (`DFH_00` through `DFH_08` + a session bootstrap file) covering product, architecture, pipeline logic, comms templates, setup, daily ops, center directory, sales/outreach | Built in the "Dylan for hire project migration" session — **this is the more complete doc set** |
| This project's root (`~/Downloads/`) | `SAAS_PROJECT_HEALTHCARE_RECRUITMENT_MASTER_CONTEXT.md` was renamed/split into `Dylan_for_Hire_Master_Context.md` | **Flagged unresolved:** two parallel doc sets now exist (this one + the DFH_00-08 set above) and nothing has reconciled them yet — see Section 3 |
| Cowork Artifacts | `Dylan Master Dashboard` (formerly "Blueline Pipeline Dashboard" — renamed today) and `Blueline Live Dashboard` | Both live, both actively fixed this session (see Section 5) |
| Project folder | Pitch deck (`dylan_for_hire_pitch_deck.html`), architecture doc (`dylan_for_hire_architecture.html`) | Both pitch-ready per the file-migration session's assessment, two small known issues (Section 3) |

---

## 2. WHAT'S ACTUALLY LIVE VS. NOT (be honest with yourself here)

**Confirmed running against real data:**
- `master_daily_agent.py` v2.6 — daily cron, 9am EST. Step 1 (re-engage stalled), Step 2 (new leads from CSV), dedup. Step 3 (SMS replies) was **pulled off this cron entirely** and handed to a separate poll service.
- `master_gmail_reviewer.py` — doc review + candidate email handling. Just fixed today (see Section 5) — was silently finding 0 candidate emails for an unknown period because of an `is:unread` gate mismatched to your actual workflow.
- Quo contact registry: **3,798 real contacts** as of this morning's run (3,785 baseline + growth).

**Built but NOT confirmed running (flagged repeatedly across sessions, never resolved):**
- `master_sms_poll_service.py` and `master_gmail_pubsub_listener.py` — the 24/7 real-time layer meant to replace the old once-daily cron for Step 3. **A BlueLine audit session explicitly flagged this as the highest-priority open item**: if these aren't actually running as background services, Step 3 (SMS reply handling) currently has no active handler at all, because it was removed from the daily cron on the assumption the poll service covers it. **You need to verify this directly — nobody has confirmed it either way.**
- Email-opt-out → SMS-opt-out auto-sync — disclosed as a known gap in `09_GO_LIVE_READINESS.md`, not fixed.
- Hepatitis B / flu vaccine doc fields — code and internal docs updated, but **the customer-facing product overview doc was deliberately left unchanged** because this hasn't been verified against a real submitted document yet.

**Go-live target:** 2026-07-15, per `09_GO_LIVE_READINESS.md` (written in the "Dylan email autoresponder setup" session). That doc has a 🟢verified / 🟡built-not-tested / 🔴gap breakdown — read it before that date.

---

## 3. OPEN ITEMS THAT NEED YOUR DECISION (nobody could resolve these without you)

These surfaced across multiple sessions and are all still open as of today:

1. **🔴 Security: a real ElevenLabs API key was committed in plaintext** into git history (`02_SYSTEM_ARCHITECTURE.md`, baseline commit `3e936f5`). The working file was redacted, but the key is still recoverable from git history. Either rotate the key on ElevenLabs (simpler) or do a destructive history rewrite. **Nobody has done either yet.**

2. **Two parallel Dylan doc sets exist and haven't been reconciled:** `Dylan_for_Hire_Master_Context.md` (this project's root) vs. the more complete `~/Downloads/DylanForHire/DFH_00...08` set. A scheduled audit flagged this as `[DECISION NEEDED]` and it's still open. **When you start the new "Dylan" session, pick one as canonical and retire the other** — this alone will remove a lot of the "messy" feeling.

3. **No permanent-skip path for stalled contacts.** The real `step1_reengage_stalled()` code will keep asking Claude to re-evaluate a non-responsive contact forever — there's no `NO_RESPONSE_FINAL` cutoff in the actual code, even though three docs (including BlueLine's own `CLAUDE.md`) claimed one exists. Decide: do you want one added, or is silent-forever acceptable?

4. **Are the poll/listener services actually running?** (repeated from Section 2 — this is the single most operationally important unanswered question right now.)

5. **Pitch deck / architecture doc small fixes:** a branding miss on slide 6 (said "BlueLine" instead of "Dylan for Hire" — already fixed), and the CPP calculator in the architecture doc labels pricing as "$800/mo Starter / $1,500/mo Professional," which doesn't cleanly match the real pricing structure ($1,500 one-time setup + $750/month retainer). Worth aligning before the next prospect sees it.

6. **BlueLine can't be physically separated from this project by Claude alone.** A prior session tried and hit a wall: "I have no way to switch to or write into a separate 'BlueLine' Cowork project from this session — that's a UI action on your end." **This is exactly what you're doing right now by creating the two new sessions** — once you do, tell whichever session is "BlueLine" to pull the live files in, since they're real files sitting in `~/Downloads/BlueLine/` already.

---

## 4. RECURRING AUTOMATION — WHAT THESE SCHEDULED TASKS ACTUALLY DO

You have several scheduled tasks running that generated most of the 107 sessions. Quick reference so you know what each one is for:

- **"Blueline live monitor" / "...continuation"** (by far the most frequent — dozens of runs): the 24hr rolling check of Quo + Gmail, producing a punch list of who needs a reply, with proposed drafts. Never auto-sends. This is the thing the Live Dashboard visualizes.
- **"Dylan audit sync daily"** and **"Blueline audit sync daily"**: daily doc-vs-code audits. These have caught real things — e.g. one caught `master_daily_agent.py` silently advancing from v2.3 to v2.6 with undocumented architecture changes (Step 3 moved off cron, 96h→72h window, 30/day cap removed).
- **"Wv audit sync daily" / "Wv master docs sync" / "Aditya master docs audit daily"**: **not Dylan/BlueLine** — these are Wealth Velocity and your master Claude-instructions docs. Irrelevant to the split you're doing now.

---

## 5. THIS SESSION'S WORK (today, 2026-07-03 — the most recent thread)

Everything below happened in *this* conversation, most recent and most directly relevant to the dashboards you're using right now:

- Created/deleted Gmail drafts for dropped candidate inquiries (Nicholas Samuel, Lakaiya Smith); cleaned up a stale Sarina Escalera draft.
- Made **Document & Onboarding Stage** live/fast on both dashboards (previously required a full 76-page Quo scan; now joins against fast activity data via a phone index).
- Added **phone-first, then name-fallback** contact resolution to `email_context_bridge.py` (closes a real gap — Sarina Escalera-type mismatches).
- Redesigned the **Total Leads** tracking: manual monthly baseline entry instead of a full-scan-derived number, plus rolling 30-day Full Scan staleness.
- Fixed a real, root-caused bug: Full Scan was truncating at 950 contacts on a workspace with 3,785+ — Quo's own pagination "no more pages" signal was firing early (a documented recurring Quo bug); fixed with a confirmation-retry mechanism, verified against the live API by hand.
- Fixed "Refine Silent List" hanging forever at "0/13" — no timeout existed anywhere in the batch-processing chain; added one, then had to re-tune it (see next point).
- **Self-inflicted regression, caught and fixed same session:** the timeout fix above was too aggressive (25s) for the Live Dashboard's LLM-based draft-generation calls, which legitimately take longer — this is exactly why drafts started "failing." Raised to 60s specifically for those call sites.
- Root-caused why Doc & Onboarding Stage / Submission Readiness showed zero: `master_gmail_reviewer.py` required `is:unread`, but real-world usage means candidate emails are read before the script ever runs. Dropped that filter (dedup is already handled separately via `processed_ids`).
- Caught a second bug the moment the above fix landed: BlueLine's own address (`info@bluelinestaffing.com`) wasn't excluded from "candidate" detection, so it got processed as if it were a candidate once Sent mail became visible. Fixed by excluding `BLUELINE_EMAIL` explicitly.
- Added a new **Submission Readiness Check** panel to the (renamed) Dylan Master Dashboard — cross-references "docs complete + onboarding returned" candidates against real Sent-mail submission history, split into "ready, no draft yet" vs. "ready, already submitted."
- Renamed "Blueline Pipeline Dashboard" → **"Dylan Master Dashboard"** (in-page title/H1 only — the outer Cowork artifact-list label couldn't be changed through available tools, still shows the old name there).

---

## 6. RECOMMENDED SPLIT FOR YOUR TWO NEW SESSIONS

**"BlueLine" session — operational, live, real candidates/centers:**
- `~/Downloads/BlueLine/` (the actual production code — source of truth)
- The two Cowork dashboards (Dylan Master Dashboard + BlueLine Live Dashboard)
- `BLUELINE_MASTER_OPS.md`, `BLUELINE_CANDIDATE_PIPELINE.md`, `BLUELINE_COMMS_PLAYBOOK.md`, `BLUELINE_TECH_CONFIG.md`, `BLUELINE_CENTER_DIRECTORY.md`
- Day-to-day: is the daily agent running clean, are candidates getting replies, is the doc pipeline tagging people correctly, dashboard bugs

**"Dylan" session — the SaaS product you're selling:**
- `~/Downloads/DylanForHire/` (recommend making this canonical over the root master context doc — it's more complete)
- Pitch deck, architecture doc, LinkedIn sequence, discovery call script, Make.com scenario specs, Calendly/Gmail setup guides
- The client-intake/adapter spec (`10_CLIENT_INTAKE_AND_ADAPTER_SPEC.md`) — this is what makes Dylan sellable to agencies other than BlueLine
- Sales funnel, pricing, revenue path, outreach targets

**The dependency to keep in mind:** Dylan's proof-of-concept numbers (the ones in the pitch deck) come FROM BlueLine's real data. The two aren't fully independent — whichever session ends up owning `scripts/sync_check.sh` should keep running it periodically so the two never silently drift the way `master_gmail_reviewer.py` already has, more than once.

---

## 7. THE ONE THING TO DO BEFORE ANYTHING ELSE

Verify whether `master_sms_poll_service.py` and `master_gmail_pubsub_listener.py` are actually running as background processes on your Mac (Section 2/3, item 4). This has been flagged as unconfirmed across at least two separate sessions and it's the highest-risk unknown — if they're not running, real candidates texting in are getting no reply at all right now.
