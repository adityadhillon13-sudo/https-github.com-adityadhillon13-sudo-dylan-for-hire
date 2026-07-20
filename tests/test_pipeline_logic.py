"""
Logic-level regression tests for the Dylan for Hire / BlueLine pipeline.

WHAT THIS SUITE PROVES: every claim in these tests was executed against the
real code in src/ in this sandbox, right now, and the result (pass/fail) is
what's reported — not a re-read of a comment claiming it was tested.

WHAT THIS SUITE DOES NOT PROVE: nothing here touches a real Quo/OpenPhone
account, real Gmail, or the live Claude API. Passing this suite means the
code's internal logic is sound and self-consistent. It does NOT mean the
24/7 services will behave correctly against Aditya's actual Mac, real
credentials, or a real inbound message — that requires the live-Mac tests
in 09_GO_LIVE_READINESS.md's 🟡 list. Do not conflate the two when reporting
status to Aditya or a customer. See 00_INDEX.md Rule 0C.

Run with:  cd tests && python3 -m pytest -v
"""
import re
import sys
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

SRC_DIR = Path(__file__).resolve().parent.parent / "src"


# ============================================================================
# GROUP 1 — CRASH-CLASS BUGS (things that would AttributeError/ImportError
# the moment a live service runs). These directly re-derive BUG-15's class
# of failure instead of trusting the doc that says it's fixed.
# ============================================================================

class TestNoCrashOnImportOrWiring:

    def test_master_daily_agent_imports_cleanly(self):
        import master_daily_agent  # noqa: F401

    def test_step3_sms_reply_handler_exists(self):
        import master_daily_agent as mda
        assert hasattr(mda, "step3_sms_reply_handler"), (
            "master_daily_agent.py must expose step3_sms_reply_handler — "
            "this is the exact function master_sms_poll_service.py calls."
        )
        assert callable(mda.step3_sms_reply_handler)

    def test_sms_poll_service_calls_the_real_function_name(self):
        """Re-derives BUG-15 independently: read the actual source text of
        master_sms_poll_service.py and confirm it references a name that
        really exists on master_daily_agent, rather than trusting the
        inline comment that says it was fixed."""
        import master_daily_agent as mda
        poll_src = (SRC_DIR / "master_sms_poll_service.py").read_text()
        called_names = re.findall(r"mda\.(\w+)\(", poll_src)
        assert called_names, "Expected at least one mda.<function>() call in master_sms_poll_service.py"
        for name in called_names:
            assert hasattr(mda, name), (
                f"master_sms_poll_service.py calls mda.{name}() but master_daily_agent.py "
                f"has no such attribute — this WILL crash with AttributeError at runtime."
            )

    def test_sms_poll_service_imports_cleanly(self):
        import master_sms_poll_service  # noqa: F401

    def test_upgrade1_imports_cleanly(self):
        import upgrade1_context_aware_messaging  # noqa: F401

    def test_email_context_bridge_imports_cleanly(self):
        import email_context_bridge  # noqa: F401

    def test_gmail_reviewer_imports_cleanly(self):
        # google-auth-oauthlib etc. must be installed for this to even import.
        import master_gmail_reviewer  # noqa: F401

    def test_gmail_pubsub_listener_imports_cleanly(self):
        import master_gmail_pubsub_listener  # noqa: F401

    def test_candidate_file_consolidator_imports_cleanly(self):
        # [ADDED 2026-07-02, Round 14 audit] Found with zero test coverage —
        # depends on pypdf/Pillow (present in master_requirements.txt) and on
        # several master_gmail_reviewer.py exports (get_all_messages_from_sender,
        # get_all_attachments, save_as_draft, STAGE_READY_FOR_SUBMISSION, etc.) —
        # this import failing would mean those names silently drifted.
        import master_candidate_file_consolidator  # noqa: F401


# ============================================================================
# GROUP 2 — TCPA COMPLIANCE CLAIMS (BUG-16, BUG-17). These are the
# highest-stakes findings from the prior audit — re-verified directly here,
# not re-asserted from a doc.
# ============================================================================

class TestTCPACompliance:

    def test_dylan_intro_includes_stop_language(self):
        import master_daily_agent as mda
        assert "stop" in mda.DYLAN_INTRO.lower(), (
            "07_COMPLIANCE.md requires every first-contact SMS to include opt-out "
            "instructions. DYLAN_INTRO must contain 'Reply STOP to opt out.' or equivalent."
        )

    @pytest.mark.parametrize("phrase", [
        "please stop", "take me off", "wrong number", "leave me alone",
        "dont text", "do not text", "dont contact", "do not contact",
        "stop", "unsubscribe", "remove", "opt out", "no thanks", "not interested",
    ])
    def test_optout_keywords_cover_documented_phrases(self, phrase):
        import master_daily_agent as mda
        assert phrase in mda.OPTOUT_KEYWORDS, (
            f"07_COMPLIANCE.md / 05_PIPELINE_REFERENCE.md document '{phrase}' as an "
            f"auto-handled opt-out phrase, but it is missing from OPTOUT_KEYWORDS in code. "
            f"A candidate sending this message would NOT be auto-opted-out — TCPA exposure."
        )

    def test_optout_keyword_actually_triggers_optout_branch(self):
        """Simulates the actual text-matching logic step3 uses, for each
        documented opt-out phrase, rather than just checking set membership."""
        import master_daily_agent as mda
        for phrase in ["please stop", "take me off", "wrong number", "STOP", "UNSUBSCRIBE"]:
            text = phrase.strip().lower()
            matched = any(kw in text for kw in mda.OPTOUT_KEYWORDS)
            assert matched, f"'{phrase}' does not match any OPTOUT_KEYWORDS via substring test"

    def test_document_checklist_msg_has_no_emoji(self):
        import master_daily_agent as mda
        emoji_pattern = re.compile(
            "["
            "\U0001F300-\U0001FAFF"
            "\U00002600-\U000027BF"
            "\U0001F1E6-\U0001F1FF"
            "]+", flags=re.UNICODE,
        )
        found = emoji_pattern.findall(mda.DOCUMENT_CHECKLIST_MSG)
        assert not found, (
            f"06_COMMUNICATIONS.md Ground Rule #3 says 'No emojis in SMS' but "
            f"DOCUMENT_CHECKLIST_MSG contains: {found}"
        )

    @pytest.mark.parametrize("phrase", [
        "yes", "yep", "yeah", "sure", "interested", "definitely", "absolutely",
        "asap", "available", "tell me more", "let me know",
    ])
    def test_interest_keywords_cover_documented_phrases(self, phrase):
        import master_daily_agent as mda
        assert phrase in mda.INTEREST_KEYWORDS

    @pytest.mark.parametrize("generic_phrase", ["ok", "okay", "send", "info", "ready", "i am", "i'm"])
    def test_interest_keywords_does_not_reintroduce_the_reblast_bug(self, generic_phrase):
        """[Round 7] These generic tokens caused the real "Joyelette Miller
        repeat-blast incident" (4x) in production — the deployed system fixed
        this on 2026-06-30. Guards against ever re-widening INTEREST_KEYWORDS
        back to the version that caused that incident."""
        import master_daily_agent as mda
        assert generic_phrase not in mda.INTEREST_KEYWORDS, (
            f"'{generic_phrase}' is a generic token that previously caused the document "
            f"checklist to re-fire on casual replies from candidates already deep in the "
            f"pipeline (Joyelette Miller / Torri Allen incidents). It must never be in "
            f"INTEREST_KEYWORDS again."
        )

    @pytest.mark.parametrize("phrase", [
        "i sent", "already sent", "did you get", "did you receive", "i uploaded",
    ])
    def test_docs_sent_keywords_cover_documented_phrases(self, phrase):
        import master_daily_agent as mda
        assert phrase in mda.DOCS_SENT_KEYWORDS

    @pytest.mark.parametrize("phrase", [
        "update", "any news", "still waiting", "following up", "checking in",
    ])
    def test_update_request_keywords_cover_documented_phrases(self, phrase):
        import master_daily_agent as mda
        assert phrase in mda.UPDATE_REQUEST_KEYWORDS

    def test_checklist_sent_state_file_path_defined(self):
        import master_daily_agent as mda
        assert mda.STATE_CHECKLIST_SENT.name == "master_checklist_sent.txt"

    def test_step3_source_updates_in_memory_handled_ids_in_every_branch(self):
        """[Round 7 — re-derives the real deployed BUG-14 fix directly from source,
        not from trusting this comment.] Every branch of step3_sms_reply_handler
        must call handled_ids.add(msg_id) in addition to the on-disk
        append_to_set(STATE_INTERESTS, msg_id) — otherwise the same msg_id could
        be processed twice in one run (the "Whitaker duplicate-message incident")."""
        src = (SRC_DIR / "master_daily_agent.py").read_text()
        step3_start = src.index("def step3_sms_reply_handler")
        step3_end = src.index("def step1_reengage_stalled")
        step3_body = src[step3_start:step3_end]
        # 4 branches (opt-out, docs-sent, update-request, interest w/ 2 sub-paths, unrecognised)
        # each need their own handled_ids.add(msg_id) call.
        assert step3_body.count("handled_ids.add(msg_id)") >= 5, (
            f"Expected at least 5 handled_ids.add(msg_id) calls across step3's branches "
            f"(opt-out, docs-sent, update-request, interest x2 sub-paths, unrecognised), "
            f"found {step3_body.count('handled_ids.add(msg_id)')}. Missing one reintroduces "
            f"the duplicate-processing bug."
        )


