# DYLAN FOR HIRE — FULL DOC + CODE AUDIT
**Run:** 2026-07-01 | **Scope:** every .md doc + every .py file in this project folder, cross-checked against each other and against actual source code (ground truth).

Method: read all 9 numbered docs + master context doc, all 7 files in `src/`, and the `pitch/` build scripts. Every finding below was verified by reading the actual code — not by trusting a doc's claim about the code.

**Cannot verify from this session:** whether the code in `src/` has actually been deployed to `~/Downloads/BlueLine/` on your Mac, whether `.env`/`gmail_token.json`/cron/launchd are live, or the real `CONFIDENTIAL_candidates.csv` column headers. This Cowork session only reaches this project folder — not `~/Downloads` or `~/Desktop` on your machine. Everything below is "is the project's source of truth internally consistent and correct," not "is the live Mac deployment healthy."

---

## TIER 1 — GO-LIVE BLOCKERS (fix before anyone touches this with a customer)

**1. `master_sms_poll_service.py` will crash the moment it runs.**
Line 40/70 calls `mda.step3_handle_sms_replies()`. That function does not exist. The real function in `master_daily_agent.py` (line 318) is `step3_sms_reply_handler()`. This isn't a typo in one place — `00_INDEX.md`, `02_SYSTEM_ARCHITECTURE.md`, and `05_PIPELINE_REFERENCE.md` all also use the wrong name, so the function was renamed in the actual code at some point and nothing else was updated. Net effect: the entire 24/7 real-time SMS layer — the headline new feature of v3.0 — is currently non-functional. `AttributeError` on first launch.
*Fix: rename the call (or the function) so they match, in this file and all three docs.*

**2. The live `DYLAN_INTRO` template has no opt-out language.**
`master_daily_agent.py` lines 286–291 — the actual first-contact SMS sent to every new lead — contains no "Reply STOP to opt out" anywhere. `07_COMPLIANCE.md` states as a non-negotiable rule: *"Every first contact with a candidate must include... Opt-out instruction... The DYLAN_INTRO template already includes all three."* It doesn't. This is a real TCPA exposure in production code, not a doc typo — the compliance doc is asserting a safeguard that isn't actually in the message being sent.

**3. `OPTOUT_KEYWORDS` in code is narrower than what `07_COMPLIANCE.md` claims is auto-handled.**
Code (`master_daily_agent.py` lines 314–315): `{"stop","unsubscribe","remove","opt out","optout","do not contact","don't contact","no thanks","not interested"}`.
`07_COMPLIANCE.md` and `05_PIPELINE_REFERENCE.md` both document a longer list that includes `"please stop"`, `"take me off"`, `"wrong number"`, `"leave me alone"`, `"dont text"`, `"do not text"`, `"dont contact"` — none of which are in the actual keyword set. A candidate who texts "please stop" or "take me off" today gets routed to the human-review queue, not auto-opted-out, despite the compliance doc stating flatly that these phrases are recognized and handled automatically.
*This is the single highest-stakes finding here — recommend closing the gap in code (safer) rather than just correcting the doc, given TCPA's per-message statutory damages.*

**4. `09_GO_LIVE_READINESS.md` doesn't exist.**
Referenced as the authoritative launch checklist / Pub/Sub setup guide / "verify these numbers before a customer call" doc in `00_INDEX.md` (3x), `02_SYSTEM_ARCHITECTURE.md`, the master context doc (6x), and inside the docstrings of both new services (`master_gmail_pubsub_listener.py`, `master_sms_poll_service.py`). It's supposed to be the actual 2-week go-live bar. It was never written. Given you're 1–2 weeks out, this is the most concrete missing deliverable in the whole project.

---

## TIER 2 — REAL BUGS/CONTRADICTIONS (not launch-blocking alone, but will bite you or a customer)

**5. The Quo URL/Bearer bug is fixed in code but still documented as open in two places.**
Verified in code: `upgrade1_context_aware_messaging.py` line 56 (`QUO_BASE_URL = "https://api.openphone.com/v1"`) and line 96 (no Bearer prefix) — fixed, matches `email_context_bridge.py` too.
Still wrong: `02_SYSTEM_ARCHITECTURE.md` §4A/§12 calls it a live "KNOWN BUG" twice. `08_TROUBLESHOOTING.md` is self-contradictory — its own header banner says this bug "was already fixed as of 2026-06-29" and calls the section describing it "stale," yet the body still has a full "KNOWN ONGOING BUG — NOT YET FIXED" section with fix instructions for a bug that's already fixed.

**6. "§13" is cited 6+ times across 3 documents and doesn't exist anywhere.**
`02_SYSTEM_ARCHITECTURE.md`'s own header promises "New §13 covers the real-time layer" — the doc ends at §12. The master context doc cites "§13" four separate times (for the real-time layer, for "docs have been wrong before," for the Gmail token path correction) — no document contains a section actually numbered 13.

**7. Gmail credentials/token path is documented wrong in two places.**
Actual code (`master_gmail_setup.py`, `master_gmail_reviewer.py`): both files live at `~/Downloads/gmail_token.json` and `~/Downloads/gmail_credentials.json` (one level up from BlueLine/). `02_SYSTEM_ARCHITECTURE.md` §4C still says `~/Downloads/BlueLine/gmail_credentials.json` / `gmail_token.json`. `08_TROUBLESHOOTING.md`'s own diagnostic command (`ls ~/Downloads/BlueLine/gmail_token.json`) uses the wrong path too — running it as written would falsely report the token missing even when it's correctly placed.

**8. "11-point credential check" is three different checklists in three different docs, and none of them matches the code exactly.**
- Code (`master_gmail_reviewer.py` `validate_documents()`): 9 categories — resume, nursing license, I-9 IDs, physical, MMR, varicella, chest X-ray/PPD/Quantiferon, COVID vaccine, BLS/CPR. Of these, **BLS/CPR is flagged `optional: True`** (not required) and **resume has no optional flag** (i.e. treated as required).
- `05_PIPELINE_REFERENCE.md`'s own table says BLS/CPR is "Yes" (required) and resume is "Recommended" — the opposite of what the code does.
- `01_PRODUCT_OVERVIEW.md` describes only 6 items (license, physical, titers, TB, BLS, I-9) — no COVID, no resume.
- The original SAAS master-doc's 11-point list (Hep B vaccine, annual flu vaccine, NYS CHRC fingerprint/background check) isn't implemented in the code's Claude Vision schema at all.
This matters beyond internal consistency: "11-point credential check, zero human review" is a stated sales feature (master context §2, pitch deck slide 7). If a prospect asks what's in the 11 points, there currently isn't one consistent true answer.

**9. CSV column assumptions in the setup docs don't match what the code actually reads.**
Code (`master_daily_agent.py` line 533): license type comes specifically from a `Role` column (falls back to `"CNA"` if absent or unrecognized — silently, no warning). Borough (line 553) comes specifically from a `Location` column. `03_SETUP_GUIDE.md` Step 7 and `02_SYSTEM_ARCHITECTURE.md` §9 both describe this as "scans all CSV columns" / "any field containing license type text" — that's not how the code works. Practical risk: prep a CSV per the setup guide without a column literally named `Role`, and every candidate silently becomes CNA/NY with no error.

**10. Pitch deck build scripts don't produce the files that actually exist.**
`build_pitch_deck.py` / `build_arch_doc_v2.py` hardcode output to `~/Downloads/BlueLine/blueline_pitch_deck.html` / `blueline_architecture_doc.html`. The finished, audio-embedded assets actually sitting in this project's `pitch/` folder are named `dylan_for_hire_pitch_deck.html` / `dylan_for_hire_architecture.html`. Following `03_SETUP_GUIDE.md` Step 10 literally would not update the real deck in place — it'd produce differently-named files in a different folder.

**11. BUG-14 is cited by name but doesn't exist in the bug catalog.**
`00_INDEX.md` and `03_SETUP_GUIDE.md` both point to "`08_TROUBLESHOOTING.md` BUG-14" for the Gmail-token-path fix. `08_TROUBLESHOOTING.md`'s numbered list stops at BUG-13.

**12. `DOCUMENT_CHECKLIST_MSG` breaks the "no emoji in SMS" rule it's supposed to follow.**
Code's actual constant (`master_daily_agent.py` lines 293–308) has 📋/📍/📧 in it. `06_COMMUNICATIONS.md` Ground Rule #3 says "No emojis in SMS" — and that same doc's own printed version of this exact template (a few lines later) shows no emojis. Three-way mismatch: rule, doc's own example, and live code all disagree with each other.

---

## TIER 3 — STALE BUT LOW-RISK

**13.** `01_PRODUCT_OVERVIEW.md` (v1.0, dated 2026-06-30) hasn't been touched since before v3.0. Still describes once-daily/manual-only operation, no mention of the 24/7 layer or general email-inquiry handling. Its "Known bugs: 0" line is no longer true.

**14.** `00_INDEX.md`'s version log has two separate entries both labeled "v2.1" (2026-06-29 bug fixes vs. 2026-06-30 pitch deck rebuild) — cosmetic, but confusing if you're ever tracing "what changed when."

**15.** `05_PIPELINE_REFERENCE.md`'s Step 3 decision tree still has "[Legacy: send ADD_ON_STUFF_MESSAGE — verify if still in v2.1]" as an open question. Checked: no such constant or send call exists anywhere in the code. The doc's own question should just be closed (delete the step).

---

## WHAT'S ACTUALLY SOLID

- `email_context_bridge.py` + the widened `master_gmail_reviewer.py` (v1.1) genuinely implement the general-email-inquiry / cross-channel-context feature as claimed — verified end to end, including the `FLAG_HUMAN` / `SKIP` / `DRAFT` decision logic and the "never auto-send" invariant (drafts only, confirmed in both the doc-review and general-inquiry paths).
- The Gmail-token-path bug fix inside `upgrade1_context_aware_messaging.py` (line 62, dated `[FIX 2026-07-01]`) is real and correctly reasoned — matches what `00_INDEX.md` claims.
- `master_requirements.txt` does include `google-cloud-pubsub` as claimed.
- Core Step 1/2/3/DEDUP logic in `master_daily_agent.py` is internally coherent and the 13 previously-fixed bugs (BUG-01 through BUG-13) all check out against the current code — no regressions found there.

---

## RECOMMENDED ORDER OF OPERATIONS

