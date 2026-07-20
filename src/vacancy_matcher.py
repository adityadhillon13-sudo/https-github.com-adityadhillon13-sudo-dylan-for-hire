"""
Dylan for Hire — Vacancy Matcher
====================================================
Version: 1.0 | 2026-07-09
STATUS: NEW. Query parsing + ranking are pure-function logic, fully covered
by tests/test_vacancy_matcher.py. End-to-end matching against a real
candidate_index.json has NOT been run against real data yet — run
candidate_index.py for real first, then this, on ONE real vacancy before
trusting it broadly.

PURPOSE
  Aditya types something like "2 RNs, nights, New Franklin" and gets back
  every RN active in the last N days who mentioned that center/borough in
  SMS or email history, isn't opted out, shows real paperwork status (not a
  placeholder), ranked by how ready they are. This is exactly the manual
  one-off search this project's own scripts used to require, generalized to
  any center and wired to run in seconds because it reads the precomputed
  candidate_index.json (candidate_index.py) instead of live-scanning Quo.

RANKING ORDER (see candidate_index.readiness_bucket for the reasoning):
  1. submission_ready   — fully vetted, ready to submit today
  2. hot_file           — docs complete, onboarding sent, awaiting return
  3. drafts_or_submitted — already mid-process for a specific center; shown,
                            not hidden, but below the two fully-open buckets
  4. docs_incomplete    — still missing required medical docs
  5. unscreened         — no pipeline stage on file at all

CLIENT-AGNOSTIC BY DESIGN — takes a ClientConfig, same as every other new
module in this feature set.
"""

import argparse
import logging
import re

from client_config import ClientConfig, BLUELINE_CONFIG
from center_alias import load_centers, build_alias_index, resolve_center_query
from candidate_index import load_candidate_index, query_index

log = logging.getLogger("master.vacancy_matcher")

RANK_ORDER = ["submission_ready", "hot_file", "drafts_or_submitted", "docs_incomplete", "unscreened"]

_SHIFT_KEYWORDS = {
    "AM": {"am", "day", "days", "morning", "mornings", "7a-3p", "7a–3p"},
    "PM": {"pm", "evening", "evenings", "3p-11p", "3p–11p"},
    "NOC": {"noc", "night", "nights", "overnight", "overnights", "11p-7a", "11p–7a"},
}

_VALID_ROLE_TOKENS = ("RN", "LPN", "CNA", "HHA", "MA", "CMA")
# KNOWN LIMITATION, not a bug: "RNS" (a distinct, rarer license code used
# elsewhere in this codebase's VALID_ROLES) is deliberately NOT in this list.
# Case-folded, "RNs" (plural of RN, e.g. "2 RNs") and "RNS" (the distinct
# code) are the literal same 3 characters — there is no regex that can tell
# them apart from free text alone. Since a natural vacancy request like "2
# RNs, nights, New Franklin" means plural RN far more often than the rarer
# RNS code, this parser always resolves that token to license_type="RN". If
# you specifically need candidates tagged with the RNS code, filter
# candidate_index.json directly (license_type == "RNS") rather than typing
# it into a vacancy query.


class VacancyRequest:
    def __init__(self, raw_text: str, count: int = None, license_type: str = None,
                 shift: str = None, location_query: str = ""):
        self.raw_text = raw_text
        self.count = count
        self.license_type = license_type
        self.shift = shift
        self.location_query = location_query

    def __repr__(self):
        return (f"VacancyRequest(count={self.count}, license_type={self.license_type}, "
                f"shift={self.shift}, location_query={self.location_query!r})")