# ============================================================================
# GROUP 2B — ROUND 7 HARDENING: process lock (no double-send from overlapping
# runs), hard opt-out guard inside send_sms() (no send can ever bypass the
# opt-out list, from any caller), and no silent loss of a candidate whose
# contact was created but whose intro SMS failed. Added at Aditya's explicit
# request for "maximum compliance, no duplication, opt-out ironclad" before
# this file is deployed over the real cron script.
# ============================================================================

class TestProcessLock:

    def test_acquire_lock_succeeds_when_no_lock_present(self, tmp_path, monkeypatch):
        import master_daily_agent as mda
        monkeypatch.setattr(mda, "LOCK_PATH", tmp_path / "agent.lock")
        assert mda.acquire_lock() is True
        assert (tmp_path / "agent.lock").exists()

    def test_acquire_lock_fails_when_a_live_lock_already_exists(self, tmp_path, monkeypatch):
        """This is the core double-send-prevention guarantee: if a second run
        starts while a first run's lock is fresh, the second run must back off
        entirely rather than proceed and risk both processes messaging the
        same candidates."""
        import master_daily_agent as mda
        lock_path = tmp_path / "agent.lock"
        monkeypatch.setattr(mda, "LOCK_PATH", lock_path)
        assert mda.acquire_lock() is True   # first run claims it
        assert mda.acquire_lock() is False  # second, overlapping run must be refused

    def test_release_lock_allows_a_subsequent_run_to_acquire_it(self, tmp_path, monkeypatch):
        import master_daily_agent as mda
        monkeypatch.setattr(mda, "LOCK_PATH", tmp_path / "agent.lock")
        assert mda.acquire_lock() is True
        mda.release_lock()
        assert mda.acquire_lock() is True  # a fresh run after the prior one finished must succeed

    def test_release_lock_is_safe_to_call_when_no_lock_exists(self, tmp_path, monkeypatch):
        """Guards main()'s `finally: release_lock()` — must never raise even if
        acquire_lock() itself was what failed (lock was never actually taken)."""
        import master_daily_agent as mda
        monkeypatch.setattr(mda, "LOCK_PATH", tmp_path / "does_not_exist.lock")
        mda.release_lock()  # must not raise

    def test_stale_lock_is_reclaimed_not_permanently_stuck(self, tmp_path, monkeypatch):
        """A hard crash (kill -9, OOM, power loss) could leave the lock file
        behind forever with no process to release it — without a staleness
        check, every future run would refuse to start, permanently. A lock
        older than LOCK_STALE_SECONDS is assumed abandoned and reclaimed."""
        import os as _os
        import master_daily_agent as mda
        lock_path = tmp_path / "agent.lock"
        lock_path.write_text("99999 stale")
        old_time = 0  # epoch — guaranteed far older than any LOCK_STALE_SECONDS threshold
        _os.utime(lock_path, (old_time, old_time))
        monkeypatch.setattr(mda, "LOCK_PATH", lock_path)
        monkeypatch.setattr(mda, "LOCK_STALE_SECONDS", 6 * 3600)
        assert mda.acquire_lock() is True

    def test_fresh_lock_is_not_reclaimed(self, tmp_path, monkeypatch):
        """The mirror image of the staleness test — a lock created moments ago
        must NOT be reclaimed, or the whole point of the lock (blocking a truly
        overlapping run) is defeated."""
        import master_daily_agent as mda
        lock_path = tmp_path / "agent.lock"
        lock_path.write_text("12345 fresh")  # mtime = now, via write_text
        monkeypatch.setattr(mda, "LOCK_PATH", lock_path)
        monkeypatch.setattr(mda, "LOCK_STALE_SECONDS", 6 * 3600)
        assert mda.acquire_lock() is False

    def test_main_calls_acquire_lock_and_release_lock_in_finally(self):
        """Source-level check that main() actually wires the lock in, not just
        that the functions exist and work in isolation."""
        src = (SRC_DIR / "master_daily_agent.py").read_text()
        main_start = src.index("def main():")
        main_body = src[main_start:]
        assert "acquire_lock()" in main_body
        assert "release_lock()" in main_body
        assert "finally:" in main_body, "release_lock() must run even if a step raises"


class TestSendSmsHardOptOutGuard:
    """[UPDATED 2026-07-02, Round 13] Every test here now also isolates
    STATE_SMS_FINGERPRINTS to a tmp_path file. Round 12 added a duplicate-send
    guard to send_sms() (fingerprints phone+exact text, refuses a repeat
    within 24h) — without this isolation, these tests write real fingerprint
    records to the shared default file, and a later pytest run in the same
    sandbox session sees "hello" already sent to +15555550100 and wrongly
    refuses it. Caught by running the suite twice in the same session, not by
    reading the code — exactly the kind of thing a single run won't reveal."""

    def test_send_sms_refuses_a_number_on_the_optout_list(self, tmp_path, monkeypatch):
        import master_daily_agent as mda
        optout_file = tmp_path / "optouts.txt"
        optout_file.write_text("+13475559999\n")
        monkeypatch.setattr(mda, "STATE_OPTOUTS", optout_file)
        monkeypatch.setattr(mda, "BLOCKED_NUMBERS", set())
        monkeypatch.setattr(mda, "STATE_SMS_FINGERPRINTS", tmp_path / "fingerprints.txt")

        network_calls = []
        monkeypatch.setattr(mda, "quo_post", lambda *a, **k: network_calls.append((a, k)))

        result = mda.send_sms("+13475559999", "this should never be sent")

        assert result == ""
        assert network_calls == [], (
            "send_sms() must refuse an opted-out number BEFORE attempting the network "
            "call — the guard tripped too late if quo_post was still invoked."
        )

    def test_send_sms_refuses_a_blocked_number(self, tmp_path, monkeypatch):
        import master_daily_agent as mda
        monkeypatch.setattr(mda, "STATE_OPTOUTS", tmp_path / "optouts_empty.txt")
        monkeypatch.setattr(mda, "BLOCKED_NUMBERS", {"+13473572031"})
        monkeypatch.setattr(mda, "STATE_SMS_FINGERPRINTS", tmp_path / "fingerprints.txt")
        network_calls = []
        monkeypatch.setattr(mda, "quo_post", lambda *a, **k: network_calls.append((a, k)))

        result = mda.send_sms("+13473572031", "this should never be sent")

        assert result == ""
        assert network_calls == []

    def test_send_sms_proceeds_for_a_number_not_on_either_list(self, tmp_path, monkeypatch):
        """Confirms the guard is a targeted check, not a blanket refusal that
        would silently break all outbound messaging."""
        import master_daily_agent as mda
        monkeypatch.setattr(mda, "STATE_OPTOUTS", tmp_path / "optouts_empty.txt")
        monkeypatch.setattr(mda, "BLOCKED_NUMBERS", set())
        monkeypatch.setattr(mda, "STATE_SMS_FINGERPRINTS", tmp_path / "fingerprints.txt")

        monkeypatch.setattr(mda, "quo_post", lambda *a, **k: {"data": {"id": "msg_123"}})

        result = mda.send_sms("+15555550100", "hello")

        assert result == "msg_123"

    def test_send_sms_guard_reads_optouts_fresh_not_a_cached_snapshot(self, tmp_path, monkeypatch):
        """The guard must catch an opt-out recorded by an earlier step in the
        SAME run (e.g. step3 processes a STOP reply, then step1 or step2 later
        in the same run must not still be able to message that number)."""
        import master_daily_agent as mda
        optout_file = tmp_path / "optouts.txt"
        optout_file.write_text("")  # starts empty
        monkeypatch.setattr(mda, "STATE_OPTOUTS", optout_file)
        monkeypatch.setattr(mda, "BLOCKED_NUMBERS", set())
        monkeypatch.setattr(mda, "STATE_SMS_FINGERPRINTS", tmp_path / "fingerprints.txt")
        monkeypatch.setattr(mda, "quo_post", lambda *a, **k: {"data": {"id": "msg_1"}})

        assert mda.send_sms("+15555550100", "first message") == "msg_1"  # allowed — not opted out yet

        # Simulate step3 recording a fresh opt-out mid-run, the way append_to_set does
        with open(optout_file, "a") as f:
            f.write("+15555550100\n")

        result = mda.send_sms("+15555550100", "second message, should be blocked")
        assert result == "", (
            "send_sms() cached the opt-out list instead of re-reading it — a number that "
            "opts out mid-run could still receive a later message in the same run."
        )


# ============================================================================
# GROUP 2D — ROUND 12: HARD DUPLICATE-SEND GUARD. Aditya's explicit rule:
# "for no reason should duplicate messages or emails be sent — ever."
# send_sms() now fingerprints (phone + exact text) and refuses a repeat
# within DUPLICATE_SEND_COOLDOWN_HOURS, regardless of which step/caller
# triggered it — same pattern as the existing opt-out guard.
# ============================================================================