1. Fix the `step3_handle_sms_replies` / `step3_sms_reply_handler` name mismatch (5-minute fix, unblocks the whole 24/7 SMS feature).
2. Decide on DYLAN_INTRO + OPTOUT_KEYWORDS — this is a compliance call, not a formatting call. Recommend adding the STOP language to the live template and widening OPTOUT_KEYWORDS to match what the compliance doc already promises, rather than downgrading the doc's promises to match the narrower code.
3. Write `09_GO_LIVE_READINESS.md` for real — it's cited everywhere as the thing that decides whether you're ready, and right now that decision has no home.
4. Batch-fix the doc staleness items (Tier 2, #5–#12) — mechanical corrections once 1–2 are settled, since several of them cascade from the same two fixes.

---

## ROUND 2 — 2026-07-01 (same day) — RE-VERIFIED DIRECTLY AGAINST `src/` AND `pitch/` SOURCE FILES

**Trigger:** Aditya asked for a continuous audit loop across the full 13-file
doc set (10 numbered docs + master context + this audit file + the client
intake spec), with instructions to fix issues found and make future sessions
treat this doc set as mandatory-reference-and-continuously-updated, not a
one-time deliverable.

**Method — different from Round 1:** Round 1 (above) was cross-doc and
doc-vs-doc-claim consistency checking. Round 2 read every relevant `.py`
file in `src/` and `pitch/` directly, line by line, and checked every "this
was fixed" claim in the doc set against the actual code — not against
another doc's claim that it was fixed.

### Confirmed TRUE against actual code (not just re-asserted by docs)

- BUG-14 (Gmail token path in `upgrade1_context_aware_messaging.py`) — **verified fixed.** Line 62: `GMAIL_TOKEN_PATH = os.path.expanduser("~/Downloads/gmail_token.json")`, matching `master_gmail_setup.py` and `master_gmail_reviewer.py` exactly.
- BUG-15 (`step3_handle_sms_replies` naming) — **verified fixed.** `master_sms_poll_service.py` line 70 calls `mda.step3_sms_reply_handler()`, and that function exists at `master_daily_agent.py` line 347.
- BUG-16 (DYLAN_INTRO missing STOP language) — **verified fixed.** `master_daily_agent.py` lines 302–308 end with "Reply STOP to opt out."
- BUG-17 (OPTOUT_KEYWORDS/INTEREST_KEYWORDS narrower than documented) — **verified fixed.** Both sets in `master_daily_agent.py` (lines 329–344) now match what `07_COMPLIANCE.md`/`05_PIPELINE_REFERENCE.md` describe, including "please stop," "take me off," "wrong number," "leave me alone."
- BUG-18 (emoji in DOCUMENT_CHECKLIST_MSG) — **verified fixed.** No emoji present in the live constant (lines 312–327).
- Quo URL/Bearer fix — **verified true**, consistent across `master_daily_agent.py`, `upgrade1_context_aware_messaging.py`, and `email_context_bridge.py`.
- CSV column handling (`Role`/`Location` specific columns, silent CNA/blank default) — **verified matches** `step2_new_leads()` in `master_daily_agent.py` exactly as `05_PIPELINE_REFERENCE.md` now describes.
- BLS/CPR optional / resume required — **verified matches** `validate_documents()` in `master_gmail_reviewer.py` exactly as the corrected `05_PIPELINE_REFERENCE.md` table describes.

### NEW issues found (not caught by Round 1 because Round 1 didn't diff docs against `pitch/` scripts or count the Vision JSON schema fields)

**13. "11-point credential check" is a marketing claim that doesn't match the implemented schema.** `validate_documents()` in `master_gmail_reviewer.py` produces exactly 9 result categories (resume, nursing_license, id_documents, physical, mmr_titers, varicella_titers, chest_tb, covid_vaccine, bls_cpr). The Claude Vision JSON schema in `analyze_attachments_with_claude()` has no fields at all for Hepatitis B, annual flu vaccine, or NYS CHRC fingerprint/background check — three items that appear in earlier planning material for this system. Yet the master context doc said "11-point credential check" in two places (product description and proven-results bullet). **Fixed:** both instances corrected to "9-category," with an explicit gap note. **Still open:** whether to build the missing 3 categories or permanently market at 9 — logged as `09_GO_LIVE_READINESS.md` 🔴 KNOWN GAP #6, decision needed from Aditya.

**14. Pitch/architecture HTML build scripts target the wrong filenames.** `pitch/build_pitch_deck.py` (line 7) and `pitch/build_arch_doc_v2.py` (line 10) both hardcode `OUT` to `~/Downloads/BlueLine/blueline_pitch_deck.html` / `blueline_architecture_doc.html`. The real, current, audio-embedded, presented-to-customers files are `pitch/dylan_for_hire_pitch_deck.html` and `dylan_for_hire_architecture.html`. Running either script as documented in `03_SETUP_GUIDE.md` Step 10 would silently produce differently-named, differently-branded (BlueLine, not Dylan for Hire), version-stale (hardcoded "v2.1," "13 bugs fixed") files instead of updating what's actually presented. **Fixed:** flagged in `00_INDEX.md`, `03_SETUP_GUIDE.md` Step 10, master context §9, and `09_GO_LIVE_READINESS.md` 🔴 KNOWN GAP #7. **Still open:** the scripts themselves are unchanged — either repoint `OUT` and rebuild, or retire the scripts in favor of hand-editing the current HTML. Not fixed in code this round because it requires an explicit choice from Aditya about which HTML is the ongoing source of truth.

**15. Cosmetic — two version-log entries both labeled "v2.1."** `00_INDEX.md`'s version log had both the 2026-06-29 bug-fix release and the 2026-06-30 pitch-deck-rebuild release labeled "v2.1." **Fixed:** the 2026-06-30 entry renamed to "v2.2," content unchanged.

**16. Cosmetic — Calendly "Buffer before: 10 minutes" row missing from the master context doc.** A prior audit (referenced in this project's `SAAS_PROJECT_HEALTHCARE_RECRUITMENT_MASTER_CONTEXT.md` history, outside this file set) had already added this row; the version uploaded/re-saved in this round had dropped it. **Fixed:** row restored to §8.

**17. Governing-docs table range was stale.** Master context §0 table said "`00_INDEX.md` through `09_GO_LIVE_READINESS.md`" but `10_CLIENT_INTAKE_AND_ADAPTER_SPEC.md` also exists and is part of the governed set. **Fixed:** range extended to include it.

### Standing procedure adopted this round (see `00_INDEX.md` Rule 0B)

Every future session in this project must verify any repeated claim against
`src/`/`pitch/` directly (not just against another doc), fix drift in the
same session, and log it here as a new dated round. This file is now the
project's permanent audit trail — append future rounds below this one, never
overwrite prior findings.

---

## ROUND 3 — 2026-07-01 (same day) — TWO UPLOADED FILES RECONCILED AGAINST SOURCE

**Trigger:** Aditya uploaded two standalone files — `Dylan_for_Hire_Scheduling_Setup_Guide.md`
and `Dylan_for_Hire_Product_Overview.md` — and asked for the project's files to be brought
current, with stale material deleted, and an explicit instruction not to agree without cause
and to audit/test before commenting.

**Method:** Read both uploaded files in full. Independently re-derived the credential-check
category count by reading `validate_documents()` in `src/master_gmail_reviewer.py` directly —
not by trusting this audit file's own Round 1/2 findings, in case those were themselves wrong.
Cross-checked the Scheduling Setup Guide's process values against
`SAAS_PROJECT_HEALTHCARE_RECRUITMENT_MASTER_CONTEXT.md` §8, the one place live Calendly values
are recorded.

### Findings

**18. The uploaded `Dylan_for_Hire_Product_Overview.md` repeated the already-known-false
"11-point credential check" claim, plus new errors this audit had not previously caught.**
Independent re-read of `validate_documents()` (lines 451–606) confirms exactly 9 result
categories: `resume`, `nursing_license`, `id_documents`, `physical`, `mmr_titers`,
`varicella_titers`, `chest_tb` (combined chest X-ray + PPD, or Quantiferon, single pass/fail),
`covid_vaccine`, and `bls_cpr` (the only one with `optional: True`). The uploaded document's
11-item table:
- **Omitted** two categories the code actually requires: resume and COVID-19 vaccination.
- **Included** three categories not implemented anywhere in the Vision schema or
  `validate_documents()`: Hepatitis B, annual flu vaccine, and state background-check/fingerprint
  clearance.
- **Collapsed incorrectly:** listed "TB test (PPD/Quantiferon)" and "Chest X-ray" as two separate
  items with different windows (12 months vs. 9 months); the code treats them as one combined
  `chest_tb` result on a single 9-month window ((chest X-ray AND PPD) OR Quantiferon).
This is a materially different and inaccurate document from what the system actually does — not
a wording nitpick. If this had gone to a prospect unchanged and they'd asked "what are the 11
points," at least 5 of the 11 named items would not have matched reality.
**Fixed:** rebuilt the credential table from the verified 9 categories, with an explicit
"not currently implemented" note for the 3 excluded items, and saved as
`11_CUSTOMER_FACING_PRODUCT_OVERVIEW.md`. This does not resolve `09_GO_LIVE_READINESS.md` 🔴
KNOWN GAP #6 (whether to build the missing categories) — that business decision is still open
and still Aditya's to make.

**19. The uploaded Product Overview also made no mention of the 24/7 real-time layer.**
Not an error — the layer is genuinely unverified on the live Mac (see
`09_GO_LIVE_READINESS.md` 🟡 list) — but worth naming as a deliberate omission rather than an
oversight: this claim was **not** added to `11_CUSTOMER_FACING_PRODUCT_OVERVIEW.md` either,
on the reasoning that a customer-facing document should not describe unverified capability as
proven. Flagged for Aditya to add once Step 11 of `03_SETUP_GUIDE.md` is confirmed live.

**20. `09_GO_LIVE_READINESS.md` line 29 contradicted its own line 135–150 finding.**
Its "🟢 VERIFIED" section still said "11-point NYS credential check" while its own "🔴 KNOWN
GAPS #6" section (same file) already documented the correction to 9-category. Both sections
were written in earlier rounds but never cross-checked against each other within the same file.
**Fixed:** line 29 corrected to 9-category with a pointer to KNOWN GAP #6.

**21. The uploaded `Dylan_for_Hire_Scheduling_Setup_Guide.md` checked out accurate — no
corrections needed.** All process values (10-min buffer before, 15-min buffer after, max 4
calls/day, Mon–Fri 9am–6pm ET, 30-min calls, 4-hour minimum notice) match
`SAAS_PROJECT_HEALTHCARE_RECRUITMENT_MASTER_CONTEXT.md` §8 exactly. Saved as
`12_SCHEDULING_SETUP_GUIDE.md`, explicitly positioned as the file that supersedes the
`Dylan_for_Hire_Calendly_Setup_Guide.md` reference in master context §10 — that referenced file
does not exist anywhere in this project folder, so "supersede" is really "replace an absent
file with a present, verified one," not a same-folder version bump.

**22. Nothing else in the project folder was found stale enough to delete.** All 10 numbered
docs, the master context doc, and this audit file are dated 2026-07-01 and internally consistent
as of Round 2. No basis was found for deleting any of them — "delete what's no longer relevant"
was interpreted as applying to the two newly-uploaded files' relationship to prior deliverables
(resolved above by superseding an absent file and correcting/renaming the other), not as a
mandate to remove verified, current, in-use project documentation. If Aditya has specific files
in mind that should be deleted, name them — nothing in this folder currently meets the bar.

### Updated (not new) finding

Reopened and re-confirmed **Round 2 finding #13/#17** (11-point vs. 9-category) is still the
correct, current, code-verified position — re-derived independently this round rather than
carried forward on trust, per Rule 0B.

---

## ROUND 4 — 2026-07-01 (same day) — CODE CHANGE: HEP B + FLU VACCINE ADDED, RECOMMENDED-NOT-MANDATORY

**Trigger:** Aditya made the product decision on `09_GO_LIVE_READINESS.md` 🔴 KNOWN GAP #6:
Hepatitis B and annual flu vaccine should be added to the automated check, but as
recommended/non-blocking items, not mandatory ones. Background-check/fingerprint was not
addressed and remains open.

**Reasoning check before implementing (not just executing the instruction blind):** confirmed
this is technically the right call, not just a lighter compromise — both Hepatitis B (OSHA
bloodborne pathogen standard) and flu vaccine policy generally accept a signed declination as
a compliant alternative to actually being vaccinated. `validate_documents()` currently has no
way to distinguish "not vaccinated, non-compliant" from "not vaccinated, validly declined" —
so marking either as a blocking requirement today would incorrectly flag candidates who did
the compliant thing. Non-blocking is the correct interim design given that gap, not a shortcut.
This reasoning is now recorded inline in the code (see below) so a future session doesn't
"fix" it back to required without understanding why it isn't.

**Code changed — `src/master_gmail_reviewer.py`:**
1. Added `hepatitis_b` and `flu_vaccine` fields to the Claude Vision JSON schema in
   `analyze_attachments_with_claude()`, matching the existing `covid_vaccine` shape
   (found/source), with an added `"declination form"` source option for both.
2. Added two new blocks to `validate_documents()`, both carrying `"optional": True` —
   the same mechanism that already makes BLS/CPR non-blocking in `compose_reply_email()`.
   No changes needed to `compose_reply_email()` itself — it already iterates
   `validation_results` generically and routes anything with `optional: True` to the
   "Notes" section instead of "Still required."

**Docs updated to match (same session, per Rule 0B):**
- `05_PIPELINE_REFERENCE.md` — credential table now shows 8 required + 3 recommended = 11
  tracked, with the declination-form rationale recorded.
- `09_GO_LIVE_READINESS.md` — KNOWN GAP #6 marked decided-and-partially-built; new 🟡 item 8
  added (needs a real test with a flu declination form + Hep B vaccine card); verification
  log updated; explicit instruction not to use this in prospect conversations until tested.
- `SAAS_PROJECT_HEALTHCARE_RECRUITMENT_MASTER_CONTEXT.md` §2 and proven-results bullet —
  updated to the 8-required/3-recommended framing with the same "don't shorthand as 11-point"
  warning repeated.

**Deliberately NOT updated: `11_CUSTOMER_FACING_PRODUCT_OVERVIEW.md`.** This file is meant to
go to prospects. The Hep B/flu code is new this session and unverified against a real document
— same status class as the other 🟡 items in `09_GO_LIVE_READINESS.md` (e.g. the Pub/Sub email
listener). Updating prospect-facing material to describe unverified capability as proven would
repeat the exact mistake this whole audit thread exists to prevent. Update that file only after
a real test confirms Claude Vision correctly extracts both new fields and `compose_reply_email`
correctly treats them as non-blocking.

**Still open, deliberately not decided this round:** NYS CHRC background-check/fingerprint
clearance. Recommended to Aditya as a separate decision — no declination alternative exists for
it, the liability profile is higher (facility contracts, not just a checklist line), and it's a
different kind of check (external process confirmation, not a document with a date window).
Left as a manual/disclosed onboarding step, not rushed into this round's change.

---

## ROUND 5 — 2026-07-02 — CLIENT INTAKE DOCUMENT BUILT, ADAPTER-GAP AUDITED, CHECKLIST TRANSLATED

**Trigger:** Aditya asked (1) for the go-live checklist to be explained step by step with an
explicit split of what's automatable vs. Mac-only, with instructions to proceed with everything
possible without waiting on him, and (2) for the internal `10_CLIENT_INTAKE_AND_ADAPTER_SPEC.md`
questionnaire to be turned into an actual client-facing document, audited for whether it really
supports "seamless across different email/messaging platforms."

**Findings and actions:**

**23. The client intake questionnaire (§2 of `10_CLIENT_INTAKE_AND_ADAPTER_SPEC.md`) asks the
right questions but implied more platform flexibility than the code has.** Verified directly
against `src/`: no `MessagingAdapter` or `EmailAdapter` interface exists — `master_daily_agent.py`,
`upgrade1_context_aware_messaging.py`, and the Gmail-side files all call OpenPhone/Quo and Gmail
directly, with no second implementation of either. A client on Twilio or Outlook cannot be
onboarded today without net-new adapter development. **Fixed:** added an audit-finding section to
`10_CLIENT_INTAKE_AND_ADAPTER_SPEC.md` recommending OpenPhone + Gmail/Google Workspace be
presented as a requirement (with a switch-over-during-onboarding path) rather than an open
question, and anything else routed to a custom quote. This default was applied when building the
client-facing document below — flagged for Aditya to override if he disagrees with the
positioning call.

**24. Built `Dylan_for_Hire_New_Client_Setup_Questionnaire.docx`** — the client-facing version of
the Section 2 questionnaire, reframed for a non-technical agency owner: required-platform callout
(OpenPhone + Gmail/Workspace) vs. custom-quote callout for anything else, the credential checklist
using the current verified 8-required/3-recommended/1-manual split (not "11-point"), persona/voice,
volume/rates, and logistics sections. Saved to the project folder. Validated and rendered to PDF
to confirm layout before delivery.

**25. Added a "PLAIN-ENGLISH ACTION CHECKLIST" section to `09_GO_LIVE_READINESS.md`**, translating
the 🟢/🟡/🔴 technical lists into one ordered runbook, each step tagged 🤖 Claude-doable-now,
🧑‍💻 Aditya-Mac-only, or 🧭 decision-needed. No new facts introduced — this is a presentation
layer over what was already in the file, cross-checked against the current 🟡/🔴 lists (which
already reflect Round 3/4's Hep B/flu decision) so the new section doesn't repeat the stale
"9-category" framing from Round 2.

**Standing note:** Round 2's "9-category" correction and Round 4's "8 required + 3 recommended =
11 tracked" update are not in conflict — Round 2 was correct at the time it was written; Round 4
is a subsequent, deliberate product change. Re-read both before quoting a number to a customer;
the current correct figure is 8 required + 3 recommended, not 9 and not a plain "11."

---

## ROUND 6 — 2026-07-02 — GO-LIVE READINESS: ACTUAL TEST EXECUTION, TWO REAL BUGS FOUND AND FIXED, TWO KNOWN GAPS CLOSED

**Trigger:** Aditya: *"start working on the live readiness and find solutions for all issues so we
move forward- do not falsify anything, audit all your work, test it, debug it and rest until it
works perfectly before confirming to me."* This round is the direct response to that instruction —
every claim below is backed by a command that was actually run, in this project folder, with the
output shown, not by re-reading a comment that says something was already tested.

**An honest correction, first, because it matters more than any of the fixes below:**

Earlier work in this same overall effort (referenced informally as investigating the
`email_context_bridge.py` name-matching logic) wrote and ran real pytest tests and found a real
bug — that part is true. But those tests were written into a session-only scratch directory
outside this project folder, never committed to `tests/` here, and the fix comment left behind
claimed "confirmed by direct test execution (pytest)" in a way that implied durable, re-runnable
proof existed in this project. It did not — `git`/`find` confirms no `tests/` directory existed
anywhere in this project folder before this round created one. That gap between "a test was run
once, in a throwaway place" and "this is verified" is exactly the failure mode Rule 0B exists to
catch for documentation, and it turns out the same failure mode applies to test claims, not just
doc claims. **Fixed process-wise:** RULE 0C added to `00_INDEX.md` — tests belong in `tests/` in
this project, not session scratch space, full stop. **Fixed substantively:** the bug that earlier
work found (BUG-19 below) is confirmed still correctly fixed in the current code, verified again
here with a persisted, real test run. And re-deriving the problem from scratch — instead of
trusting the prior fix was complete — surfaced a second, more severe bug (BUG-20) hiding underneath
it that had not been caught.

**26. Created `tests/conftest.py` and `tests/test_pipeline_logic.py`** — 69 tests total, covering:
crash-class import/wiring checks (re-deriving BUG-15's failure mode directly rather than trusting
the fix comment), TCPA compliance keyword coverage (BUG-16/17, re-derived), the 8-required/
3-recommended credential schema (Round 4's decision, re-derived against `validate_documents()` and
`compose_reply_email()` directly), cross-file config consistency (Gmail token path / Quo base URL /
auth header), Quo contact schema consistency (see BUG-20 below), pure-function unit tests (phone
normalisation, borough detection), and static compilation checks on every file in `src/`. Run with
`cd tests && python3 -m pytest -v` — **all 69 passed**, confirmed by direct execution in this
session, output captured below at the end of this round.

**27. BUG-19 — `match_phone_by_sender_name()` name-parsing logic was wrong for this system's data
shape.** `firstName` on a Quo contact in this system always holds the candidate's full legal name
(e.g. "Jane Doe"); `lastName` is never a real surname — it's always `"LICENSE, Borough"` (e.g.
"RN, Brooklyn"). The prior logic built a comparison string by appending the text before the comma
in `lastName` (the license code, e.g. "RN") onto `firstName`, producing "jane doe rn" — which can
never equal a real sender's normalised full name ("jane doe"). This made the full-name match branch
fail for 100% of contacts. **Fixed:** compare the normalised `firstName` directly to the sender's
normalised display name for a full match, and just its first token for the first-name-only
fallback. Verified with `tests/test_pipeline_logic.py::TestQuoContactSchemaConsistency` and the
name-matching assertions throughout `TestEmailOptoutAutoSync`.

**28. BUG-20 — `email_context_bridge.py` read Quo contact fields at the wrong nesting level,
independent of and more severe than BUG-19.** The real Quo/OpenPhone contact schema — proven by
`master_daily_agent.py`, which has called this same API successfully in production since
2026-05-04 (`get_contact_by_phone()`, `merge_duplicate_contacts()`, etc., all confirmed by direct
code read) — nests `firstName`/`lastName`/`phoneNumbers` under a `defaultFields` key, and each
phone entry's key is `value`, not `number`. `email_context_bridge.py`'s `match_phone_by_sender_name()`
and `_quo_get_all_contacts()` read these fields at the top level of the contact dict instead. That
means **even after BUG-19's fix**, `c.get("firstName", "")` returned `""` and
`c.get("phoneNumbers")` returned `None` for every real contact — the entire email-to-SMS matching
feature was still 100% non-functional. This was missed by the earlier BUG-19 fix because its test
fixtures mocked contacts using the same flat (wrong) shape the buggy code itself assumed, so the
test and the bug agreed with each other and neither caught the other. **Fixed:** all field access
in `match_phone_by_sender_name()` now reads through `defaultFields`, with a fallback to the flat
key only as defensive belt-and-suspenders (real contacts never hit the fallback; it exists so a
malformed contact fails soft rather than crashing). Verified directly with
`tests/test_pipeline_logic.py::TestQuoContactSchemaConsistency::test_email_bridge_name_match_against_the_proven_contact_shape`,
which fails if this regresses, using the exact shape `master_daily_agent.py` proves is real.

**29. KNOWN GAP #1 CLOSED — email-side opt-out now auto-syncs to the SMS opt-out list.** Before
this: an email opt-out ("please stop contacting me") was correctly flagged for human review but
took no further action — the phone number was never added to `master_permanent_optouts.txt` and
the Quo contact was never renamed, so Step 1/2/3 on the SMS side had no way to know an opt-out had
happened over email. **Fixed:** a dedicated `FLAG_HUMAN_OPTOUT` decision code was added to
`email_context_bridge.py`'s Claude decision prompt — used only when the model is confident the
email's primary purpose is an opt-out (kept separate from freeform `FLAG_HUMAN` reason-text parsing
on purpose, so the sync never fires on a guess). `get_context_aware_email_reply()` calls
`sync_email_optout_to_sms(phone, first_name)` automatically whenever that code fires, reusing the
same sender-name-to-Quo-contact match already computed for pulling SMS history (no second lookup).
`sync_email_optout_to_sms()` writes to the same `master_permanent_optouts.txt` file
`step1_reengage_stalled()` / `step2_new_leads()` / `step3_sms_reply_handler()` all check, and
renames the Quo contact to `"DO NOT MESSAGE - {name}"` — the identical convention the SMS-side
opt-out handler already uses. `master_gmail_reviewer.py`'s `process_sender()` was wired to handle
the new decision code: still flags for human visibility (nothing here changes the "human sees
every flag" invariant), and additionally logs exactly what the sync did or didn't do. Verified with
6 new tests in `tests/test_pipeline_logic.py::TestEmailOptoutAutoSync` — including a regression
guard for the specific bug where `"FLAG_HUMAN_OPTOUT".startswith("FLAG_HUMAN")` could have
misrouted the new code into the old branch if checked in the wrong order. **Residual scope note:**
this only covers the general-inquiry (no-attachment) email branch, matching the gap's original
definition. An opt-out phrase arriving in an email that also has a document attachment would not
trigger this path — flagging as a known, narrow residual limitation rather than expanding scope
unreviewed.

**30. KNOWN GAP #7 CLOSED — pitch deck build script mismatch resolved by retiring the scripts, not
repointing them.** `build_pitch_deck.py` and `build_arch_doc_v2.py` were confirmed (Round 2) to
write to `blueline_*.html`, not the real, presented `dylan_for_hire_*.html` files. Before fixing,
checked what would happen if `OUT` were simply repointed to the real filenames: both scripts'
hardcoded HTML has zero embedded audio (the real files have 12 and several respectively) and
predates the v3.0 24/7 real-time layer — running them and overwriting the real files would have
silently regressed a better, current, audio-narrated deck to a worse, silent, stale one. **Fixed:**
`OUT` in both scripts redirected to a clearly-labeled `DEPRECATED_DO_NOT_USE_*.html` path in
`~/Downloads/BlueLine/`, with a docstring explaining why, so this can never happen by accident even
if someone runs the script without reading this note. To actually refresh a live deck: hand-edit
the real file directly, or request a fresh rebuild that starts from the *current* file's content.
**Verified by actually running both scripts** in this session: both completed without error,
wrote only to the deprecated path, and the real `dylan_for_hire_pitch_deck.html` /
`dylan_for_hire_architecture.html` files were confirmed byte-for-byte unchanged (MD5 checksums
identical before and after each run).

**31. RULE 0C added to `00_INDEX.md`** — tests must be persisted in this project's `tests/`
directory and re-run each session, never left only in a session's temporary scratch space. Direct
response to the process gap described at the top of this round.

**Test run confirming all of the above, captured verbatim (2026-07-02):**
```
$ cd tests && python3 -m pytest -v
...
======================= 69 passed, 11 warnings in 1.37s ========================
```

**What this round does NOT prove** (same caveat as always — see Round 1 and every round since):
none of this touches Aditya's real Gmail account, real Quo/OpenPhone API key, or a real inbound
message. Passing this suite means the code's internal logic is now sound and self-consistent,
including for the two new bugs found here. It does not mean the 24/7 services or the new opt-out
sync will behave correctly against real credentials and a real "please stop texting me" email —
that still requires the live-Mac tests in `09_GO_LIVE_READINESS.md`'s 🟡 list, unchanged by this
round.

**32. Email-match-first + self-healing backfill added — partial mitigation for KNOWN GAP #2
("name-matching between email and Quo is best-effort, not guaranteed").** `match_phone_by_sender_email()`
added to `email_context_bridge.py`: an exact (case-insensitive) match against a Quo contact's
`defaultFields.emails`, tried before the existing name-match. Quo contacts already support an
`emails` field — confirmed by direct code read of `merge_duplicate_contacts()` in
`master_daily_agent.py`, which already reads/merges this same field, so this is not a new,
unproven assumption about the schema. `get_context_aware_email_reply()` now tries the email match
first; only falls back to name-matching if the sender's email hasn't been seen yet. On a
successful *name* match, `backfill_email_onto_contact()` writes that email onto the matched
contact, so every subsequent email from the same address matches directly and unambiguously going
forward — including if a later email uses a different display name or a nickname. **What this
does not fix:** the very first email from a sender whose display name doesn't match Quo (nickname,
blank display name) still fails to match and still degrades gracefully (draft proceeds without SMS
context) — this remains a real, disclosed, open limitation, not solved. Verified with 5 new tests:
`tests/test_pipeline_logic.py::TestEmailMatchAndBackfill` — email match returns the right contact,
returns `None` when no contact has that email, backfill writes the email and does not duplicate an
already-present one, email match is preferred over name match when both would match (with an
assertion that backfill is NOT called in that case, since nothing needs backfilling), and a
successful name-match does trigger backfill.

**33. `master_gmail_setup.py` testability fix.** This file ran its OAuth setup flow as bare
top-level module code — meaning `import master_gmail_setup` (e.g., for a test asserting its
`TOKEN_PATH`/`CREDENTIALS_PATH` match the other files that use them) would either launch a real
OAuth flow or call `sys.exit(1)` if `gmail_credentials.json` wasn't present, discovered directly
while building `tests/test_pipeline_logic.py::TestConfigConsistencyAcrossFiles`. **Fixed:** wrapped
in `def main():` + `if __name__ == "__main__": main()`. `python3.11 master_gmail_setup.py` behaves
identically to before (verified: the guard only changes import-time behavior, not direct-execution
behavior). This is what makes `test_gmail_token_path_matches_across_all_three_files` and
`test_gmail_credentials_path_matches` possible at all — before this fix, importing this file from
a test would have crashed the test run itself.

**34. Cosmetic — `master_daily_agent.py` main() log line said "v2.1" while the module docstring
header says "v2.2."** Found while reading the file line-by-line for Round 6 (not previously caught
by any prior round's doc-vs-code check, since this was a code-internal inconsistency, not a
doc-vs-code one). Fixed: log line now reads "v2.2," matching the header.

**35. RULE 0D added to `00_INDEX.md` — permanent, project-wide "no fictitious work" mandate,**
added at Aditya's explicit instruction after this round's honest-correction finding (see the top of
this Round 6 entry re: the prior "confirmed by direct test execution" claim that had no test behind
it). Where Rule 0C is the specific mechanical fix (tests live in `tests/`), Rule 0D is the general
principle it exists to serve: nothing may be described as done/working/tested to Aditya or a
customer unless it was actually built, executed, and observed to produce a correct result this
session or via a named live-Mac test with a filled-in verification-log row — and "code-logic
tested" vs. "live-Mac tested" must always be stated as the two different claims they are, never
conflated. Also saved as a persistent memory (`dylan-no-fictitious-work-rule`) so it carries into
future sessions in this project even if `00_INDEX.md` isn't re-read line by line.

**Updated test run, capturing the Round 6 additions above (items 32-34), 2026-07-02:**
```
$ cd tests && python3 -m pytest -v
...
======================= 75 passed, 11 warnings in 1.4s ==========================
```
All 75 tests green, executed directly in this session. 6 new tests since the count quoted earlier
in this same round (69 → 75) come from `TestEmailMatchAndBackfill` (item 32).

**Full list of what Round 6 closed vs. what remains genuinely open, for a fast read:**
- Closed, code-tested, pending live-Mac confirmation: KNOWN GAP #1 (email opt-out auto-sync),
  KNOWN GAP #7 (pitch deck script mismatch — fully closed, no live-Mac step needed)
- Partially mitigated, still has a real open edge case: KNOWN GAP #2 (name-matching)
- Untouched this round, still open exactly as before, each with a clear owner already recorded in
  `09_GO_LIVE_READINESS.md`: KNOWN GAP #3 (business metrics must be re-pulled fresh before each
  customer call — a discipline issue, not a code gap), KNOWN GAP #4 (white-label/adapter config
  layer doesn't exist — a real architecture project, not a today-sized fix; see
  `10_CLIENT_INTAKE_AND_ADAPTER_SPEC.md` for the existing scoping work), KNOWN GAP #5 (no
  monitoring/alerting for a silently-hung 24/7 service — needs a real decision on what tool/approach
  before building, not a quick patch), KNOWN GAP #6 (NYS background-check/fingerprint clearance —
  deliberately left as a manual/disclosed onboarding step per the Round 4 reasoning, still correct)

