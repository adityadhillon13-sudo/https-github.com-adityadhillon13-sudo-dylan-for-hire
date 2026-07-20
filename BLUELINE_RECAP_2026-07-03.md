
# BLUELINE — OPERATIONAL RECAP ACROSS ALL COWORK SESSIONS
### Compiled 2026-07-03 · for the new "BlueLine" session

---

## WHY THIS DOCUMENT EXISTS

This is the operational half of the split — everything about BlueLine Staffing's actual live production system: the daily agent, the candidate/center email and SMS pipeline, and the two Cowork dashboards. The companion doc, `DYLAN_RECAP_2026-07-03.md`, covers the SaaS-product/sales side (Dylan for Hire) separately. Hand this doc to your new "BlueLine" session.

---

## 1. WHERE THE REAL CODE LIVES

**`~/Downloads/BlueLine/` is the source of truth.** Everything here runs against your real Gmail and Quo:
- `master_daily_agent.py` (v2.6) — daily cron, 9am EST
- `master_gmail_reviewer.py` — candidate email + doc review (just fixed twice today, see Section 4)
- `email_context_bridge.py` — cross-channel (email ↔ Quo) contact matching
- `master_gmail_pubsub_listener.py` + `master_sms_poll_service.py` — the intended 24/7 real-time reply layer
- `master_gmail_setup.py`, state files (`master_processed_*.txt`, `master_checklist_sent.txt`, `master_needs_human_review.txt`, cron logs)

A separate copy lives at `~/Claude/Projects/Dylan for Hire.../src/` — that's a **mirror only**, kept in sync via `scripts/sync_check.sh`. Never edit that copy directly; it should always flow FROM BlueLine.

Reference docs: `BLUELINE_MASTER_OPS.md`, `BLUELINE_CANDIDATE_PIPELINE.md`, `BLUELINE_COMMS_PLAYBOOK.md`, `BLUELINE_TECH_CONFIG.md`, `BLUELINE_CENTER_DIRECTORY.md` — all synced to `~/Desktop/BlueLine_Master_Docs/` by a daily audit task.

Cowork Artifacts: **Dylan Master Dashboard** (renamed today from "Blueline Pipeline Dashboard" — parent/primary view) and **BlueLine Live Dashboard** (inbox/reply monitor).

---

## 2. TOP PRIORITY — VERIFY THIS FIRST

**Are `master_sms_poll_service.py` and `master_gmail_pubsub_listener.py` actually running as background processes on your Mac?**

Step 3 (SMS reply handling) was deliberately pulled off the 9am daily cron on the assumption these two services now cover it 24/7. A dedicated audit session flagged this as unconfirmed and it's still unresolved: **if these aren't actually running, Step 3 currently has no active handler at all**, meaning real candidates texting in get no automated reply. This is the single highest-risk open item across every session reviewed. Check it directly — `ps aux | grep master_sms_poll` / `ps aux | grep master_gmail_pubsub` or however you'd confirm a background process on your Mac.

---

## 3. WHAT'S CONFIRMED LIVE VS. STILL UNCERTAIN

**Confirmed running, real data:**
- Daily agent v2.6 — Step 1 (re-engage stalled contacts), Step 2 (new leads from CSV + dedup). Re-engagement window is now 72h (was 96h). 30/day new-lead send cap was removed entirely.
- Quo registry: **3,798 real contacts** as of this morning.
- `master_gmail_reviewer.py` — now finding real candidate emails again as of today's fix (Section 4).

**Built, not confirmed running:**
- The poll/listener 24/7 layer (Section 2 — verify this).
- Email-opt-out → SMS-opt-out auto-sync. Known, disclosed gap. Not fixed.