class TestSendSmsDuplicateGuard:

    def test_second_identical_message_to_same_phone_is_refused(self, tmp_path, monkeypatch):
        import master_daily_agent as mda
        monkeypatch.setattr(mda, "STATE_OPTOUTS", tmp_path / "optouts_empty.txt")
        monkeypatch.setattr(mda, "BLOCKED_NUMBERS", set())
        monkeypatch.setattr(mda, "STATE_SMS_FINGERPRINTS", tmp_path / "fingerprints.txt")

        send_calls = []
        monkeypatch.setattr(mda, "quo_post", lambda *a, **k: send_calls.append(1) or {"data": {"id": "msg_1"}})

        first = mda.send_sms("+15555550100", "Hi Jane, this is Dylan...")
        second = mda.send_sms("+15555550100", "Hi Jane, this is Dylan...")  # exact same text, same phone

        assert first == "msg_1"
        assert second == "", "identical message to the same phone must be refused within the cooldown"
        assert len(send_calls) == 1, "the network must only actually be hit once, not twice"

    def test_different_message_to_same_phone_is_not_blocked(self, tmp_path, monkeypatch):
        """The guard must be scoped to (phone, exact text) — a legitimately
        different message to the same candidate (intro, then later a rate
        sheet) must never be confused with a duplicate."""
        import master_daily_agent as mda
        monkeypatch.setattr(mda, "STATE_OPTOUTS", tmp_path / "optouts_empty.txt")
        monkeypatch.setattr(mda, "BLOCKED_NUMBERS", set())
        monkeypatch.setattr(mda, "STATE_SMS_FINGERPRINTS", tmp_path / "fingerprints.txt")
        monkeypatch.setattr(mda, "quo_post", lambda *a, **k: {"data": {"id": "msg_ok"}})

        first = mda.send_sms("+15555550100", "message one")
        second = mda.send_sms("+15555550100", "a totally different message")

        assert first == "msg_ok"
        assert second == "msg_ok"

    def test_same_message_to_different_phones_is_not_blocked(self, tmp_path, monkeypatch):
        """A static template (e.g. NO_RESPONSE_FINAL) legitimately goes to
        many different candidates — the guard must be per-phone, not global."""
        import master_daily_agent as mda
        monkeypatch.setattr(mda, "STATE_OPTOUTS", tmp_path / "optouts_empty.txt")
        monkeypatch.setattr(mda, "BLOCKED_NUMBERS", set())
        monkeypatch.setattr(mda, "STATE_SMS_FINGERPRINTS", tmp_path / "fingerprints.txt")
        monkeypatch.setattr(mda, "quo_post", lambda *a, **k: {"data": {"id": "msg_ok"}})

        first = mda.send_sms("+15555550100", "same template text")
        second = mda.send_sms("+15555550200", "same template text")

        assert first == "msg_ok"
        assert second == "msg_ok"

    def test_duplicate_guard_does_not_bypass_optout_check(self, tmp_path, monkeypatch):
        """Order matters: opt-out must still be checked even for a message
        that would otherwise pass the duplicate check."""
        import master_daily_agent as mda
        optout_file = tmp_path / "optouts.txt"
        optout_file.write_text("+15555550100\n")
        monkeypatch.setattr(mda, "STATE_OPTOUTS", optout_file)
        monkeypatch.setattr(mda, "BLOCKED_NUMBERS", set())
        monkeypatch.setattr(mda, "STATE_SMS_FINGERPRINTS", tmp_path / "fingerprints.txt")
        network_calls = []
        monkeypatch.setattr(mda, "quo_post", lambda *a, **k: network_calls.append(1))

        result = mda.send_sms("+15555550100", "brand new message, never sent before")

        assert result == ""
        assert network_calls == []

    def test_fingerprint_cooldown_expires_after_window(self, tmp_path, monkeypatch):
        import master_daily_agent as mda
        monkeypatch.setattr(mda, "STATE_OPTOUTS", tmp_path / "optouts_empty.txt")
        monkeypatch.setattr(mda, "BLOCKED_NUMBERS", set())
        fp_path = tmp_path / "fingerprints.txt"
        monkeypatch.setattr(mda, "STATE_SMS_FINGERPRINTS", fp_path)
        monkeypatch.setattr(mda, "quo_post", lambda *a, **k: {"data": {"id": "msg_ok"}})

        first = mda.send_sms("+15555550100", "repeatable message")
        assert first == "msg_ok"

        # Manually back-date the recorded fingerprint past the cooldown window.
        import re as _re
        content = fp_path.read_text()
        old_ts = (datetime.now() - timedelta(hours=mda.DUPLICATE_SEND_COOLDOWN_HOURS + 1)).isoformat()
        backdated = _re.sub(r"^[^|]+\|", f"{old_ts}|", content, flags=_re.MULTILINE)
        fp_path.write_text(backdated)

        second = mda.send_sms("+15555550100", "repeatable message")
        assert second == "msg_ok", "a message outside the cooldown window must be allowed again"


class TestStep2NoSilentLossOnSendFailure:

    def test_source_flags_send_failure_to_review_not_just_the_log(self):
        """[Round 7 hardening] Before this fix, a candidate whose Quo contact
        was created but whose intro SMS failed to send would be silently lost
        forever — future runs see the Quo contact and skip them as a
        'duplicate', and log_action() alone only writes to a per-run CSV
        nobody reliably reviews. append_to_review() writes to
        master_needs_human_review.txt, the file Aditya actually checks."""
        src = (SRC_DIR / "master_daily_agent.py").read_text()
        step2_start = src.index("def step2_new_leads")
        step2_end = src.index("# ── MAIN")
        step2_body = src[step2_start:step2_end]
        send_failed_idx = step2_body.index('"SEND_FAILED"')
        # The append_to_review call for this path must appear before the
        # log_action("...SEND_FAILED"...) call, in the same else: branch.
        preceding = step2_body[:send_failed_idx]
        last_else_idx = preceding.rindex("else:")
        branch = step2_body[last_else_idx:send_failed_idx]
        assert "append_to_review(" in branch, (
            "step2_new_leads()'s SMS-send-failure branch does not call append_to_review() — "
            "a candidate whose contact was created but never messaged would be silently lost."
        )


# ============================================================================
# GROUP 2C — ROUND 11: THREE EXPLICIT RULES FROM ADITYA (2026-07-02), found
# necessary after a crontab change (30-min cadence for master_daily_agent.py)
# exposed that Step 2's "30/day" cap was actually re-granted on every same-day
# rerun (days_missed computed from .days is always 0 within one calendar day),
# and that Step 3 running from both the cron AND the 24/7 poll service could
# double-process the same reply. Rules: (1) replies are handled exclusively,
# continuously by the poll service — main() skips Step 3 by default; (2) the
# stall window is 72h, not 96h; (3) Step 2 has no per-run cap anymore.
# ============================================================================

class TestRound11PipelineRules:

    def test_stall_window_is_72_hours_not_96(self):
        import master_daily_agent as mda
        assert mda.STALL_WINDOW_HOURS == 72

    def test_daily_new_leads_cap_constants_are_gone(self):
        """DAILY_NEW_LEADS / CATCHUP_MAX drove the old 30/day (up to 150
        catchup) cap — they must be fully removed, not just unused, so no
        future code path can accidentally reference stale limits."""
        import master_daily_agent as mda
        assert not hasattr(mda, "DAILY_NEW_LEADS")
        assert not hasattr(mda, "CATCHUP_MAX")

    def test_step2_sends_to_every_eligible_row_no_matter_how_many(self, tmp_path, monkeypatch):
        """The old cap would have stopped at 30. This fixture has 40 eligible
        rows, all with distinct phones/names not already in Quo — every one
        of them must get an intro SMS in a single run now."""
        import master_daily_agent as mda

        csv_path = tmp_path / "leads.csv"
        rows = ["Name,Phone,Role,Location"]
        for i in range(40):
            rows.append(f"Candidate {i},+1347555{i:04d},CNA,Brooklyn NY")
        csv_path.write_text("\n".join(rows))

        monkeypatch.setattr(mda, "CSV_PATH", csv_path)
        monkeypatch.setattr(mda, "STATE_PROCESSED", tmp_path / "processed.txt")
        monkeypatch.setattr(mda, "STATE_OPTOUTS", tmp_path / "optouts.txt")
        monkeypatch.setattr(mda, "STATE_TIMESTAMP", tmp_path / "timestamp.txt")
        monkeypatch.setattr(mda, "BLOCKED_NUMBERS", set())
        monkeypatch.setattr(mda, "get_all_contacts", lambda: [])  # no existing Quo contacts
        monkeypatch.setattr(mda, "quo_post", lambda *a, **k: {"data": {"id": "contact_1"}})

        sent_to = []
        monkeypatch.setattr(mda, "send_sms", lambda phone, text: sent_to.append(phone) or "msg_id")

        mda.step2_new_leads()

        assert len(sent_to) == 40, (
            f"Expected all 40 eligible leads to be messaged in one run (no cap), "
            f"only {len(sent_to)} were sent to."
        )

    def test_main_skips_step3_by_default(self, tmp_path, monkeypatch):
        """main() must not call step3_sms_reply_handler() unless
        --include-step3 is explicitly passed — Step 3 belongs exclusively to
        the poll service now."""
        import master_daily_agent as mda

        monkeypatch.setattr(mda, "LOCK_PATH", tmp_path / "agent.lock")
        monkeypatch.setattr(mda.sys, "argv", ["master_daily_agent.py"])

        step3_calls = []
        monkeypatch.setattr(mda, "step3_sms_reply_handler", lambda: step3_calls.append(1))
        monkeypatch.setattr(mda, "step1_reengage_stalled", lambda: None)
        monkeypatch.setattr(mda, "merge_duplicate_contacts", lambda: None)
        monkeypatch.setattr(mda, "step2_new_leads", lambda: None)
        monkeypatch.setattr(mda, "save_run_log", lambda: None)

        mda.main()

        assert step3_calls == [], "main() called step3_sms_reply_handler() without --include-step3"

    def test_main_runs_step3_when_include_flag_passed(self, tmp_path, monkeypatch):
        """The escape hatch for manual/debug use must actually work."""
        import master_daily_agent as mda

        monkeypatch.setattr(mda, "LOCK_PATH", tmp_path / "agent.lock")
        monkeypatch.setattr(mda.sys, "argv", ["master_daily_agent.py", "--include-step3"])

        step3_calls = []
        monkeypatch.setattr(mda, "step3_sms_reply_handler", lambda: step3_calls.append(1))
        monkeypatch.setattr(mda, "step1_reengage_stalled", lambda: None)
        monkeypatch.setattr(mda, "merge_duplicate_contacts", lambda: None)
        monkeypatch.setattr(mda, "step2_new_leads", lambda: None)
        monkeypatch.setattr(mda, "save_run_log", lambda: None)

        mda.main()

        assert step3_calls == [1]

    def test_step1_uses_the_72h_stall_cutoff_function(self):
        """Regression guard: step1_reengage_stalled() must call the renamed
        stall_cutoff_ts(), not a leftover reference to the old 96h function
        name (which would be a NameError at runtime, not caught by import
        alone since it's only hit when step1 actually executes)."""
        src = (SRC_DIR / "master_daily_agent.py").read_text()
        step1_start = src.index("def step1_reengage_stalled")
        step1_end = src.index("def step2_new_leads")
        step1_body = src[step1_start:step1_end]
        assert "stall_cutoff_ts()" in step1_body
        assert "ninety_six_hours_ago_ts" not in step1_body


