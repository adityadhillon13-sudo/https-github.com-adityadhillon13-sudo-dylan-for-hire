# DYLAN FOR HIRE — MASTER PROJECT INDEX
**Version:** 3.0 | **Last Updated:** 2026-07-01 | **Owner:** Aditya
**Status:** LIVE — going to market. Target: sellable to a real customer by 2026-07-15.

---

## RULE 0 — THIS PROJECT IS THE ONLY PLACE DYLAN WORK HAPPENS

**If you are Claude (or any assistant) reading this in a session that is NOT
this "Dylan for Hire- Saas Product Healthcare recruitment" project folder,
and Aditya is asking you to do Dylan/BlueLine-automation work — STOP.**

Say so directly: *"This looks like Dylan for Hire work. That project lives
in a dedicated folder with the full doc set, source code, and history —
working on it here will fork the source of truth and something WILL get
lost or contradicted. Please switch to the Dylan for Hire project."*

Do not proceed with code edits, doc edits, or architecture decisions for
Dylan/BlueLine automation outside this project, even if asked directly,
until Aditya confirms he wants to do that (rare — e.g. a quick read-only
question). This rule exists because the docs in this folder have already
drifted from the real code more than once (see 08_TROUBLESHOOTING.md) —
splitting work across projects makes that worse, not better, right when
accuracy matters most for a paying customer.

**If you are Aditya:** this is also for you. One project, one source of
truth, especially during the 2-week go-to-market push. If you start a
Dylan conversation somewhere else, expect to get redirected back here.

---

## RULE 0B — MANDATORY: THIS DOC SET IS AUDITED, NOT JUST READ, EVERY SESSION

This doc set has drifted from the real code more than once (see v3.0 and
v3.0-Round-2 entries in the version log below, and `DYLAN_AUDIT_2026-07-01_FULL.md`).
That is not a one-time event to fix and move on from — it is the default
failure mode for any multi-file doc set describing a live codebase. To keep
it from recurring silently, every session working in this project — Claude
or Aditya — follows this procedure, no exceptions:

1. **Read first.** Start with this file and `SAAS_PROJECT_HEALTHCARE_RECRUITMENT_MASTER_CONTEXT.md`
   before doing any build, sales, or planning work.
2. **Verify before repeating.** Before telling Aditya or a customer what the
   system does, does NOT do, or has fixed — check the actual `.py` file in
   `src/` (or the actual HTML/build script in `pitch/`) that the claim is
   about. A doc saying something is fixed is a claim, not proof.
3. **Fix in place, same session.** If a doc is found to be stale, wrong, or
   internally contradictory, correct it immediately in this project folder —
   don't leave a note to fix it "later." Later is how this drifted the first time.
4. **Log it.** Append a new dated section to `DYLAN_AUDIT_2026-07-01_FULL.md`
   describing what was checked, what was found, and what was changed —
   append, never overwrite or delete a prior round's findings. This is the
   project's audit trail for its own documentation, the same way
   `master_run_log_*.csv` is the audit trail for agent actions.
5. **Update the version log below** if the change is more than a typo fix.

This rule exists so that "the docs said X" is never an acceptable excuse for
telling a customer something false. Docs are cheap to fix; a compliance or
credibility mistake in front of a paying customer is not.

---

## RULE 0C — MANDATORY: TESTS LIVE IN `tests/`, NOT IN A SESSION'S SCRATCH SPACE

**Why this exists:** during the 2026-07-02 go-live audit (Round 6, see
`DYLAN_AUDIT_2026-07-01_FULL.md`), a bug (BUG-19, a name-matching logic error
in `email_context_bridge.py`) was found and fixed by writing and running real
pytest tests — genuinely, not a fabricated claim. But those tests were only
ever written into an ephemeral sandbox scratch directory outside this project
folder. The fix was real; the proof of the fix was not persisted anywhere
Aditya or a future session could re-run it. A later pass, re-deriving the
same area of code from scratch because no evidence of prior testing existed
in the project, found a SECOND bug (BUG-20 — a Quo contact schema mismatch)
that had been sitting underneath BUG-19 the whole time, silently making the
whole feature non-functional even after BUG-19's fix. BUG-20 would very
likely have been caught immediately if BUG-19's tests had been persisted and
re-run against a realistic fixture the first time.

**The rule:** every test written to verify a fix or a claim in this project
goes into `tests/` in this project folder — never only into a session's
temporary/scratch directory — and gets re-run (`cd tests && python3 -m
pytest -v`) at the start of any session touching related code, before
trusting an existing doc's claim that something "was tested." A test that
only ever ran once, in a throwaway directory, and was never committed to the
project is functionally equivalent to no test — treat it that way.

---