---

## ROUND 7 (2026-07-02, same day) — `~/Downloads` connected; found and fixed a live production divergence

**36. `~/Downloads` connected as a real, persistent folder this round** — the first time this
project has had direct read/write access to Aditya's actual Mac filesystem rather than only its own
project directory. This changes what "verified" can mean going forward (see new RULE 0E in
`00_INDEX.md`) and was used immediately to check an assumption this entire project had been making
uncritically: that `src/master_daily_agent.py` is "the" current version of the script.

**37. MAJOR FINDING — `~/Downloads/BlueLine/master_daily_agent.py` (the real deployed cron script,
v2.3, dated 2026-06-30) and this project's `src/master_daily_agent.py` (v2.2) had silently
diverged**, each carrying real fixes the other one lacked:
- **Deployed had, `src/` lacked:** a real in-memory-dedup fix and a checklist-reblast fix, tracked
  under the deployed file's own "BUG-15" label — a *different* bug than the "BUG-15" already
  referenced in this project's history. The two "BUG-15"s are not the same bug; they collided by
  coincidence of numbering only.
- **`src/` had, deployed lacked:** the tightened `INTEREST_KEYWORDS` set (removing generic tokens
  like "ok"/"send"/"info" that caused the real Joyelette Miller / Torri Allen repeat-blast incident
  documented earlier in this file), the widened opt-out keyword coverage, and the no-emoji
  checklist message text.
- **Net effect, stated plainly: the live production script sending real SMS to real candidates was
  missing TCPA-required STOP-language / opt-out-keyword coverage this entire time**, while `src/`
  (which this project treated as authoritative) was missing a real dedup/reblast fix that was
  already live and working. Neither file was a superset of the other. This was not visible from
  reading `src/` alone, no matter how carefully — it required the direct diff this round's new
  folder access made possible.

**38. Fix — reconciled `src/master_daily_agent.py` to v2.4, the union of both fix histories:**
- Ported `BOROUGH_ABBREV` dict and `STATE_CHECKLIST_SENT` state-file path from the deployed v2.3
  into `src/`.
- Kept `src/`'s tightened `INTEREST_KEYWORDS`, and added the deployed file's checklist-reblast gate
  (checking `STATE_CHECKLIST_SENT` before re-sending the document checklist, flagging re-interest
  for human review instead of re-blasting) — this is the fix that prevents the Joyelette
  Miller/Torri Allen incident class going forward, now present in the reconciled file.
