"""
BlueLine Staffing -- Pipeline Depth Lookup (Biz Dev Tool)
====================================================
Version: 1.0 | 2026-07-09

Answers "how many qualified candidates do we have who'd plausibly work at
this facility/borough" -- for biz dev conversations, without guessing.
Reads the same candidate_center_index.json the Vacancy Matcher uses.

USAGE:
  python3.11 blueline_pipeline_depth.py --center "Franklin"
  python3.11 blueline_pipeline_depth.py --center "Franklin" --license RN
"""

import json
import argparse
from pathlib import Path
from collections import Counter

from blueline_center_aliases import canonicalize_center_name

INDEX_PATH = Path.home() / "Downloads" / "BlueLine" / "candidate_center_index.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--center", required=True)
    parser.add_argument("--license", choices=["RN", "LPN", "CNA"])
    args = parser.parse_args()

    if not INDEX_PATH.exists():
        print(f"ERROR: {INDEX_PATH} missing -- run blueline_candidate_index_builder.py first.")
        return

    data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    target = canonicalize_center_name(args.center)

    matches = [
        c for c in data["candidates"]
        if target in c.get("matched_centers", [])
        and (not args.license or args.license in c["license"])
    ]
    by_license = Counter(c["license"] for c in matches)

    print(f"Pipeline depth for '{args.center}' (canonical: '{target}'):")
    print(f"  Index built: {data['built_at']} ({data['candidate_count']} candidates indexed total)")
    print(f"  Total matches: {len(matches)}")
    for lic, count in by_license.items():
        print(f"    {lic}: {count}")


if __name__ == "__main__":
    main()