# ============================================================================
# GROUP 3 — DOCUMENT VALIDATION SCHEMA (the "11-point" claim). Independently
# re-derives the category count and required/optional split from the actual
# validate_documents() function, using synthetic Claude-Vision-shaped input —
# not from re-reading the prior audit's conclusion.
# ============================================================================

class TestCredentialCheckSchema:

    FULL_ANALYSIS = {
        "candidate_name": "Jane Doe",
        "nursing_license": {"found": True, "type": "RN", "state": "NY",
                             "expiry_date": "2027-01-01", "is_valid": True},
        "resume": {"found": True},
        "ids": [{"document_type": "U.S. Passport", "i9_list": "A",
                  "expiry_date": "2030-01-01", "is_expired": False, "restrictions": None}],
        "physical": {"found": True, "exam_date": "2026-01-01", "months_ago": 6},
        "mmr_titers": {"found": True, "test_date": "2024-01-01", "years_ago": 2, "result": "immune"},
        "varicella_titers": {"found": True, "test_date": "2024-01-01", "years_ago": 2, "result": "immune"},
        "chest_xray": {"found": False},
        "ppd": {"found": False},
        "quantiferon": {"found": True, "date": "2026-01-01", "months_ago": 3},
        "covid_vaccine": {"found": True, "source": "vaccine card"},
        "hepatitis_b": {"found": False},
        "flu_vaccine": {"found": False},
        "bls_cpr": {"found": False},
    }

    def test_category_count_is_12_total(self):
        """[Round 7] master_gmail_reviewer.py v1.2 added `employment_application`
        as its own tracked Vision category (candidate's signed onboarding form
        coming back), on top of the original 11 medical/credential categories.
        12 = 8 required + 4 optional-and-tracked-separately."""
        import master_gmail_reviewer as gr
        results = gr.validate_documents(self.FULL_ANALYSIS)
        assert len(results) == 12, (
            f"Expected 12 tracked categories (8 required + 4 optional, incl. "
            f"employment_application), got "
            f"{len(results)}: {sorted(results.keys())}. If this changed, "
            f"09_GO_LIVE_READINESS.md / master context §2 / "
            f"11_CUSTOMER_FACING_PRODUCT_OVERVIEW.md all need updating in the same session."
        )

    def test_required_vs_optional_split_is_8_and_4(self):
        import master_gmail_reviewer as gr
        results = gr.validate_documents(self.FULL_ANALYSIS)
        required = [k for k, v in results.items() if not v.get("optional")]
        optional = [k for k, v in results.items() if v.get("optional")]
        assert len(required) == 8, f"Expected 8 required categories, got {len(required)}: {sorted(required)}"
        assert len(optional) == 4, f"Expected 4 optional categories, got {len(optional)}: {sorted(optional)}"
        assert set(optional) == {"bls_cpr", "hepatitis_b", "flu_vaccine", "employment_application"}

    def test_missing_optional_field_does_not_block_completion(self):
        """A candidate missing only optional items (BLS/CPR, Hep B, flu) should
        be treated as complete — this is the whole point of Round 4's decision,
        and needs to actually be true in compose_reply_email(), not just in
        validate_documents()."""
        import master_gmail_reviewer as gr
        analysis = dict(self.FULL_ANALYSIS)  # all required fields present, all 3 optional missing
        results = gr.validate_documents(analysis)
        missing_required = [k for k, v in results.items() if not v.get("optional") and not v["ok"]]
        assert missing_required == [], (
            f"All 8 required categories were satisfied in this fixture but "
            f"validate_documents() still reports these as missing/required: {missing_required}"
        )

    def test_compose_reply_email_routes_optional_gaps_to_notes_not_still_required(self):
        import master_gmail_reviewer as gr
        results = gr.validate_documents(self.FULL_ANALYSIS)
        msg = gr.compose_reply_email(
            to_address="candidate@example.com",
            candidate_name="Jane Doe",
            validation_results=results,
            license_type="RN",
            original_subject="Documents",
        )
        payload = msg.get_payload()[0]
        raw = payload.get_payload(decode=True)
        body = raw.decode("utf-8") if raw is not None else payload.get_payload()
        assert "Documents Received" in msg["Subject"], (
            "All required docs present + all gaps optional should be treated as a complete file "
            "(subject line should say 'Documents Received', not 'Documents Update')."
        )
        assert "Still required" not in body, (
            "No required items are missing in this fixture — 'Still required:' section should not appear."
        )
        assert "Notes:" in body, (
            "Missing optional items (BLS/CPR, Hep B, flu) should appear under 'Notes:', "
            "confirming they're non-blocking, not silently dropped."
        )


# ============================================================================
# GROUP 4 — CONFIG CONSISTENCY (Gmail token path, Quo base URL/auth header).
# These re-derive BUG-14 and the Quo URL fix independently by comparing the
# actual constants across files, not by trusting either file's comment.
# ============================================================================

class TestConfigConsistencyAcrossFiles:

    def test_gmail_token_path_matches_across_all_three_files(self):
        import master_gmail_setup as setup
        import master_gmail_reviewer as reviewer
        import upgrade1_context_aware_messaging as upgrade1
        assert setup.TOKEN_PATH == reviewer.TOKEN_PATH == upgrade1.GMAIL_TOKEN_PATH, (
            f"Gmail token path mismatch — this is exactly BUG-14's failure mode "
            f"(silently reads from the wrong path, no error, just empty results). "
            f"setup={setup.TOKEN_PATH!r} reviewer={reviewer.TOKEN_PATH!r} "
            f"upgrade1={upgrade1.GMAIL_TOKEN_PATH!r}"
        )

    def test_gmail_credentials_path_matches(self):
        import master_gmail_setup as setup
        import master_gmail_reviewer as reviewer
        assert setup.CREDENTIALS_PATH == reviewer.CREDENTIALS_PATH

    def test_quo_base_url_consistent_across_all_files(self):
        import master_daily_agent as mda
        import upgrade1_context_aware_messaging as upgrade1
        import email_context_bridge as bridge
        assert mda.QUO_BASE == upgrade1.QUO_BASE_URL == bridge.QUO_BASE_URL == "https://api.openphone.com/v1"

    def test_quo_auth_header_has_no_bearer_prefix(self):
        """The 2026-06-29 fix removed an incorrect 'Bearer ' prefix. Re-verify
        directly rather than trusting the doc that says it's fixed."""
        import master_daily_agent as mda
        assert not mda.QUO_HEADERS["Authorization"].startswith("Bearer "), (
            "QUO_HEADERS should send the raw API key, not 'Bearer <key>' — "
            "OpenPhone's API does not use Bearer auth. Regression of the pre-06-29 bug."
        )


# ============================================================================
# GROUP 5 — QUO CONTACT SCHEMA CONSISTENCY. New finding, Round 6: does
# email_context_bridge.py parse Quo contacts using the SAME shape that
# master_daily_agent.py (the proven-in-production code) uses? If not, the
# email-to-Quo name match is not "best-effort/nickname-dependent" as
# documented in 07_COMPLIANCE.md / KNOWN GAP #2 — it may be structurally
# broken for 100% of contacts, a materially different and worse problem.
# ============================================================================

class TestQuoContactSchemaConsistency:

    # This is the exact shape master_daily_agent.py's get_all_contacts() /
    # get_contact_by_phone() / merge_duplicate_contacts() all assume, and
    # which has been proven correct in production since 2026-05-04 (per
    # 00_INDEX.md v2.1 and the BUG-01..13 fix history).
    PROVEN_SHAPE_CONTACT = {
        "id": "contact_123",
        "defaultFields": {
            "firstName": "Jane Doe",
            "lastName": "RN, Brooklyn",
            "phoneNumbers": [{"value": "+13475551234", "type": "mobile"}],
            "emails": [],
        },
    }

    def test_master_daily_agent_reads_the_proven_shape(self):
        """Sanity check on the fixture itself against the real, in-production
        reader — this must pass or the fixture is wrong, not the code."""
        import master_daily_agent as mda
        role, borough = mda.extract_role_borough_from_contact(self.PROVEN_SHAPE_CONTACT)
        assert role == "RN"
        assert borough == "Brooklyn"

    def test_email_bridge_name_match_against_the_proven_contact_shape(self, monkeypatch):
        """THE KEY TEST. If email_context_bridge.py's _quo_get_all_contacts()
        parsing assumes a different shape than the one proven correct in
        master_daily_agent.py, this will fail — meaning name-matching between
        email replies and Quo/SMS history is not just nickname-limited, it's
        non-functional for every real contact regardless of name match quality."""
        import email_context_bridge as bridge

        monkeypatch.setattr(bridge, "_quo_get_all_contacts", lambda: [self.PROVEN_SHAPE_CONTACT])

        result = bridge.match_phone_by_sender_name("Jane Doe")
        assert result is not None, (
            "match_phone_by_sender_name('Jane Doe') returned None against a contact shaped "
            "exactly like the one master_daily_agent.py proves is the real Quo API response "
            "shape (nested under 'defaultFields', phone key 'value'). email_context_bridge.py "
            "reads contacts as flat dicts with a top-level 'phoneNumbers' list and phone key "
            "'number' — a schema mismatch with the proven-correct reader. If this assertion "
            "fails, cross-channel email-to-SMS context is broken for 100% of real contacts, "
            "not just nickname edge cases as currently documented in KNOWN GAP #2."
        )


