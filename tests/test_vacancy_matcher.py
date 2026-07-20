"""
Tests for the 2026-07-09 Vacancy Matcher feature set: center_alias.py,
candidate_index.py, vacancy_matcher.py, outreach_drafts.py, pipeline_depth.py.

Same posture as test_pipeline_logic.py (see its own docstring): every claim
here was executed against the real code in src/ in this sandbox, right now.
No test in this file makes a real network call to api.openphone.com or the
Claude API — every Quo call is mocked.
"""
import json
import sys
from pathlib import Path

import pytest

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

import client_config as cc  # noqa: E402
import center_alias as ca  # noqa: E402
import candidate_index as ci  # noqa: E402
import vacancy_matcher as vm  # noqa: E402
import outreach_drafts as od  # noqa: E402
import pipeline_depth as pd  # noqa: E402
import master_daily_agent as mda  # noqa: E402


# ============================================================================
# GROUP 1 — center_alias.py
# ============================================================================

class TestCenterAliasResolution:

    def test_exact_curated_alias_matches(self):
        centers = ca.load_centers(cc.BLUELINE_CONFIG)
        index = ca.build_alias_index(centers)
        match = ca.resolve_center_query("2 RNs nights New Franklin", index, centers)
        # Canonical name is the short form ("Franklin"), not the full formal
        # name — see CURATED_ALIASES's Round 18 comment: real candidate data
        # confirmed short names are what this codebase actually uses.
        assert match.matched_center == "Franklin"
        assert match.method == "exact"

    def test_fort_tryon_typo_resolves(self):
        """The exact example Aditya gave when this feature was requested —
        confirmed real via BlueLine Automation's independent, real-data-
        validated build (Round 18 reconciliation)."""
        centers = ca.load_centers(cc.BLUELINE_CONFIG)
        index = ca.build_alias_index(centers)
        match = ca.resolve_center_query("fort tyrone", index, centers)
        assert match.matched_center == "Fort Tryon"

    def test_canonical_full_name_matches_exactly(self):
        centers = ca.load_centers(cc.BLUELINE_CONFIG)
        index = ca.build_alias_index(centers)
        match = ca.resolve_center_query("Bushwick Center for Rehabilitation and Healthcare", index, centers)
        assert match.matched_center == "Bushwick Center for Rehabilitation and Healthcare"
        assert match.method == "exact"

    def test_fuzzy_typo_still_resolves(self):
        """'concrod' is a made-up one-letter-swapped typo of the real seeded
        center 'Concord Nursing and Rehabilitation Center' — this is exactly
        the class of typo (like the user's own 'fort tyrone' example) the
        fuzzy layer exists to catch."""
        centers = ca.load_centers(cc.BLUELINE_CONFIG)
        index = ca.build_alias_index(centers)
        match = ca.resolve_center_query("concrod", index, centers)
        assert match.matched_center == "Concord Nursing and Rehabilitation Center"
        assert match.method == "fuzzy"
        assert match.confidence >= ca.FUZZY_ACCEPT_THRESHOLD

    def test_borough_fallback_when_no_center_named(self):
        centers = ca.load_centers(cc.BLUELINE_CONFIG)
        index = ca.build_alias_index(centers)
        match = ca.resolve_center_query("looking for shifts in the bronx", index, centers)
        assert match.matched_center is None
        assert match.matched_borough == "Bronx"
        assert match.method == "borough"

    def test_nonsense_query_matches_nothing(self):
        centers = ca.load_centers(cc.BLUELINE_CONFIG)
        index = ca.build_alias_index(centers)
        match = ca.resolve_center_query("xyzzy plugh qwerty", index, centers)
        assert match.matched_center is None
        assert match.matched_borough is None
        assert match.method is None

    def test_load_centers_falls_back_to_seed_when_real_file_missing(self, tmp_path, monkeypatch):
        fake_config = cc.ClientConfig(
            client_id="test",
            center_directory_path=tmp_path / "does_not_exist.md",
        )
        centers = ca.load_centers(fake_config)
        assert len(centers) > 0
        names = {c.canonical_name for c in centers}
        assert "Franklin" in names
        assert "Fort Tryon" in names

    def test_markdown_borough_section_parser_on_real_format(self, tmp_path):
        """Uses the EXACT structure this project's own 06_COMMUNICATIONS.md
        uses today (### Borough heading, - bullet lines) — real format,
        not invented."""
        text = (
            "### Brooklyn\n"
            "- Test Rehab Center One\n"
            "- Test Rehab Center Two\n"
            "\n"
            "### Bronx\n"
            "- Test Bronx Facility\n"
        )
        path = tmp_path / "centers.md"
        path.write_text(text)
        fake_config = cc.ClientConfig(client_id="test", center_directory_path=path)
        centers = ca.load_centers(fake_config)
        names_and_boroughs = {(c.canonical_name, c.borough) for c in centers}
        assert ("Test Rehab Center One", "Brooklyn") in names_and_boroughs
        assert ("Test Bronx Facility", "Bronx") in names_and_boroughs

    def test_near_miss_below_accept_threshold_is_not_matched(self):
        centers = ca.load_centers(cc.BLUELINE_CONFIG)
        index = ca.build_alias_index(centers)
        # Deliberately unrelated-enough text that no real center/borough
        # should match, to confirm the log-only near-miss path doesn't leak
        # into an accepted match.
        match = ca.resolve_center_query("completely unrelated random text here", index, centers)
        assert match.matched_center is None


