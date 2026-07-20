"""
Dylan for Hire — Pipeline-Depth Lookup For Biz Dev
====================================================
Version: 1.0 | 2026-07-09
STATUS: NEW, covered by tests/test_vacancy_matcher.py.

PURPOSE
  Flips Vacancy Matcher around for biz dev: before pitching a new facility,
  "how many qualified candidates in our pool have said they'd work in this
  borough" becomes a one-line proof point instead of a guess. Reads the same
  precomputed candidate_index.json as vacancy_matcher.py — no separate data
  source, no separate Quo calls, so the two can never disagree about who's
  actually in the pool.

CLIENT-AGNOSTIC BY DESIGN — takes a ClientConfig, same as every other new
  module in this feature set.
"""

import argparse
import logging
from collections import defaultdict

from client_config import ClientConfig, BLUELINE_CONFIG
from center_alias import load_centers, build_alias_index, resolve_center_query
from candidate_index import load_candidate_index, query_index
from vacancy_matcher import RANK_ORDER

log = logging.getLogger("master.pipeline_depth")


def pipeline_depth_report(location_query: str, config: ClientConfig = BLUELINE_CONFIG) -> dict:
    """Returns {"resolved_center": ..., "resolved_borough": ..., "match_method": ...,
    "total": N, "by_license": {"RN": N, ...}, "by_readiness_bucket": {"submission_ready": N, ...}}
    """
    centers = load_centers(config)
    alias_index = build_alias_index(centers)
    center_match = resolve_center_query(location_query, alias_index, centers)

    index = load_candidate_index(config)
    matched = query_index(index, center=center_match.matched_center, borough=center_match.matched_borough)

    by_license = defaultdict(int)
    by_bucket = defaultdict(int)
    for c in matched:
        by_license[c.get("license_type", "UNKNOWN")] += 1
        by_bucket[c.get("readiness_bucket", "unscreened")] += 1

    return {
        "location_query": location_query,
        "resolved_center": center_match.matched_center,
        "resolved_borough": center_match.matched_borough,
        "match_method": center_match.method,
        "total": len(matched),
        "by_license": dict(by_license),
        "by_readiness_bucket": dict(by_bucket),
    }


def format_report(report: dict) -> str:
    where = report["resolved_center"] or report["resolved_borough"] or "(no center/borough recognized)"
    lines = [f"Pipeline depth for: {where}", f"Total qualified candidates: {report['total']}", ""]
    if report["by_license"]:
        lines.append("By license type:")
        for lic, n in sorted(report["by_license"].items()):
            lines.append(f"  {lic}: {n}")
        lines.append("")
    if report["by_readiness_bucket"]:
        lines.append("By readiness:")
        for bucket in RANK_ORDER:
            n = report["by_readiness_bucket"].get(bucket)
            if n:
                lines.append(f"  {bucket}: {n}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Pipeline-depth lookup for biz dev")
    parser.add_argument("location", help='e.g. "Bronx" or "New Franklin"')
    parser.add_argument("--client", default="blueline", choices=["blueline"])
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    config = BLUELINE_CONFIG
    report = pipeline_depth_report(args.location, config)
    print(format_report(report))


if __name__ == "__main__":
    main()