# ============================================================================
# GROUP 6 — PURE-FUNCTION UNIT TESTS (borough detection, phone normalisation,
# CSV column semantics) — fast, no mocking needed, no network.
# ============================================================================

class TestPureFunctions:

    @pytest.mark.parametrize("raw,expected", [
        ("3475551234", "+13475551234"),
        ("13475551234", "+13475551234"),
        ("+13475551234", "+13475551234"),
        ("(347) 555-1234", "+13475551234"),
    ])
    def test_normalise_phone(self, raw, expected):
        import master_daily_agent as mda
        assert mda.normalise_phone(raw) == expected

    @pytest.mark.parametrize("text,expected", [
        ("I live in Brooklyn NY", "Brooklyn"),
        ("Bronx, 10451", "Bronx"),
        ("Astoria Queens", "Queens"),
        ("no borough mentioned here", "NY"),
    ])
    def test_detect_borough(self, text, expected):
        import master_daily_agent as mda
        assert mda.detect_borough(text) == expected

    def test_extract_role_borough_handles_legacy_malformed_lastname(self):
        import master_daily_agent as mda
        contact = {"defaultFields": {"lastName": "some garbage RN text"}}
        role, borough = mda.extract_role_borough_from_contact(contact)
        assert role == "RN"

    @pytest.mark.parametrize("borough,expected_abbr", [
        ("Manhattan", "Mhtn"), ("Brooklyn", "Bklyn"), ("Queens", "Qns"),
        ("Bronx", "Bx"), ("Staten Island", "SI"), ("NY", "NY"),
    ])
    def test_borough_abbrev_covers_every_detect_borough_output(self, borough, expected_abbr):
        """[Round 7] BOROUGH_ABBREV (ported from the deployed v2.3 script) must
        have an entry for every value detect_borough() can actually return —
        otherwise step2_new_leads would silently fall back to the unabbreviated
        name for some boroughs and not others."""
        import master_daily_agent as mda
        assert mda.BOROUGH_ABBREV.get(borough) == expected_abbr

    def test_extract_role_borough_defaults_when_totally_unparseable(self):
        import master_daily_agent as mda
        contact = {"defaultFields": {"lastName": ""}}
        role, borough = mda.extract_role_borough_from_contact(contact)
        assert role == "CNA" and borough == "NY"


# ============================================================================
# GROUP 7 — STATIC SOURCE CHECKS (syntax compiles cleanly; no leftover
# TODO-class placeholders masquerading as finished work).
# ============================================================================

class TestStaticSourceHealth:

    @pytest.mark.parametrize("filename", [
        "master_daily_agent.py",
        "master_gmail_reviewer.py",
        "master_gmail_setup.py",
        "master_sms_poll_service.py",
        "master_gmail_pubsub_listener.py",
        "upgrade1_context_aware_messaging.py",
        "email_context_bridge.py",
        # [ADDED 2026-07-02, Round 14 audit] master_candidate_file_consolidator.py
        # existed in src/ with zero test coverage until this audit — found by
        # listing src/ directly and diffing against this parametrize list,
        # not by trusting a prior round's file inventory.
        "master_candidate_file_consolidator.py",
    ])
    def test_file_compiles(self, filename):
        import py_compile
        py_compile.compile(str(SRC_DIR / filename), doraise=True)


# ============================================================================
# GROUP 7B — NO UNBOUNDED NETWORK CALLS (Round 10, found live while
# diagnosing an apparent SMS poll service hang). requests defaults to
# timeout=None ("wait forever") when the kwarg is omitted — one stalled Quo
# connection would freeze the entire 24/7 poll loop indefinitely with zero
# error output. This test walks the actual AST of every file that talks to
# Quo/Gmail/Claude over HTTP and fails if ANY requests.get/post/patch/put/
# delete call is missing a timeout kwarg — structural, so it also catches
# any *future* call site someone adds without a timeout, not just today's six.
# ============================================================================

class TestNoUnboundedNetworkCalls:

    HTTP_METHODS = {"get", "post", "patch", "put", "delete"}

    @pytest.mark.parametrize("filename", [
        "master_daily_agent.py",
        "master_gmail_reviewer.py",
        "email_context_bridge.py",
        "upgrade1_context_aware_messaging.py",
        "master_candidate_file_consolidator.py",
    ])
    def test_every_requests_call_has_a_timeout(self, filename):
        import ast
        tree = ast.parse((SRC_DIR / filename).read_text())
        offenders = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            # Matches requests.get(...), requests.post(...), etc.
            if (isinstance(func, ast.Attribute) and func.attr in self.HTTP_METHODS
                    and isinstance(func.value, ast.Name) and func.value.id == "requests"):
                has_timeout = any(kw.arg == "timeout" for kw in node.keywords)
                if not has_timeout:
                    offenders.append(f"line {node.lineno}: requests.{func.attr}(...)")
        assert offenders == [], (
            f"{filename} has requests call(s) with no timeout= kwarg — these will hang "
            f"forever on a stalled connection instead of failing and letting the caller's "
            f"retry/backoff logic handle it: {offenders}"
        )


# ============================================================================
# GROUP 8 — EMAIL OPT-OUT AUTO-SYNC (closes KNOWN GAP #1, added Round 6).
# Exercises the real sync_email_optout_to_sms() function against a temp file
# standing in for master_permanent_optouts.txt, and confirms the decision
# engine's FLAG_HUMAN_OPTOUT parsing/routing is wired correctly — with the
# real Claude call mocked out (no live API key used in this suite).
# ============================================================================

