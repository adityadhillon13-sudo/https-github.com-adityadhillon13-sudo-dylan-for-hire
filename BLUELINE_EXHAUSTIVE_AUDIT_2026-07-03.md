# BLUELINE STAFFING — EXHAUSTIVE OPERATIONAL AUDIT & RECAP
### Compiled 2026-07-03 · line-by-line review of every BlueLine doc + direct code/log verification
### Supersedes: `BLUELINE_RECAP_2026-07-03.md` (same-day, shallower pass)

---

## 0. SCOPE OF THIS PASS (honest accounting, not a rounded-up claim)

**Read in full:** all five `BLUELINE_*.md` docs (`MASTER_OPS`, `CANDIDATE_PIPELINE`, `COMMS_PLAYBOOK`, `TECH_CONFIG`, `CENTER_DIRECTORY`), BlueLine's own `CLAUDE.md`, both `Dylan_for_Hire_BlueLine_*.md` files, every audit-log entry embedded inside `BLUELINE_MASTER_OPS.md` (six dated audit sessions from 2026-06-30 through 2026-07-02), and the Dylan-for-Hire project's full `DYLAN_AUDIT_2026-07-01_FULL.md` audit trail insofar as it concerns the live BlueLine deployment (which is most of it — BlueLine is where nearly every real bug in that trail was actually found and fixed).

**Verified directly, not just read as a claim:** live `master_daily_agent.py` version header (says "Version: 2.5" in its own docstring while runtime logs print "v2.6" — a real, still-unresolved internal inconsistency), byte-identical sync between BlueLine's 7 pipeline files and the Dylan-for-Hire project's `src/` mirror (confirmed via `diff -q`, all identical), the actual purpose of `blueline_intake.py` (read directly — see §6), whether `master_candidate_file_consolidator.py` exists on this deployment (it does not), the real gap between BlueLine's own `tests/test_pipeline_logic.py` (16 tests) and the project's reference copy (~79 test functions, higher collected count), and the live tail of `cron_output.log` from earlier today, which surfaced a real, previously-undocumented bug (§7).

**Not verifiable from any Cowork/Claude Code session, regardless of how much is read:** whether `master_sms_poll_service.py` and `master_gmail_pubsub_listener.py` are actually running as background processes on your Mac right now. This is the single most-repeated open flag across every document in this audit — see §1.

---

## 1. TOP PRIORITY — VERIFY THIS BEFORE ANYTHING ELSE

**Run `launchctl list | grep blueline` on your actual Mac.**

Step 3 (SMS reply handling) was deliberately removed from the 9am daily cron on 2026-07-02 (Round 11), on the explicit assumption that `master_sms_poll_service.py` — a 90-second poll loop meant to run permanently via `launchd` — now covers it 24/7. This is not a minor detail: it means **if that service isn't actually running as a background process, real candidates texting "YES" or "STOP" right now get no automated reply of any kind**, because the old once-daily fallback was intentionally deleted, not left as a backup.

This exact question is raised, independently, in `09_GO_LIVE_READINESS.md` (Dylan-for-Hire project), `BLUELINE_MASTER_OPS.md` §3, and `BLUELINE_TECH_CONFIG.md` §4 — three separately-audited documents all converge on this one unresolved item. It has been flagged since at least 2026-07-02 and, as far as every document I read states, has never been confirmed either way.

---

## 2. WHERE THE REAL CODE AND DOCS LIVE