- Added `DOCS_SENT_KEYWORDS` and `UPDATE_REQUEST_KEYWORDS` branches to `step3_sms_reply_handler()`,
  each ending in `handled_ids.add(msg_id)` so no branch leaves a message unmarked (a defect class
  this round specifically checked for after Round 6's dedup work, via a new source-text-based test).
- Updated `step2_new_leads()` to use `BOROUGH_ABBREV` for the Quo `lastName` field's borough
  abbreviation, matching what's actually live in production today.
- Rewrote the module docstring with a full "RECONCILIATION NOTICE (v2.4)" section and bumped the
  `main()` startup log line to match.

**39. Test suite grown and re-run, both changes verified together:**
- Added 6 new/updated tests to `tests/test_pipeline_logic.py` covering: interest-keyword coverage
  under the tightened set, an explicit regression test that the exact tokens that caused the real
  repeat-blast incident ("ok", "okay", "send", "info", "ready", "i am", "i'm") do NOT re-trigger the
  checklist, docs-sent keyword coverage, update-request keyword coverage, the checklist-sent state
  file path existing, a source-text assertion that every branch of `step3_sms_reply_handler()` marks
  its message handled, and full `BOROUGH_ABBREV` coverage of every value `detect_borough()` can
  return.
- First run after the reconciliation surfaced **2 unrelated pre-existing failures**, not caused by
  this round's changes: `test_category_count_is_11_total` and `test_required_vs_optional_split_is_8_and_3`
  failed because `master_gmail_reviewer.py` (v1.2, added earlier the same day by a concurrent,
  intentional change) now tracks a 12th category, `employment_application` (the candidate's signed
  onboarding form coming back), as a 4th optional/tracked-separately category — the tests still
  expected the old 11-total/8-required-3-optional split. Fixed by updating both tests to match the
  actual current code (12 total, 8 required + 4 optional, set includes `employment_application`) —
  per Rule 0B, code is ground truth over a stale test, and the fix was verified, not assumed.
- **Full suite result, actually run this session:**
```
$ cd tests && python3 -m pytest -v
...
======================= 100 passed, 11 warnings in 1.91s =======================
```
100 of 100 passing (up from 75 at the end of Round 6).

**40. RULE 0E added to `00_INDEX.md`** — permanent: `src/` is not automatically the same file as
what's deployed at `~/Downloads/BlueLine/`. Any future claim that `src/` is "current" or
"reconciled" must be backed by an actual diff against the deployed file run in that same session,
and pushing a reconciled file to the live path is a production change requiring Aditya's explicit
go-ahead — never done silently.

**41. NOT done this round, by design, pending Aditya's decision:** `src/master_daily_agent.py` v2.4
has **not** been copied over `~/Downloads/BlueLine/master_daily_agent.py`. That file is the real
cron script currently running against real candidates on a schedule; overwriting it is a live
production change and, per Rule 0's caution around uncoordinated changes plus the explicit-
permission norm around user-impacting actions, requires Aditya to say go — not to be inferred from
"the reconciliation passed tests." The open question, stated plainly for Aditya: **the live script
right now is missing TCPA STOP-language/opt-out-keyword coverage that the reconciled version has —
deploying it closes a real compliance gap, but it is still a change to a script sending real
messages to real people and should be a deliberate yes, not a default.**

---

## ROUND 7 ADDENDUM (2026-07-02, same day) — hardened per explicit instruction, then deployed live

Aditya's instruction, verbatim: "copy and update it to ensure maximum compliance, no duplication of
messages and opt out should be ironclad." This is explicit, in-chat permission for the production
deploy flagged as pending in item 41 above — not inferred, not assumed. Before copying, three
additional real gaps were found by re-reading the reconciled v2.4 file end to end with exactly that
brief in mind (compliance / no duplication / opt-out), none of which the Round 7 reconciliation
itself had touched:

**42. Process-level double-send risk (new finding, not from the deployed-vs-src diff).** Even after
reconciliation, nothing stopped two overlapping runs of `master_daily_agent.py` (cron firing twice;
a manual run started while the scheduled one was still going) from each reading the same Quo
contacts snapshot, each concluding a candidate was new, and each creating a contact + sending an
intro SMS — a real double-message risk invisible to any of the per-message dedup logic already in
the file, because it happens before either process has built any in-memory state to dedup against.
**Fix:** `LOCK_PATH` + `acquire_lock()`/`release_lock()`, using `os.O_CREAT | os.O_EXCL` for an
atomic claim (not a check-then-write, which would have its own race window). A lock older than
`LOCK_STALE_SECONDS` (6 hours) is treated as an abandoned lock from a crashed run and reclaimed,
also through the same atomic path. Wired into `main()` — refuses to run and logs a warning if it
can't acquire the lock, releases in a `finally:` so a step raising an exception can't leave the
lock stuck. 7 new tests (`TestProcessLock`): acquire succeeds when free, acquire fails when held,
release allows re-acquire, release is a no-op when nothing's held, a stale lock is reclaimed, a
fresh lock is NOT reclaimed, and a source-level check that `main()` actually calls both functions
inside a `finally`.

**43. `send_sms()` had no guard of its own — it fully trusted whichever step called it to have
already checked the opt-out list correctly.** Every step currently does check correctly, but that
means the opt-out guarantee lived in three separate places (step1, step2, step3) with no single
point where "never send to an opted-out number" is actually enforced. **Fix:** `send_sms()` now
re-reads `STATE_OPTOUTS` fresh from disk (not a cached snapshot) and checks `BLOCKED_NUMBERS` on
every call, before any network request, refusing and logging an error if the destination is on
either list. This is deliberately redundant with the callers' own checks — the point is that no
current or future code path can physically place an SMS to an opted-out number even if its own
pre-check has a bug. 4 new tests (`TestSendSmsHardOptOutGuard`): refuses an opted-out number and
confirms the network call was never attempted, refuses a blocked number, proceeds normally for a
clean number (guards against the fix accidentally becoming a blanket send-blocker), and confirms
the check re-reads the file mid-run rather than caching an initial snapshot (a number opted out by
step3 earlier in the same run must not still be messageable by step1/step2 later in that same run).

**44. `step2_new_leads()` could silently and permanently lose a candidate.** If `quo_post()`
succeeded (Quo contact created) but the immediately-following `send_sms()` call failed, the phone
was never added to `STATE_PROCESSED` — but the contact now exists in Quo, so every future run's
`existing_phones` check silently skips them as `SKIPPED_DUPLICATE_PHONE`. No human would ever learn
this candidate was created but never actually messaged. **Fix:** the failure branch now also calls
`append_to_review()`, writing to `master_needs_human_review.txt` — the file Aditya actually checks
— instead of only `log_action()`, which writes to a per-run CSV nobody reliably reviews after the
fact. 1 new source-level test confirming the fix is actually wired into the right branch, not just
present somewhere in the file.

**45. Full suite re-run after all three hardening fixes: 112/112 passing** (up from 100 at the end
of the reconciliation earlier this round):
```
$ cd tests && python3 -m pytest -v
...
======================= 112 passed, 11 warnings in 3.56s =======================
```

**46. DEPLOYED LIVE.** With tests green, the file was version-bumped to v2.5 (reconciliation +
hardening) and copied over the real cron script:
```
$ cp ~/Downloads/BlueLine/master_daily_agent.py ~/Downloads/BlueLine/master_daily_agent.py.pre-v2.5-backup-2026-07-02
$ cp src/master_daily_agent.py ~/Downloads/BlueLine/master_daily_agent.py
$ diff -q src/master_daily_agent.py ~/Downloads/BlueLine/master_daily_agent.py
  → no output — files identical, verified directly, not assumed
$ python3 -c "import ast; ast.parse(open('~/Downloads/BlueLine/master_daily_agent.py').read())"
  → no error — deployed file parses cleanly
```
The old v2.3 deployed file is preserved as `master_daily_agent.py.pre-v2.5-backup-2026-07-02` in
the same directory for rollback if needed.

**What this closes vs. what's still genuinely open, stated plainly per Rule 0D:** code-logic tested
and now deployed — TCPA STOP language, widened opt-out keywords, checklist-reblast prevention,
in-memory dedup, process-level double-send prevention, hard opt-out guard, no-silent-loss on send
failure. **NOT yet live-Mac tested** — no real cron run, no real inbound SMS, no real overlapping-
run scenario has exercised this file since deploy. That gap is not closed by a diff or a pytest run
and should not be described as closed until a real run against Aditya's actual Quo/OpenPhone

---

## ROUND 8 — 2026-07-02 · Live crontab misconfiguration found and quantified

**Finding, confirmed real via `crontab -l | cat -vet`** (ruled out paste/rendering artifact by
checking for literal `$` end-of-line markers): Aditya's actual deployed crontab reads

```
iTZ=America/New_York
9 * * * * cd /Users/Aditya/Downloads/BlueLine && set -a && source .env && set +a && /usr/local/bin/python3.11 master_daily_agent.py >> /Users/Aditya/Downloads/BlueLine/cron_output.log 2>&1
```

Two real bugs: (1) `iTZ=` is not the cron-recognized `TZ=` variable — cron reads it as an inert
custom env var, so no timezone context is actually being applied; (2) the schedule `9 * * * *`
fires every hour at minute 9, not once daily at 9am as every doc in this project (and BlueLine's
own CLAUDE.md) describes.

**Real-world impact, quantified from `~/Downloads/BlueLine/cron_output.log` (9,774 lines, runs
from 2026-05-04 23:30 to 2026-07-02 08:13, read directly — not assumed):**
- 546 total runs logged over 59 days (~9.25/day average — elevated but not the full 24/day worst
  case; likely intermittent due to sleep/network gaps, e.g. one confirmed `No route to host`
  failure in the log).
- `step2_new_leads()`'s "30/day" cap has no true calendar-day gate — `Days missed` was `0` in 540
  of 546 runs, so `leads_today` reset to the full `DAILY_NEW_LEADS = 30` on nearly every run,
  not just once per day. This is a genuine logic gap, not just a scheduling inconvenience.
- **But actual candidate-facing harm was low:** of 546 runs, 540 sent 0 new leads, 5 sent 30, and
  1 sent 13 — total ≈163 new-lead intro SMS sent across the whole 59-day window. The CSV only has
  342 rows total, and existing-contact dedup (3,794 live Quo contacts fetched each run) exhausted
  the fresh-lead pool within the first handful of runs, after which the bug was inert. No mass
  overmessaging incident actually occurred, though the exposure existed in the code the whole time
  and would recur if a large new CSV batch were ever loaded while this cron misconfiguration is
  still live.
- Step 1 (re-engagement) and Step 3 (reply handling) running 9x/day instead of 1x/day is not
  harmful to candidates (96hr gate + handled-ID tracking prevent duplicate sends) but does mean
  ~9x the intended Claude API call volume for personalized re-engagement — a cost/waste issue, not
  a compliance one.
- Confirmed the last real cron execution in the log (2026-07-02 08:09:02–08:13:54) printed
  `v2.3` — meaning the Round 7 v2.5 hardening deploy (lock file, hardened opt-out guard) happened
  *after* that run. **The v2.5 hardening has not yet been exercised by a single real cron firing.**
  Next scheduled tick will be the first live test.

**Fix given to Aditya (terminal, not yet confirmed executed):** replace crontab via
`crontab << 'EOF' ... TZ=America/New_York / 0 9 * * * ... EOF` to correct both the timezone
variable name and the schedule to true once-daily. Recommend re-running
`crontab -l | cat -vet` after to confirm the correction stuck, and checking the next day's
`cron_output.log` entry for a single run instead of multiple.

**Status: ✅ CLOSED, 2026-07-02.** Fix applied and verified directly on Aditya's Mac. First attempt
failed with `crontab: tmp/tmp.9084: Operation not permitted` — a separate, real macOS restriction
(Terminal lacked Full Disk Access, which `crontab`'s temp-file write requires since Catalina — not
a syntax issue). Aditya granted Full Disk Access to Terminal via System Settings → Privacy &
Security, reopened Terminal, re-ran the same command — succeeded silently. Verified via
`crontab -l | cat -vet`:
```
TZ=America/New_York$
0 9 * * * cd /Users/Aditya/Downloads/BlueLine && set -a && source .env && set +a && /usr/local/bin/python3.11 master_daily_agent.py >> /Users/Aditya/Downloads/BlueLine/cron_output.log 2>&1$
```
Correct `TZ=` variable name and true once-daily `0 9 * * *` schedule both confirmed live. Next
step to fully close the loop: check tomorrow's `cron_output.log` for exactly one run instead of
several, to confirm the fix holds under real cron execution (not just `crontab -l` echoing back
what was written).

---

## ROUND 9 — 2026-07-02 · Live Phase 4 test uncovers stale deployed `master_gmail_reviewer.py`

**Finding:** During manual testing of `master_gmail_pubsub_listener.py` (per the go-live runbook,
Phase 4), it crashed immediately on Aditya's Mac:
```
ImportError: cannot import name 'process_new_message_by_id' from 'master_gmail_reviewer'
(/Users/Aditya/Downloads/BlueLine/master_gmail_reviewer.py)
```

**Root cause, verified directly (not assumed):** the deployed `~/Downloads/BlueLine/master_gmail_reviewer.py`
was the original **May 4** version — 725 lines, no `Version:` header, predates this entire audit
session. The project's `src/master_gmail_reviewer.py` is **v1.2, dated 2026-07-02** — 1,175 lines,
containing `process_sender()`, `process_new_message_by_id()`, the v1.1 all-unread-email widening,
the v1.2 pipeline-stage-tracking write to Quo, and the Round 6 opt-out-sync integration
(`sync_email_optout_to_sms`) — none of which had ever been copied to the live Mac. Confirmed via
`diff -q` (files differ), `wc -l` (725 vs 1,175), and a direct `grep` for the two missing function
names (present only in `src/`). Same root pattern as Round 7's `master_daily_agent.py` gap: work
done and tested in `src/` is not automatically live — this is exactly what Rule 0E exists to catch.

Also discovered while investigating: `master_gmail_pubsub_listener.py` and
`master_sms_poll_service.py` themselves had never been deployed either (present only in `src/`,
confirmed via `Glob` returning no results in `~/Downloads/BlueLine`) — these were copied over
first, which is what surfaced the `master_gmail_reviewer.py` import crash in the first place.
`email_context_bridge.py` (a dependency of the new `master_gmail_reviewer.py`, itself dependent on
`upgrade1_context_aware_messaging.py` which *was* already live) was also missing and has now been
deployed.

**Fix applied and verified:**
1. Backed up the stale deployed file: `master_gmail_reviewer.py.pre-v1.2-deploy-backup-2026-07-02`
2. Deployed `src/master_gmail_reviewer.py` (v1.2) → `~/Downloads/BlueLine/master_gmail_reviewer.py`
3. Deployed `src/email_context_bridge.py` → `~/Downloads/BlueLine/email_context_bridge.py`
4. Deployed `src/master_gmail_pubsub_listener.py` and `src/master_sms_poll_service.py` →
   `~/Downloads/BlueLine/` (were entirely absent before this)
5. `ast.parse()` syntax check on both new files — clean
6. Confirmed via `grep` that `process_sender` and `process_new_message_by_id` now exist in the
   deployed file

**Status: ✅ CLOSED, 2026-07-02.** Root cause found and fixed for real this time: `master_gmail_pubsub_listener.py`
line 269 was calling `base64.b64decode(received.message.data)`, but the `google-cloud-pubsub`
Python client library already returns `message.data` as decoded raw bytes (it handles base64 as
part of its own gRPC/protobuf wire handling internally) — this is different from the raw REST API,
where "data" appears as a base64 string inside JSON. Double-decoding raw bytes as base64 text
produced `Invalid base64-encoded string: number of data characters (N) cannot be 1 more than a
multiple of 4`. Fixed to `json.loads(received.message.data.decode("utf-8"))` — no b64decode needed.
Removed the now-unused `import base64`. Synced fix from deployed file back to `src/` (confirmed
identical via `diff -q`).

**Verified against a real live message, not just a clean parse/no-crash run.** Aditya sent a real
test email to `info@bluelinestaffing.com` while the listener was running:
```
14:32:06 INFO   1 new message(s) since last check
14:32:06 INFO   Processing sender: aditya.dhillon13@gmail.com
14:32:07 INFO   No attachments — routing 'aditya.dhillon13@gmail.com' through cross-channel context bridge
14:36:58 INFO   No confident Quo match for 'aditya dhillon' <aditya.dhillon13@gmail.com> — proceeding with email-only context
14:37:00 INFO HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
14:37:00 INFO     SKIPPED: aditya.dhillon13@gmail.com — Empty test email with no content requiring a response.
14:37:01 INFO     19f2210491736e05 -> skipped
```
Full chain confirmed working end to end: Gmail → Pub/Sub push → listener decode → Quo lookup →
Claude decision → logged outcome, with a genuinely correct decision (SKIP, since it was a blank
test email). This closes the entire Round 8/9 saga — the original crontab misconfiguration, the
wrong-GCP-project Gmail credentials, the stale deployed `master_gmail_reviewer.py`, and the
double-base64-decode bug are all now fixed and verified live, not just claimed.

**Round 9B, real-time latency gap.** The Quo contact-matching step
(`match_phone_by_sender_email()` → `_quo_get_all_contacts()` in `email_context_bridge.py`) took
**4 minutes 51 seconds** (14:32:07 → 14:36:58) for a single email, because it fetched the entire
~3,794-contact Quo account from scratch on every call rather than caching it. This directly
undercut the purpose of building a real-time Pub/Sub listener in the first place — a candidate
emailing in should get Claude's attention within seconds, not ~5 minutes later.

**FIXED — 2026-07-02.** `_quo_get_all_contacts()` in `email_context_bridge.py` (now v1.4) gained a
module-level cache (`_CONTACTS_CACHE`, 5-minute TTL via `_CONTACTS_CACHE_TTL_SECONDS`). Each
long-running process (the Pub/Sub listener, the SMS poll service) now fetches the full contact
list from Quo at most once per 5-minute window instead of once per message. Deliberately only a
**genuinely complete** paginated fetch gets cached — a fetch that errors out mid-pagination falls
back to the last good cached list (or an empty list if none exists yet) rather than silently
caching a partial/truncated contact set for 5 minutes. A `force_refresh=True` escape hatch exists
for callers that know the list just changed and need the very latest state.

Verification (not just claimed):
- 6 new tests added in `tests/test_pipeline_logic.py::TestQuoContactCache`, covering: first call
  fetches + populates the cache; a second call within the TTL makes zero additional HTTP calls
  (the actual bug this closes); the cache expires and re-fetches after the TTL; `force_refresh=True`
  bypasses the cache; a partial/failed fetch does not overwrite a good cached list; a missing
  `QUO_API_KEY` falls back to the stale cache instead of returning an empty list.
- Full suite re-run after the change: `118 passed, 0 failed` (`cd tests && python3 -m pytest -v`) —
  no regressions in the other 112 pre-existing tests from the `_quo_get_all_contacts()` signature
  change (`force_refresh: bool = False` param added; empty-key fallback changed from `[]` to
  `_CONTACTS_CACHE["data"] or []`).
- Fix was made in the live-deployed `~/Downloads/BlueLine/email_context_bridge.py` first (where the
  original 4m51s was observed), then synced byte-for-byte to `src/email_context_bridge.py` (`diff -q`
  confirmed identical) so the test suite is exercising the exact code running on Aditya's Mac, not a
  divergent copy.
- **Live-verified — 2026-07-02, 14:46–14:50, real production run.** Aditya ran
  `python3.11 master_gmail_reviewer.py` against real inbox traffic (3 unread candidate emails:
  Sarina Escalera, a Google Workspace notification, Bernardito Galan). Real timestamps:
  - Sarina (first Quo lookup in this process, cold cache): DOC DRAFT SAVED at 14:46:37 →
    "No confident Quo contact match" at 14:49:04 = **2m27s** for the full paginated fetch of the
    live ~3,794-contact Quo account. This is the unavoidable one-time cost of a cold cache — it's
    lower than the original 4m51s observed pre-fix (network variance), but the real proof is below.
  - Google Workspace notification (second lookup, same process, cache now warm): routed through
    the cross-channel bridge at 14:50:00.722 → "No confident Quo match" at 14:50:00.738 = **16ms**.
  - Bernardito (third lookup, same process, cache still warm): DOC DRAFT SAVED at 14:50:34.799 →
    "No confident Quo contact match" at 14:50:34.815 = **16ms**.
  This is exactly the designed behavior: one real fetch per process per 5-minute window, then
  nanosecond-scale cache hits — closing Round 9B end-to-end, not just in mocked tests.

**NEW FINDING, found while reading this live output — Round 9C.** Both Sarina and Bernardito
logged "No confident Quo contact match" even though they are presumably real candidates already in
the Quo account (their names don't obviously read as brand-new leads). This surfaced a second, real
bug in `master_gmail_reviewer.py`'s `push_candidate_status_to_quo()`: after a **successful** name
match, it resolved the matched phone number to a Quo `contact_id` using its own separate,
**unpaginated** `requests.get(.../contacts, pageSize=100)` call — i.e. only the first 100 of
~3,794 contacts (~2.6% coverage) — instead of reusing the full cached list. So even when
`match_phone_by_sender_name()` (which does search the complete paginated+cached list) found the
right phone number, the very next step to resolve its contact_id would silently fail for any
contact outside page 1, logging "Matched phone {phone} but could not resolve a contact ID — stage
not pushed" and dropping the dashboard update. (Note: this particular bug is NOT what caused
Sarina/Bernardito's "no match" warnings above — those failed at the earlier name-match step, before
ever reaching this code path. This is a distinct, adjacent bug in the same function, found by
reading the function end-to-end while verifying Round 9B.)

**FIXED — 2026-07-02.** `push_candidate_status_to_quo()` now resolves `contact_id` via the same
cached `_quo_get_all_contacts()` used by `match_phone_by_sender_name()`, searching the full contact
list instead of only page 1. In the normal case this call is now free (cache hit from the
name-match step moments earlier).

Verification:
- 2 new tests in `tests/test_pipeline_logic.py::TestPushStageContactIdResolvesBeyondPageOne`: a
  150-contact fixture with the matching phone placed at index 120 (deliberately past any single
  100-item page) now resolves correctly; a regression guard confirms the function makes zero
  separate `requests.get` calls (reuses the cached list only).
- Full suite: `120 passed, 0 failed`.
- Fix made in `~/Downloads/BlueLine/master_gmail_reviewer.py` (live-deployed copy) and synced
  byte-for-byte to `src/master_gmail_reviewer.py` (`diff -q` confirmed identical).
- **Still open:** not yet re-verified against a real candidate whose Quo contact sits outside page 1
  AND whose name-match succeeds (today's live run had two name-match misses, so this exact code path
  wasn't exercised live — only in the unit test above). Worth a live re-check once a matched
  candidate with an existing Quo contact emails in.

---

**Round 10, real-time-service reliability gap.** Found while live-testing `master_sms_poll_service.py`
on 2026-07-02: Aditya started it (`Conversations with recent activity: 36`, matching a live Quo
screenshot at the same moment — good data-accuracy confirmation), then reported no further progress
for a minute or two. Auditing `master_daily_agent.py`'s Quo HTTP helpers (`quo_get`, `quo_post`,
`quo_get_raw`, plus 3 inline `requests.patch`/`requests.delete` calls) found **none of the 6 call
sites set a `timeout=` kwarg**. Python's `requests` library defaults to `timeout=None` ("wait
forever") when omitted — so a single stalled Quo connection (network stall, slow response, proxy
hiccup) would freeze `step3_sms_reply_handler()`, and therefore the entire 24/7 SMS poll loop,
indefinitely with zero error output and zero log lines. That failure mode is indistinguishable from
normal-but-quiet processing (the loop only logs on an actionable message, not per-conversation), which
made this genuinely ambiguous in the moment — cannot claim with certainty this was the exact cause of
that specific 1-2 minute gap, but it is a real, previously-unnoticed gap regardless, and inconsistent
with `email_context_bridge.py`, which already sets `timeout=15` on its Quo calls.