**Real product gap, needs your call:**
- `step1_reengage_stalled()` has no permanent-skip path — a non-responsive contact gets re-evaluated by Claude forever, with no `NO_RESPONSE_FINAL` cutoff, even though three docs (including BlueLine's own `CLAUDE.md`) claimed one exists. Decide: add one, or is silent-forever acceptable?

**Recent drift caught (already resolved):** a scheduled audit found `master_daily_agent.py` had silently jumped from documented v2.3 to v2.6 with real architecture changes (Step 3 off-cron, 96h→72h, 30/day cap removed, two long-standing bugs fixed) — all now reflected in the docs. Also found and fixed: 7 real opt-out keywords the code already handled that the playbook didn't list, and one stale emoji in a template (your rule is no emoji in SMS).

---

## 4. TODAY'S SESSION (2026-07-03) — DASHBOARD + PIPELINE FIXES

This is everything worked on in this specific conversation:

- Created/cleaned up Gmail drafts for dropped candidate inquiries (Nicholas Samuel, Lakaiya Smith); deleted a stale Sarina Escalera draft.
- Made **Document & Onboarding Stage** live/fast on both dashboards — previously required a full 76-page Quo scan to populate; now joins fast activity data against a phone index built from the last Full Scan.
- Added **phone-first, then name-fallback** contact resolution to `email_context_bridge.py` — closes the exact gap that caused the Sarina Escalera mismatch (BUG-21).
- Redesigned **Total Leads**: manual monthly baseline entry (asked once a month via an in-page modal) instead of deriving it from a full scan, decoupling it from the expensive scan entirely. Full Scan staleness widened to a rolling 30 days.
- **Root-caused and fixed: Full Scan was truncating at 950 of 3,785+ contacts.** Confirmed by manually paging the live Quo API by hand past that exact point — the API itself was fine there. The real cause: Quo's own pagination "no more pages" signal fires early sometimes (a documented, recurring Quo bug — this happened once before at 200 contacts too). Fixed with a confirm-before-trusting-end-of-list check. Verified live.
- Fixed **"Refine Silent List" hanging forever at "0/13"** — no timeout existed anywhere in the batch-processing chain, so one stuck request froze the whole batch. Added a timeout.
- **Caught my own regression from that fix:** the 25s timeout was too aggressive for the Live Dashboard's LLM-based draft-generation calls (email classification, SMS draft writing), which legitimately take longer — this is exactly why drafts started "failing" right after. Raised to 60s specifically for those two call sites, verified with a real test.
- **Root-caused why Doc & Onboarding Stage / Submission Readiness showed all zeros:** `master_gmail_reviewer.py` required `is:unread` in its Gmail query, but you read your inbox in the normal course of work — so candidate emails were almost always already read by the time the script ran. Dropped that filter; dedup is handled separately and safely via `processed_ids`.
- **Caught immediately after that fix landed:** BlueLine's own address (`info@bluelinestaffing.com`) was never explicitly excluded from "is this a candidate" detection. Once Sent mail became visible (no more `is:unread` gate), one of your own sent threads got processed as if you were a candidate, producing a bogus doc draft. Fixed — `BLUELINE_EMAIL` is now explicitly excluded, verified directly against the real function.
- Added a new **Submission Readiness Check** panel — cross-references "docs complete + onboarding returned" candidates (the existing stage tag, no new doc-checking logic) against real Sent-mail submission history, splitting into "ready, no draft sent yet" vs. "ready, already submitted."
- Renamed the dashboard's in-page title to **"Dylan Master Dashboard"** and repositioned it as the primary view (Live Dashboard is the companion inbox monitor). Note: the outer Cowork artifact-list label still shows the old name — no tool available to change that part.

**Where things stand right now:** you re-ran `master_gmail_reviewer.py` this morning after both fixes — it went from finding 0 candidate emails to 89, confirming the `is:unread` diagnosis was correct. It hit its 10-document-per-sender cap while processing the (now-excluded) BlueLine address. Re-run it once more to process the real candidates in that batch of 89, then refresh the dashboards.

---

## 5. RECURRING AUTOMATION — WHAT'S WATCHING THIS SYSTEM

- **"Blueline live monitor" / "...continuation"** (runs most frequently): 24hr rolling Quo + Gmail check, producing a punch list of who needs a reply with proposed drafts. Never auto-sends.
- **"Blueline audit sync daily"**: daily doc-vs-code audit. This is what caught the v2.3→v2.6 drift above.
- **"Blueline dylan drift check"** / manual `scripts/sync_check.sh` runs: confirms the BlueLine ↔ Dylan-for-Hire `src/` mirror hasn't diverged. Two real bugs were found and fixed in the script itself today (it always printed "Drift was found" even after a successful `--apply`, and it called `python3` which resolves to a version without `pytest` installed — fixed to expect `python3.11`).

---

## 6. THE ONE DEPENDENCY ON THE "DYLAN" SIDE

The Dylan for Hire pitch deck's proof numbers all come from BlueLine's real data (37 nurses, payroll, billing, etc.). Whoever owns `scripts/sync_check.sh` going forward should keep running it periodically so BlueLine's live code and the Dylan-for-Hire reference mirror don't silently drift again — it's already happened more than once.