class TestBoroughKeywordsStayInSync:
    """This project has a real prior incident (Round 7's INTEREST_KEYWORDS
    reconciliation) of two copies of the same constant silently diverging.
    center_alias.py deliberately duplicates master_daily_agent.py's
    BOROUGH_KEYWORDS (see that module's comment for why) — this test makes
    sure that duplication can never silently drift."""

    def test_borough_keywords_identical_to_master_daily_agent(self):
        assert ca.BOROUGH_KEYWORDS == mda.BOROUGH_KEYWORDS


class TestExtractRoleBoroughStaysInSync:
    """Same reasoning as above, for candidate_index.py's duplicated
    extract_role_borough()."""

    @pytest.mark.parametrize("last_name,expected", [
        ("RN, Brooklyn", ("RN", "Brooklyn")),
        ("CNA, Bronx", ("CNA", "Bronx")),
        ("LPN, Queens", ("LPN", "Queens")),
        ("garbage no comma", ("CNA", "NY")),
        ("RNS, Manhattan", ("RNS", "Manhattan")),
    ])
    def test_matches_master_daily_agent_output(self, last_name, expected):
        contact = {"defaultFields": {"lastName": last_name}}
        mda_result = mda.extract_role_borough_from_contact(contact)
        ci_result = ci.extract_role_borough(contact, mda.VALID_ROLES)
        assert ci_result == expected
        assert ci_result == mda_result


# ============================================================================
# GROUP 2 — candidate_index.py
# ============================================================================

