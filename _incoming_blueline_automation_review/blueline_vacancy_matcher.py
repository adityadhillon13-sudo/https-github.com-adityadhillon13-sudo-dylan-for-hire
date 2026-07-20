"""
BlueLine Staffing -- Vacancy Matcher
====================================================
Version: 1.0 | 2026-07-09

Given a center name (and optionally a license type), returns every active
candidate who plausibly wants to work there, ranked by paperwork readiness.
Reads the precomputed candidate_center_index.json (built by
blueline_candidate_index_builder.py) -- if that file is missing or stale
(>24h old), this warns loudly rather than silently matching stale data.

USAGE:
  python3.11 blueline_vacancy_matcher.py --center "Franklin" --license RN
  python3.11 blueline_vacancy_matcher.py --center "Franklin" --license RN --draft

--draft writes ready-to-review outreach message text (one per matched
candidate) to vacancy_outreach_drafts.txt -- nothing is ever auto-sent, same
draft-only invariant as every other candidate-facing output in this codebase.
"""

import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

from blueline_center_aliases import canonicalize_center_name

INDEX_PATH  = Path.home() / "Downloads" / "BlueLine" / "candidate_center_index.json"
DRAFTS_PATH = Path.home() / "Downloads" / "BlueLine" / "vacancy_outreach_drafts.txt"

STAGE_RANK = {
    "PIPELINE:ONBOARD_RETURNED_READY_FOR_SUBMISSION": 0,
    "PIPELINE:DOCS_COMPLETE_ONBOARD_SENT": 1,
    "PIPELINE:DOCS_INCOMPLETE": 2,
}


def paperwork_rank(role_field: str) -> int:
    if role_field in STAGE_RANK:
        return STAGE_RANK[role_field]
    if role_field.startswith("PIPELINE:SUBMITTED") or role_field.startswith("PIPELINE:SUBMISSION_DRAFTS_READY"):
        return -1
    return 3


def paperwork_label(role_field: str) -> str:
    if role_field.startswith("PIPELINE:SUBMITTED"):
        return f"Already submitted ({role_field.split(':', 2)[-1]})"
    if role_field.startswith("PIPELINE:SUBMISSION_DRAFTS_READY"):
        return "Submission draft(s) created, not yet sent"
    if role_field == "PIPELINE:ONBOARD_RETURNED_READY_FOR_SUBMISSION":
        return "READY FOR SUBMISSION"
    if role_field == "PIPELINE:DOCS_COMPLETE_ONBOARD_SENT":
        return "Hot file (docs complete, onboarding sent)"
    if role_field == "PIPELINE:DOCS_INCOMPLETE":
        return "Docs incomplete"
    return "NOT YET EVALUATED (blank/license-type only -- real status unknown)"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--center", required=True, help="Center name (e.g. 'Franklin')")
    parser.add_argument("--license", choices=["RN", "LPN", "CNA"])
    parser.add_argument("--draft", action="store_true")
    args = parser.parse_args()

    if not INDEX_PATH.exists():
        print(f"ERROR: {INDEX_PATH} does not exist.")
        print("Run 'python3.11 blueline_candidate_index_builder.py' first.")
        return

    data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    built_at = datetime.fromisoformat(data["built_at"])
    age_hours = (datetime.now(timezone.utc) - built_at).total_seconds() / 3600
    if age_hours > 24:
        print(f"WARNING: index is {age_hours:.1f} hours old (built {data['built_at']}).")
        print("Results may be stale. Consider re-running blueline_candidate_index_builder.py.\n")

    target = canonicalize_center_name(args.center)
    print(f"Searching for candidates matching center: '{args.center}' -> canonical: '{target}'")
    if args.license:
        print(f"Filtered to license: {args.license}")
    print()

    hits = [
        c for c in data["candidates"]
        if (not args.license or args.license in c["license"])
        and target in c.get("matched_centers", [])
    ]
    hits.sort(key=lambda c: (paperwork_rank(c["quo_role_field"]), c.get("last_message_at") or ""))

    print("=" * 70)
    print(f"RESULT: {len(hits)} candidate(s) matched")
    print("=" * 70)

    drafts = []
    for c in hits:
        status = paperwork_label(c["quo_role_field"])
        print(f"\n{c['name']} ({c['license']})")
        print(f"  Phone: {c['phone']}")
        print(f"  Paperwork status: {status}")
        print(f"  Last said (dated {c['last_message_at']}): \"{c['last_message_snippet']}\"")

        if args.draft:
            first_name = c["name"].split()[0] if c["name"] else "there"
            draft_text = (
                f"Hi {first_name}, this is Dylan from BlueLine Staffing -- we have a "
                f"{args.license or c['license']} opening at {args.center} that matches "
                f"what you told us before. Still interested? Let me know and I'll get "
                f"you moving on it."
            )
            drafts.append(f"TO: {c['name']} ({c['phone']})\n{draft_text}\n")

    if args.draft and drafts:
        with open(DRAFTS_PATH, "a", encoding="utf-8") as f:
            f.write(f"\n{'=' * 70}\nVACANCY: {args.center} ({args.license or 'any license'}) -- "
                     f"{datetime.now(timezone.utc).isoformat()}\n{'=' * 70}\n")
            for d in drafts:
                f.write(d + "\n")
        print(f"\n{len(drafts)} outreach draft(s) written to {DRAFTS_PATH} -- review before sending.")

    if not hits:
        print("\nNo matches. Either no candidate mentioned this center, or the alias table")
        print("doesn't yet recognize the phrasing they used -- check candidate_center_index.json")
        print("'matched_centers' fields for what WAS captured, and extend")
        print("blueline_center_aliases.py's SEED_ALIASES if a real mention was missed.")


if __name__ == "__main__":
    main()