class TestEmailOptoutAutoSync:

    def test_sync_writes_phone_to_optout_file(self, tmp_path, monkeypatch):
        import email_context_bridge as bridge
        optout_file = tmp_path / "master_permanent_optouts.txt"
        monkeypatch.setattr(bridge, "STATE_OPTOUTS_PATH", str(optout_file))
        monkeypatch.setattr(bridge, "QUO_API_KEY", None)  # skip the rename-contact network call

        result = bridge.sync_email_optout_to_sms("(347) 555-9999", "Jane Doe")

        assert result["synced"] is True
        assert result["already_synced"] is False
        assert optout_file.exists()
        assert "+13475559999" in optout_file.read_text().splitlines()

    def test_sync_does_not_duplicate_existing_optout(self, tmp_path, monkeypatch):
        import email_context_bridge as bridge
        optout_file = tmp_path / "master_permanent_optouts.txt"
        optout_file.write_text("+13475559999\n")
        monkeypatch.setattr(bridge, "STATE_OPTOUTS_PATH", str(optout_file))
        monkeypatch.setattr(bridge, "QUO_API_KEY", None)

        result = bridge.sync_email_optout_to_sms("+13475559999", "Jane Doe")

        assert result["already_synced"] is True
        assert optout_file.read_text().count("+13475559999") == 1

    def test_sync_attempts_contact_rename_when_quo_match_found(self, tmp_path, monkeypatch):
        import email_context_bridge as bridge
        optout_file = tmp_path / "master_permanent_optouts.txt"
        monkeypatch.setattr(bridge, "STATE_OPTOUTS_PATH", str(optout_file))
        monkeypatch.setattr(bridge, "QUO_API_KEY", "fake-key-for-test")

        fake_contact = {
            "id": "contact_999",
            "defaultFields": {"firstName": "Jane Doe", "lastName": "RN, Brooklyn",
                               "phoneNumbers": [{"value": "+13475559999"}]},
        }
        monkeypatch.setattr(bridge, "_quo_get_all_contacts", lambda: [fake_contact])

        patch_calls = []

        class FakeResp:
            ok = True
            def raise_for_status(self):
                pass

        def fake_patch(url, headers=None, json=None, timeout=None):
            patch_calls.append((url, json))
            return FakeResp()

        monkeypatch.setattr(bridge.requests, "patch", fake_patch)

        result = bridge.sync_email_optout_to_sms("+13475559999", "Jane Doe")

        assert result["rename_ok"] is True
        assert len(patch_calls) == 1
        assert "contact_999" in patch_calls[0][0]
        assert patch_calls[0][1]["defaultFields"]["firstName"].startswith("DO NOT MESSAGE")

    def test_decide_email_reply_parses_flag_human_optout_before_flag_human(self, monkeypatch):
        """FLAG_HUMAN_OPTOUT is a superstring of FLAG_HUMAN's prefix check —
        this test guards the ordering bug that would misroute it."""
        import email_context_bridge as bridge

        class FakeContent:
            def __init__(self, text):
                self.text = text

        class FakeResponse:
            def __init__(self, text):
                self.content = [FakeContent(text)]

        class FakeMessages:
            def create(self, **kwargs):
                return FakeResponse("FLAG_HUMAN_OPTOUT: candidate asked to stop being contacted")

        class FakeClient:
            messages = FakeMessages()

        monkeypatch.setattr(bridge.anthropic, "Anthropic", lambda api_key: FakeClient())
        monkeypatch.setattr(bridge, "CLAUDE_API_KEY", "fake-key-for-test")

        result = bridge.decide_email_reply(
            sender_name="Jane Doe", sender_email="jane@example.com", subject="Please stop",
            inbound_body="Please stop emailing and texting me.",
            gmail_thread_history="", quo_sms_history="",
        )

        assert result["decision"] == "FLAG_HUMAN_OPTOUT"
        assert result["decision"] != "FLAG_HUMAN"  # the exact misrouting this test guards against

    def test_get_context_aware_email_reply_syncs_on_optout_with_match(self, tmp_path, monkeypatch):
        import email_context_bridge as bridge
        optout_file = tmp_path / "master_permanent_optouts.txt"
        monkeypatch.setattr(bridge, "STATE_OPTOUTS_PATH", str(optout_file))
        monkeypatch.setattr(bridge, "QUO_API_KEY", None)

        monkeypatch.setattr(bridge, "match_phone_by_sender_email", lambda email: None)
        monkeypatch.setattr(bridge, "match_phone_by_sender_name",
                             lambda name: ("+13475559999", "Jane Doe", "RN, Brooklyn"))
        monkeypatch.setattr(bridge, "get_quo_history", lambda phone: "")
        monkeypatch.setattr(bridge, "backfill_email_onto_contact", lambda name, email: False)
        monkeypatch.setattr(bridge, "decide_email_reply",
                             lambda **kwargs: {"decision": "FLAG_HUMAN_OPTOUT",
                                                "reason": "opt-out", "draft_body": None})

        result = bridge.get_context_aware_email_reply(
            sender_name="Jane Doe", sender_email="jane@example.com", subject="Stop",
            inbound_body="stop", gmail_thread_history="",
        )

        assert result["sync_result"]["synced"] is True
        assert "+13475559999" in optout_file.read_text()

    def test_get_context_aware_email_reply_reports_no_match_instead_of_silent_noop(self, monkeypatch):
        """If there's no Quo match, the sync can't happen — this must be
        visible in the returned dict, not silently absent."""
        import email_context_bridge as bridge

        monkeypatch.setattr(bridge, "match_phone_by_sender_email", lambda email: None)
        monkeypatch.setattr(bridge, "match_phone_by_sender_name", lambda name: None)
        monkeypatch.setattr(bridge, "decide_email_reply",
                             lambda **kwargs: {"decision": "FLAG_HUMAN_OPTOUT",
                                                "reason": "opt-out", "draft_body": None})

        result = bridge.get_context_aware_email_reply(
            sender_name="Unknown Sender", sender_email="unknown@example.com", subject="Stop",
            inbound_body="stop", gmail_thread_history="",
        )

        assert result["sync_result"]["synced"] is False


# ============================================================================
# GROUP 9 — EMAIL-TO-QUO MATCH BY EXACT EMAIL + SELF-HEALING BACKFILL
# (partial mitigation for KNOWN GAP #2, added Round 6). Email match should be
# tried first and be unambiguous; a successful name-match should backfill the
# email so next time no name comparison is needed at all.
# ============================================================================

class TestEmailMatchAndBackfill:

    def test_match_by_email_finds_contact_with_matching_email_on_file(self):
        import email_context_bridge as bridge
        contact = {
            "id": "c1",
            "defaultFields": {
                "firstName": "Jane Doe", "lastName": "RN, Brooklyn",
                "phoneNumbers": [{"value": "+13475559999"}],
                "emails": [{"value": "jane.d@gmail.com"}],
            },
        }
        import email_context_bridge as bridge
        orig = bridge._quo_get_all_contacts
        bridge._quo_get_all_contacts = lambda: [contact]
        try:
            result = bridge.match_phone_by_sender_email("Jane.D@gmail.com")  # case-insensitive
            assert result is not None
            assert result[0] == "+13475559999"
        finally:
            bridge._quo_get_all_contacts = orig

    def test_match_by_email_returns_none_when_no_contact_has_that_email(self):
        import email_context_bridge as bridge
        orig = bridge._quo_get_all_contacts
        bridge._quo_get_all_contacts = lambda: [{
            "id": "c1",
            "defaultFields": {"firstName": "Jane Doe", "phoneNumbers": [{"value": "+13475559999"}],
                               "emails": []},
        }]
        try:
            assert bridge.match_phone_by_sender_email("nobody@example.com") is None
        finally:
            bridge._quo_get_all_contacts = orig

    def test_backfill_writes_email_onto_matching_contact(self, monkeypatch):
        import email_context_bridge as bridge
        monkeypatch.setattr(bridge, "QUO_API_KEY", "fake-key-for-test")
        contact = {
            "id": "c1",
            "defaultFields": {"firstName": "Jane Doe", "lastName": "RN, Brooklyn",
                               "phoneNumbers": [{"value": "+13475559999"}], "emails": []},
        }
        monkeypatch.setattr(bridge, "_quo_get_all_contacts", lambda: [contact])

        patch_calls = []

        class FakeResp:
            ok = True

        def fake_patch(url, headers=None, json=None, timeout=None):
            patch_calls.append((url, json))
            return FakeResp()

        monkeypatch.setattr(bridge.requests, "patch", fake_patch)

        result = bridge.backfill_email_onto_contact("Jane Doe", "jane.d@gmail.com")

        assert result is True
        assert len(patch_calls) == 1
        assert patch_calls[0][1]["defaultFields"]["emails"] == [{"value": "jane.d@gmail.com"}]

    def test_backfill_does_not_duplicate_already_present_email(self, monkeypatch):
        import email_context_bridge as bridge
        monkeypatch.setattr(bridge, "QUO_API_KEY", "fake-key-for-test")
        contact = {
            "id": "c1",
            "defaultFields": {"firstName": "Jane Doe",
                               "phoneNumbers": [{"value": "+13475559999"}],
                               "emails": [{"value": "jane.d@gmail.com"}]},
        }
        monkeypatch.setattr(bridge, "_quo_get_all_contacts", lambda: [contact])
        monkeypatch.setattr(bridge.requests, "patch",
                             lambda *a, **k: (_ for _ in ()).throw(AssertionError("should not PATCH — already on file")))

        result = bridge.backfill_email_onto_contact("Jane Doe", "jane.d@gmail.com")
        assert result is False

    def test_get_context_aware_email_reply_prefers_email_match_over_name_match(self, monkeypatch):
        """If both an email match and a name match are available, the email
        match must win — it's unambiguous, name match is best-effort."""
        import email_context_bridge as bridge

        monkeypatch.setattr(bridge, "match_phone_by_sender_email",
                             lambda email: ("+13475551111", "Jane Doe", "RN, Brooklyn"))
        monkeypatch.setattr(bridge, "match_phone_by_sender_name",
                             lambda name: ("+13475552222", "Wrong Match", "CNA, Queens"))
        monkeypatch.setattr(bridge, "get_quo_history", lambda phone: "")
        monkeypatch.setattr(bridge, "backfill_email_onto_contact",
                             lambda name, email: (_ for _ in ()).throw(
                                 AssertionError("should not backfill — email match already succeeded")))
        monkeypatch.setattr(bridge, "decide_email_reply",
                             lambda **kwargs: {"decision": "SKIP", "reason": "test", "draft_body": None})

        result = bridge.get_context_aware_email_reply(
            sender_name="Jane Doe", sender_email="jane.d@gmail.com", subject="Hi",
            inbound_body="hi", gmail_thread_history="",
        )
        # No direct return of matched phone from get_context_aware_email_reply,
        # but backfill NOT being called (would have raised AssertionError above)
        # is itself proof the email-match path was taken over the name-match path.
        assert result["decision"] == "SKIP"

    def test_get_context_aware_email_reply_backfills_after_successful_name_match(self, monkeypatch):
        import email_context_bridge as bridge

        monkeypatch.setattr(bridge, "match_phone_by_sender_email", lambda email: None)
        monkeypatch.setattr(bridge, "match_phone_by_sender_name",
                             lambda name: ("+13475551111", "Jane Doe", "RN, Brooklyn"))
        monkeypatch.setattr(bridge, "get_quo_history", lambda phone: "")
        backfill_calls = []
        monkeypatch.setattr(bridge, "backfill_email_onto_contact",
                             lambda name, email: backfill_calls.append((name, email)))
        monkeypatch.setattr(bridge, "decide_email_reply",
                             lambda **kwargs: {"decision": "SKIP", "reason": "test", "draft_body": None})

        bridge.get_context_aware_email_reply(
            sender_name="Jane Doe", sender_email="jane.d@gmail.com", subject="Hi",
            inbound_body="hi", gmail_thread_history="",
        )

        assert backfill_calls == [("Jane Doe", "jane.d@gmail.com")]


# ============================================================================
# GROUP 10 — QUO CONTACT LIST CACHING (Round 9B, live-traffic finding).
# _quo_get_all_contacts() re-fetched all ~3,794 Quo contacts (paginated, ~38
# sequential HTTP calls) on EVERY call — confirmed live on 2026-07-02 to take
# 4m51s for a single email, defeating the point of the real-time listener.
# These tests exercise the real caching logic (module-level _CONTACTS_CACHE),
# not a monkeypatched stand-in for the function — that's the whole point:
# GROUP 9's tests replace _quo_get_all_contacts() wholesale to isolate other
# logic; these tests are what actually prove the cache itself works. Network
# is mocked at the requests.get layer only.
# ============================================================================