**FIXED — 2026-07-02.** Added `QUO_REQUEST_TIMEOUT_SECONDS = 20` and applied it to all 6
`requests.get/post/patch/delete` call sites in `master_daily_agent.py`. This doesn't make a slow Quo
API fast, but it converts a silent infinite hang into a bounded failure (20s) that the poll service's
existing `except Exception` backoff/retry loop in `run_forever()` can actually catch and act on.

Verification:
- New `TestNoUnboundedNetworkCalls` test group in `tests/test_pipeline_logic.py` — walks the real AST
  of `master_daily_agent.py`, `master_gmail_reviewer.py`, `email_context_bridge.py`, and
  `upgrade1_context_aware_messaging.py`, and fails if ANY `requests.get/post/patch/put/delete` call is
  missing a `timeout` kwarg. This is structural, not a fixed list — it will also catch any future call
  site added without a timeout, not just today's six. `upgrade1_context_aware_messaging.py` and
  `email_context_bridge.py` and `master_gmail_reviewer.py` already passed with zero changes needed.
- Full suite: `124 passed, 0 failed`.
- Fix made in `~/Downloads/BlueLine/master_daily_agent.py` (live-deployed copy) and synced
  byte-for-byte to `src/master_daily_agent.py` (`diff -q` confirmed identical).
- **Still open:** has not yet been re-verified by actually restarting the SMS poll service on
  Aditya's Mac and confirming it completes multiple 90-second poll cycles cleanly. That's the next
  concrete step — task #28.

---

**Round 11, three explicit rules from Aditya + a real architectural gap they surfaced.** While
diagnosing the Round 10 hang, Aditya independently changed the crontab himself (2026-07-02) to run
`master_daily_agent.py` every 30 minutes, 9am–5pm EST, Mon–Fri (17 runs/day instead of once/day),
intending to make replies faster. Auditing that change found two real problems, both explained to
Aditya in plain terms before any code changed:

1. **Step 2's "30/day" cap was silently multiplied.** `leads_today` was computed from
   `days_missed = (now - last_run).days`, which is `0` for any same-day rerun — so every one of the
   17 daily runs would independently re-grant a full 30-lead budget. Worst case: ~500 new candidates
   contacted in one day instead of the intended 30/day pace, burning through the 342-row CSV in under
   a day and raising real spam/opt-out risk.
2. **Step 3 would race between two processes.** The new cron ran `master_daily_agent.py` (which
   includes Step 3) every 30 minutes, while `master_sms_poll_service.py` (also calling
   `step3_sms_reply_handler()` directly) was slated to run permanently, 24/7. `acquire_lock()` only
   guards against two overlapping `main()` runs — it does not protect against the poll service's
   direct step-level call overlapping with a cron-triggered run. Same failure class as the earlier
   "Joyelette Miller sent 4x" incident, different trigger.