class TestReadinessBucket:

    def test_ready_for_submission_is_top_bucket(self):
        from master_gmail_reviewer import STAGE_READY_FOR_SUBMISSION
        assert ci.readiness_bucket(STAGE_READY_FOR_SUBMISSION) == "submission_ready"

    def test_docs_complete_sent_is_hot_file(self):
        from master_gmail_reviewer import STAGE_DOCS_COMPLETE_SENT
        assert ci.readiness_bucket(STAGE_DOCS_COMPLETE_SENT) == "hot_file"

    def test_drafts_ready_prefix_bucketed_correctly(self):
        from master_candidate_file_consolidator import STAGE_DRAFTS_READY_PREFIX
        assert ci.readiness_bucket(STAGE_DRAFTS_READY_PREFIX + "2026-07-09") == "drafts_or_submitted"

    def test_submitted_prefix_bucketed_correctly(self):
        from master_gmail_reviewer import STAGE_SUBMITTED_PREFIX
        assert ci.readiness_bucket(STAGE_SUBMITTED_PREFIX + "2026-07-09") == "drafts_or_submitted"

    def test_docs_incomplete(self):
        from master_gmail_reviewer import STAGE_DOCS_INCOMPLETE
        assert ci.readiness_bucket(STAGE_DOCS_INCOMPLETE) == "docs_incomplete"

    def test_blank_or_new_is_unscreened(self):
        from master_gmail_reviewer import STAGE_NEW
        assert ci.readiness_bucket(STAGE_NEW) == "unscreened"
        assert ci.readiness_bucket("") == "unscreened"
        assert ci.readiness_bucket(None) == "unscreened"


class TestOptOutDetection:

    def test_do_not_message_prefix_is_opted_out(self):
        contact = {"defaultFields": {"firstName": "DO NOT MESSAGE - Jane Doe"}}
        assert ci.is_opted_out(contact, "+15551234567", set()) is True

    def test_phone_in_optouts_file_is_opted_out(self):
        contact = {"defaultFields": {"firstName": "Jane Doe"}}
        assert ci.is_opted_out(contact, "+15551234567", {"+15551234567"}) is True

    def test_normal_contact_not_opted_out(self):
        contact = {"defaultFields": {"firstName": "Jane Doe"}}
        assert ci.is_opted_out(contact, "+15551234567", set()) is False