class TestQuoContactCache:

    def _reset_cache(self, bridge):
        bridge._CONTACTS_CACHE["data"] = None
        bridge._CONTACTS_CACHE["fetched_at"] = 0.0

    def _one_page_response(self, contacts):
        class FakeResp:
            ok = True
            def json(inner_self):
                return {"data": contacts, "nextPageToken": None}
        return FakeResp()

    def test_first_call_fetches_and_populates_cache(self, monkeypatch):
        import email_context_bridge as bridge
        self._reset_cache(bridge)
        monkeypatch.setattr(bridge, "QUO_API_KEY", "fake-key")

        call_count = {"n": 0}
        contact = {"id": "c1", "defaultFields": {"firstName": "Jane Doe"}}

        def fake_get(url, headers=None, params=None, timeout=None):
            call_count["n"] += 1
            return self._one_page_response([contact])

        monkeypatch.setattr(bridge.requests, "get", fake_get)

        result = bridge._quo_get_all_contacts()

        assert result == [contact]
        assert call_count["n"] == 1
        assert bridge._CONTACTS_CACHE["data"] == [contact]
        assert bridge._CONTACTS_CACHE["fetched_at"] > 0

    def test_second_call_within_ttl_skips_fetch(self, monkeypatch):
        """This is the core fix: within the 5-minute TTL, a second call must
        NOT hit the network again — that's the 4m51s-per-email bug closing."""
        import email_context_bridge as bridge
        self._reset_cache(bridge)
        monkeypatch.setattr(bridge, "QUO_API_KEY", "fake-key")

        call_count = {"n": 0}
        contact = {"id": "c1", "defaultFields": {"firstName": "Jane Doe"}}

        def fake_get(url, headers=None, params=None, timeout=None):
            call_count["n"] += 1
            return self._one_page_response([contact])

        monkeypatch.setattr(bridge.requests, "get", fake_get)

        first = bridge._quo_get_all_contacts()
        second = bridge._quo_get_all_contacts()

        assert first == second == [contact]
        assert call_count["n"] == 1  # only ONE real fetch across both calls

    def test_cache_expires_after_ttl(self, monkeypatch):
        import email_context_bridge as bridge
        self._reset_cache(bridge)
        monkeypatch.setattr(bridge, "QUO_API_KEY", "fake-key")

        call_count = {"n": 0}

        def fake_get(url, headers=None, params=None, timeout=None):
            call_count["n"] += 1
            return self._one_page_response([{"id": f"c{call_count['n']}"}])

        monkeypatch.setattr(bridge.requests, "get", fake_get)

        # Freeze "now" to a known value, populate the cache.
        fake_now = {"t": 1000.0}
        monkeypatch.setattr(bridge.time, "time", lambda: fake_now["t"])
        bridge._quo_get_all_contacts()
        assert call_count["n"] == 1

        # Advance time past the TTL — next call must re-fetch.
        fake_now["t"] = 1000.0 + bridge._CONTACTS_CACHE_TTL_SECONDS + 1
        bridge._quo_get_all_contacts()
        assert call_count["n"] == 2

    def test_force_refresh_bypasses_cache_even_within_ttl(self, monkeypatch):
        import email_context_bridge as bridge
        self._reset_cache(bridge)
        monkeypatch.setattr(bridge, "QUO_API_KEY", "fake-key")

        call_count = {"n": 0}

        def fake_get(url, headers=None, params=None, timeout=None):
            call_count["n"] += 1
            return self._one_page_response([{"id": f"c{call_count['n']}"}])

        monkeypatch.setattr(bridge.requests, "get", fake_get)

        bridge._quo_get_all_contacts()
        bridge._quo_get_all_contacts(force_refresh=True)

        assert call_count["n"] == 2  # force_refresh must trigger a real second fetch

    def test_partial_failed_fetch_does_not_poison_cache(self, monkeypatch):
        """A fetch that errors out mid-pagination must NOT overwrite a good
        cached list with an incomplete one — silently masking real contacts
        for 5 minutes would be worse than the stale-but-complete data."""
        import email_context_bridge as bridge
        self._reset_cache(bridge)
        monkeypatch.setattr(bridge, "QUO_API_KEY", "fake-key")

        good_contact = {"id": "good"}

        class GoodResp:
            ok = True
            def json(self):
                return {"data": [good_contact], "nextPageToken": None}

        class FailResp:
            ok = False
            status_code = 500
            text = "Quo API error"

        responses = iter([GoodResp(), FailResp()])
        monkeypatch.setattr(bridge.requests, "get",
                             lambda *a, **kw: next(responses))

        # First call succeeds and populates the cache.
        first = bridge._quo_get_all_contacts()
        assert first == [good_contact]

        # Force past TTL so the second call actually attempts a real fetch.
        bridge._CONTACTS_CACHE["fetched_at"] = 0.0
        second = bridge._quo_get_all_contacts()

        # The failed fetch must fall back to the last good cached list, not
        # an empty/partial result, and must NOT have overwritten the cache.
        assert second == [good_contact]
        assert bridge._CONTACTS_CACHE["data"] == [good_contact]

    def test_missing_api_key_returns_stale_cache_instead_of_empty_list(self, monkeypatch):
        """If QUO_API_KEY disappears mid-run (env issue), a caller that
        already had a good cached list should keep working, not silently
        start seeing zero contacts."""
        import email_context_bridge as bridge
        self._reset_cache(bridge)

        contact = {"id": "c1"}
        bridge._CONTACTS_CACHE["data"] = [contact]
        bridge._CONTACTS_CACHE["fetched_at"] = 0.0  # stale, but present

        monkeypatch.setattr(bridge, "QUO_API_KEY", None)

        result = bridge._quo_get_all_contacts()
        assert result == [contact]


# ============================================================================
# GROUP 11 — CONTACT-ID RESOLUTION BEYOND PAGE 1 (Round 9C, found live while
# verifying Round 9B on 2026-07-02). push_candidate_status_to_quo() used to
# resolve a matched phone number's Quo contact_id via its own unpaginated
# fetch (pageSize=100 only, out of ~3,794 total contacts) — so any match
# outside the first 100 contacts would silently fail to resolve an ID and
# drop the dashboard stage push, even though match_phone_by_sender_name()
# (which searches the FULL paginated+cached list) had already found the
# right phone number. Fixed to reuse _quo_get_all_contacts() instead.
# ============================================================================

class TestPushStageContactIdResolvesBeyondPageOne:

    def test_contact_id_resolves_when_match_is_outside_first_page(self, monkeypatch):
        import master_gmail_reviewer as reviewer

        # 150 contacts total — more than one API "page" (100) — with the
        # matching phone number placed at index 120, deliberately past where
        # the old pageSize=100-only fetch would ever have looked.
        contacts = [
            {"id": f"c{i}", "defaultFields": {"phoneNumbers": [{"value": f"+1347555{i:04d}"}]}}
            for i in range(150)
        ]
        target_phone = "+13475550120"
        contacts[120]["defaultFields"]["phoneNumbers"] = [{"value": target_phone}]

        # [UPDATED 2026-07-02, Round 13 — sync with the other concurrent session's
        # v1.5 change] push_candidate_status_to_quo() now resolves the candidate
        # via resolve_candidate_contact() (phone-first, then email, then fuzzy
        # name — see that function's own docstring) instead of calling
        # match_phone_by_sender_name() directly. The contact-ID-from-full-list
        # fix this test guards (Round 9C) is unaffected — it's the next step
        # after the match is found — so only the mock target changes here.
        monkeypatch.setattr(reviewer, "QUO_API_KEY", "fake-key")
        monkeypatch.setattr(reviewer, "resolve_candidate_contact",
                             lambda sender_email, sender_display_name, email_body_text="":
                             (target_phone, "Jane Doe", "RN, Brooklyn"))
        monkeypatch.setattr(reviewer, "_quo_get_all_contacts", lambda: contacts)

        class FakePatchResp:
            ok = True
        monkeypatch.setattr(reviewer.requests, "patch", lambda *a, **kw: FakePatchResp())

        result = reviewer.push_candidate_status_to_quo(
            sender_email="jane.d@gmail.com", sender_display_name="Jane Doe",
            stage="PIPELINE:DOCS_INCOMPLETE",
        )

        assert result is True, (
            "Contact at index 120 (beyond any single 100-item page) must still "
            "resolve — this is exactly the case the old pageSize=100 fetch missed."
        )

    def test_contact_id_resolution_uses_cached_list_not_a_fresh_unpaginated_fetch(self, monkeypatch):
        """Regression guard: this must NOT call requests.get for a second,
        separate /contacts fetch — it should reuse the same cached full list
        resolve_candidate_contact() already used."""
        import master_gmail_reviewer as reviewer

        contact = {"id": "c1", "defaultFields": {"phoneNumbers": [{"value": "+13475551111"}]}}

        monkeypatch.setattr(reviewer, "QUO_API_KEY", "fake-key")
        monkeypatch.setattr(reviewer, "resolve_candidate_contact",
                             lambda sender_email, sender_display_name, email_body_text="":
                             ("+13475551111", "Jane Doe", "RN, Brooklyn"))
        monkeypatch.setattr(reviewer, "_quo_get_all_contacts", lambda: [contact])

        get_calls = []
        monkeypatch.setattr(reviewer.requests, "get", lambda *a, **kw: get_calls.append(1))

        class FakePatchResp:
            ok = True
        monkeypatch.setattr(reviewer.requests, "patch", lambda *a, **kw: FakePatchResp())

        reviewer.push_candidate_status_to_quo(
            sender_email="jane.d@gmail.com", sender_display_name="Jane Doe",
            stage="PIPELINE:DOCS_INCOMPLETE",
        )

        assert get_calls == [], "push_candidate_status_to_quo must not make its own separate /contacts GET call"