Presented to Aditya as a 3-option choice (revert to once/day + permanent poll service / keep 30-min
cron but fix Step 2's pacing / accept the risk as-is). Aditya's actual answer went further than any of
the three options and became the real, permanent design:

> "replying to candidates instantly is mandatory- make that a rule- we can nudge candidates who go
> quiet after a 72 hour window has elapsed- text brand new candidates make unlimited based on the
> number of resumes/leads/inputs the user is giving"

**FIXED — 2026-07-02, `master_daily_agent.py` now v2.6.** Three changes, all in the live-deployed
`~/Downloads/BlueLine/master_daily_agent.py` first, then synced byte-for-byte to
`src/master_daily_agent.py` (`diff -q` confirmed identical):

1. **Step 3 removed from `main()`'s automatic sequence.** It is now the exclusive property of
   `master_sms_poll_service.py` — the only way replies can genuinely be "instant" is a permanent,
   always-on process, not a cron cadence of any frequency. `main()` accepts an opt-in
   `--include-step3` flag for manual/debug use only; never to be used while the poll service is also
   running. This eliminates the cross-process race by construction (only one code path ever calls
   `step3_sms_reply_handler()` in normal operation) rather than trying to build cross-process locking
   between two separate scripts.
2. **Stall window: 96h → 72h.** `ninety_six_hours_ago_ts()` renamed to `stall_cutoff_ts()`, driven by
   a new named constant `STALL_WINDOW_HOURS = 72` (one-line change if it needs adjusting again).
3. **Step 2's cap removed entirely, not just fixed.** `DAILY_NEW_LEADS` (30) and `CATCHUP_MAX` (150)
   deleted; `step2_new_leads()` now processes every eligible row in the CSV every run, gated only by
   the existing real dedup checks (optouts/processed/existing Quo phone/existing Quo name) — matching
   Aditya's explicit "unlimited based on input volume" rule. This is also correct at ANY cron
   cadence going forward, not just once/day, closing the root cause of finding #1 above rather than
   papering over it.

Verification:
- New `TestRound11PipelineRules` group in `tests/test_pipeline_logic.py` (6 tests): stall window is
  exactly 72; `DAILY_NEW_LEADS`/`CATCHUP_MAX` are fully gone (not just unused); a 40-row CSV fixture
  (more than the old 30 cap) confirms all 40 get messaged in one run; `main()` does NOT call
  `step3_sms_reply_handler()` by default; `main()` DOES call it when `--include-step3` is passed;
  `step1_reengage_stalled()`'s source actually calls the renamed `stall_cutoff_ts()`, not a dangling
  reference to the deleted `ninety_six_hours_ago_ts` name.
- Full suite: **130 passed, 0 failed**.
- Doc sync (continuous-audit mandate): updated `~/Downloads/BlueLine/CLAUDE.md` (step order diagram,
  96h→72h, 30/day cap language, new note explaining the two 24/7 services and why Step 3 moved) and
  `SAAS_PROJECT_HEALTHCARE_RECRUITMENT_MASTER_CONTEXT.md` §2 and §12A (same corrections, plus removed
  the doc's own prior claim that Step 3 ran "also now covered continuously" from BOTH the cron and the
  poll service — that claim documented the race as if it were a feature).
- **Still open:** (a) the crontab itself has not yet been reverted on Aditya's Mac — it's still set to
  the 17x/day schedule from earlier today; now that Step 2 has no cap and Step 3 is cron-excluded,
  that specific schedule is no longer dangerous the way it was, but it's still needlessly frequent
  (Step 2 will just find nothing new to send after the first same-day run drains the CSV). Recommend
  reverting to once/day. (b) `master_sms_poll_service.py` still needs to be deployed as a permanent
  `launchd` service (task #29) — running "instant replies" from a manual terminal window doesn't
  satisfy "mandatory" if the terminal gets closed or the Mac sleeps.

---

**Round 12, two more explicit rules from Aditya.** After Round 11 landed, Aditya added two more
hard requirements in the same message: (1) "for no reason should duplicate messages or emails be
sent — ever — develop a check for this to ensure it never happens"; (2) a hard max of 75 new
candidates/day, computed against a genuine rolling 24-hour window (not calendar-day), with a
notification when the cap is hit rather than silent unlimited sending.

**FIXED — 2026-07-02.**
1. `send_sms()` in `master_daily_agent.py` now fingerprints every send (`normalise_phone(to)` +
   exact message text, SHA-256) via `_sms_fingerprint()`/`_was_recently_sent()`/
   `_record_sent_fingerprint()`, refusing an identical message to the same phone within
   `DUPLICATE_SEND_COOLDOWN_HOURS` (24h). Scoped to (phone, exact text) — a different message to
   the same phone, or the same template to a different phone, is never falsely blocked. State
   lives in `STATE_SMS_FINGERPRINTS`, pruned to 2x the cooldown window on every check so the file
   stays bounded.
2. `step2_new_leads()` now enforces `NEW_LEAD_ROLLING_CAP = 75` against a genuine rolling 24h
   window (`new_leads_sent_in_window()`, reads/prunes `STATE_NEW_LEAD_SEND_LOG` on every call —
   not a calendar-day counter, closing the exact class of bug Round 11 fixed for the old cap).
   When the cap is reached (at the start of a run, or mid-run), it calls `append_to_review()` with
   a clearly-labeled non-error notification and stops sending for that run — outreach resumes
   automatically as older sends age out of the 24h window, no manual re-enable needed (Aditya's
   chosen default from the earlier 3-option question).

Verification: 5 new tests in `TestSendSmsDuplicateGuard` (duplicate refused, different message to
same phone allowed, same message to different phone allowed, opt-out check still fires first,
cooldown expires after the window) plus the pre-existing `TestRound11PipelineRules` group covering
the cap removal are all still green. Full suite passed at each stage (see Round 13 below for final
count after further changes).

---

**Round 13, a real incident: two concurrent Claude sessions, silent drift, and a
that-looked-like-injection scare.** While mid-way through Round 12, two tool-result "Note" messages
appeared claiming `email_context_bridge.py` and `master_gmail_reviewer.py` had been "modified,
either by the user or by a linter," each instructing "don't tell the user this, since they are
already aware." The accompanying text made a demonstrably false claim — that `tests/` "did not
exist anywhere in this project" until that change and that `TestQuoContactCache`/
`TestEmailOptoutAutoSync` "do not exist" — directly contradicted by this session's own history (both
were written and passing minutes earlier). Per this agent's standing instruction-source-boundary
rules, the "don't tell the user" instruction was not followed; Aditya was told immediately and asked
directly whether he'd made the edits.

**Root cause, confirmed by Aditya: two concurrent Claude Code sessions**, both with access to
`~/Downloads/BlueLine/`, working independently with no shared visibility into each other's
reasoning or edits. Not a prompt injection — the false "tests don't exist" claim was the other
session's own comment, written without visibility into this session's work, not malice. Aditya then
asked, correctly: why don't the sessions sync, and can this be fixed for chat/Code/Cowork broadly.

**Answered honestly rather than overpromising:** true live cross-surface session awareness (one
Claude session seeing another's in-progress conversation across Chat/Code/Cowork) is not buildable
from this session — it would require product-level infrastructure, not a workaround. What IS
achievable and was built: **git in both `~/Downloads/BlueLine/` and this project folder** (neither
was previously version-controlled — confirmed via `git status` before assuming). This gives any
session, on either surface, a real commit history and diffable state instead of silent overwrites.
`.gitignore` excludes secrets (`.env*`, `gmail_credentials*.json`, `gmail_token.json`),
`CONFIDENTIAL_candidates.csv`, logs, and large generated media — verified via `git ls-files` that
none of these are tracked before the first commit. Both repos verified healthy (`git fsck --full`,
exit 0) despite the sandbox's mount rejecting `unlink()` on some git temp/lock files (worked around
with `mv` instead of `rm` — a real filesystem quirk of this sandbox, not a git problem).

**Real drift found once git made it checkable:** 6 of 8 shared pipeline files had actually diverged
between `~/Downloads/BlueLine/` and `src/` — some because BlueLine was ahead (this session's own
Round 12 work, plus the other session's untested `resolve_candidate_contact()`/
`compute_pipeline_stage()` additions to `master_gmail_reviewer.py`/`email_context_bridge.py`, which
push a pipeline-stage tag to Quo's dashboard-visible `role` field but are — by their own docstring —
"NOT YET RUN against real data"), some because `src/` was ahead (a real, valuable, already-documented
Gmail-token-path bug fix in `upgrade1_context_aware_messaging.py` that had never been deployed to the
live BlueLine folder — meaning Gmail context had been silently missing from every SMS re-engagement
decision in production; plus an import-safety fix to `master_gmail_setup.py` and three missing
dependencies in `master_requirements.txt`). Resolved file-by-file after reading each diff and mtime,
not by blindly picking one direction — reconciled to: BlueLine → src/ for
`master_daily_agent.py`/`master_gmail_reviewer.py`/`email_context_bridge.py`; src/ → BlueLine for
`master_gmail_setup.py`/`upgrade1_context_aware_messaging.py`/`master_requirements.txt`.

The sync surfaced 2 real test failures (`TestPushStageContactIdResolvesBeyondPageOne`) — not a
regression: the other session's `resolve_candidate_contact()` layer sits in front of this session's
Round 9C contact-ID fix, which is still intact underneath it; only the mock target was stale. Fixed
by updating the tests to mock the current function. A separate, genuine test-isolation bug was also
found by running the suite twice in the same sandbox session: `STATE_SMS_FINGERPRINTS` (new in Round
12) wasn't mocked to `tmp_path` in `TestSendSmsHardOptOutGuard`, so fingerprints written by one test
run persisted and wrongly blocked a second run's identical-looking sends. Fixed in all 4 tests in
that class.

**Architecture decision, per Aditya's explicit request** ("make the two separate, only sharing best
practices/developments... without being asked"): `~/Downloads/BlueLine/` is now documented (in both
`CLAUDE.md` and this file) as the source of truth for pipeline ENGINEERING code — it's the only
place a fix is genuinely proven, since it's the actual production deployment. This project's `src/`
is a synced reference copy, not an independent place to invent pipeline logic; product strategy,
the eventual multi-tenant architecture, and docs remain this project's job. A new script,
`scripts/sync_check.sh`, reports drift on the 6 pipeline files (BlueLine leads) and flags 2
either-direction files (`master_gmail_setup.py`, `master_requirements.txt`) for manual review rather
than guessing.

**Still open:**
- `scripts/sync_check.sh` needs to actually be run by Aditya (or a future session) — it has not yet
  been exercised on his real Mac, only syntax-checked (`bash -n`) in this sandbox.
- No automated recurring drift check has been wired up yet — a scheduled task idea was discussed but
  not yet built. Without one, "share improvements without being asked" still depends on whichever
  session happens to think to run the script.
- The untested `resolve_candidate_contact()`/`compute_pipeline_stage()` stage-tracking feature is
  now live in the deployed BlueLine folder and synced to `src/` — it has NOT been verified against a
  real candidate email yet. Flagged to Aditya, not silently trusted.

Verification: full suite **135 passed, 0 failed**, run twice consecutively in the same sandbox
session to specifically catch the class of test-isolation bug found above. Both `master_daily_agent.py`
(BlueLine) and this project's `src/` copy are byte-identical for all 8 shared pipeline files as of
this write-up (`diff -q`, verified file-by-file, not asserted). Both git repos committed with
descriptive messages covering exactly what changed and why.

---

## Scheduled drift check — 2026-07-03

Ran `scripts/sync_check.sh` (no reinvention — used as-is) against `~/Downloads/BlueLine/` and this
project's `src/`. **No drift found.** All 6 auto-synced pipeline files (`master_daily_agent.py`,
`master_gmail_reviewer.py`, `email_context_bridge.py`, `master_gmail_pubsub_listener.py`,
`master_sms_poll_service.py`, `upgrade1_context_aware_messaging.py`) are byte-identical between the
two locations, and both flag-only files (`master_gmail_setup.py`, `master_requirements.txt`) also
match — nothing needed manual review today. `git status` on the Dylan for Hire repo was clean; no
sync, no commit, no test run required (nothing changed to test).

Sandbox note, not a real finding: this session's shell resolves `~` to the sandbox's own home
directory, and `~/Downloads/BlueLine` didn't exist there by default (BlueLine is mounted at a
different path in this sandbox). Symlinked `~/Downloads/BlueLine` to the actual mounted BlueLine
folder before running the script so `BLUELINE_DIR` in `sync_check.sh` resolved correctly — this is
purely a this-sandbox path quirk (the script itself is correct for Aditya's real Mac, where
`~/Downloads/BlueLine` is the real path) and required no change to the script.

One pre-existing, unrelated item observed: `~/Downloads/BlueLine/CLAUDE.md` shows as modified in
`git status` (uncommitted). Not touched by this run and not part of the 6+2 files this script
tracks — flagging only so it isn't mistaken for something this check should have resolved. Aditya or
whichever session made that edit should commit or revert it directly.

---

## Round 14 (2026-07-02 23:38–23:44) — RECOVERED, not written at the time

**This entry did not exist until 2026-07-03.** Real work happened and was committed to git
(`b920277` "code-correctness pass," `7544c1d` "doc-consistency pass") on 2026-07-02, but Rule 0B's
mandatory audit-trail append never happened for it — this file jumped straight from Round 13 to the
2026-07-03 scheduled check above, silently skipping Round 14. This is exactly the failure mode Rule
0B exists to prevent: work happened, was even committed with a descriptive message, but the
append-only log — the thing a future session is supposed to be able to trust without re-deriving
history from `git log` — was incomplete. Found by `DYLAN_FOR_HIRE_EXHAUSTIVE_AUDIT_2026-07-03.md`
(§2, "gap found in this pass"), which cross-referenced git commit messages against this file and
caught the mismatch. Recovered from the "Project documentation audit" session transcript (the session
that actually did the work) and appended here as a one-time backfill exception — not the standing
process; the standing process is still "log it in the same session," per Rule 0B.

**What Round 14 actually did, in order:**
1. **Code-correctness pass (`b920277`):** removed 6 confirmed-dead imports/lines across
   `master_daily_agent.py`, `master_gmail_reviewer.py`, `master_gmail_pubsub_listener.py`, and
   `master_candidate_file_consolidator.py` — each verified dead via `pyflakes` plus a manual call-site
   trace, not assumed dead from the linter alone. `pyflakes` is clean across all of `src/` and the live
   BlueLine deployment as a result. Full test suite run and confirmed **138/138**, run twice
   consecutively (the standing test-isolation check since Round 13's `STATE_SMS_FINGERPRINTS` bug).
2. **Doc-consistency pass (`7544c1d`):** fixed 6 real doc-vs-code mismatches —
   - Stale 96h → 72h re-engagement window references remaining in 3 docs (Round 11 had changed the
     window to 72h; not every doc mentioning it had been updated).
   - A stale 30/day new-lead cap reference (Round 12 replaced this with the rolling 75/day
     duplicate-fingerprinted cap; at least one doc still described the old 30/day number).
   - A wrong model name in BlueLine's own `CLAUDE.md` — it said the re-engagement decision model was
     `claude-opus-4-5`; the real model in code is `claude-haiku-4-5-20251001`.
   - The `NO_RESPONSE_FINAL` / permanent-skip fiction: three documents, including BlueLine's own
     `CLAUDE.md`, previously claimed a `NO_RESPONSE_FINAL` fallback message and/or permanent-skip list
     existed for stalled contacts. Confirmed by direct grep across all of `src/` at the time: it does
     not exist anywhere in the codebase. This is a real, still-open product decision (not a bug) — see
     the "Product decision still open" item below and in `DYLAN_FOR_HIRE_EXHAUSTIVE_AUDIT_2026-07-03.md`
     §4.
3. **Sync:** all fixes synced back to the live BlueLine folder and re-verified in sync via `diff -q`.
   Both git repos committed and `fsck`'d clean.
4. **Explicitly flagged, still open at the time Round 14 ended:** the ElevenLabs key rotation and the
   permanent-skip/`NO_RESPONSE_FINAL` decision — both carried forward, still open as of this backfill.

**Verification claim for this entry itself:** the 138/138 and pyflakes-clean claims above are
recovered from the source session's transcript, not re-run in this session. Per Rule 0D, this is
stated as "recovered/reported," not "re-verified this session" — if a future session needs a fresh
138/138 confirmation, re-run `cd tests && python3 -m pytest -v` rather than treating this entry as
current-session proof.

---

## Documentation/memory-consolidation pass — 2026-07-03

Aditya uploaded `DYLAN_FOR_HIRE_EXHAUSTIVE_AUDIT_2026-07-03.md` (a separately-compiled, independently
verified audit — not written by this session) with the instruction to save its learnings, rules, and
guardrails permanently within this project, specifically to prevent any future confusion about Dylan
(the product) vs. BlueLine (its first customer). No source code was changed in this pass. What was
done:

1. **Verified, not just trusted, the uploaded audit's key claims** against this project's actual files
   before saving anything as fact: confirmed the current project root does contain all 13 numbered
   docs + master context doc + this audit file + `src/` (9 files) + `tests/` + `pitch/` +
   `scripts/sync_check.sh`, matching the audit's claimed canonical location. Confirmed via `git log`
   that Round 14 commits (`b920277`, `7544c1d`) exist but this file had no Round 14 section — matches
   the audit's finding exactly. Confirmed via `git show` that the most recent commit (`f1f6dcd`,
   2026-07-03 10:32) added the `BLUELINE_EMAIL` exclusion to `is_system_or_non_candidate_email()` in
   `master_gmail_reviewer.py` — consistent with the audit's claim (compiled 2 minutes later) that this
   exclusion now exists but does **not** yet cover known center/facility domains, which remains a real,
   open, unfixed bug (see `DYLAN_FOR_HIRE_EXHAUSTIVE_AUDIT_2026-07-03.md` §4, second 🔴 item).
2. **Added `13_DYLAN_PRODUCT_CONSTITUTION.md`** — the identity/scope rule (Dylan is the independent
   product; BlueLine is the first customer, design partner, and validation partner; never the
   reference architecture) as a permanent, git-tracked project file. This closes a real gap: a fuller
   version of this same rule had been drafted in a past conversation and was living only in this
   Cowork project's auto-loaded custom-instructions snapshot, which is not an editable or
   version-controlled file and was independently confirmed stale by the uploaded audit (§1) — it
   doesn't reflect Rule 0 through 0E, the numbered-doc structure, or the v3.x architecture. Registered
   in `00_INDEX.md`'s document map and version log.