class TestBuildCandidateIndexNeverHitsRealNetwork:
    """The core of the '429s went away' claim: this test mocks
    requests.get entirely and verifies build_candidate_index() produces a
    correct, filtered, atomically-written index from that fake data."""

    def _fake_response(self, payload):
        class FakeResp:
            ok = True
            status_code = 200
            headers = {}
            def json(inner_self):
                return payload
        return FakeResp()

    def test_end_to_end_index_build_with_mocked_quo(self, tmp_path, monkeypatch):
        config = cc.ClientConfig(
            client_id="test",
            candidate_index_path=tmp_path / "index.json",
            optouts_path=tmp_path / "optouts.txt",
            center_directory_path=tmp_path / "missing_centers.md",  # forces seed fallback
        )
        monkeypatch.setenv("QUO_API_KEY", "fake-key")
        monkeypatch.setenv("QUO_PHONE_NUMBER_ID", "fake-phone-id")

        active_contact = {
            "defaultFields": {
                "firstName": "Jane Doe",
                "lastName": "RN, Brooklyn",
                "role": "PIPELINE:ONBOARD_RETURNED_READY_FOR_SUBMISSION",
                "phoneNumbers": [{"value": "+15551111111"}],
            }
        }
        opted_out_contact = {
            "defaultFields": {
                "firstName": "DO NOT MESSAGE - John Smith",
                "lastName": "CNA, Bronx",
                "role": "",
                "phoneNumbers": [{"value": "+15552222222"}],
            }
        }

        def fake_get(url, headers=None, params=None, timeout=None):
            if "/conversations" in url:
                return self._fake_response({
                    "data": [
                        {"participants": ["+15551111111"],
                         "lastActivityAt": "2026-07-09T10:00:00Z"},
                        {"participants": ["+15552222222"],
                         "lastActivityAt": "2026-07-09T09:00:00Z"},
                    ],
                    "nextPageToken": None,
                })
            if "/contacts" in url:
                return self._fake_response({
                    "data": [active_contact, opted_out_contact],
                    "nextPageToken": None,
                })
            if "/messages" in url:
                phone = None
                for p in (params or []):
                    if isinstance(p, tuple) and p[0] == "participants[]":
                        phone = p[1]
                if phone == "+15551111111":
                    return self._fake_response({
                        "data": [{"text": "I can work at New Franklin", "createdAt": "2026-07-09T10:00:00Z"}],
                        "nextPageToken": None,
                    })
                return self._fake_response({"data": [], "nextPageToken": None})
            return self._fake_response({"data": [], "nextPageToken": None})

        monkeypatch.setattr(ci.requests, "get", fake_get)

        index = ci.build_candidate_index(config, active_days=30)

        assert index["client_id"] == "test"
        assert len(index["candidates"]) == 1  # opted-out contact must be excluded
        candidate = index["candidates"][0]
        assert candidate["phone"] == "+15551111111"
        assert candidate["license_type"] == "RN"
        assert candidate["readiness_bucket"] == "submission_ready"
        assert "Franklin" in candidate["centers_mentioned"]

        # File was actually written, atomically, and is re-loadable.
        assert config.candidate_index_path.exists()
        reloaded = json.loads(config.candidate_index_path.read_text())
        assert reloaded == index

    def test_messages_call_includes_required_phone_number_id(self, tmp_path, monkeypatch):
        """[ADDED 2026-07-10, Round 18 reconciliation] Direct regression test
        for a real bug found by comparing this file against BlueLine
        Automation's independently-built blueline_quo_helpers.py: /messages
        REQUIRES phoneNumberId or it can silently return empty results with
        no error. fetch_message_text() was missing it before this round."""
        config = cc.ClientConfig(client_id="test")
        monkeypatch.setenv("QUO_API_KEY", "fake-key")
        monkeypatch.setenv("QUO_PHONE_NUMBER_ID", "the-real-phone-id")
        monkeypatch.setattr(ci.time, "sleep", lambda s: None)

        seen_params = {}

        def fake_get(url, headers=None, params=None, timeout=None):
            if "/messages" in url:
                seen_params["params"] = params
            return self._fake_response({"data": [], "nextPageToken": None})

        monkeypatch.setattr(ci.requests, "get", fake_get)
        ci.fetch_message_text(config, "+15551111111")

        param_keys = [p[0] for p in seen_params["params"] if isinstance(p, tuple)]
        assert "phoneNumberId" in param_keys, (
            "fetch_message_text() must send phoneNumberId on every /messages call — "
            "without it, OpenPhone can silently return empty results with no error."
        )

    def test_outgoing_messages_excluded_from_center_scanning(self, tmp_path, monkeypatch):
        """[ADDED 2026-07-10, Round 18 reconciliation] Direct regression test
        for the second bug found via the same comparison: only the
        CANDIDATE's own words should count as a stated center preference —
        Dylan's own automated outbound text shouldn't be scanned as if the
        candidate said it."""
        config = cc.ClientConfig(client_id="test")
        monkeypatch.setenv("QUO_API_KEY", "fake-key")
        monkeypatch.setenv("QUO_PHONE_NUMBER_ID", "fake-phone-id")
        monkeypatch.setattr(ci.time, "sleep", lambda s: None)

        def fake_get(url, headers=None, params=None, timeout=None):
            if "/messages" in url:
                return self._fake_response({
                    "data": [
                        {"text": "I only want Bronx Park", "direction": "incoming",
                         "createdAt": "2026-07-09T10:00:00Z"},
                        {"text": "Great, we have an opening at Franklin for you",
                         "direction": "outgoing", "createdAt": "2026-07-09T10:01:00Z"},
                    ],
                    "nextPageToken": None,
                })
            return self._fake_response({"data": [], "nextPageToken": None})

        monkeypatch.setattr(ci.requests, "get", fake_get)
        text = ci.fetch_message_text(config, "+15551111111")

        assert "Bronx Park" in text
        assert "Franklin" not in text

    def test_429_triggers_retry_not_immediate_failure(self, monkeypatch, tmp_path):
        """Directly re-derives the 429 fix: a first 429 response must be
        retried, not treated as terminal."""
        config = cc.ClientConfig(client_id="test")
        monkeypatch.setenv("QUO_API_KEY", "fake-key")
        monkeypatch.setattr(ci.time, "sleep", lambda s: None)  # don't actually wait in tests

        call_log = []

        def fake_get(url, headers=None, params=None, timeout=None):
            call_log.append(1)
            if len(call_log) == 1:
                class RateLimited:
                    ok = False
                    status_code = 429
                    headers = {}
                return RateLimited()
            return self._fake_response({"data": [], "nextPageToken": None})

        monkeypatch.setattr(ci.requests, "get", fake_get)
        resp = ci._quo_get(config, "/contacts")
        assert len(call_log) == 2  # first 429, then a real retry happened
        assert resp.ok