def parse_vacancy_query(text: str) -> VacancyRequest:
    """Deterministic regex/keyword parse — no LLM call, so this runs in
    milliseconds and costs nothing per query. If free-text phrasing turns
    out too varied for this in practice, the natural upgrade is one small
    Claude Haiku call (same pattern already used for per-attachment
    classification in master_candidate_file_consolidator.py's
    classify_attachment) — not built here since it's unverified whether it's
    actually needed yet."""
    remaining = text

    count = None
    count_match = re.search(r"\b(\d+)\b", remaining)
    if count_match:
        count = int(count_match.group(1))
        remaining = remaining[:count_match.start()] + " " + remaining[count_match.end():]

    license_type = None
    for role in _VALID_ROLE_TOKENS:
        pattern = re.compile(rf"\b{role}s?\b", re.IGNORECASE)
        m = pattern.search(remaining)
        if m:
            license_type = role
            remaining = remaining[:m.start()] + " " + remaining[m.end():]
            break

    shift = None
    lowered = remaining.lower()
    for canonical, keywords in _SHIFT_KEYWORDS.items():
        for kw in keywords:
            if re.search(rf"\b{re.escape(kw)}\b", lowered):
                shift = canonical
                remaining = re.sub(rf"\b{re.escape(kw)}\b", " ", remaining, flags=re.IGNORECASE)
                lowered = remaining.lower()
                break
        if shift:
            break

    location_query = re.sub(r"[,\s]+", " ", remaining).strip(" ,")

    return VacancyRequest(raw_text=text, count=count, license_type=license_type,
                           shift=shift, location_query=location_query)


class MatchedCandidate:
    def __init__(self, candidate: dict, match_method: str, match_confidence: float):
        self.candidate = candidate
        self.match_method = match_method
        self.match_confidence = match_confidence


class MatchResult:
    def __init__(self, request: VacancyRequest, resolved_center: str, resolved_borough: str,
                 match_method: str, matches: list, total_before_count_cap: int):
        self.request = request
        self.resolved_center = resolved_center
        self.resolved_borough = resolved_borough
        self.match_method = match_method
        self.matches = matches
        self.total_before_count_cap = total_before_count_cap


def rank_candidates(candidates: list) -> list:
    """Sorts by readiness bucket (see RANK_ORDER), then by most-recently-active
    within each bucket.

    Two-pass: primary ascending on bucket_rank, secondary descending on
    last_active_iso. sorted() is stable, so sort by the secondary key
    descending first, then by the primary key ascending.
    """
    by_recency_desc = sorted(candidates, key=lambda c: c.get("last_active_iso") or "", reverse=True)
    return sorted(by_recency_desc, key=lambda c: (
        RANK_ORDER.index(c.get("readiness_bucket", "unscreened"))
        if c.get("readiness_bucket", "unscreened") in RANK_ORDER else len(RANK_ORDER)
    ))


def match_vacancy(query_text: str, config: ClientConfig = BLUELINE_CONFIG) -> MatchResult:
    request = parse_vacancy_query(query_text)

    centers = load_centers(config)
    alias_index = build_alias_index(centers)
    center_match = resolve_center_query(request.location_query, alias_index, centers) if request.location_query else None

    resolved_center = center_match.matched_center if center_match else None
    resolved_borough = center_match.matched_borough if center_match else None
    match_method = center_match.method if center_match else None

    index = load_candidate_index(config)
    filtered = query_index(index, license_type=request.license_type,
                            center=resolved_center, borough=resolved_borough)

    ranked = rank_candidates(filtered)
    total = len(ranked)
    capped = ranked[:request.count] if request.count else ranked

    return MatchResult(request=request, resolved_center=resolved_center,
                        resolved_borough=resolved_borough, match_method=match_method,
                        matches=capped, total_before_count_cap=total)


def format_match_result(result: MatchResult) -> str:
    lines = []
    where = result.resolved_center or result.resolved_borough or "(no center/borough recognized)"
    method_note = f" [matched via {result.match_method}]" if result.match_method else ""
    lines.append(
        f"Vacancy: {result.request.count or 'any #'} "
        f"{result.request.license_type or 'any license'} "
        f"{result.request.shift or 'any shift'} @ {where}{method_note}"
    )
    lines.append(f"{result.total_before_count_cap} candidate(s) matched"
                 + (f", showing top {len(result.matches)}" if result.request.count else ""))
    lines.append("")
    for i, c in enumerate(result.matches, 1):
        lines.append(
            f"{i}. {c.get('name')} — {c.get('license_type')} — "
            f"[{c.get('readiness_bucket')}] — {c.get('phone')} — "
            f"last active {c.get('last_active_iso') or 'unknown'}"
        )
    if not result.matches:
        lines.append("(no matches)")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Vacancy Matcher — find candidates for an opening")
    parser.add_argument("query", help='e.g. "2 RNs, nights, New Franklin"')
    parser.add_argument("--client", default="blueline", choices=["blueline"])
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    config = BLUELINE_CONFIG
    result = match_vacancy(args.query, config)
    print(format_match_result(result))


if __name__ == "__main__":
    main()