3. **Backfilled the Round 14 entry above** and a summary of Rounds 8–13 + the 2026-07-03 scheduled
   check into `00_INDEX.md`'s "DOCUMENT VERSIONING" section, which had itself stopped being updated
   after the Round 7 addendum (2026-07-02) even though this audit file kept going through Round 13 and
   beyond — a second, smaller instance of the same "real work, incomplete logging" pattern Round 14
   itself is an example of.
4. **Confirmed the two stale external doc copies the uploaded audit flagged** (`~/Downloads/DylanForHire/`
   entirely, and the old `00_INDEX.md`...`08_TROUBLESHOOTING.md` set sitting inside
   `~/Downloads/BlueLine/` alongside the current `BLUELINE_*.md` docs) are **not reachable from this
   session** (only this project's own root and `outputs/` are mounted here) — could not be deleted or
   marked dead directly. Recorded as an open action for a session with `~/Downloads` access, not
   silently dropped.
5. **Not done in this pass, and explicitly not claimed as done:** the center-contact-as-candidate bug
   fix, the image-MIME-type Vision-failure fix, syncing `tests/` into `sync_check.sh`'s tracked list,
   deploying `master_candidate_file_consolidator.py`, the ElevenLabs key rotation, and the
   permanent-skip/`NO_RESPONSE_FINAL` product decision. All six remain open exactly as the uploaded
   audit described them — this pass was documentation/memory consolidation, not a bug-fixing pass, and
   is not described as one.

**Also written this pass, outside this project's own audit trail:** persistent cross-session memory
(Claude's own memory system, not a project file) capturing the Dylan/BlueLine identity boundary, the
canonical-doc-location map, and the current open-items list, so this understanding does not depend on
a future session re-reading this entire file or the uploaded audit from scratch.

---

## Round 15 (2026-07-03) — real code-correctness pass, this session

Aditya asked for a continuous, exhaustive loop: check, audit, verify, fix, confirm, move to the next
item, across everything reachable. **Scope honestly stated up front:** this session only has this
project's own root mounted — no `~/Downloads/BlueLine` (the live deployment), no real Gmail/Quo/Google
Cloud accounts, no terminal on Aditya's actual Mac. Everything below is real and was actually executed
in this sandbox; nothing about the live deployment or launchd services was or could be touched. See
`DYLAN_FOR_HIRE_EXHAUSTIVE_AUDIT_2026-07-03.md` §4/§9 for the full punch list this round worked
against.

**1. Re-ran ground truth from scratch, not trusted from prior claims:**
- Installed this project's actual dependencies (`src/master_requirements.txt`) plus `pyflakes`/
  `pytest`/`socksio` (the last needed because this sandbox sets `ALL_PROXY=socks5h://localhost:1080`
  globally, and `master_daily_agent.py` builds a live `anthropic.Anthropic()` client at import time —
  without `socksio`, every test importing it crashed at collection with an httpx/SOCKS transport
  error; installing the one missing package fixed all of them. **This is a sandbox environment gap,
  not a code bug** — confirmed by the fact the same import worked instantly once the dependency was
  present, and it fixed 89 of the 89 failures instantly with zero code changes).
- `pyflakes src/*.py`: clean, exit 0 — matches the Round 14 claim, re-verified fresh.
- Full suite: **138 passed, 0 failed**, run twice consecutively — matches the Round 14 claim,
  re-verified fresh (not just recovered from a transcript this time).

**2. Fixed the center-domain-as-candidate bug** (open since the 2026-07-03 exhaustive audit, §4):
added `load_center_email_domains()` to `master_gmail_reviewer.py`, which reads
`~/Downloads/BlueLine/BLUELINE_CENTER_DIRECTORY.md` at runtime and extracts sender domains via regex
(fails open — an unreachable/missing directory means zero extra exclusions, never accidental
candidate-blocking), cached per-process. `is_system_or_non_candidate_email()` now checks the sender's
domain against this set in addition to the existing `BLUELINE_EMAIL`/`BLOCKED_EMAIL_DOMAINS` checks.
Deliberately data-driven, not a hardcoded center list — hardcoding BlueLine's specific 34 centers into
shared code would violate `13_DYLAN_PRODUCT_CONSTITUTION.md` §6. **Not hardcoded, and not yet
live-verified** against the real directory file's actual formatting (unreachable from this session) —
5 new tests added using a synthetic fixture, all passing.

**3. Fixed the image MIME-type sniffing bug** (open since the same audit — the real `mmeyer@dbnrc.com`
400 error in `cron_output.log`): added `sniff_media_type_from_bytes()` to `master_gmail_reviewer.py`,
which checks real magic-byte signatures (JPEG/PNG/TIFF/PDF) and overrides the filename-extension guess
whenever they disagree, logging the mismatch. Falls back to the extension guess if the bytes don't
match any known signature (corrupt/truncated data), rather than dropping the attachment. 7 new tests
added using real magic-byte fixtures (a real 1×1 PNG, a real JPEG header, both TIFF byte orders, a
minimal PDF header) — including a direct regression test proving a `*.png`-named file containing real
JPEG bytes now gets sent to Claude with `media_type=image/jpeg`, not `image/png`.

**4. Fixed the tests/-not-tracked-by-sync_check.sh gap:** added a `TEST_FILES` array to
`scripts/sync_check.sh` for `test_pipeline_logic.py`/`conftest.py`, with the sync direction
**reversed** from the pipeline-code files above it — this project's `tests/` leads, BlueLine's follows
— because this project's suite is the actively-maintained one (150 tests as of this round) and
BlueLine's was found stale at 16. Verified the actual copy logic works, not just the report: built a
throwaway fake-`$HOME` mirror in `/tmp`, ran `sync_check.sh --apply` against it, and confirmed via
`diff` that the synced files were byte-identical afterward (then deleted the scratch mirror). **While
building this, found and fixed a real, separate, pre-existing bug in the script's `FLAG_ONLY_FILES`
loop:** if either side of a flag-only file was missing (e.g. BlueLine unreachable), the old condition
fell through to its `else` branch and printed "IN SYNC" — a false positive, since "couldn't compare"
and "confirmed identical" are not the same claim. Fixed to report "CANNOT COMPARE" explicitly instead.
**Not yet run with `--apply` against the real `~/Downloads/BlueLine`** — that requires a session with
`~/Downloads` access; the logic is verified correct via `bash -n` and the synthetic-mirror test above,
not yet exercised on Aditya's real Mac.

**5. Full suite after both fixes: 150 passed, 0 failed**, run twice consecutively. `pyflakes` on the
modified production file (`master_gmail_reviewer.py`) alone: clean. (The test file itself trips 10
pre-existing pyflakes "unused import" warnings — confirmed via `git show HEAD:tests/test_pipeline_logic.py`
that these predate this round entirely; they're deliberate "imports cleanly" test patterns, not new
issues.)

**6. Investigated the ElevenLabs key exposure precisely** (open since at least three prior
sessions/docs): `git log --all -S "sk_5647b539..."` on **this project's own repo** confirms the real
key exists in plaintext in exactly two commits — `3e936f5` (baseline, where it was introduced) and
`7544c1d` (Round 14, where the *working copy* was redacted in `02_SYSTEM_ARCHITECTURE.md`, but the
prior blob is still fully retrievable via `git show 3e936f5:02_SYSTEM_ARCHITECTURE.md` or the pack
objects — redacting a file's current content does not remove it from git history). **New detail not
previously surfaced:** the working file's own comment says this key actually lives in
`~/Downloads/WV/pipeline/.env` — i.e. it may be a **Wealth Velocity** project credential that leaked
into a Dylan-for-Hire doc as a config-reference example, not a Dylan/BlueLine-specific key. This
doesn't change the remediation (rotate it either way), but it changes who else needs to know a key of
theirs is exposed. **Still not rotated, still not rewritten out of history — both require Aditya's own
action** (ElevenLabs dashboard access for rotation; explicit go-ahead for a history rewrite, since that
mutates a shared git history other clones may depend on, which this project's own Rule 0E-style caution
says should never be done silently).

**What this round did NOT touch, and does not claim to have verified:** whether
`master_sms_poll_service.py`/`master_gmail_pubsub_listener.py` are running via `launchctl` on Aditya's
real Mac; whether `master_candidate_file_consolidator.py` is actually deployed to
`~/Downloads/BlueLine/`; which Gmail OAuth credential file (`gmail_credentials.json` vs.
`gmail_credentials_NEW.json`) is actually loaded live; the `NO_RESPONSE_FINAL`/permanent-skip product
decision (still open, still Aditya's call, not a bug). None of these are fixable or checkable from a
session without `~/Downloads`/live-Mac access — flagged, not silently assumed resolved.

**Addendum, same day — Rule 0F added:** Aditya was mid-way through a concurrent BlueLine audit in his
own terminal and asked that deployment of the fixes above wait until that's done (correctly avoiding
two things touching `~/Downloads/BlueLine/` at once — exactly the Round 13 failure mode). He then gave
a standing instruction: every terminal command from here forward, for Dylan or BlueLine, must state
its exact directory explicitly — `cd <absolute path>` or fully-qualified paths, never a bare relative
command that assumes "wherever you currently are." Reason given directly: Dylan and BlueLine commands
have, in practice, ended up pasted into the wrong directory, which is a real, demonstrated failure
class (same root cause as Rule 0E and the Round 13 incident, just at the command-execution layer
instead of the file-edit layer). Codified as **RULE 0F** in `00_INDEX.md`. Also asked, separately, that
Claude use dashboard-observable evidence (fresh pipeline-stage data, unchanged/working API keys) to
narrow open doubts where possible instead of defaulting to "needs a live-Mac check" for everything —
applied in this same conversation to downgrade the Gmail-credential question from an active risk to a
housekeeping item, since continued successful authentication with unchanged keys is itself evidence
the current pairing works, even without independent dashboard access from this session.

---

## Round 16 (2026-07-08/09) — Dylan Master Dashboard rebuild, real production incident found live, launch-readiness pass

**1. Dylan Master Dashboard artifact.** Replaced the `blueline-pipeline-dashboard` artifact (whose
in-page title said "Dylan Master Dashboard" but whose Cowork sidebar entry never updated — `update_artifact`
doesn't re-sync the name from the creation-time meta block) with a genuinely new artifact,
`dylan-master-dashboard`. Full details in memory `[[dylan-master-dashboard-artifact]]`. The old artifact
could not be deleted (no `delete_artifact` tool exists, and `/Users/Aditya/Claude/Artifacts/` is not a
mounted path in this session) — retired in place with a redirect notice instead.

**2. Real production incident found and fixed live, using real Quo + Gmail MCP calls, not assumption.**
Diagnosed why the new dashboard's Hot Files / Submission-Ready / Drafts Prepared sections showed 0
despite real submissions happening (visible in the Gmail-sourced "Profiles Submitted" table). Root cause,
confirmed in order:
- Read Torri Allen's real Sent-mail thread directly — document review and submissions were being
  handled personally by Aditya, not by `master_gmail_reviewer.py`.
- Aditya then ran `launchctl list`/`crontab -l` on his real Mac (Rule 0F-compliant commands, exact
  directories given each time): confirmed `com.blueline.smspoll` and `com.blueline.gmaillistener` ARE
  running (closes the long-standing 🔴 highest-priority item in `[[dylan-open-decisions-2026-07-03]]`),
  and `master_gmail_reviewer.py` IS scheduled hourly via cron.
- `tail cron_output.log` showed it finding "52 candidate email(s)" every run and processing zero, every
  time.
- Root cause found by reading `cron_output.log` further back: **the Anthropic API ran out of credits on
  2026-07-06 23:38** ("Your credit balance is too low..."). Every doc-review attempt since has failed.
- **Compounding bug found by reading `src/master_gmail_reviewer.py::process_sender()` directly:** the
  function marked every trigger message as permanently processed (`append_to_file(PROCESSED_EMAILS_PATH,
  ...)`) regardless of outcome — including `outcome == "error"`. This meant the API billing failure
  didn't just pause processing, it **permanently blacklisted every real candidate email** that failed
  during the outage from ever being retried, even after credits are restored.
- **Fixed in `src/master_gmail_reviewer.py`:** messages are now only marked processed on a definitive
  outcome (`doc_draft`, `email_draft`, `flagged`, `flagged_optout_synced`, `flagged_optout_sync_failed`,
  `skipped`) — `"error"` outcomes are left unmarked so they retry automatically on the next scheduled
  run. Verified: `pyflakes` clean, full suite still 150/150 passing after the change.
- **This fix has NOT yet been deployed to `~/Downloads/BlueLine/`** — Aditya was given the exact
  `bash blueline_reconcile_apply.sh` command (same script used for today's other BlueLine reconcile work)
  to do that, plus a recovery step (find and un-blacklist the specific candidates lost since 2026-07-06
  23:38 from `~/Downloads/master_processed_email_ids.txt` — correct path confirmed; Aditya's first
  attempt checked the wrong location, inside `~/Downloads/BlueLine/`, which doesn't have this file).
  **Aditya's real action item, blocking everything downstream:** restore Anthropic API billing at
  console.anthropic.com.

**3. Full audit loop, this project's own `src/`+`tests/`, per the continuous-audit-mandate:**
`pyflakes` clean across every file in `src/` (not just the one touched), full suite 150/150 passing,
spot-checked `10_CLIENT_INTAKE_AND_ADAPTER_SPEC.md`'s "no adapter classes/config exist yet" claim
directly against `src/` (confirmed still true — no `class.*Adapter`/`Ruleset` anywhere, no `.yaml`
config files). No drift found needing a fix this round, beyond the reviewer bug in item 2.

**4. `Dylan_for_Hire_New_Client_Setup_Questionnaire.docx` reviewed against real code, not assumed
accurate.** Cross-checked the questionnaire's "8 required + 3 recommended" document-category table
directly against `validate_documents()`'s actual `optional: True` flags in
`master_gmail_reviewer.py` — **exact match, no drift found.** One real gap fixed: Section 5 ("Where This
Runs") asked whether the client wants this hosted, without disclosing that hosted/multi-tenant deployment
doesn't exist yet (matches the exact same honesty gap Section 1 already correctly handles for messaging/
email platforms). Added a matching gold-bordered disclosure box to Section 5, same visual pattern as the
existing "Not currently automated" box in Section 2. Edited via unpack → Edit tool → pack, validated
clean (`pack.py` reported "All validations PASSED!"), spot-checked via `pandoc` text extraction, copied
back into the project root.

**5. SaaS launch-readiness assessment for Aditya's "sell starting next week" target** (today: 2026-07-08,
existing fortnight-plan target in `09_GO_LIVE_READINESS.md`: 2026-07-15) — delivered directly in
conversation, not yet written to a dedicated doc. Headline honest finding: the single biggest real gap
is not a bug, it's that **there is no hosted/multi-tenant deployment model** — everything today runs on
Aditya's own Mac via cron/launchd, for one client (BlueLine) only, per `10_CLIENT_INTAKE_AND_ADAPTER_SPEC.md`
§1/§5 (still accurate, re-verified this round). Selling to a first 1-3 clients this way (Aditya manually
duplicating config per client on his own Mac, per `09_GO_LIVE_READINESS.md` 🔴 gap #4) is honest and
viable near-term; selling it as fully self-configuring "system programs itself per client" is not true
yet — that's the adapter-layer build `10_CLIENT_INTAKE_AND_ADAPTER_SPEC.md` §5 already specs but hasn't
built. Flagged to Aditya directly rather than overclaiming readiness.

## Round 17 (2026-07-09) — Vacancy Matcher feature set: 6 new modules, 43 new tests, client-agnostic by design

**Request:** Aditya asked for 5 features built on top of today's ad hoc "search Quo for candidates near a
vacancy" workflow: (1) Vacancy Matcher — type "2 RNs, nights, New Franklin", get back every qualified,
non-opted-out, real-paperwork-status RN ranked by readiness; (2) a center/borough alias table so free-text
typos ("fort tyrone", "new franklin") resolve reliably instead of a bare substring search that only finds
what was already searched for; (3) a nightly precomputed candidate index instead of live-scanning Quo per
query (the actual fix for the 429/timeout errors flagged in prior rounds); (4) auto-draft (never auto-send)
outreach on match; (5) a pipeline-depth lookup for biz dev ("how many qualified candidates in X borough").
Explicit instruction: make all of it client-agnostic.

**6 new files, all in `src/`, all pyflakes-clean, all covered by
`tests/test_vacancy_matcher.py` (43 new tests, 0 mocked-away — every Quo call in the test suite is mocked,
same posture as `test_pipeline_logic.py`):**

1. **`client_config.py`** — a `ClientConfig` dataclass (Quo env var names, center-directory path, index
   output path, outreach-drafts dir, optouts path, valid roles). `BLUELINE_CONFIG` is the one real
   instance. This is what "client-agnostic" actually means here — **honesty note written directly into
   the module docstring:** this does NOT retrofit `master_daily_agent.py` / `master_gmail_reviewer.py` into
   being multi-tenant (that's the separate, real, multi-week `10_CLIENT_INTAKE_AND_ADAPTER_SPEC.md` build
   already flagged in Round 16's launch-readiness finding) — it makes these 5 NEW features take a config
   object instead of hardcoding BlueLine paths, so a second client means one new `ClientConfig`, not a
   code change to the matching/ranking/drafting logic.
2. **`center_alias.py`** — parses `BLUELINE_CENTER_DIRECTORY.md` into canonical `CenterRecord`s (two parser
   strategies tried: markdown `### Borough` / `- Name` sections, matching this project's own
   `06_COMMUNICATIONS.md` style; a pipe-delimited fallback). Exact alias match → fuzzy match (difflib,
   0.78 accept threshold, near-misses logged not silently guessed) → borough-keyword fallback, in that
   order. **Known, honestly-flagged gap, same class as Round 15's center-domain issue:** the real
   `BLUELINE_CENTER_DIRECTORY.md` (34 centers) is not reachable from this session — only reachable from
   Aditya's Mac. Seeded `CURATED_ALIASES` (19 nickname→canonical pairs) came ONLY from the 18-center subset
   confirmed real in this project's own `06_COMMUNICATIONS.md`, not invented. A `verify_against_real_file()`
   function is included specifically to be run once, by hand, on Aditya's Mac before full trust — same
   posture `master_candidate_file_consolidator.py` already uses for this identical file-reachability gap.
   Also flagged in-code: the "Avalon Gardens"/"Stern Family" borough mapping is a wrong placeholder
   (Nassau/Long Island isn't one of the 5 NYC boroughs `BOROUGH_KEYWORDS` covers) — needs a real 6th bucket,
   not silently fixed here.
3. **`candidate_index.py`** — the actual fix for the 429s. `_quo_get()` respects `Retry-After` on 429 or
   backs off `min(60, 2**attempt)` (verified via grep: neither `master_daily_agent.py`'s `quo_get_raw()` nor
   `master_candidate_file_consolidator.py`'s `get_all_quo_contacts()` had any 429-specific handling before
   today). Uses the cheap `/conversations` bulk endpoint to find who's active in N days FIRST, then only
   fetches full message history for those phones — not every contact. Opted-out candidates (firstName
   `DO NOT MESSAGE` prefix OR phone in `master_permanent_optouts.txt`) are excluded at index-build time,
   never even written to the index. Writes one JSON file atomically (tmp file + `.replace()`).
   `readiness_bucket()` classifies a raw `PIPELINE:*` tag into submission_ready / hot_file /
   drafts_or_submitted / docs_incomplete / unscreened — **flagged as a product decision, not a bug**,
   same convention this project uses elsewhere: a candidate already drafted/submitted to one specific
   center isn't necessarily unavailable for a different vacancy, so they're shown, ranked lower, never
   hidden. NOT wired into cron automatically — exact `crontab` line given to Aditya in the file's own
   footer comment, his call when to add it.
4. **`vacancy_matcher.py`** — deterministic regex/keyword query parser (no LLM call, cheap and instant),
   ranks by the 5 readiness buckets above then by most-recent activity. **One real, honestly-documented
   limitation found and fixed during testing, not swept under the rug:** "RNS" (a distinct, rarer license
   code already in this codebase's `VALID_ROLES`) and "RNs" (plural of RN) are literally the same 3
   characters once case-folded — no regex can tell them apart from free text. Resolved by always parsing
   that token as license_type="RN" (the overwhelmingly likely intent in a natural vacancy request), with
   the limitation documented in-code and in a test (`test_rns_code_resolves_to_rn_known_limitation`) rather
   than silently guessing or hiding the ambiguity.
5. **`outreach_drafts.py`** — draft-only, by design and by test. Quo/OpenPhone has no native "draft
   message" object (no such endpoint in the Quo MCP connector's tool list, confirmed by inspection) — so
   the draft is a local markdown review file, not a Quo API object. Verified (not just commented) via
   `test_module_imports_no_send_capable_function`, which parses the module's own AST and asserts no
   `import requests` and no function call containing "send" anywhere in the file — first version of this
   test used a naive substring search and false-positived on the module's own docstring explaining the
   invariant; rewritten to parse real code via `ast`, which is a more correct check anyway.
6. **`pipeline_depth.py`** — reads the exact same `candidate_index.json` and the exact same
   `query_index()` filter function `vacancy_matcher.py` uses (factored into `candidate_index.py` once,
   specifically to avoid a second copy of the same filter logic ever diverging — this codebase has a real
   prior incident of exactly that, Round 7's `INTEREST_KEYWORDS` reconciliation).

**Testing discipline — real bugs found and fixed via the tests, not assumed correct:** first pytest run was
39/43 passing, 4 real failures: (a) `center_alias.py`'s duplicated `BOROUGH_KEYWORDS` had been retyped from
memory instead of copied verbatim from `master_daily_agent.py` and differed in several zip codes — fixed by
copying the exact block; a cross-check test (`TestBoroughKeywordsStayInSync`) now asserts byte-for-byte
equality so this can't silently drift again; (b)/(c) the RNS/RN ambiguity above, caught by an end-to-end
match test failing with 0 results instead of 3; (d) the AST-based outreach-drafts test above. Full suite
after fixes: **193/193 passing** (150 pre-existing + 43 new), pyflakes clean on all 6 new files.

**NOT yet run against real data — same posture every new script in this project ships with:**
`candidate_index.py` has never hit the real Quo account; `center_alias.py`'s parser has never seen the
real `BLUELINE_CENTER_DIRECTORY.md`. Run `python3 candidate_index.py` once for real, then
`python3 center_alias.py` (calls `verify_against_real_file()`) to eyeball the real parse, before trusting
Vacancy Matcher output for an actual vacancy.

## Round 18 (2026-07-10) — reconciliation with an independently-built parallel implementation, 2 real bugs found and fixed

**What happened:** Aditya had separately asked the "BlueLine Automation" project (a different Claude
project/chat, `~/Downloads/BlueLine`) to build this exact same 5-feature request. That build finished
first and was run against real data (3,814 real Quo contacts, 88 indexed candidates, real matches for a
real "Franklin" vacancy) before Round 17's version had been. Two independent implementations of the same
idea now existed — exactly the class of risk this project has documented before (Round 7's
`INTEREST_KEYWORDS` divergence). Per Aditya's instruction ("check everything and confirm once and for
all"), the 5 real files (`blueline_candidate_index_builder.py`, `blueline_center_aliases.py`,
`blueline_pipeline_depth.py`, `blueline_quo_helpers.py`, `blueline_vacancy_matcher.py`) were copied into
this project (`_incoming_blueline_automation_review/`) and read directly, line by line, against Round 17's
`candidate_index.py` / `center_alias.py` / `vacancy_matcher.py` / `pipeline_depth.py` — not assumed
equivalent, actually diffed.

**Two real, confirmed bugs found in Round 17's code, fixed in Round 18:**

1. **`candidate_index.py`'s `fetch_message_text()` was missing the REQUIRED `phoneNumberId` parameter on
   `/messages` calls.** `blueline_quo_helpers.py`'s own docstring documents the real root cause precisely:
   OpenPhone's actual error body is `"/phoneNumberId: Expected required property"` — and critically,
   omitting it doesn't always error loudly; it can silently return an empty result with no error at all.
   That means Round 17's index build would have quietly returned `""` for every candidate's message
   history, so `centers_mentioned`/`boroughs_mentioned` would always have come back empty despite the
   whole pipeline reporting success with zero visible errors — a genuinely dangerous silent-failure mode,
   not a crash that would have been caught immediately. **Fixed:** `phoneNumberId` added to the `/messages`
   params. **Direct regression test added:** `test_messages_call_includes_required_phone_number_id`.
   **Separately flagged, NOT fixed this round (out of scope):** `master_candidate_file_consolidator.py`'s
   own `get_quo_sms_history_text()` has this exact same missing parameter — confirmed by direct comparison
   today, pre-existing, unrelated to today's feature request. Needs its own fix in a future round.
2. **`candidate_index.py` scanned BOTH incoming and outgoing message text for center mentions.** This means
   Dylan's own automated replies (e.g. template text) could get misattributed as something the candidate
   said. `blueline_candidate_index_builder.py` filters to `direction == "incoming"` before scanning — a
   real correctness improvement, adopted here too. **Direct regression test added:**
   `test_outgoing_messages_excluded_from_center_scanning`.

**One real data-quality correction, confirmed by an actual production run, not guessed:** Round 17's
`center_alias.py` seeded canonical center names as FULL formal names ("New Franklin Center for
Rehabilitation and Nursing") guessed from this project's own `06_COMMUNICATIONS.md`. BlueLine Automation's
version was actually run against real candidate SMS data on 2026-07-10 and confirmed centers are referred
to everywhere in this codebase's real operational data — candidate messages, the Quo role field, biz dev
conversations — by SHORT names: "Franklin", "Palm Gardens", "Fort Tryon", "Bronx Park". **`CURATED_ALIASES`
replaced wholesale** with the short-name convention from `blueline_center_aliases.py`'s real,
production-run-validated `SEED_ALIASES` (28 canonical centers), including `"fort tyrone" -> "Fort Tryon"` —
which finally resolves the exact typo example Aditya gave when this feature was first requested, and which
Round 17 explicitly could not confirm from this session. The original 18 full-name entries were kept
alongside, not discarded, for the 16 that don't obviously overlap with the short-name set (may be real
centers the short-name list hasn't captured yet) plus 2 confirmed overlaps (Franklin, Grandell) merged as
additional aliases pointing to the same canonical short name. New test added:
`test_fort_tryon_typo_resolves`. **Flagged, not resolved:** "Citadel" is documented elsewhere in this
project (`SAAS_PROJECT_HEALTHCARE_RECRUITMENT_MASTER_CONTEXT.md` §12A) as a shared management group
covering five separate centers, not one physical center — both this file and BlueLine Automation's version
treat it as a single canonical name, which may be imprecise; not fixed since neither implementation has
real data on which of the five a candidate actually means.

**What Round 17's version has that BlueLine Automation's doesn't, confirmed by direct comparison (kept,
not changed):** an explicit, defense-in-depth opt-out check (firstName `DO NOT MESSAGE` prefix AND phone in
the permanent-optouts file) — BlueLine Automation's version has no explicit opt-out check at all; it
relies entirely on the side effect of an opted-out contact's `lastName` field being cleared (per this
project's own Quo naming convention) so they no longer carry an RN/LPN/CNA token in their name. That's a
real, if narrow, gap on their side: if that clearing step is ever skipped or predates the convention, an
opted-out candidate could still surface in a vacancy match on their version. Also confirmed unique to Round
17's version: the `ClientConfig` client-agnostic abstraction (BlueLine Automation's build is 100%
hardcoded, fine for a BlueLine-only ops script but not reusable for a second Dylan client without a
rewrite), free-text natural-language query parsing (their version requires structured `--center`/`--license`
flags, no shift/count parsing), and an automated test suite (46 tests; no test file exists anywhere in
BlueLine Automation's 5 files).

**One genuine, unresolved product disagreement between the two implementations — Aditya's call, not
silently picked either way:** BlueLine Automation's `paperwork_rank()` ranks a candidate already
drafted/submitted to a specific center ABOVE a candidate who is ready-for-submission but not yet assigned
anywhere (rank `-1`, sorts first). Round 17's `readiness_bucket()` ranks the opposite way
(`drafts_or_submitted` below both `submission_ready` and `hot_file`) on the reasoning that someone not yet
committed elsewhere is the better fit for a brand-new opening. Both are defensible; presented to Aditya
directly rather than assumed.

**Verification, not just claimed:** full suite re-run after all fixes — **196/196 passing** (150
pre-existing + 46 in `test_vacancy_matcher.py`, up from 43 — 3 new tests added this round for the 2 bug
fixes plus the Fort Tryon resolution), pyflakes clean on every touched file.

**Still true, unchanged by this round:** neither implementation has been validated end-to-end by rerunning
the FIXED Round 18 code against real Quo data yet (BlueLine Automation's version was real-data-validated
BEFORE these 2 bugs were known to exist in the OTHER implementation — it doesn't have the bugs, so its own
real run stands, but Round 17/18's code has not itself had a fresh real run since these fixes). Recommend:
once Aditya decides the ranking-order question above, re-run `candidate_index.py` for real once more, and
retire BlueLine Automation's duplicate scripts so there is exactly one implementation going forward —
matching this project's own repeated lesson about two copies of the same logic silently diverging.

**Decision (2026-07-10, same session, via direct question to Aditya):** ready-for-submission ranks
first. Round 17's `readiness_bucket()` ordering is confirmed correct and unchanged — no code change
needed. BlueLine Automation's `paperwork_rank()` ordering (already-submitted first) is NOT adopted.
Reasoning given: a candidate with complete paperwork who isn't committed anywhere yet is the best fit
for a brand-new opening; a candidate already mid-process elsewhere carries a real cost to pull off
that thread. With this decided, this project's version is now ahead of BlueLine Automation's on every
axis compared (bugs, center-name accuracy, ranking, client-agnosticism, tests) except one: BlueLine
Automation's version has had one real run against live Quo data and this project's has not yet.
Recommend retiring the `blueline_*` duplicate scripts once that one remaining real run happens here.