class TestQueryIndex:

    def _sample_index(self):
        return {
            "candidates": [
                {"phone": "+1", "license_type": "RN", "home_borough": "Brooklyn",
                 "boroughs_mentioned": ["Brooklyn"], "centers_mentioned": ["Bushwick Center for Rehabilitation and Healthcare"],
                 "readiness_bucket": "submission_ready", "last_active_iso": "2026-07-09T10:00:00Z"},
                {"phone": "+2", "license_type": "CNA", "home_borough": "Bronx",
                 "boroughs_mentioned": ["Bronx"], "centers_mentioned": [],
                 "readiness_bucket": "docs_incomplete", "last_active_iso": "2026-07-08T10:00:00Z"},
            ]
        }

    def test_filters_by_license_type(self):
        results = ci.query_index(self._sample_index(), license_type="RN")
        assert len(results) == 1
        assert results[0]["phone"] == "+1"

    def test_filters_by_center(self):
        results = ci.query_index(self._sample_index(), center="Bushwick Center for Rehabilitation and Healthcare")
        assert len(results) == 1
        assert results[0]["phone"] == "+1"

    def test_filters_by_borough_mentioned_or_home(self):
        results = ci.query_index(self._sample_index(), borough="Bronx")
        assert len(results) == 1
        assert results[0]["phone"] == "+2"

    def test_no_filters_returns_everyone(self):
        results = ci.query_index(self._sample_index())
        assert len(results) == 2


# ============================================================================
# GROUP 3 — vacancy_matcher.py
# ============================================================================

class TestParseVacancyQuery:

    def test_the_exact_example_from_the_feature_request(self):
        req = vm.parse_vacancy_query("2 RNs, nights, New Franklin")
        assert req.count == 2
        assert req.license_type == "RN"
        assert req.shift == "NOC"
        assert "new franklin" in req.location_query.lower()

    def test_am_shift_and_cnas(self):
        req = vm.parse_vacancy_query("3 CNAs AM Bushwick")
        assert req.count == 3
        assert req.license_type == "CNA"
        assert req.shift == "AM"
        assert "bushwick" in req.location_query.lower()

    def test_no_count_given(self):
        req = vm.parse_vacancy_query("LPN overnight Bronx")
        assert req.count is None
        assert req.license_type == "LPN"
        assert req.shift == "NOC"

    def test_rns_code_resolves_to_rn_known_limitation(self):
        """Documents a real, unfixable ambiguity: case-folded, 'RNs' (plural
        of RN) and 'RNS' (the distinct rarer license code) are the literal
        same 3 characters. This parser always resolves the token to 'RN'
        since that's overwhelmingly the intended meaning in a natural
        vacancy request — see vacancy_matcher.py's comment on
        _VALID_ROLE_TOKENS for the full reasoning."""
        req = vm.parse_vacancy_query("1 RNS Manhattan")
        assert req.license_type == "RN"