## RULE 0D — PERMANENT, NON-NEGOTIABLE: NO FICTITIOUS WORK, EVER
**Added 2026-07-02, at Aditya's explicit instruction. This rule outranks
convenience, speed, and the desire to give a complete-sounding answer. It
does not expire and does not get relaxed under deadline pressure — the
2026-07-15 go-live date is not an exception to it; if anything it is the
reason it exists.**

**The standard:** nothing — no feature, fix, integration, number, or claim —
may be described to Aditya or a customer as existing, working, fixed, or
tested unless it was actually built, actually executed, actually observed to
produce a correct result, and that observation is either (a) a real pytest
run in `tests/` whose output is quoted, not paraphrased, or (b) an explicit,
named live-Mac test in `09_GO_LIVE_READINESS.md`'s verification log with a
real date and real result filled in — not left blank while the surrounding
prose implies it's done.

**This directly codifies a real failure this project already had once
(2026-07-02, see Rule 0C above and `DYLAN_AUDIT_2026-07-01_FULL.md` Round 6):
a code comment claimed "confirmed by direct test execution (pytest)" for a
fix that had no test, no `tests/` directory, and no audit log entry anywhere
in this project. The fix underneath the claim was also incomplete — a second,
more basic bug (BUG-20) was hiding under the first (BUG-19) the entire time.
The false claim of verification and the incomplete fix were not two separate
problems; the false claim is what let the incomplete fix go unnoticed. This
rule exists because that exact failure mode — sounding confident and finished
instead of being confident and finished — is more dangerous than an honest
"not yet tested," precisely because it stops anyone from re-checking.**

**How this applies in practice, every session, no exceptions:**
1. **Distinguish, out loud, every time:** "code-logic tested" (a real pytest
   run in this sandbox, no live account touched) is not the same claim as
   "live-Mac tested" (an actual run against Aditya's real Gmail/Quo/Google
   Cloud). Both are legitimate and useful. Conflating them — letting a
   passing pytest run imply the live service works — is exactly the
   violation this rule forbids. Say which one, every time.
2. **A comment or doc claiming a test happened is not evidence a test
   happened.** The evidence is the test file existing in `tests/`, plus a
   quoted pass/fail result from actually running it in the current session.
   If you did not just run it, say "not re-verified this session," not
   "confirmed."
3. **An empty verification-log row is an honest "not done," not a rounding
   error.** Do not fill in a result you did not observe. Do not describe the
   overall feature as "done" while its row is blank.
4. **If something cannot be tested from this environment (anything requiring
   Aditya's Mac, Google Cloud Console, terminal, or a real inbound
   text/email), say exactly that, name the specific blocking dependency, and
   stop there** — do not simulate, assume, or extrapolate a result for it.
5. **When a gap is found, either fix it for real in the same session and
   prove the fix with a test, or log it as an explicitly open, undecided gap
   with a named owner (Aditya-decision, Aditya-Mac-only, or
   needs-dedicated-scoping).** There is no third option where a gap is quietly
   implied to be handled.
6. **Speed is not an excuse.** If real testing/validation would take longer
   than the time available in a session, the correct output is "here is what
   I built, here is what's verified, here is what's still open" — not a
   faster answer that skips the "still open" part.

This rule does not replace Rule 0B (audit the doc set every session) or Rule
0C (persist tests in `tests/`) — it is the umbrella principle both of those
exist to serve, stated explicitly so it also covers claims that aren't about
this doc set at all (sales numbers, pitch deck stats, setup guide steps,
anything said out loud in a customer call).

---

## RULE 0E — PERMANENT: `src/` IS NOT AUTOMATICALLY THE SAME FILE AS WHAT'S DEPLOYED

**Added 2026-07-02 (Round 7), after this project's own "Rule 0 — one source
of truth" assumption was found to be wrong in practice.**

**What happened:** `~/Downloads/BlueLine/master_daily_agent.py` is Aditya's
real cron script — it is what actually runs against real candidates and real
Quo/Gmail accounts every day. This project's `src/master_daily_agent.py` was
being treated all session as "the source of truth," but the two files had
silently diverged: the deployed file (v2.3) had a real in-memory-dedup fix
and a checklist-reblast fix (BUG-15 in its own numbering) that `src/` did
not have; `src/` (v2.2) had TCPA-required STOP-language, opt-out-keyword-
widening, and no-emoji-checklist fixes that the deployed file did not have.
Neither file was a superset of the other. This means a real compliance gap
(missing STOP-language coverage) was live in production while `src/` "looked"
ahead. It was only caught because `~/Downloads` got connected this session
and the two files were diffed directly — it would not have been caught by
reading `src/` alone, no matter how carefully.

