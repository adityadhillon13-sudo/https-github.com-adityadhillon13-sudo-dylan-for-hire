# DYLAN FOR HIRE — GO-LIVE READINESS
**Version:** 1.0 | **Created:** 2026-07-01 | **Target:** sellable to a real customer by 2026-07-15
**Purpose:** One honest list — what's actually verified, what's built but
untested on your real Mac, and what's a genuine open gap. Read this before
any customer call between now and launch.

> **2026-07-08/09 UPDATE — read this first.** A real production incident was found and fixed this
> round (Anthropic API credit exhaustion permanently blacklisting real candidates in
> `master_gmail_reviewer.py` — see `DYLAN_AUDIT_2026-07-01_FULL.md` Round 16). It is NOT yet deployed to
> `~/Downloads/BlueLine/` and NOT yet verified live — do not treat document review as reliable until
> Aditya (1) restores API billing, (2) runs `blueline_reconcile_apply.sh`, (3) recovers the backlog.
> Separately: the biggest real gap against the "sell starting next week" goal is not a bug — it's that
> **no hosted/multi-tenant deployment exists**. Section 5 of the client questionnaire now discloses this
> honestly (updated same round). Selling to 1-3 clients via manual per-client setup on Aditya's own Mac
> is viable now; "the system self-configures per client" is the adapter-layer architecture this doc set
> already specs (`10_CLIENT_INTAKE_AND_ADAPTER_SPEC.md`) but has not built.

---

## ✅ RESOLVED — LIVE PRODUCTION TCPA GAP (found and closed 2026-07-02, Round 7)

**Was:** `~/Downloads/BlueLine/master_daily_agent.py` (v2.3, your real cron script) was missing
TCPA STOP-language and opt-out-keyword coverage that this project's `src/` copy had. Found by
diffing the two files directly after `~/Downloads` was connected this round.