class TestRankCandidates:

    def test_submission_ready_ranks_above_hot_file(self):
        candidates = [
            {"name": "B", "readiness_bucket": "hot_file", "last_active_iso": "2026-07-09T00:00:00Z"},
            {"name": "A", "readiness_bucket": "submission_ready", "last_active_iso": "2026-07-08T00:00:00Z"},
        ]
        ranked = vm.rank_candidates(candidates)
        assert [c["name"] for c in ranked] == ["A", "B"]

    def test_full_order_all_five_buckets(self):
        candidates = [
            {"name": "unscreened", "readiness_bucket": "unscreened", "last_active_iso": "2026-07-01T00:00:00Z"},
            {"name": "docs_incomplete", "readiness_bucket": "docs_incomplete", "last_active_iso": "2026-07-01T00:00:00Z"},
            {"name": "drafts_or_submitted", "readiness_bucket": "drafts_or_submitted", "last_active_iso": "2026-07-01T00:00:00Z"},
            {"name": "hot_file", "readiness_bucket": "hot_file", "last_active_iso": "2026-07-01T00:00:00Z"},
            {"name": "submission_ready", "readiness_bucket": "submission_ready", "last_active_iso": "2026-07-01T00:00:00Z"},
        ]
        ranked = vm.rank_candidates(candidates)
        assert [c["name"] for c in ranked] == [
            "submission_ready", "hot_file", "drafts_or_submitted", "docs_incomplete", "unscreened",
        ]

    def test_most_recently_active_wins_within_same_bucket(self):
        candidates = [
            {"name": "older", "readiness_bucket": "hot_file", "last_active_iso": "2026-07-01T00:00:00Z"},
            {"name": "newer", "readiness_bucket": "hot_file", "last_active_iso": "2026-07-08T00:00:00Z"},
        ]
        ranked = vm.rank_candidates(candidates)
        assert [c["name"] for c in ranked] == ["newer", "older"]


class TestMatchVacancyEndToEnd:

    def test_matches_and_caps_by_count(self, tmp_path, monkeypatch):
        config = cc.ClientConfig(
            client_id="test",
            candidate_index_path=tmp_path / "index.json",
            center_directory_path=tmp_path / "missing.md",
        )
        index_data = {
            "candidates": [
                {"phone": f"+{i}", "name": f"Candidate {i}", "license_type": "RN",
                 "home_borough": "Manhattan", "boroughs_mentioned": [],
                 "centers_mentioned": ["Franklin"],
                 "readiness_bucket": "submission_ready" if i == 1 else "docs_incomplete",
                 "last_active_iso": "2026-07-09T00:00:00Z"}
                for i in range(1, 4)
            ]
        }
        config.candidate_index_path.write_text(json.dumps(index_data))

        result = vm.match_vacancy("2 RNs, nights, New Franklin", config)
        assert result.resolved_center == "Franklin"
        assert result.total_before_count_cap == 3
        assert len(result.matches) == 2
        assert result.matches[0]["readiness_bucket"] == "submission_ready"


# ============================================================================
# GROUP 4 — outreach_drafts.py (draft-only invariant)
# ============================================================================