**The standing rule:** whenever `~/Downloads/BlueLine/` is reachable in a
session, any claim that `src/master_daily_agent.py` (or any other file with a
live counterpart) is "the current version" or "reconciled" must be backed by
an actual diff against the deployed file run in that same session — not
assumed from the last time it was checked. Deployment is not automatic;
nothing pushes `src/` changes to `~/Downloads/BlueLine/` on its own. A
reconciliation is only real once both files are confirmed identical (or the
difference is an intentional, named one) by direct comparison, and pushing a
reconciled file to the live path is a production change requiring Aditya's
explicit go-ahead in the same session — never done silently, per Rule 0's
caution around uncoordinated changes to what real candidates and real staff
actually interact with. See `DYLAN_AUDIT_2026-07-01_FULL.md` Round 7 for the
full write-up.

---

## RULE 0F — PERMANENT, NON-NEGOTIABLE: EVERY TERMINAL COMMAND MUST STATE ITS EXACT DIRECTORY

**Added 2026-07-03, at Aditya's explicit instruction, after he flagged that Dylan-for-Hire and
BlueLine-automation terminal commands have, in practice, ended up pasted into the wrong directory —
a Dylan command run inside the BlueLine folder, or a BlueLine command run inside this project's
`src/`. This is not hypothetical: it's the same underlying risk Rule 0E and the Round 13 incident
(two concurrent sessions silently clobbering the same folder) already describe, just showing up at
the command-execution layer instead of the file-edit layer. Wrong-directory execution produces
exactly the kind of silent failure this doc set exists to prevent — a script that "did nothing" or
edited the wrong copy, with no error to signal it.**

**The rule:** Any terminal/shell command given for this project or for BlueLine — by Claude, in any
session (Cowork or Claude Code), to be run on Aditya's Mac or in a sandbox — must make its target
directory explicit, every time, no exceptions:
1. Either start the command block with an explicit `cd <full absolute path>`, or
2. Use fully-qualified absolute paths for every file/script the command touches (never a bare
   relative name like `python3.11 master_daily_agent.py` with the working directory left implied).

No command may rely on "wherever you currently are" or "whichever directory you last `cd`'d into."
That assumption is exactly what causes a Dylan command to land in the BlueLine folder or vice versa.

**Applies with extra care to the two directories most at risk of confusion:**
- `~/Downloads/BlueLine/` — the live BlueLine production deployment.
- `"/Users/Aditya/Claude/Projects/Dylan for Hire- Saas Product Healthcare recruitment/"` — this
  project's own root (the product/reference copy).