**Now:** at your explicit instruction ("copy and update it to ensure maximum compliance, no
duplication of messages and opt out should be ironclad"), the reconciled file was hardened with
three additional fixes beyond the reconciliation, tested (112/112 passing), and **deployed live**
— `~/Downloads/BlueLine/master_daily_agent.py` is now v2.5, byte-identical to `src/`, verified by
direct diff after copy:
1. **Process lock** (`LOCK_PATH`) — closes a double-send risk the reconciliation alone didn't:
   two overlapping runs (cron firing twice, or a manual run overlapping the scheduled one) could
   each decide a candidate is new and both send an intro SMS. Now only one run can hold the lock;
   a second run exits immediately, sending nothing. Stale locks (crashed run) self-heal after 6hrs.
2. **`send_sms()` hard opt-out guard** — every send, from every caller, is now re-checked against
   the opt-out/blocked lists fresh from disk at send time, independent of whichever step called it.
   No current or future code path can physically message an opted-out number, even if that path's
   own pre-check has a bug.
3. **No silent loss on send failure** — previously, if a Quo contact was created but the intro SMS
   failed to send, that candidate vanished forever (future runs see the contact and skip them as a
   "duplicate"). Now flagged to `master_needs_human_review.txt` instead.

A pre-deploy backup of the old v2.3 deployed file was kept at
`~/Downloads/BlueLine/master_daily_agent.py.pre-v2.5-backup-2026-07-02` in case a rollback is ever
needed. Full technical write-up: `DYLAN_AUDIT_2026-07-01_FULL.md` Round 7 (hardening addendum).
Standing rule against this class of gap recurring: `00_INDEX.md` Rule 0E.

**Still open, by design — needs a live-Mac test, not more code:** none of this has been exercised
against a real Quo/OpenPhone account yet. Code-logic tested ≠ live-Mac tested (Rule 0D). Send one
real STOP reply and one real casual "ok" follow-up on a test number before trusting this in front
of a customer — see the 🟡 section below for what a real test run should check.

---

## HOW TO READ THIS DOCUMENT

Everything below is sorted into three buckets, because they carry very
different risk if you get them wrong in front of a paying customer:

- 🟢 **VERIFIED** — read directly from source code, true as of 2026-07-01
- 🟡 **BUILT, NOT YET VERIFIED ON YOUR MAC** — new code exists and follows
  the same patterns as the proven parts of the system, but has not been
  run against your real Gmail/Quo/Google Cloud accounts yet. This is
  expected for anything built in this session — it cannot be tested from
  a synced project folder, only on your actual machine.
- 🔴 **KNOWN GAP** — a real limitation, not yet closed. Don't claim these
  are solved to a customer.

---

## PLAIN-ENGLISH ACTION CHECKLIST (added 2026-07-02 — read this first)

Everything below this point is the detailed, technical version. This section
is the same information reorganized as one ordered to-do list, with who
actually does each step:

- 🤖 **CLAUDE** — done inside this project session, no Mac/account access needed
- 🧑‍💻 **ADITYA, ON YOUR MAC** — needs your physical machine, your Google/OpenPhone
  accounts, or a real inbound test message. Cannot be done from this session —
  this Cowork project only reaches this synced folder, not your `~/Downloads`
  or `~/Desktop` or a live terminal.
- 🧭 **DECISION** — not a technical task, needs your judgment call first

### Already done — nothing left to do here
🤖 Core SMS pipeline (proven since May), BUG-01 through BUG-18 (all confirmed
fixed directly in code), doc corrections across all 13 files, the client
setup questionnaire, this project's continuous-audit process. See
`DYLAN_AUDIT_2026-07-01_FULL.md` for the full trail.

### In order, starting from today

1. 🧑‍💻 **Sanity-check the ORIGINAL setup is still intact.** This predates
   this whole audit and should already be true, but confirm before building
   on top of it:
   ```bash
   ls ~/Downloads/.env ~/Downloads/gmail_token.json
   ls ~/Desktop/aditya/ | grep Onboarding
   head -3 ~/Downloads/BlueLine/CONFIDENTIAL_candidates.csv
   crontab -l
   ```
2. 🧑‍💻 **Build the new 24/7 layer** — `03_SETUP_GUIDE.md` Step 11, parts A
   through G. **Parts B and C done for you (2026-07-02, via browser control,
   with your approval):**
   - ✅ Created a dedicated GCP project — `dylan-for-hire` (project number
     18529386694), separate from the unrelated `wv-pipeline` project already
     on your account
   - ✅ Enabled the Cloud Pub/Sub API and Gmail API on it
   - ✅ Created topic `gmail-dylan-notify` and its pull subscription
     `gmail-dylan-notify-sub` — names match the code's defaults exactly, no
     `.env` override needed for the names themselves
   - ✅ Granted `gmail-api-push@system.gserviceaccount.com` the Pub/Sub
     Publisher role on the topic (confirmed in the topic's IAM panel:
     "Pub/Sub Publisher (1)")

   **Still needs you — genuinely can't be done from here:**
   - 🧑‍💻 `pip3.11 install google-cloud-pubsub --break-system-packages`
   - 🧑‍💻 Add to **both** `~/Downloads/.env` (the one the code actually
     loads) **and** `~/Downloads/BlueLine/.env` (checked — not yet present
     in either):
     ```
     GCP_PROJECT_ID=dylan-for-hire
     GMAIL_PUBSUB_TOPIC=gmail-dylan-notify
     GMAIL_PUBSUB_SUBSCRIPTION=gmail-dylan-notify-sub
     ```
   - 🧑‍💻 `gcloud auth application-default login` (needs your Google login
     in a real terminal)
   - 🧑‍💻 **Manually test both new scripts in a terminal before making them
     permanent**, then create and load the two launchd services
3. 🧑‍💻 **Run the 4 live tests in the 🟡 list below** (email general-inquiry
   draft, Gmail pickup <30s, SMS reply pickup <2min, BUG-14 Gmail-context
   test) and fix anything that breaks.
4. 🧑‍💻 **Test the new Hep B / flu vaccine fields** (🟡 item 8) — send a test
   document set with a flu declination form and a Hep B vaccine card, confirm
   they show as non-blocking notes, not "still required."
5. 🧑‍💻 **Let both services run 48+ hours**, checking `04_DAILY_OPERATIONS.md`
   Part 0 daily.
6. 🧑‍💻 **Measure real Claude API cost** after a few days of continuous
   operation — update §6A of the master context doc with the real number.
7. ✅ **DONE (2026-07-02, Round 6)** — email opt-out auto-sync (🔴 gap #1) is
   built and logic-tested (6 passing tests, `tests/test_pipeline_logic.py::
   TestEmailOptoutAutoSync`). 🧑‍💻 **Still needs you:** a live test — send a
   real "please stop contacting me" test email and confirm the phone lands
   in `master_permanent_optouts.txt` and the Quo contact gets renamed. See
   🟡 item 9 below.
8. ✅ **DONE (2026-07-02, Round 6)** — pitch deck script gap (🔴 gap #7) is
   closed: both scripts now write to a clearly-labeled deprecated path
   instead of the real files, verified by actually running them and
   confirming the real HTML files' checksums didn't change. No action
   needed from you here.
9. 🧑‍💻 **Update the Loom walkthrough and pitch deck** to show real-time
   behavior, and re-verify every Proof-slide number before your next demo.
10. 🧑‍💻 **Run the discovery call script once** against the system's actual
    current state, not as originally written.

**What I cannot do for you, ever, from this session:** anything requiring
your Google Cloud Console login, your terminal, your OpenPhone/Quo account,
launchd/cron on your actual Mac, or a real test text/email round-trip. Those
are steps 1–6 and 9–10 above. **What I can do without waiting on you:**
anything in this project's files — code fixes, doc fixes, new documents,
audits, and step 8's mechanical part once you've made the call.

---

## 🟢 VERIFIED (read from source code, 2026-07-01)

- The core SMS pipeline (intro, reply handling, re-engagement, dedup) —
  proven in production since 2026-05-04, 13 bugs fixed and confirmed
- Document review via Gmail (Claude Vision, 9-category NYS credential check —
  corrected from "11-point," see 🔴 KNOWN GAPS #6 below; this line itself
  still said "11-point" until the 2026-07-01 Round 3 audit caught the
  self-contradiction against this file's own §6 finding) —
  proven, draft-only, never auto-sends
- Context-aware SMS re-engagement checks Quo history correctly (the
  previously-reported URL bug was already fixed as of 2026-06-29)
- TCPA opt-out handling for SMS — keyword detection, permanent file, contact
  rename, all confirmed in code **as of the BUG-15/16/17 fixes made 2026-07-01**
  (see below — this line was inaccurate before today: `DYLAN_INTRO` had no
  STOP language and `OPTOUT_KEYWORDS` was missing several phrases this same
  doc had assumed were already handled. Both are fixed now; re-verify on your
  Mac before relying on this in front of a customer.)
- Never-auto-send invariant — confirmed true for every code path, including
  the new email general-inquiry flow

**Four bugs found and fixed during this same audit pass (2026-07-01) — see
`08_TROUBLESHOOTING.md` BUG-15 through BUG-18:**
- BUG-15: `master_sms_poll_service.py` called a function name
  (`step3_handle_sms_replies`) that didn't exist anywhere in the codebase —
  the 24/7 SMS service would have crashed with `AttributeError` on first run.
  Fixed: corrected to the real name, `step3_sms_reply_handler`.
- BUG-16: `DYLAN_INTRO` had no "Reply STOP to opt out." despite
  `07_COMPLIANCE.md` asserting it did. Fixed: added.
- BUG-17: `OPTOUT_KEYWORDS`/`INTEREST_KEYWORDS` in code were narrower than
  what `07_COMPLIANCE.md`/`05_PIPELINE_REFERENCE.md` documented as already
  handled. Fixed: widened to match.
- BUG-18: `DOCUMENT_CHECKLIST_MSG` contained emoji, violating
  `06_COMMUNICATIONS.md`'s own "no emoji in SMS" rule. Fixed: removed.

All four are code-level fixes made directly in this project folder — they
still need the same real-Mac verification as everything else in the 🟡
bucket below before you rely on them with a customer.

**Two more bugs found and fixed 2026-07-02 (Round 6), this time with actual
persisted pytest evidence — see `DYLAN_AUDIT_2026-07-01_FULL.md` Round 6 and
`tests/test_pipeline_logic.py`:**
- BUG-19: `email_context_bridge.py`'s `match_phone_by_sender_name()` built
  its full-name comparison by appending part of `lastName` (which always
  holds a license code, e.g. "RN," never a surname) onto `firstName` —
  guaranteed to never match a real sender's name. Fixed.
- BUG-20: the same function read Quo contact fields at the flat top level
  instead of nested under `defaultFields` (the schema `master_daily_agent.py`
  proves is real) — independent of BUG-19 and more severe, this alone made
  every contact match fail even after BUG-19's fix. Fixed. Both verified
  with `tests/test_pipeline_logic.py::TestQuoContactSchemaConsistency` and
  `TestEmailOptoutAutoSync` — 75 tests total in the suite, all passing as of
  this write-up (`cd tests && python3 -m pytest -v`). **Still needs a
  live-Mac test** — see 🟡 item 9 below.

---

## 🟡 BUILT THIS SESSION, NOT YET VERIFIED ON YOUR MAC

Everything in this bucket was written following the same style and
patterns as the proven code above, but none of it has touched your real
Gmail account, your real Quo API key, or a real Google Cloud project yet.
**This is the actual bug-bar for the next two weeks** — closing this list
is what "as close to bug-free as possible" means in practice.

1. **`email_context_bridge.py`** — general email inquiry drafting. Needs a
   real test: send a plain question email to info@bluelinestaffing.com
   from a test address whose display name matches an existing Quo
   contact, confirm the draft correctly references that contact's SMS
   history.
2. **`master_gmail_reviewer.py` v1.1 widened scope** — needs a test that a
   plain email with no attachment now gets a draft/skip/flag outcome
   instead of being silently ignored (the old behavior).
3. **`master_gmail_pubsub_listener.py`** — the whole Google Cloud Pub/Sub
   chain (topic, subscription, IAM grant, `watch()`, pull loop) needs the
   one-time setup in `03_SETUP_GUIDE.md` Step 11 done for real, then a
   live test: send an email, confirm it's picked up within ~20 seconds.
4. **`master_sms_poll_service.py`** — needs a live test: text the BlueLine
   number, confirm a reply within ~90 seconds instead of waiting for 9am.
5. **BUG-14 fix (Gmail token path in `upgrade1_context_aware_messaging.py`)**
   — needs `ls ~/Downloads/gmail_token.json` confirmed to exist, then one
   context-aware SMS re-engagement test where a known recent email exists,
   to confirm the drafted message now references it (it didn't before).
6. **Two new launchd services** — need to actually be loaded, confirmed
   running (`launchctl list | grep blueline`), and stress-tested by
   letting them run 24+ hours to check for memory growth or silent death.
7. **Claude API cost under 24/7 load** — genuinely unknown until measured.
   Section 6A of the master context doc has a placeholder estimate
   (~$135-145/mo including Pub/Sub) — treat this as unconfirmed until
   you've run a full week and checked console.anthropic.com usage.
8. **`hepatitis_b` and `flu_vaccine` fields (added to `validate_documents()` and the
   Vision JSON schema this session, per Aditya's 2026-07-01 decision)** — needs a
   real test: send a test document set that includes a flu-vaccine declination form
   and a Hepatitis B vaccine card, confirm Claude Vision extracts both correctly and
   `compose_reply_email` shows them as non-blocking "Notes," not as "Still required."
   **Do not add these two categories to `11_CUSTOMER_FACING_PRODUCT_OVERVIEW.md` or
   any prospect-facing material until this test passes.**
9. **Email opt-out auto-sync (closes 🔴 gap #1, built and logic-tested
   2026-07-02, Round 6)** — needs a live test: send a real email containing
   an opt-out phrase ("please stop contacting me") from an address whose
   display name matches an existing Quo contact. Confirm (a) the phone
   number appears in `master_permanent_optouts.txt`, (b) the Quo contact is
   renamed to "DO NOT MESSAGE - {name}," and (c) the email is still flagged
   for your review in `master_needs_human_review_email.txt` with a note on
   whether the sync succeeded.

**None of items 1–7 or 9 can be verified from this project folder or by me
in this session — they all require your actual Mac, your actual Google
account, and real inbound test messages.**

---

## 🔴 KNOWN GAPS — DO NOT CLAIM THESE ARE SOLVED

1. **✅ CODE FIX BUILT AND TEST-VERIFIED 2026-07-02 (Round 6) — pending your
   real-Mac/real-credential confirmation before you can call this fully
   closed.** Email opt-outs did not auto-sync to the SMS opt-out file — an
   email like "stop contacting me" was correctly flagged (FLAG_HUMAN) but
   never touched `master_permanent_optouts.txt`. **Now fixed:**
   `email_context_bridge.py` has a dedicated `FLAG_HUMAN_OPTOUT` decision
   code (only set by Claude when it's confident the email is really an
   opt-out — never guessed from freeform reason text) that automatically
   calls `sync_email_optout_to_sms()`, which writes the matched phone to
   `master_permanent_optouts.txt` and renames the Quo contact to
   `"DO NOT MESSAGE - {name}"` — the same convention the SMS side already
   uses. `master_gmail_reviewer.py` is wired to log exactly what happened.
   Verified with 6 real, passing tests in
   `tests/test_pipeline_logic.py::TestEmailOptoutAutoSync` (mocked Quo/
   Claude calls — no live API used). **What's NOT yet verified:** a real
   opt-out email, through your real Gmail + real Quo account, actually
   getting synced end to end. Added to the 🟡 list below as item 9 — do
   the live test before telling a second customer this is solved. See
   `DYLAN_AUDIT_2026-07-01_FULL.md` Round 6.
2. **PARTIALLY MITIGATED 2026-07-02 (Round 6) — still a real, open limitation
   for a sender's FIRST email.** Name-matching between email and Quo is
   best-effort, not guaranteed — a candidate emailing under a nickname or
   with no display name won't get matched to their Quo history on that first
   email. **New this round:** `match_phone_by_sender_email()` now tries an
   exact email-address match first (no name comparison at all, so nickname
   quality is irrelevant once an email is on file), and a successful
   name-match now backfills that email onto the Quo contact
   (`backfill_email_onto_contact()`) so every subsequent email from that
   address matches directly, even if a later email uses a different display
   name. 5 passing tests in
   `tests/test_pipeline_logic.py::TestEmailMatchAndBackfill`. **What's still
   genuinely open:** the very first email from a sender whose display name
   doesn't match Quo (nickname, blank display name) still degrades
   gracefully — draft still happens, just without SMS context, same as
   before. This is a real, disclosed limitation, not solved — only the
   "does it get worse every time" part is fixed.
3. **Business-reported metrics (344+ candidates, 41 active conversations,
   $30-35K payroll, etc.) are not verifiable from code.** They live in
   Quo/Google Sheets/actual billing. Re-pull these fresh before every
   customer-facing use — don't reuse the 2026-06-30 snapshot indefinitely.
4. **White-label parameters are documented but not tested on a second
   agency's data.** Everything in `01_PRODUCT_OVERVIEW.md` §8 (rename
   persona, agency, rates, facility list) is a code change you'd make by
   hand today — there's no config file / admin panel. For a single early
   customer this is fine (you're doing the setup yourself); if you sell
   more than 2-3 before building a config layer, this becomes a real
   scaling constraint, not just a nice-to-have.
5. **No monitoring/alerting if a 24/7 service silently dies.** launchd's
   `KeepAlive` will restart a crashed process, but if it gets stuck (not
   crashed, just hung — e.g. Google auth token needs interactive
   re-approval), nothing will page you. Part 0 of `04_DAILY_OPERATIONS.md`
   is a manual daily check — there's no automated alert yet if you forget
   to look for a day.

6. **"11-point credential check" is a marketing claim the code doesn't match
   (found 2026-07-01, Round 2 audit — verified directly against
   `validate_documents()` in `master_gmail_reviewer.py`).**
   **DECISION MADE 2026-07-01 (Round 4), partially closed:** Aditya decided to add
   Hepatitis B and annual flu vaccine to the automated check, explicitly as
   **recommended, not mandatory** — same non-blocking pattern as BLS/CPR, not the
   same treatment as the 8 required categories. Rationale: both allow a signed
   declination as a compliant alternative to vaccination, and the system can't yet
   tell "no vaccine, non-compliant" apart from "no vaccine, validly declined" — so
   blocking on either would falsely flag candidates who already did the right thing.
   **Code change made this session:** `validate_documents()` and the Claude Vision
   JSON schema in `master_gmail_reviewer.py` now include `hepatitis_b` and
   `flu_vaccine`, both `optional: True`. This moves the tracked total from 9 to
   **11 (8 required + 3 recommended)** — see the new 🟡 item below before this is
   safe to say to a customer.
   **Still open, not decided:** NYS CHRC fingerprint/background-check clearance.
   Unlike the two above, there generally isn't a "declination" alternative for a
   facility that requires it — this is a different kind of gap (external process
   confirmation, not a document-with-a-date-window) and a higher-liability one if
   gotten wrong. Recommend not folding this into the same fast decision — treat as
   a separate, deliberately manual/disclosed step in onboarding until it's built
   and tested properly, not rushed into the pre-launch window.
   **Marketing discipline going forward:** never say "11-point check" without the
   8-required/3-recommended split in the same breath — that exact shorthand
   collapse is what caused this entire finding in the first place.

7. **✅ CLOSED 2026-07-02 (Round 6) — verified by actually running both
   scripts.** `pitch/build_pitch_deck.py` and `pitch/build_arch_doc_v2.py`
   hardcoded their output to `blueline_*.html`, not the real, presented
   `dylan_for_hire_*.html` files. Repointing them was considered and
   rejected: both scripts' hardcoded HTML has zero embedded audio (the real
   files have it) and predates the v3.0 24/7 real-time layer — running them
   against the real filenames would have silently regressed the current,
   audio-narrated decks to worse, stale, silent ones. **Fixed instead:**
   both scripts' `OUT` path now points to a clearly-labeled
   `DEPRECATED_DO_NOT_USE_*.html` file in `~/Downloads/BlueLine/`, with a
   docstring explaining why. **Verified by running both scripts in this
   session:** both completed without error, wrote only to the deprecated
   path, and the real `dylan_for_hire_pitch_deck.html` /
   `dylan_for_hire_architecture.html` files were confirmed byte-for-byte
   unchanged (MD5 identical before/after). To refresh a live deck going
   forward: hand-edit the real HTML file directly, or request a fresh
   rebuild starting from its current content. `03_SETUP_GUIDE.md` Step 10
   should be read with this in mind — it should NOT say "run
   build_pitch_deck.py" without this caveat. See
   `DYLAN_AUDIT_2026-07-01_FULL.md` Round 6.

---

## THE FORTNIGHT PLAN (2026-07-01 → 2026-07-15)

**Week 1 (by 2026-07-08): make the 🟡 list real**
- Complete `03_SETUP_GUIDE.md` Step 11 end to end on your Mac
- Run all 4 live tests in the 🟡 list above; fix anything that breaks
- Let both services run a full 48 hours; check logs daily (Part 0 of
  `04_DAILY_OPERATIONS.md`)
- Pull real Claude API cost data after day 3-4 of continuous operation

**Week 2 (by 2026-07-15): close or explicitly disclose the 🔴 list**
- Gaps #1 and #7 are now code-closed (Round 6, 2026-07-02) — remaining work
  is the live-Mac test for #1 (🟡 item 9) and normal use for #7 (nothing
  further to decide)
- Update the Loom walkthrough and pitch deck (V8) to show real-time
  behavior, per the note in the master context doc §9
- Re-verify every Proof-slide number is current, not a launch-day snapshot
- Run through the discovery call script once against the ACTUAL current
  system state, not the script as originally written

**Go/no-go for the first customer conversation:**
All of Week 1's 🟡 items tested and passing (including the new item 9,
email opt-out live test) — the two 🔴 gaps that used to require a decision
here are now built and logic-tested; what's left is live verification, not
a judgment call.

---

## VERIFICATION LOG — FILL THIS IN AS YOU TEST

| Item | Date tested | Result | Notes |
|------|-------------|--------|-------|
| Email general-inquiry draft (real test email) | | | |
| Real-time Gmail pickup (<30s) | | | |
| SMS reply pickup (<2min) | | | |
| BUG-14 fix confirmed (Gmail context in SMS re-engagement) | | | |
| Both launchd services stable 48hrs+ | | | |
| Claude API cost/week measured | | | |
| Email opt-out gap — code fix built + logic-tested | 2026-07-02 | 🟡 CODE DONE | Round 6 — `FLAG_HUMAN_OPTOUT` + `sync_email_optout_to_sms()` built and verified with 6 passing tests (`TestEmailOptoutAutoSync`). Live-Mac test still needed — see 🟡 item 9. |
| Email opt-out — live test (real opt-out email, real Gmail/Quo) | | | |
| BUG-15 fix confirmed (SMS poll service runs without AttributeError) | 2026-07-02 | ✅ PASS (logic) | Round 6 — actually imported and exercised `master_sms_poll_service.py`/`master_gmail_pubsub_listener.py` with mocked network calls (`tests/test_pipeline_logic.py::TestNoCrashOnImportOrWiring`); confirms no AttributeError against real function names. Live 24/7 run on your Mac still needed. |
| BUG-16 fix confirmed (DYLAN_INTRO includes STOP language, live SMS checked) | 2026-07-02 | 🟡 CODE-LOGIC PASS, DEPLOYED, LIVE SMS NOT YET CHECKED | Round 6 verified via `TestTCPACompliance`. Round 7: found this fix was NOT present in the real deployed file (v2.3) despite passing in `src/` — the two had diverged. **Now deployed** — `~/Downloads/BlueLine/master_daily_agent.py` is v2.5, confirmed byte-identical to `src/` by direct diff. Still needs one real test SMS on your Mac to see the actual STOP language land in a real message. |
| BUG-17 fix confirmed (test "please stop"/"take me off" auto-opt-out on a real test number) | 2026-07-02 | ✅ PASS (logic) | Round 6 — `TestTCPACompliance` parametrized over every documented opt-out phrase, all match. Real test number on your Mac still needed. |
| BUG-14/15/16/17/18 fixes re-verified directly against `.py` source (not just docs) | 2026-07-01 | ✅ PASS | Round 2 audit — read master_daily_agent.py, upgrade1_context_aware_messaging.py, master_sms_poll_service.py directly. All 5 fixes confirmed present in actual code. |
| BUG-19/BUG-20 found and fixed (Quo contact name-matching in `email_context_bridge.py`) | 2026-07-02 | ✅ PASS | Round 6 — found via actual pytest execution (not a code read), fixed, verified with `TestQuoContactSchemaConsistency` + regression tests. See `DYLAN_AUDIT_2026-07-01_FULL.md` Round 6 for the full write-up, including a process-failure note this round corrected. |
| Full test suite (`tests/test_pipeline_logic.py`) run end to end | 2026-07-02 | ✅ 112/112 PASS | Round 7 final re-run: `cd tests && python3 -m pytest -v` — all logic-level tests passing (75 end of Round 6 → 100 after reconciliation → 112 after hardening: +6 reconciliation, +2 corrected for master_gmail_reviewer.py v1.2, +12 for the lock/opt-out-guard/no-silent-loss hardening). Does not cover live Gmail/Quo/Claude API — see Rule 0D in `00_INDEX.md`. |
| `src/master_daily_agent.py` reconciled (v2.4) + hardened (v2.5) — deployed | 2026-07-02 | ✅ DEPLOYED, code-logic verified | Round 7 — found deployed (`~/Downloads/BlueLine/`, v2.3) and `src/` (v2.2) had diverged; reconciled to v2.4 (union of both fix histories). At Aditya's explicit instruction, hardened to v2.5 with a process lock, a hard opt-out guard in `send_sms()`, and a fix for silent candidate loss on SMS-send failure — then **copied live to `~/Downloads/BlueLine/master_daily_agent.py`**, verified byte-identical by direct diff post-copy, old v2.3 backed up alongside it as `.pre-v2.5-backup-2026-07-02`. Live-Mac behavioral test (real STOP reply, real overlapping-run scenario) still needed before claiming this is proven in production, not just in this sandbox. |
| 11-point vs 9-category credential check — decision made | 2026-07-01 | 🟡 PARTIAL | Hep B + flu vaccine added as recommended (non-blocking), code changed same session — needs live test (see 🟡 item 8). Background-check/fingerprint still undecided and explicitly deferred — see 🔴 KNOWN GAPS #6. |
| Hep B / flu vaccine fields extract correctly from a real test document | | | |
| Pitch deck build script filename mismatch — fix or retire decision | 2026-07-02 | ✅ CLOSED | Round 6 — redirected `OUT` in both scripts to a deprecated path; verified by actually running both scripts and confirming the real `dylan_for_hire_*.html` files' MD5 checksums were unchanged before/after. See 🔴 KNOWN GAPS #7. |