class TestOutreachDraftsNeverSend:

    def test_module_imports_no_send_capable_function(self):
        """Parses outreach_drafts.py's actual AST (not a substring search
        over the raw text, which would false-positive on this exact
        module's own docstring explaining the invariant) and asserts: no
        `import requests` (there's no legitimate reason this module needs
        network access), and no call anywhere named send_sms/send_message/
        send-anything. Same spirit as test_pipeline_logic.py's
        TestNoCrashOnImportOrWiring — verify the real code, not a comment
        claiming it's safe."""
        import ast
        tree = ast.parse((SRC_DIR / "outreach_drafts.py").read_text())

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "requests", (
                        "outreach_drafts.py imports `requests` — this module must "
                        "never be capable of reaching the network."
                    )
            if isinstance(node, ast.Call):
                func_name = ""
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr
                assert "send" not in func_name.lower(), (
                    f"outreach_drafts.py calls a function named '{func_name}' — "
                    f"this module must only ever write a local draft file, never send."
                )

    def test_write_outreach_drafts_produces_a_file_not_a_send(self, tmp_path):
        config = cc.ClientConfig(client_id="test", outreach_drafts_dir=tmp_path)
        request = vm.VacancyRequest(raw_text="2 RNs nights New Franklin", count=2,
                                     license_type="RN", shift="NOC",
                                     location_query="new franklin")
        result = vm.MatchResult(
            request=request,
            resolved_center="New Franklin Center for Rehabilitation and Nursing",
            resolved_borough=None, match_method="exact",
            matches=[{"name": "Jane Doe", "phone": "+15551111111",
                      "license_type": "RN", "readiness_bucket": "submission_ready"}],
            total_before_count_cap=1,
        )
        path = od.write_outreach_drafts(result, config)
        assert path is not None
        assert path.exists()
        content = path.read_text()
        assert "DRAFT — NOT SENT" in content
        assert "Jane Doe" in content
        assert "Reply STOP to opt out." in content

    def test_no_matches_writes_no_file(self, tmp_path):
        config = cc.ClientConfig(client_id="test", outreach_drafts_dir=tmp_path)
        request = vm.VacancyRequest(raw_text="1 RN nowhere", count=1, license_type="RN")
        result = vm.MatchResult(request=request, resolved_center=None, resolved_borough=None,
                                 match_method=None, matches=[], total_before_count_cap=0)
        path = od.write_outreach_drafts(result, config)
        assert path is None
        assert list(tmp_path.iterdir()) == []


class TestOutreachDraftContent:

    def test_no_emoji_and_includes_optout_line(self):
        candidate = {"name": "Jane Doe", "license_type": "RN"}
        message = od.draft_message_for_candidate(candidate, "New Franklin Center for Rehabilitation and Nursing", None, "NOC")
        assert "Reply STOP to opt out." in message
        # 06_COMMUNICATIONS.md Ground Rule #3 — no emojis in SMS.
        assert all(ord(ch) < 0x1F300 for ch in message)


# ============================================================================
# GROUP 5 — pipeline_depth.py
# ============================================================================

class TestPipelineDepthReport:

    def test_counts_by_license_and_bucket_for_a_borough(self, tmp_path):
        config = cc.ClientConfig(
            client_id="test",
            candidate_index_path=tmp_path / "index.json",
            center_directory_path=tmp_path / "missing.md",
        )
        index_data = {
            "candidates": [
                {"phone": "+1", "license_type": "RN", "home_borough": "Bronx",
                 "boroughs_mentioned": ["Bronx"], "centers_mentioned": [],
                 "readiness_bucket": "submission_ready", "last_active_iso": "2026-07-09T00:00:00Z"},
                {"phone": "+2", "license_type": "CNA", "home_borough": "Bronx",
                 "boroughs_mentioned": ["Bronx"], "centers_mentioned": [],
                 "readiness_bucket": "docs_incomplete", "last_active_iso": "2026-07-09T00:00:00Z"},
                {"phone": "+3", "license_type": "RN", "home_borough": "Queens",
                 "boroughs_mentioned": ["Queens"], "centers_mentioned": [],
                 "readiness_bucket": "hot_file", "last_active_iso": "2026-07-09T00:00:00Z"},
            ]
        }
        config.candidate_index_path.write_text(json.dumps(index_data))

        report = pd.pipeline_depth_report("Bronx", config)
        assert report["resolved_borough"] == "Bronx"
        assert report["total"] == 2
        assert report["by_license"] == {"RN": 1, "CNA": 1}
        assert report["by_readiness_bucket"] == {"submission_ready": 1, "docs_incomplete": 1}

    def test_unresolvable_location_returns_zero(self, tmp_path):
        config = cc.ClientConfig(
            client_id="test",
            candidate_index_path=tmp_path / "index.json",
            center_directory_path=tmp_path / "missing.md",
        )
        config.candidate_index_path.write_text(json.dumps({"candidates": []}))
        report = pd.pipeline_depth_report("nonsense query xyz", config)
        assert report["total"] == 0