# ============================================================================
# GROUP — CENTER-DOMAIN EMAIL EXCLUSION (added 2026-07-03).
# Guards the bug found live in cron_output.log: known BlueLine center/facility
# contacts (dp@fvrehab.com, mmeyer@dbnrc.com, etc.) were processed as if they
# were candidates because is_system_or_non_candidate_email() only excluded
# BlueLine's own address, not center domains. Fix reads domains dynamically
# from BLUELINE_CENTER_DIRECTORY.md rather than hardcoding BlueLine's specific
# centers into shared code (13_DYLAN_PRODUCT_CONSTITUTION.md §6).
# ============================================================================

class TestCenterDomainEmailExclusion:

    SAMPLE_DIRECTORY_TEXT = """
    # BLUELINE CENTER DIRECTORY (sample fixture — not the real file)

    ## Forest View Rehab
    Contact: Debbie Umrao-Paray
    Email: dp@fvrehab.com

    ## Downtown Brooklyn Nursing
    Contact: contact
    Email: mmeyer@dbnrc.com

    ## Rebekah Rehab
    Email: scormack@rebekahrehab.org
    """

    def test_load_center_email_domains_extracts_domains_from_directory_text(self, tmp_path, monkeypatch):
        import master_gmail_reviewer as gr
        directory_file = tmp_path / "BLUELINE_CENTER_DIRECTORY.md"
        directory_file.write_text(self.SAMPLE_DIRECTORY_TEXT)
        monkeypatch.setattr(gr, "CENTER_DIRECTORY_PATH", directory_file)
        gr.reset_center_domain_cache()

        domains = gr.load_center_email_domains()

        assert domains == {"fvrehab.com", "dbnrc.com", "rebekahrehab.org"}

    def test_load_center_email_domains_caches_after_first_read(self, tmp_path, monkeypatch):
        """Directory shouldn't be re-read from disk on every email checked in a run."""
        import master_gmail_reviewer as gr
        directory_file = tmp_path / "BLUELINE_CENTER_DIRECTORY.md"
        directory_file.write_text(self.SAMPLE_DIRECTORY_TEXT)
        monkeypatch.setattr(gr, "CENTER_DIRECTORY_PATH", directory_file)
        gr.reset_center_domain_cache()

        first = gr.load_center_email_domains()
        directory_file.write_text("")  # if it re-read now, this would wipe the result
        second = gr.load_center_email_domains()

        assert first == second == {"fvrehab.com", "dbnrc.com", "rebekahrehab.org"}

    def test_load_center_email_domains_fails_open_when_file_missing(self, tmp_path, monkeypatch):
        """An unreachable directory must degrade to 'no extra exclusions', never to
        accidentally blocking real candidates."""
        import master_gmail_reviewer as gr
        monkeypatch.setattr(gr, "CENTER_DIRECTORY_PATH", tmp_path / "does_not_exist.md")
        gr.reset_center_domain_cache()

        assert gr.load_center_email_domains() == set()

    def test_center_domain_sender_is_excluded_as_non_candidate(self, tmp_path, monkeypatch):
        """This is the exact live bug: dp@fvrehab.com must now be excluded."""
        import master_gmail_reviewer as gr
        directory_file = tmp_path / "BLUELINE_CENTER_DIRECTORY.md"
        directory_file.write_text(self.SAMPLE_DIRECTORY_TEXT)
        monkeypatch.setattr(gr, "CENTER_DIRECTORY_PATH", directory_file)
        gr.reset_center_domain_cache()

        assert gr.is_system_or_non_candidate_email("dp@fvrehab.com") is True
        assert gr.is_system_or_non_candidate_email("mmeyer@dbnrc.com") is True
        assert gr.is_system_or_non_candidate_email("MMeyer@DBNRC.com") is True  # case-insensitive

    def test_real_candidate_email_still_passes_through(self, tmp_path, monkeypatch):
        """A real candidate at a gmail/yahoo/etc. address must not be caught by
        this new exclusion — only known center domains should be blocked."""
        import master_gmail_reviewer as gr
        directory_file = tmp_path / "BLUELINE_CENTER_DIRECTORY.md"
        directory_file.write_text(self.SAMPLE_DIRECTORY_TEXT)
        monkeypatch.setattr(gr, "CENTER_DIRECTORY_PATH", directory_file)
        gr.reset_center_domain_cache()

        assert gr.is_system_or_non_candidate_email("jane.doe.rn@gmail.com") is False


# ============================================================================
# GROUP — MIME-TYPE SNIFFING (added 2026-07-03).
# Guards the bug found live in cron_output.log: a document from
# mmeyer@dbnrc.com failed Claude Vision analysis with a 400 (declared
# image/png, actual bytes image/jpeg) because media_type was derived purely
# from the filename extension. Real magic-byte fixtures below, not fabricated
# placeholders — a 1x1 real PNG/JPEG and a minimal valid PDF header.
# ============================================================================

class TestMimeTypeSniffing:

    REAL_PNG_BYTES = bytes.fromhex(
        "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
        "0000000a49444154789c6360000002000155a3f0b70000000049454e44ae426082"
    )
    REAL_JPEG_BYTES = bytes.fromhex("ffd8ffe000104a46494600010100000100010000" + "00" * 20)
    REAL_TIFF_LE_BYTES = bytes.fromhex("49492a00" + "00" * 20)
    REAL_TIFF_BE_BYTES = bytes.fromhex("4d4d002a" + "00" * 20)
    REAL_PDF_BYTES = b"%PDF-1.4\n%..."

    def test_sniff_detects_real_png(self):
        import master_gmail_reviewer as gr
        assert gr.sniff_media_type_from_bytes(self.REAL_PNG_BYTES) == "image/png"

    def test_sniff_detects_real_jpeg(self):
        import master_gmail_reviewer as gr
        assert gr.sniff_media_type_from_bytes(self.REAL_JPEG_BYTES) == "image/jpeg"

    def test_sniff_detects_tiff_both_byte_orders(self):
        import master_gmail_reviewer as gr
        assert gr.sniff_media_type_from_bytes(self.REAL_TIFF_LE_BYTES) == "image/tiff"
        assert gr.sniff_media_type_from_bytes(self.REAL_TIFF_BE_BYTES) == "image/tiff"

    def test_sniff_detects_pdf(self):
        import master_gmail_reviewer as gr
        assert gr.sniff_media_type_from_bytes(self.REAL_PDF_BYTES) == "application/pdf"

    def test_sniff_returns_none_for_unrecognized_or_empty_bytes(self):
        """None means 'don't know' — the caller must fall back to the extension
        guess, not have this function invent an answer for corrupt/truncated data."""
        import master_gmail_reviewer as gr
        assert gr.sniff_media_type_from_bytes(b"not a real image at all") is None
        assert gr.sniff_media_type_from_bytes(b"") is None

    def test_analyze_attachments_uses_sniffed_type_over_mismatched_extension(self, monkeypatch):
        """This is the exact live bug: a file named *.png that is actually JPEG bytes
        must be sent to Claude with media_type=image/jpeg, not image/png."""
        import master_gmail_reviewer as gr

        captured = {}

        class FakeContent:
            text = '{"candidate_name": null}'

        class FakeResponse:
            content = [FakeContent()]

        class FakeMessages:
            def create(self, **kwargs):
                captured["content_blocks"] = kwargs["messages"][0]["content"]
                return FakeResponse()

        class FakeClient:
            messages = FakeMessages()

        attachments = [{
            "filename": "physical_exam.png",  # extension says PNG
            "data": self.REAL_JPEG_BYTES,       # actual bytes are JPEG
            "mime_type": "image/png",
            "message_id": "msg1",
        }]

        gr.analyze_attachments_with_claude(attachments, FakeClient())

        image_blocks = [b for b in captured["content_blocks"] if b.get("type") == "image"]
        assert len(image_blocks) == 1
        assert image_blocks[0]["source"]["media_type"] == "image/jpeg", (
            "Extension said image/png but the real bytes are JPEG — the API call must use the "
            "sniffed type, or Claude's API will reject it with the exact 400 seen live in "
            "cron_output.log."
        )

    def test_analyze_attachments_falls_back_to_extension_when_bytes_unrecognized(self, monkeypatch):
        """Corrupt/truncated data (sniff returns None) must not block analysis outright —
        falls back to the pre-existing extension-based guess."""
        import master_gmail_reviewer as gr

        captured = {}

        class FakeContent:
            text = '{"candidate_name": null}'

        class FakeResponse:
            content = [FakeContent()]

        class FakeMessages:
            def create(self, **kwargs):
                captured["content_blocks"] = kwargs["messages"][0]["content"]
                return FakeResponse()

        class FakeClient:
            messages = FakeMessages()

        attachments = [{
            "filename": "scan.png",
            "data": b"totally-corrupt-not-a-real-image",
            "mime_type": "image/png",
            "message_id": "msg1",
        }]

        gr.analyze_attachments_with_claude(attachments, FakeClient())

        image_blocks = [b for b in captured["content_blocks"] if b.get("type") == "image"]
        assert image_blocks[0]["source"]["media_type"] == "image/png"