`~/Downloads/BlueLine/` is the **source of truth** for pipeline engineering code — this was made explicit policy on 2026-07-02 (Round 13) after two concurrent Claude sessions (this Cowork project's earlier work, and a separate Claude Code session) both had access to this folder with no visibility into each other, causing real silent drift. The rule now: fix/harden/improve **here first**, verify with tests (ideally a live run), only then sync to the Dylan-for-Hire project's `src/` (a reference mirror, not an independent place to invent pipeline logic).

**Files actually here, confirmed by direct listing (130 total, most are pitch-deck audio/video assets and generated `.pyc` caches, not operational):**

- `master_daily_agent.py` (v2.5 per its own docstring / v2.6 per runtime log — unresolved cosmetic mismatch, flagged since at least 2026-07-02, still present)
- `master_gmail_reviewer.py`, `master_gmail_setup.py`, `master_gmail_pubsub_listener.py`, `master_sms_poll_service.py`, `email_context_bridge.py`, `upgrade1_context_aware_messaging.py` — all confirmed byte-identical to the Dylan-for-Hire project's `src/` copies via direct diff
- `blueline_intake.py` — a standalone CSV pre-processing utility (see §6; previously flagged as unconfirmed purpose in `BLUELINE_TECH_CONFIG.md`, resolved here)
- Three backup files: `master_daily_agent.py.pre-v2.5-backup-2026-07-02`, `master_daily_agent_backup.py`, `master_gmail_reviewer.py.pre-v1.2-deploy-backup-2026-07-02`
- `tests/test_pipeline_logic.py` (only 16 test functions — see §8, this is a real, current gap)
- `CONFIDENTIAL_candidates.csv`, `.env`, `gmail_credentials.json`, `gmail_credentials_NEW.json` (dated Jul 2 — see §7), `gmail_token.json` (dated May 8, unchanged — see §7), `cron_output.log`
- The 5 `BLUELINE_*.md` docs plus `CLAUDE.md`, plus **a separate, stale copy** of an older `00_INDEX.md`...`08_TROUBLESHOOTING.md` doc set and `DYLAN_AUDIT_2026-07-01_FULL.md` — these belong to the Dylan-for-Hire project's doc lineage and are out of date relative to that project's own current copies (its `00_INDEX.md` is 474 lines; the copy sitting here is 106). Not part of BlueLine's own 5-doc governance set, but sitting in the same folder and worth cleaning up so a future session doesn't read the stale copy by mistake.
- **Not here, despite being referenced by `04_DAILY_OPERATIONS.md` Part 3C:** `master_candidate_file_consolidator.py` — exists only in the Dylan-for-Hire project's `src/`, never deployed. Running the documented command (`python3.11 master_candidate_file_consolidator.py --email ...`) will fail today.
- Also present, unrelated to BlueLine ops and likely misfiled: a `WV_EP006_cue_sheet.txt` and `WV_EP006_Assets/` folder (Wealth Velocity content, not BlueLine).

**Reference docs, all confirmed current as of their last audit pass:** `BLUELINE_MASTER_OPS.md` (v2.2), `BLUELINE_CANDIDATE_PIPELINE.md` (v2.2), `BLUELINE_COMMS_PLAYBOOK.md` (v2.2), `BLUELINE_TECH_CONFIG.md` (v2.2), `BLUELINE_CENTER_DIRECTORY.md` (v2.1) — all synced to `~/Desktop/BlueLine_Master_Docs/` per the daily audit task's own log.

---

## 3. THE PIPELINE, EXACTLY AS IT RUNS TODAY (not the legacy 0→3→1→2 model still described in a few older doc corners)

```
CONTINUOUS, 24/7, NOT ON CRON (both status UNCONFIRMED as running — see §1):
  master_sms_poll_service.py       ← Step 3 (SMS replies), EXCLUSIVE owner, every ~90s
  master_gmail_pubsub_listener.py  ← Step 0/5 (Gmail doc review + general inquiry), real-time via Pub/Sub push

DAILY CRON, 9:00 AM EST (America/New_York, DST-aware):
  master_daily_agent.py main():
    Step 1 → Re-engage stalled contacts (72hr window, lowered from 96h on 2026-07-02)
    DEDUP  → Live deduplication against Quo contacts
    Step 2 → New lead intro SMS — UNLIMITED per run (30/day cap + 150 catchup removed
             entirely 2026-07-02, per your explicit rule; gated by real dedup checks
             and a rolling 75-messages/trailing-24h safety cap with duplicate-send
             fingerprinting, not a calendar-day count)

MANUAL / ON-DEMAND (backstop, in case the listener above isn't running):
  master_gmail_reviewer.py  ← same Step 0/5 logic, run by hand when needed
```

**This is a real architecture change from what several older doc corners still describe** (BlueLine's own `CLAUDE.md` had — until Round 14's doc-consistency pass — some stale references to the old 96h window and 30/day cap; three docs total needed correcting for this). If you're reading any BlueLine reference material that says "Step 3 runs at 9am" or "96-hour stall window" or "30 leads/day," it predates 2026-07-02 and is wrong.

### Step 3 — 5-branch reply classifier (unchanged logic, just runs continuously now instead of at 9am)
Evaluated top-down, first match wins: **(1) Opt-out** keywords → permanent removal · **(2) Docs-sent** keywords ("i sent," "already emailed," "did you get," etc.) → flagged for human review, checklist never re-sent · **(3) Update-request** keywords ("any news," "still waiting," etc.) → flagged, no auto-response · **(4) Interest** keywords ("yes," "interested," "asap," etc.) → gated by `master_checklist_sent.txt`, so the document checklist fires exactly once per phone number, ever · **(5) Anything else** → flagged for human review. The generic tokens that caused the original repeat-blast incidents (Joyelette Miller 4x, Torri Allen) — "ok," "okay," "send," "info," "i'm" — are explicitly excluded from the interest-keyword set and must never be added back.

### Step 1 — Re-engagement (72-hour window)
Calls `get_context_aware_sms()` (Claude Haiku, reads last 4 days of Quo + Gmail history) for every contact past the stall window. Returns a personalized message → sent. Returns `None` → skipped entirely, no fallback text. **There is no separate "final message" and no permanent-skip list** — a stalled contact that keeps getting evaluated-and-skipped just keeps getting re-evaluated by Claude on every run, indefinitely, until they reply or opt out. This is confirmed by direct grep: `NO_RESPONSE_FINAL` and `GENERIC_FOLLOWUP` do not exist anywhere in the current codebase, despite being referenced as if real in BlueLine's own `CLAUDE.md` (corrected in the Round 14 doc-consistency pass) and in the older `Dylan_for_Hire_BlueLine_Technical_Reference.md`. **This is an open product decision for you, not a bug** — add a real cutoff, or accept silent-forever re-evaluation as fine given how cheap one Haiku call every ~3 days is.

### Step 2 — New leads
Every eligible CSV row processed every run (no cap), gated by: opt-out check, blocked-number check, 3-pass dedup (phone / full name / first name) against live Quo contacts, SHA-256 message fingerprinting with a 24h cooldown (prevents any identical message reaching the same phone twice), and the rolling 75/24h safety cap (auto-resumes as older sends age out — no manual re-enable needed).

---

## 4. CONTACT NAMING, TEMPLATES, AND CENTER DIRECTORY — REFERENCE DATA (unlikely to be wrong, worth having in one place)

**Quo naming convention (never deviate):** `firstName` = candidate's full legal name · `lastName` = `"{LICENSE}, {BoroughAbbr}"` (e.g. `"RN, Bklyn"`). Opt-out: `firstName` = `"DO NOT MESSAGE - {name}"`, `lastName` cleared. License codes: RN/RNS/LPN/CNA/HHA. Borough abbreviations: Bx/Bklyn/Mhtn/Qns/SI, default "NY."

**Templates currently live** (verified against `BLUELINE_COMMS_PLAYBOOK.md`, cross-checked against the Dylan-project docs — both agree): `DYLAN_INTRO` (first CSV contact, includes STOP language since BUG-16's fix), `INDEED_INTRO` (first contact with an Indeed applicant — verbatim text confirmed still matches real sent messages as of the "Resume screening and intro message" session), `DOCUMENT_CHECKLIST_MSG`/`RATE_AND_CENTERS_MESSAGE` (fires once per phone on first genuine interest reply, no emoji since BUG-18's fix), and the context-aware re-engagement fallback (same text used for both the Claude-unavailable fallback and — per BlueLine's docs — the only re-engagement message that currently exists at all).

**Center directory:** 34 active centers — Bronx (14), Brooklyn (6), Queens (13), Long Island (1). Full contact/rate detail lives in `BLUELINE_CENTER_DIRECTORY.md`; known outstanding data issues (unchanged, still open, genuinely need your input rather than a code fix): Rebekah Rehab email discrepancy (use `scormack@rebekahrehab.org`, not the contract sheet's `SCORMICK@`), Grandell's CNA/LPN rates listed as unexplained multipliers (13.3202 / 24.6962 — likely a billing factor, not a flat rate, unconfirmed), The Plaza Nursing rates marked TBC, 16 centers still missing a contact's first name, and Debbie Umrao-Paray's triple-center portfolio (Forest View/Cliffside/Woodcrest) needs a decision on whether that's one billing relationship or three.

**Rate ranges across all 34 centers:** CNA $29–$32.75/hr · LPN $46–$59/hr · RN $55–$75.50/hr · RNS $65–$83/hr · HHA $24.50–$27.50/hr.

---

## 5. THE FULL AUDIT HISTORY, AS RECORDED INSIDE `BLUELINE_MASTER_OPS.md` ITSELF

BlueLine's own docs carry six dated, appended audit-session logs (separate from, but describing the same underlying work as, the Dylan-for-Hire project's `DYLAN_AUDIT_2026-07-01_FULL.md`):

- **2026-06-30, session 1:** fixed inverted section numbering in `COMMS_PLAYBOOK`, corrected a Bronx center count (13→14 actual entries), fixed the Step-2-doesn't-use-context-aware-messaging documentation error, flagged (then resolved) a missing TCPA opt-out line in `DYLAN_INTRO`.
- **2026-06-30, session 2:** confirmed BUG-15 fixed in code (tightened `INTEREST_KEYWORDS`, added `DOCS_SENT_KEYWORDS`/`UPDATE_REQUEST_KEYWORDS`/`STATE_CHECKLIST_SENT` guard) — traced the Joyelette Miller repeat-blast incident to a pre-fix run, confirmed no recurrence. 4 live Quo replies sent with your approval.
- **2026-06-30, session 3 (bug sync migration):** root-caused and fully documented the repeat-blast incidents; backfilled `master_checklist_sent.txt` with 18 phones already past the checklist stage; established the standing rule that agent code changes sync to BlueLine docs in the same session, no prompting needed.
- **2026-07-01 (light-touch):** no material drift found — the prior day's three sessions had already resolved everything live.
- **2026-07-02 (NOT light-touch — real drift found):** a direct diff against live code found the production agent had jumped from documented v2.3 to v2.6 (Round 11) in two days with real architecture changes none of the 5 BlueLine docs reflected — Step 3 off-cron, 96h→72h, cap removed, 3 new hardening invariants. All 5 docs updated same session. This is also where the "is the 24/7 layer actually running" flag first appears in this doc lineage, and where the existence of the Dylan-for-Hire reconciliation project (the parallel `00_INDEX.md`.../`DYLAN_AUDIT...` files sitting in the same folder) is explicitly noted as the source of that day's changes.

**Compliance flags carried forward across every one of these sessions, still open, requiring your input, not a code fix:** the Fort Tryon/Riverside borough uncertainty (both centers lack street addresses on file), the Grandell billing-multiplier question, Plaza Nursing's TBC rates, and 16 centers with an unknown contact first name.

---

## 6. RESOLVED THIS PASS: `blueline_intake.py`'s PURPOSE

`BLUELINE_TECH_CONFIG.md` has carried a `[VERIFY: purpose still unconfirmed]` flag on this file. Read directly: it's a standalone **CSV intake cleaner**, meant to be run manually *before* `master_daily_agent.py` on days you have a fresh Indeed export or new lead batch. It reads a dropped-in `~/Downloads/BlueLine/new_leads.csv`, normalizes phone/name fields, validates the role against a `VALID_ROLES` set (`CNA`, `LPN`, `RN`, `CHHA`, `HHA`, `MA`, `CMA` — note `MA`/`CMA` appear here but nowhere else in any BlueLine or Dylan doc; worth confirming whether BlueLine actually places Medical Assistants or this is leftover/aspirational scope), and appends clean rows onto `CONFIDENTIAL_candidates.csv`. It is not imported or called by any other script — it's a manual pre-processing step, not part of the automated daily pipeline. Recommend closing this flag out in `BLUELINE_TECH_CONFIG.md` with this description.

---

## 7. NEW FINDINGS FROM THIS PASS — NOT IN ANY PRIOR AUDIT ROUND

These came from reading the live tail of `~/Downloads/BlueLine/cron_output.log` directly (from earlier today), not from any doc:

1. **The Gmail document reviewer is processing known center/facility contacts as if they were candidates.** Real entries in today's log: `dp@fvrehab.com` (Debbie Umrao-Paray — Forest View/Cliffside/Woodcrest, a real, active center contact per `BLUELINE_CENTER_DIRECTORY.md`), `mmeyer@dbnrc.com` (Downtown Brooklyn Nursing), `mhaynes@bgrehabcare.com` (Beach Gardens), `nsathi@theriversiderehab.com` (Riverside Rehabilitation) all produced `DOC DRAFT SAVED ... (license: None)` output and attempted `PIPELINE:DOCS_INCOMPLETE` Quo stage pushes — nonsensical for people who run nursing homes, not people applying to work at one. The system correctly failed to push the bogus stage tag each time (no Quo contact match for a center email), so nothing corrupted the dashboard, but real Claude Vision calls and doc-review drafts are being wasted on every center email that happens to have any attachment (a resume PDF forwarded from a candidate, a signed contract, anything). `is_system_or_non_candidate_email()` already excludes BlueLine's own address — it doesn't yet exclude the ~30 known center domains from `BLUELINE_CENTER_DIRECTORY.md`. Cheap fix, real and current waste until it's made.

2. **A real Claude Vision failure from a MIME-type mismatch.** One of `mmeyer@dbnrc.com`'s attachments failed with `400 Bad Request: ... the image was specified using the image/png media type, but the image appears to be a image/jpeg image`. The code trusts the attachment's declared content-type rather than checking actual file bytes. This is a real, silent failure mode that could just as easily happen to a genuine candidate's document — it would fail the same way, log a generic "Claude returned no analysis," and give no visible signal that a document was lost to a fixable type mismatch rather than genuinely missing.

3. **`gmail_credentials_NEW.json` (dated July 2, the same day the dedicated `dylan-for-hire` GCP project was created) sits alongside the original `gmail_credentials.json` (May 8), but `gmail_token.json` is still dated May 8** — meaning whatever's currently authenticating was generated under the old credentials, before the new GCP project existed. This looks like an unfinished credential migration, not a stale leftover, but that's not confirmed either way from here. Worth a direct check on your Mac of which credentials file `master_gmail_reviewer.py`/`master_gmail_pubsub_listener.py` is actually loading against, especially since Round 9's "wrong-GCP-project Gmail credentials" saga is exactly this class of problem.

---

## 8. THE TEST-SUITE GAP — A REAL, CURRENT VERIFICATION PROBLEM

`~/Downloads/BlueLine/tests/test_pipeline_logic.py` — the test file sitting next to the code that's actually running on your Mac — has **16** `def test_` functions. The Dylan-for-Hire project's `src/tests/test_pipeline_logic.py` — the reference copy — has roughly **79** `def test_` blocks, and a collected-pytest count that's grown 69→75→100→112→118→120→124→130→135→138 across the audit rounds. These two files are not the same file, and unlike the 7 pipeline `.py` files (which `scripts/sync_check.sh` actively keeps in sync, confirmed byte-identical today), the test suite is **not** one of the tracked files.

**What this means in practice:** every "N/N passing" claim in `09_GO_LIVE_READINESS.md`'s verification log, and every "verified with tests" note throughout `DYLAN_AUDIT_2026-07-01_FULL.md`, is true of the project's reference copy — it has not been re-confirmed against whatever test file would actually run if someone `cd`'d into `~/Downloads/BlueLine/tests/` and ran `pytest`, which is literally what several of this project's own docs instruct. Recommend copying the current `tests/` folder (both `test_pipeline_logic.py` and `conftest.py`) from the Dylan-for-Hire project's `src/` sibling into `~/Downloads/BlueLine/tests/`, and adding both files to `sync_check.sh`'s tracked list going forward so this can't silently re-drift.

---

## 9. KEY INVARIANTS — STILL TRUE, WORTH RESTATING PLAINLY

Nothing sends automatically except the two pre-approved, hardcoded SMS flows that predate this whole audit effort (intro SMS, document-checklist-on-YES) — every email reply and every general-inquiry SMS is a draft/decision a human confirms. Opt-outs are permanent (phone in `master_permanent_optouts.txt` + Quo contact renamed) and checked fresh from disk at send time by `send_sms()` itself, independent of whatever the calling step already checked (hardened 2026-07-02 specifically so no future code path can bypass this even with a bug). A process lock prevents two overlapping runs from both deciding to send. A created-but-unmessaged Quo contact is flagged for human review rather than silently lost forever (previously a real gap — a failed SMS send used to make a candidate permanently invisible to every future run, since the existing contact would look like an already-handled duplicate).

---

## 10. RECOMMENDED IMMEDIATE ACTIONS, IN ORDER

1. **Confirm both 24/7 services are actually running** — `launchctl list | grep blueline`. This is the one item that could mean real candidates are getting no reply right now.
2. Add the ~30 known center-contact email domains (from `BLUELINE_CENTER_DIRECTORY.md`) to `is_system_or_non_candidate_email()`'s exclusion list — stops real, current wasted Vision calls and bogus stage-tag attempts.
3. Fix or at least catch-and-retry the image-MIME-type mismatch in the Gmail Vision call path — a genuine candidate document could silently fail the same way.
4. Confirm which Gmail credentials file (`gmail_credentials.json` vs. `gmail_credentials_NEW.json`) is actually in use, and finish or abandon whatever migration `gmail_credentials_NEW.json` represents.
5. Copy the current, 138-test `tests/` folder from the Dylan-for-Hire project into `~/Downloads/BlueLine/tests/`, and add it to `sync_check.sh`'s tracked files.
6. Deploy `master_candidate_file_consolidator.py` here if you plan to use the Submission-Ready workflow described in `04_DAILY_OPERATIONS.md` Part 3C — it will fail today as documented.
7. Decide the `NO_RESPONSE_FINAL`/permanent-skip question for stalled contacts (§3).
8. Resolve the remaining `BLUELINE_CENTER_DIRECTORY.md` data gaps that need your input, not a fix: Grandell billing format, Plaza Nursing TBC rates, Fort Tryon/Riverside borough confirmation, 16 missing first names.
9. Clean up the stale Dylan-for-Hire doc copies sitting in this folder (`00_INDEX.md` through `08_TROUBLESHOOTING.md`, `DYLAN_AUDIT_2026-07-01_FULL.md`) so they aren't mistaken for current by a future session working here.