The same discipline applies to any other directory that comes up (`~/Downloads/WV/`,
`~/Downloads/DylanForHire/`, a sandbox's own mount paths, etc.) — no directory is "obvious enough"
to skip stating explicitly.

**If a single sequence of commands needs to touch two different directories, make the switch
explicit** (e.g. `cd DIR_A && cmd1 ...` then a new line `cd DIR_B && cmd2 ...`) rather than leaving a
directory change implied between commands.

**How to apply:** before outputting any command block to Aditya (or running one directly in a
sandbox), state which directory it runs in or against. If unsure which of two similarly-purposed
directories a command belongs in, say so and ask, rather than guessing — the directories that look
most interchangeable at a glance (BlueLine's live deployment vs. this project's reference copy) are
exactly the ones this rule is protecting.

---

## WHAT IS THIS PROJECT

Dylan for Hire is an AI recruiting agent for healthcare staffing agencies.
It contacts nurses, processes credential documents, reads and responds to
inbound SMS and email, and drives placements — with a human (Aditya, or
your customer) reviewing anything sensitive before it goes out.

The agent runs as a persona named **Dylan** at BlueLine Staffing (Allendale,
NJ) — the live proof of concept — and the system is built to be
white-labelable for other agencies.

**What changed in v3.0 (2026-07-01):** Two real gaps closed, and two real
bugs found and fixed while auditing the actual code against these docs:

1. Email replies used to only happen for document-submission emails, and
   never checked Quo/SMS history. Now general email inquiries are covered
   too, and every email reply — document or general — checks both Gmail
   and Quo history first. See `email_context_bridge.py` and
   `02_SYSTEM_ARCHITECTURE.md` §12.
2. The whole system used to run once a day (9am cron) and otherwise do
   nothing. Two new always-on services
   (`master_gmail_pubsub_listener.py`, `master_sms_poll_service.py`) now
   handle inbound email and SMS continuously, all day. See
   `03_SETUP_GUIDE.md` Step 11 and `09_GO_LIVE_READINESS.md`.
3. **Bug found:** `upgrade1_context_aware_messaging.py` was reading the
   Gmail token from the wrong path — Gmail context has been silently
   absent from every SMS re-engagement decision since it was built. Fixed.
4. **Docs found stale:** `08_TROUBLESHOOTING.md` and
   `02_SYSTEM_ARCHITECTURE.md` both said the Quo API URL bug was still
   open. It wasn't — it was already fixed in code as of 2026-06-29. Docs
   now match code. Lesson: don't trust a doc's bug list over a direct
   code read — verify before repeating a claim to a customer.

---

## DOCUMENT MAP — ALL FILES LIVE IN THIS PROJECT FOLDER

| File | What it covers | Who reads it |
|------|---------------|--------------|
| `SAAS_PROJECT_HEALTHCARE_RECRUITMENT_MASTER_CONTEXT.md` | Single source of truth — carry into every session | Everyone, first |
| `00_INDEX.md` | This file — master index, Rule 0, project overview | Everyone |
| `01_PRODUCT_OVERVIEW.md` | What the product truly does today, business model, honest gap list | Owner, sales |
| `02_SYSTEM_ARCHITECTURE.md` | Full technical structure, data flow, file map | Developer, operator |
| `03_SETUP_GUIDE.md` | Zero-to-live setup, including the new 24/7 real-time layer | Developer, new operator |
| `04_DAILY_OPERATIONS.md` | Every day: run checklist, what to review, what to do | Operator (Aditya) |
| `05_PIPELINE_REFERENCE.md` | Step-by-step logic for every pipeline step, including the new email bridge | Developer, troubleshooter |
| `06_COMMUNICATIONS.md` | All SMS/email templates + decision prompts, when they fire | Operator, copywriter |
| `07_COMPLIANCE.md` | TCPA + email compliance rules, opt-out protocol, what never to do | Owner, legal |
| `08_TROUBLESHOOTING.md` | Diagnosis flowcharts, known bugs (corrected), exact fixes | Developer, operator |
| `09_GO_LIVE_READINESS.md` | **New** — the 2-week bug-bar and launch checklist | Owner |
| `10_CLIENT_INTAKE_AND_ADAPTER_SPEC.md` | **New (2026-07-01)** — the exhaustive client-intake questionnaire + adapter architecture for making this system-agnostic beyond BlueLine | Owner, developer |
| `11_CUSTOMER_FACING_PRODUCT_OVERVIEW.md` | **New (2026-07-01)** — sanitized, prospect-safe product overview. No internal identity/contact info. Facts must stay in sync with the master context doc and `09_GO_LIVE_READINESS.md` — do not edit independently | Sales, prospects |
| `12_SCHEDULING_SETUP_GUIDE.md` | **New (2026-07-01)** — supersedes the previously-referenced `Dylan_for_Hire_Calendly_Setup_Guide.md` (not present in this folder). Process only — live account values stay in the master context doc §8 | Owner, whoever runs the sales funnel |
| `13_DYLAN_PRODUCT_CONSTITUTION.md` | **New (2026-07-03)** — identity/scope rule: Dylan is the independent product, BlueLine is its first customer and design partner, never the reference architecture. Founder decision filter for what belongs in core product vs. BlueLine-only config. Governs *what kind of thing Dylan is*; Rule 0 family below governs *where work happens* | Owner, anyone making a product/architecture call |

**Important framing (added 2026-07-01, made a standing rule 2026-07-03 —
see `13_DYLAN_PRODUCT_CONSTITUTION.md`):** BlueLine is the reference client, not
the product. Everything BlueLine-specific in `src/` — persona, agency name,
OpenPhone, Gmail, CSV column names, NY credential rules, rates, facility list —
should eventually be expressed as answers to `10_CLIENT_INTAKE_AND_ADAPTER_SPEC.md`'s
questionnaire, not as hardcoded values in shared code. Don't assume the current
integrations are the final architecture.

---

## SOURCE CODE — `src/`

| Source file | What it does | Status |
|------------|-------------|--------|
| `master_daily_agent.py` | Main daily orchestrator — Steps 3→1→DEDUP→2, still on 9am cron | Proven, unchanged in v3.0 |
| `master_gmail_reviewer.py` | Gmail review — document AND general-inquiry replies (v1.1) | Rewritten in v3.0 |
| `master_gmail_setup.py` | One-time Google OAuth2 setup | Unchanged |
| `upgrade1_context_aware_messaging.py` | Context-aware SMS re-engagement (v1.1) | Bug-fixed in v3.0 |
| `email_context_bridge.py` | **New** — cross-channel context for email replies | New in v3.0 |
| `master_gmail_pubsub_listener.py` | **New** — 24/7 real-time email service | New in v3.0 |
| `master_sms_poll_service.py` | **New** — 24/7 near-real-time SMS reply service | New in v3.0 |
| `master_requirements.txt` | All pip dependencies (now includes google-cloud-pubsub) | Updated in v3.0 |

---

## PRESENTATION ASSETS — `pitch/`

| File | What it is |
|------|-----------|
| `dylan_for_hire_pitch_deck.html` | Pitch deck with embedded audio |
| `dylan_for_hire_architecture.html` | Animated architecture walkthrough with audio |
| `build_pitch_deck.py` / `build_arch_doc_v2.py` | Rebuild the HTML (no audio) |
| `gen_all_audio.py` / `embed_audio.py` | Generate + embed ElevenLabs narration |
| `audio2/` | Generated MP3 narration segments |

**Before you sell with these:** the numbers on the proof slides (candidates
contacted, active conversations, response time) must match what's actually
true on the day you present — see `09_GO_LIVE_READINESS.md` for how to
verify before every customer call, not just at build time.

**⚠️ Build-script/filename mismatch (found 2026-07-01, verified in code):**
`build_pitch_deck.py` / `build_arch_doc_v2.py` write to
`~/Downloads/BlueLine/blueline_pitch_deck.html` /
`blueline_architecture_doc.html` — not the `dylan_for_hire_pitch_deck.html` /
`dylan_for_hire_architecture.html` files actually sitting in this folder.
Running these scripts today creates new, differently-named, BlueLine-branded
files rather than updating the real assets. Do not run Step 10 of
`03_SETUP_GUIDE.md` expecting it to refresh the current deck until this is
fixed. See `09_GO_LIVE_READINESS.md` 🔴 KNOWN GAPS.

---

## SENSITIVE FILES — NEVER COPY OUT OF THIS SETUP

| File | Location | Why sensitive |
|------|----------|--------------|
| `.env` | `~/Downloads/.env` | API keys + (new) GCP project ID |
| `gmail_credentials.json` | `~/Downloads/` | Google OAuth2 client credentials |
| `gmail_token.json` | `~/Downloads/` | Google OAuth2 access token |
| `CONFIDENTIAL_candidates.csv` | `~/Downloads/BlueLine/` | All candidate names and phone numbers (PII) |

---

## STATE FILES — DO NOT DELETE WITHOUT READING `07_COMPLIANCE.md` FIRST

| File | Why critical |
|------|-------------|
| `~/Downloads/master_permanent_optouts.txt` | **NEVER DELETE** — TCPA compliance |
| `~/Downloads/master_processed_contacts.txt` | Prevents duplicate intro messages |
| `~/Downloads/master_handled_interest_replies.txt` | Prevents double-responding to interested candidates |
| `~/Downloads/master_needs_human_review.txt` | SMS replies flagged for you |
| `~/Downloads/master_needs_human_review_email.txt` | **New** — email replies flagged for you (kept separate on purpose) |
| `~/Downloads/master_last_gmail_history_id.txt` | **New** — real-time listener's cursor; don't hand-edit |

---

## QUICK START — ALREADY HAVE THE CODE, JUST WANT TO RUN IT

```bash
# Daily batch (unchanged)
cat ~/Downloads/.env    # must show all keys incl. GCP_PROJECT_ID
cd ~/Downloads/BlueLine
python3.11 master_daily_agent.py

# 24/7 services (new — see 03_SETUP_GUIDE.md Step 11 before first use)
launchctl list | grep blueline    # should show both services running

# Check what happened
open mail.google.com
cat ~/Downloads/master_needs_human_review.txt
cat ~/Downloads/master_needs_human_review_email.txt
```

---

## DOCUMENT VERSIONING

- v1.0 (2026-05-04): System first deployed
- v2.0 (2026-06-28): Context-aware messaging (upgrade1) integrated
- v2.1 (2026-06-29): 13 bugs fixed — verified live, production-stable
- v2.2 (2026-06-30): Pitch deck and architecture doc rebuilt with ElevenLabs audio
  (corrected 2026-07-01, Round 2 audit: this entry and the 2026-06-29 entry
  were both previously mislabeled "v2.1" — renumbered for clarity, no content change)
- **v3.0 (2026-07-01):** Full doc set audited against actual source code and
  rewritten. Email general-inquiry + cross-channel context added. 24/7
  real-time layer added (Gmail push + SMS poll services). Two real bugs
  found and fixed (Gmail token path in upgrade1; stale bug claims in this
  doc set itself). Rule 0 added. Go-live readiness doc added — target
  2026-07-15.
- **v3.0 Round 2 (2026-07-01, same day):** Full doc set re-verified line-by-line
  against actual `.py` files in `src/` and `pitch/` (not just cross-doc
  consistency). Confirmed BUG-14 through BUG-18 fixes are real in code, not
  just claimed. Found and fixed two new issues: (1) "11-point credential
  check" claimed in the master context doc but `validate_documents()` in
  `master_gmail_reviewer.py` implements 9 categories — corrected, gap logged
  in `09_GO_LIVE_READINESS.md`; (2) `pitch/build_pitch_deck.py` and
  `build_arch_doc_v2.py` output `blueline_*.html` but the real delivered
  assets are `dylan_for_hire_*.html` — flagged, not yet fixed in code. See
  `DYLAN_AUDIT_2026-07-01_FULL.md` for the full Round 2 write-up.
- **v3.0 Round 3 (2026-07-01, same day):** Aditya uploaded two standalone files
  (`Dylan_for_Hire_Scheduling_Setup_Guide.md`, `Dylan_for_Hire_Product_Overview.md`)
  for reconciliation into this project. Both were independently re-verified
  against `src/master_gmail_reviewer.py` directly (not against this doc set's
  own prior claim). The uploaded Product Overview repeated the same "11-point"
  claim already known-false from Round 2, plus additional errors not previously
  caught: it omitted resume and COVID vaccine (both actually required in code)
  and included Hepatitis B, flu vaccine, and background-check/fingerprint (none
  implemented in code). Corrected and saved as `11_CUSTOMER_FACING_PRODUCT_OVERVIEW.md`.
  The uploaded Scheduling Setup Guide checked out accurate against master context
  §8 with no corrections needed — saved as `12_SCHEDULING_SETUP_GUIDE.md`,
  explicitly superseding the `Dylan_for_Hire_Calendly_Setup_Guide.md` reference in
  master context §10 (that file does not exist in this project folder). Also fixed
  a self-contradiction found in `09_GO_LIVE_READINESS.md` line 29 — its own
  "VERIFIED" section still said "11-point" while its "KNOWN GAPS" section
  (written in the same file, same day) already said 9-category. See
  `DYLAN_AUDIT_2026-07-01_FULL.md` Round 3 for the full write-up.
- **v3.0 Round 4 (2026-07-01, same day):** Aditya decided KNOWN GAP #6 —
  Hepatitis B and annual flu vaccine added to `validate_documents()` and the
  Vision schema in `master_gmail_reviewer.py`, both `optional: True`
  (recommended, not blocking), because both accept a signed declination as a
  compliant alternative to vaccination. Tracked categories now 8 required + 3
  recommended = 11 total — do not shorthand as "11-point" without that split.
  NYS background-check/fingerprint left undecided on purpose (different risk
  profile, no declination alternative). New code is unverified against a real
  document — `11_CUSTOMER_FACING_PRODUCT_OVERVIEW.md` deliberately NOT updated
  until tested. See `DYLAN_AUDIT_2026-07-01_FULL.md` Round 4.
- **v3.0 Round 5 (2026-07-02):** Client-facing setup questionnaire built
  (`Dylan_for_Hire_New_Client_Setup_Questionnaire.docx`); audited whether the
  system is actually platform-agnostic (it is not yet — no adapter layer
  exists in `src/`, confirmed by direct read) and positioned OpenPhone +
  Gmail/Workspace as a requirement rather than an open question in that
  document. Added the "PLAIN-ENGLISH ACTION CHECKLIST" to
  `09_GO_LIVE_READINESS.md`. See `DYLAN_AUDIT_2026-07-01_FULL.md` Round 5.
- **v3.0 Round 6 (2026-07-02):** Actually ran tests against `src/` for the
  first time this project has a persisted record of (`tests/conftest.py`,
  `tests/test_pipeline_logic.py` — 69 tests, all passing, re-run and
  confirmed at the end of this round). Found and fixed two real bugs in
  `email_context_bridge.py`'s Quo contact name-matching: BUG-19 (name-parsing
  logic assumed `lastName` held a surname; it never does — see Rule 0C
  above for the process failure this also exposed) and BUG-20 (contact
  fields were read at the flat top level instead of nested under
  `defaultFields`, the schema `master_daily_agent.py` proves is real —
  this alone made every name match fail, independent of BUG-19). Built and
  wired the email-side opt-out auto-sync (closes KNOWN GAP #1): a dedicated
  `FLAG_HUMAN_OPTOUT` decision code, only ever set by the Claude decision
  engine on a confident opt-out reading, triggers
  `sync_email_optout_to_sms()` to write the matched phone to
  `master_permanent_optouts.txt` and rename the Quo contact — verified by
  test, not just read. Resolved KNOWN GAP #7 (pitch deck build script
  mismatch): redirected `build_pitch_deck.py` / `build_arch_doc_v2.py`
  output to a clearly-labeled deprecated path rather than repointing them
  at the real files, because their hardcoded content is stale (no embedded
  audio, predates the 24/7 layer) and would have regressed the real,
  presented decks if repointed — confirmed by actually running both
  scripts and diffing the real files' checksums before/after (unchanged).
  Added RULE 0C (tests must be persisted in `tests/`, not session scratch
  space). See `DYLAN_AUDIT_2026-07-01_FULL.md` Round 6 for the full write-up,
  including an honest note on an earlier, non-persisted test claim this
  round corrected. **Same-round continuation (items 32-35):** added
  `match_phone_by_sender_email()` + `backfill_email_onto_contact()` — email
  match now tried before name match, and a successful name match backfills
  the email so future emails from that address match directly (partial
  mitigation of KNOWN GAP #2, 5 new tests). Fixed `master_gmail_setup.py`
  running its OAuth flow as unguarded top-level code (made it unsafe to
  import — found while building the config-consistency tests). Fixed a
  cosmetic version-string mismatch in `master_daily_agent.py`'s startup log.
  Added **RULE 0D** — the permanent, project-wide "no fictitious work" rule,
  added at Aditya's explicit instruction: nothing may be described as
  done/working/tested unless actually built, executed, and observed to pass
  this session, or via a named, filled-in live-Mac test — "code-logic
  tested" and "live-Mac tested" are always stated as the distinct claims
  they are. Test suite: 75 passing (up from 69), re-run and confirmed at the
  end of this round.
- **v3.1 Round 7 (2026-07-02, same day):** Aditya connected `~/Downloads` as a
  real, persistent folder (previously this project could only read/write its
  own directory). First thing done with that access: diffed
  `~/Downloads/BlueLine/master_daily_agent.py` (the real deployed cron
  script, v2.3) against `src/master_daily_agent.py` (v2.2, previously assumed
  to be current) — **found they had silently diverged**, each with real fixes
  the other lacked (deployed: in-memory dedup + checklist-reblast fix under
  its own "BUG-15"; `src/`: TCPA STOP-language, opt-out-keyword-widening,
  no-emoji-checklist fixes). Net effect: **the live production script was
  missing TCPA-required STOP-language coverage this entire time** — a real
  compliance gap, not a documentation gap. Reconciled `src/master_daily_agent.py`
  to v2.4, the union of both fix histories (ported `BOROUGH_ABBREV` +
  `STATE_CHECKLIST_SENT` from deployed; kept the tightened `INTEREST_KEYWORDS`
  plus new `DOCS_SENT_KEYWORDS`/`UPDATE_REQUEST_KEYWORDS` branches from
  `src/`), added 6 new/updated tests covering the reconciled logic, and
  re-ran the full suite: **100 passing** (up from 75; the jump also includes
  2 pre-existing tests updated to match `master_gmail_reviewer.py` v1.2's
  intentional `employment_application` 12th category — 8 required + 4
  optional, not 8+3). Added **RULE 0E** (`src/` is not automatically the same
  file as what's deployed — diff before claiming reconciliation, never push
  to the live path silently). **`src/master_daily_agent.py` v2.4 has NOT been
  deployed to `~/Downloads/BlueLine/master_daily_agent.py`** — that is a
  live-production change to a script sending real messages to real
  candidates and requires Aditya's explicit decision, asked for separately,
  not assumed. See `DYLAN_AUDIT_2026-07-01_FULL.md` Round 7.
- **v3.2 Round 7 addendum (2026-07-02, same day):** Aditya gave explicit instruction — "copy and
  update it to ensure maximum compliance, no duplication of messages and opt out should be ironclad."
  Before deploying, re-read the reconciled v2.4 file against exactly that brief and found 3 further
  gaps the reconciliation itself hadn't touched: no protection against two overlapping runs both
  double-sending to the same candidate (process-level, not per-message), `send_sms()` trusting its
  callers' opt-out checks with no guard of its own, and a candidate silently lost forever if their
  Quo contact was created but the intro SMS failed to send. Fixed all three (process lock via atomic
  `O_EXCL`, a hard opt-out re-check inside `send_sms()` read fresh from disk every call, and a
  send-failure path that now flags to `master_needs_human_review.txt` instead of vanishing), added
  12 new tests, re-ran the full suite: **112/112 passing.** Version-bumped to v2.5 and **deployed
  live** — copied over `~/Downloads/BlueLine/master_daily_agent.py`, verified byte-identical to
  `src/` by direct diff post-copy, old v2.3 preserved as a `.pre-v2.5-backup-2026-07-02` file for
  rollback. See `DYLAN_AUDIT_2026-07-01_FULL.md` Round 7 addendum (items 42-46). **Still open:** no
  live-Mac test has exercised this deploy yet — code-logic tested and deployed is not the same claim
  as live-Mac tested, per Rule 0D.
- **v3.2 Rounds 8–13 + 2026-07-03 scheduled check (gap closed 2026-07-03 — this entry had not been
  appended here even though all of this was logged in `DYLAN_AUDIT_2026-07-01_FULL.md` at the time;
  flagged by the 2026-07-03 exhaustive audit and backfilled now per Rule 0B item 5):** 24/7 SMS poll
  service and Gmail Pub/Sub listener live-tested, a real crontab `TZ` misconfiguration found and fixed
  (had caused ~163 extra intro SMS over 59 days), `master_gmail_reviewer.py` found 4+ months behind on
  the live Mac and deployed, Quo contact-lookup cache added (4m51s → 16ms), unbounded-timeout bug fixed
  across all 6 Quo HTTP call sites, the 30/day cap bug fixed and replaced with a rolling 75/day
  duplicate-send-fingerprinted cap (per Aditya's explicit "no duplicate sends, ever" instruction), git
  initialized in both `~/Downloads/BlueLine/` and this project after a two-concurrent-session drift
  incident (Round 13 — see `[[blueline-dylan-git-separation]]`-equivalent write-up in the audit file),
  and `scripts/sync_check.sh` built and run clean. Full detail in `DYLAN_AUDIT_2026-07-01_FULL.md`
  Rounds 8 through the 2026-07-03 scheduled check — not reproduced here.
- **v3.3 Round 14 (2026-07-02 23:38–23:44, recovered 2026-07-03 — see `DYLAN_AUDIT_2026-07-01_FULL.md`
  for the full recovered write-up):** `pyflakes` clean across all of `src/` and the live deployment
  after removing 6 confirmed-dead imports/lines; full suite 138/138, run twice consecutively; 6 real
  doc-vs-code mismatches fixed, including a wrong model name in `CLAUDE.md` (said `claude-opus-4-5`,
  real model is `claude-haiku-4-5-20251001`) and the `NO_RESPONSE_FINAL` fiction — three docs, including
  BlueLine's own `CLAUDE.md`, claimed this fallback existed; confirmed by direct grep it does not exist
  anywhere in `src/`. This round's own audit-trail entry was never appended to
  `DYLAN_AUDIT_2026-07-01_FULL.md` despite being committed to git (`7544c1d`, `b920277`) — exactly the
  failure Rule 0B exists to prevent. Recovered from session transcript and appended 2026-07-03, see
  `DYLAN_FOR_HIRE_EXHAUSTIVE_AUDIT_2026-07-03.md` §5.
- **v3.4 (2026-07-03, this pass):** Added `13_DYLAN_PRODUCT_CONSTITUTION.md` — the identity/scope rule
  (Dylan is the independent product, BlueLine is the first customer/design partner, never the
  reference architecture) made permanent and git-tracked, closing a gap where a fuller version of this
  rule existed only in this Cowork project's non-editable, confirmed-stale custom-instructions
  snapshot. Appended the recovered Round 14 write-up and this consolidation pass to
  `DYLAN_AUDIT_2026-07-01_FULL.md` per Rule 0B. No code changed this pass — this was a documentation/
  memory-consolidation pass triggered by Aditya uploading `DYLAN_FOR_HIRE_EXHAUSTIVE_AUDIT_2026-07-03.md`
  and asking that its learnings, rules, and guardrails be made permanent within this project, not left
  as one-off recap files. The 🔴/🟡 open items that audit identified (launchctl live-Mac verification,
  center-domain-email-as-candidate bug, image-MIME-type Vision failure, `tests/` not tracked by
  `sync_check.sh`, undeployed `master_candidate_file_consolidator.py`, stale Gmail OAuth credential
  question, uncommitted ElevenLabs key rotation, the permanent-skip/`NO_RESPONSE_FINAL` product
  decision) are **still open as of this entry** — this pass did not fix code, it made sure none of
  those findings or the identity rule above depend on any one conversation's memory to survive.
- **v3.5 Round 15 (2026-07-03, this pass):** Real code-correctness loop against everything reachable
  from this session (this project's own root only — no `~/Downloads/BlueLine`, no live Mac). Re-ran
  `pyflakes` (clean) and the full suite (138/138, re-confirmed fresh, not just recovered) from scratch.
  Fixed 2 of the 6 open items from the 2026-07-03 exhaustive audit: the center-domain-as-candidate bug
  (`load_center_email_domains()`, data-driven from `BLUELINE_CENTER_DIRECTORY.md`, not hardcoded) and
  the image MIME-type sniffing bug (`sniff_media_type_from_bytes()`, fixes the exact live 400 seen in
  `cron_output.log`) — both in `master_gmail_reviewer.py`, both proven with new tests (150/150 full
  suite after). Fixed the `tests/`-not-tracked-by-`sync_check.sh` gap (reversed sync direction — this
  project's `tests/` leads, BlueLine's follows) and, while doing so, found and fixed a real pre-existing
  false-positive bug in the script's flag-only-files comparison. Pinned down the ElevenLabs key exposure
  to exactly 2 commits (`3e936f5`, `7544c1d`) via `git log -S` and found it may actually be a Wealth
  Velocity credential, not Dylan's — still not rotated, still Aditya's action. **Still open, unchanged
  by this pass:** launchctl live-Mac verification, `master_candidate_file_consolidator.py` deployment,
  the stale-Gmail-credential question, the `NO_RESPONSE_FINAL` product decision, and actually running
  `sync_check.sh --apply` against the real BlueLine folder. See `DYLAN_AUDIT_2026-07-01_FULL.md` Round
  15 for the full write-up.
- **v3.6 (2026-07-03, same day):** Added **RULE 0F** — every terminal command given for this project
  or BlueLine must state its exact directory (explicit `cd <absolute path>` or fully-qualified paths),
  no exceptions. Added at Aditya's explicit instruction after he flagged that Dylan and BlueLine
  automation commands have, in practice, ended up pasted into the wrong directory. No code changed;
  this is a standing process rule, same category as Rule 0D/0E.
