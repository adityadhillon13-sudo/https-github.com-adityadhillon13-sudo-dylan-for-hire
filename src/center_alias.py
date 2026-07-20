"""
Dylan for Hire — Center / Borough Alias Table
====================================================
Version: 1.1 | 2026-07-10 (Round 18 reconciliation — see CURATED_ALIASES for
what changed and why)
STATUS: The alias data itself is now real-data-validated (see CURATED_ALIASES
below), but load_centers()'s PARSER for the real BLUELINE_CENTER_DIRECTORY.md
file has still not been run against that file's actual formatting (that file
lives only on Aditya's Mac, at ~/Downloads/BlueLine/, and is not reachable
from this session per the same gap flagged in
master_candidate_file_consolidator.py's KNOWN GAPS section). Verify
load_centers() against the real file on Aditya's Mac before trusting this in
production — see verify_against_real_file() at the bottom of this module,
which is meant to be run once, by hand, for exactly that check.

PURPOSE
  Candidates write center names in free text, not a structured field:
  "New Franklin," "fort tyrone" (typo for a real center), "forest view,"
  "split rock." A bare substring search only ever finds what someone already
  thought to search for. This module builds one canonical alias table, once,
  from the client's center directory file, so any free-text mention resolves
  reliably to a real center (or its borough, as a fallback) instead of a
  one-off manual search.

MATCHING STRATEGY (in order, first hit wins)
  1. Exact alias match against a normalized lookup table (canonical names +
     known nicknames/abbreviations + curated known typos).
  2. Fuzzy match (difflib) against the same table, for typos not already
     curated in. Anything at or above FUZZY_ACCEPT_THRESHOLD is accepted;
     anything between FUZZY_LOG_THRESHOLD and FUZZY_ACCEPT_THRESHOLD is
     rejected but LOGGED as a near-miss, so Aditya can review the log and add
     a real typo to CURATED_ALIASES below instead of the system silently
     guessing wrong forever.
  3. Borough-level fallback: if no specific center matches, check whether the
     query text mentions a borough by name/keyword/zip — matches every
     candidate who said that borough, even without naming a specific center.

CLIENT-AGNOSTIC BY DESIGN
  Every function here takes a ClientConfig (see client_config.py) and reads
  that client's own center_directory_path — nothing here is hardcoded to
  BlueLine's file path or center names except the CURATED_ALIASES seed list,
  which is explicitly BlueLine-specific and documented as such below.
"""

import difflib
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from client_config import ClientConfig, BLUELINE_CONFIG

log = logging.getLogger("master.center_alias")

FUZZY_ACCEPT_THRESHOLD = 0.78
FUZZY_LOG_THRESHOLD = 0.60

# Duplicated from master_daily_agent.py's BOROUGH_KEYWORDS ON PURPOSE — this
# module must be importable/testable with zero Quo credentials and zero
# network dependency, and importing master_daily_agent.py requires
# QUO_API_KEY/QUO_PHONE_NUMBER_ID/CLAUDE_API_KEY to already be set in the
# environment (os.environ["..."], not os.getenv, so it KeyErrors otherwise).
# tests/test_vacancy_matcher.py::TestBoroughKeywordsStayInSync cross-checks
# these two dicts stay identical, so this duplication can't silently drift —
# this codebase has a real prior incident (the Round 7 INTEREST_KEYWORDS
# reconciliation) of exactly two copies of the same constant diverging.
BOROUGH_KEYWORDS = {
    "Manhattan": ["manhattan", "new york, ny", "new york ny", "10001","10002","10003",
                  "10004","10005","10006","10007","10009","10010","10011","10012",
                  "10013","10014","10016","10017","10018","10019","10020","10021",
                  "10022","10023","10024","10025","10026","10027","10028","10029",
                  "10030","10031","10032","10033","10034","10035","10036","10037",
                  "10038","10039","10040","10044","10065","10069","10075","10128"],
    "Brooklyn":  ["brooklyn","11201","11203","11204","11205","11206","11207","11208",
                  "11209","11210","11211","11212","11213","11214","11215","11216",
                  "11217","11218","11219","11220","11221","11222","11223","11224",
                  "11225","11226","11228","11229","11230","11231","11232","11233",
                  "11234","11235","11236","11237","11238","11239"],
    "Queens":    ["queens","astoria","flushing","jamaica","11354","11355","11356",
                  "11357","11358","11360","11361","11362","11363","11364","11365",
                  "11366","11367","11368","11369","11370","11371","11372","11373",
                  "11374","11375","11377","11378","11379","11385","11411","11412",
                  "11413","11414","11415","11416","11417","11418","11419","11420",
                  "11421","11422","11423","11424","11425","11426","11427","11428",
                  "11429","11430","11432","11433","11434","11435","11436"],
    "Bronx":     ["bronx","10451","10452","10453","10454","10455","10456","10457",
                  "10458","10459","10460","10461","10462","10463","10464","10465",
                  "10466","10467","10468","10469","10470","10471","10472","10473",
                  "10474","10475"],
    "Staten Island": ["staten island","10301","10302","10303","10304","10305",
                      "10306","10307","10308","10309","10310","10312","10314"],
}


@dataclass
class CenterRecord:
    canonical_name: str
    borough: str
    email: Optional[str] = None
    aliases: list = field(default_factory=list)


# ── BlueLine-specific curated aliases ────────────────────────────────────────
# [REPLACED 2026-07-10, Round 18 reconciliation] The original version of this
# list (2026-07-09) used FULL formal names ("New Franklin Center for
# Rehabilitation and Nursing") guessed from this project's own
# 06_COMMUNICATIONS.md. Aditya independently asked a separate project
# ("BlueLine Automation") to build this same feature, and its version was
# actually run against real candidate SMS data on 2026-07-10 — that real run
# confirmed centers are referred to, everywhere in this codebase's real
# operational data (candidate messages, the Quo role field, biz dev
# conversations), by SHORT names: "Franklin", "Palm Gardens", "Fort Tryon",
# "Bronx Park", not the long formal names. The short-name convention below is
# adopted wholesale from that independently-built, real-data-validated
# module (blueline_center_aliases.py's SEED_ALIASES) rather than guessed a
# second time — including "fort tyrone" -> "Fort Tryon", which resolves the
# exact typo example Aditya originally gave when this feature was requested
# and which this file's first version explicitly could NOT confirm.
# This project's original 06_COMMUNICATIONS.md-derived full names are KEPT as
# additional aliases below (not discarded) for the two centers confirmed to
# be the same real place under both naming conventions (Franklin, Grandell);
# the other 16 full names from that list don't obviously overlap with the
# real short-name set and are kept as their own separate seed entries in
# case they're real centers the short-name list just hasn't captured yet.
CURATED_ALIASES = {
    "bronx park": "Bronx Park", "bronxpark": "Bronx Park",
    "bq rehab": "BQ", "bq": "BQ",
    "morningside": "Morningside", "morningside nrc": "Morningside",
    "fort tryon": "Fort Tryon", "fort tyrone": "Fort Tryon",
    "ft tryon": "Fort Tryon", "ft tyrone": "Fort Tryon",
    "brooklyn gardens": "Brooklyn Gardens",
    "palm gardens": "Palm Gardens", "pgc": "Palm Gardens",
    "split rock": "Split Rock", "splitrock": "Split Rock", "split rock rehab": "Split Rock",
    "caton park": "Caton Park",
    "franklin": "Franklin", "new franklin": "Franklin",
    "citadel": "Citadel",
    "forest view": "Forest View", "forestview": "Forest View", "fv rehab": "Forest View",
    "cliffside": "Cliffside",
    "park terrace": "Park Terrace",
    "rockaway": "Rockaway", "rockaway cc": "Rockaway",
    "midway": "Midway",
    "fordham": "Fordham", "fordham nrc": "Fordham",
    "nchhc": "NCHHC",
    "bg rehab": "BG Rehab", "bgrehab": "BG Rehab",
    "dbn": "DBN",
    "green hill": "Green Hill", "greenhill": "Green Hill",
    "riverside": "Riverside", "riverside premier": "Riverside", "the riverside": "Riverside",
    "beach terrace": "Beach Terrace",
    "grandell": "Grandell", "the grandell rehabilitation and nursing center": "Grandell",
    "wcmc": "WCMC",
    "rebekah": "Rebekah Rehab", "rebekah rehab": "Rebekah Rehab",
    "hempstead park": "Hempstead Park", "hempstead": "Hempstead Park",
    "vnhsi": "VNHSI",
    "queens nassau": "Queens Nassau",
    "workmen's": "Workmen's", "workmens": "Workmen's",
    # Kept from this file's original 06_COMMUNICATIONS.md-derived seed — real
    # centers, just not yet confirmed against the short-name convention above.
    "bushwick": "Bushwick Center for Rehabilitation and Healthcare",
    "harbor care": "Harbor Care Center",
    "concord": "Concord Nursing and Rehabilitation Center",
    "cobble hill": "Cobble Hill Health Center",
    "king david": "King David Center for Nursing and Rehabilitation",
    "throgs neck": "Throgs Neck Extended Care",
    "northeast bronx": "Northeast Bronx Health & Rehabilitation",
    "rivera": "Rivera Nursing and Rehabilitation Center",
    "laconia": "Laconia Nursing and Rehabilitation Center",
    "daughters of jacob": "Daughters of Jacob Nursing Home",
    "isabella": "Isabella Geriatric Center",
    "1199": "1199 SEIU Home Care",
    "silvercrest": "Silvercrest Center for Nursing and Rehabilitation",
    "triboro": "Triboro Center for Rehabilitation and Nursing",
    "woodhaven": "Woodhaven Center of Care",
    "avalon gardens": "Avalon Gardens Rehabilitation and Health Care Center",
    "stern family": "Stern Family Center for Rehabilitation",
}

# [FLAG, not resolved here] "Citadel" is documented elsewhere in this project
# (SAAS_PROJECT_HEALTHCARE_RECRUITMENT_MASTER_CONTEXT.md §12A) as a shared
# MANAGEMENT GROUP covering five separate centers (Bronx Gardens, Plaza
# Rehab, Hudson Pointe, Riverdale, The Plaza), not one physical center.
# Both this file and the independently-built blueline_center_aliases.py treat
# "Citadel" as a single canonical center name — that may be wrong/imprecise,
# but fixing it needs real confirmation of which of those five a candidate
# actually means, which neither implementation has yet. Kept as-is rather
# than guessed further.

# Borough mapping only exists for the ORIGINAL 06_COMMUNICATIONS.md-derived
# names (the short-name set adopted above doesn't come with confirmed
# borough data — blueline_center_aliases.py didn't map centers to boroughs
# either, so "NY" (unknown) is the honest default for those until the real
# BLUELINE_CENTER_DIRECTORY.md is parsed directly). Used for the
# CenterRecord.borough field when the seed list is used as a fallback (see
# load_centers()).
_SEED_CENTER_BOROUGHS = {
    "Bushwick Center for Rehabilitation and Healthcare": "Brooklyn",
    "Harbor Care Center": "Brooklyn",
    "Concord Nursing and Rehabilitation Center": "Brooklyn",
    "Cobble Hill Health Center": "Brooklyn",
    "Brooklyn Center for Rehabilitation and Healthcare": "Brooklyn",
    "King David Center for Nursing and Rehabilitation": "Brooklyn",
    "Throgs Neck Extended Care": "Bronx",
    "Northeast Bronx Health & Rehabilitation": "Bronx",
    "Rivera Nursing and Rehabilitation Center": "Bronx",
    "Laconia Nursing and Rehabilitation Center": "Bronx",
    "Daughters of Jacob Nursing Home": "Bronx",
    "Isabella Geriatric Center": "Manhattan",
    "1199 SEIU Home Care": "Manhattan",
    "Silvercrest Center for Nursing and Rehabilitation": "Queens",
    "Queens Center for Rehabilitation and Residential Healthcare": "Queens",
    "Triboro Center for Rehabilitation and Nursing": "Queens",
    "Woodhaven Center of Care": "Queens",
    "Avalon Gardens Rehabilitation and Health Care Center": "Staten Island",
    "Stern Family Center for Rehabilitation": "Staten Island",
    # Short-name set — borough genuinely unknown from this session's data.
    "Franklin": "NY", "Grandell": "NY", "Bronx Park": "NY", "BQ": "NY",
    "Morningside": "NY", "Fort Tryon": "NY", "Brooklyn Gardens": "NY",
    "Palm Gardens": "NY", "Split Rock": "NY", "Caton Park": "NY", "Citadel": "NY",
    "Forest View": "NY", "Cliffside": "NY", "Park Terrace": "NY", "Rockaway": "NY",
    "Midway": "NY", "Fordham": "NY", "NCHHC": "NY", "BG Rehab": "NY", "DBN": "NY",
    "Green Hill": "NY", "Riverside": "NY", "Beach Terrace": "NY", "WCMC": "NY",
    "Rebekah Rehab": "NY", "Hempstead Park": "NY", "VNHSI": "NY",
    "Queens Nassau": "NY", "Workmen's": "NY",
}
# [FLAG] Avalon Gardens / Stern Family are listed under "Nassau County / Long
# Island" in 06_COMMUNICATIONS.md, which isn't one of BOROUGH_KEYWORDS' five
# NYC boroughs. Mapped to "Staten Island" here is WRONG and a placeholder —
# this file doesn't have a real answer for non-NYC-borough regions yet.
# Verify against the real BLUELINE_CENTER_DIRECTORY.md and fix properly
# (likely needs a 6th bucket, e.g. "Long Island", added to BOROUGH_KEYWORDS
# and master_daily_agent.py's copy in the same change) before relying on
# these two specific centers' borough-fallback matching.


def _normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", " ", (s or "").lower()).strip()
    # Not fully collapsing whitespace on purpose — difflib is tolerant of
    # small differences and collapsing here would fight the fuzzy layer.


def load_centers(config: ClientConfig = BLUELINE_CONFIG) -> list:
    """Parses config.center_directory_path into CenterRecord objects.

    UNVERIFIED FORMAT WARNING: this parser handles the two patterns actually
    observed in this project (06_COMMUNICATIONS.md's "### Borough\\n- Name"
    style, and a "Name | email | ..." pipe-delimited style matching this
    project's other Quo-adjacent files) but the REAL BLUELINE_CENTER_DIRECTORY.md
    has not been read from this session — verify against it directly (see
    verify_against_real_file() below) before trusting this broadly.

    Falls back to the curated seed list (real center names, but NOT the full
    34-center directory — see CURATED_ALIASES's comment for provenance) if
    the real file isn't present or doesn't parse into anything — so this
    module still works today, with an honest, smaller, degraded center set,
    rather than silently returning nothing.
    """
    path = Path(config.center_directory_path)
    records = []

    if path.exists():
        text = path.read_text(encoding="utf-8", errors="replace")
        records = _parse_directory_text(text)
        if not records:
            log.warning(
                f"{path} exists but no centers could be parsed from it — "
                f"falling back to the {len(CURATED_ALIASES)}-alias seed list. "
                f"This means the real file's formatting doesn't match either "
                f"pattern this parser knows — verify by hand and fix "
                f"_parse_directory_text()."
            )
    else:
        log.warning(
            f"Center directory not found at {path} — falling back to the "
            f"seed list built from 06_COMMUNICATIONS.md (18 of the real 34 "
            f"centers). Matching will miss any center not in that subset "
            f"until the real file is present at this path."
        )

    if not records:
        seen = set()
        for canonical in _SEED_CENTER_BOROUGHS:
            if canonical in seen:
                continue
            seen.add(canonical)
            records.append(CenterRecord(
                canonical_name=canonical,
                borough=_SEED_CENTER_BOROUGHS.get(canonical, "NY"),
            ))

    return records


def _parse_directory_text(text: str) -> list:
    """Two parsing strategies, tried in order. Returns [] if neither yields
    anything — caller decides what to do about that (see load_centers)."""
    records = _parse_markdown_borough_sections(text)
    if records:
        return records
    return _parse_pipe_delimited(text)


def _parse_markdown_borough_sections(text: str) -> list:
    """Matches 06_COMMUNICATIONS.md's own style:
        ### Brooklyn
        - Bushwick Center for Rehabilitation and Healthcare
        - Harbor Care Center
    """
    records = []
    current_borough = None
    for line in text.splitlines():
        stripped = line.strip()
        heading = re.match(r"^#{2,4}\s+(.+)$", stripped)
        if heading:
            candidate_borough = heading.group(1).strip()
            # Only treat it as a borough section if it looks like one —
            # avoids misreading an unrelated markdown heading as a borough.
            known = {"manhattan", "brooklyn", "queens", "bronx",
                     "staten island", "nassau county / long island",
                     "nassau", "long island"}
            if candidate_borough.lower() in known or any(
                k in candidate_borough.lower() for k in known
            ):
                current_borough = candidate_borough
            continue
        bullet = re.match(r"^[-*]\s+(.+)$", stripped)
        if bullet and current_borough:
            name = bullet.group(1).strip()
            if name:
                records.append(CenterRecord(
                    canonical_name=name,
                    borough=current_borough,
                ))
    return records


def _parse_pipe_delimited(text: str) -> list:
    """Fallback for a 'Name | Email | ...' style row format, in case
    BLUELINE_CENTER_DIRECTORY.md's real layout looks more like this project's
    other pipe-delimited Quo data than 06_COMMUNICATIONS.md's markdown list.
    Only used if the markdown-section parser found nothing."""
    records = []
    for line in text.splitlines():
        if "|" not in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        parts = [p for p in parts if p]
        if not parts:
            continue
        name = parts[0]
        if not name or name.lower() in {"name", "center", "facility"}:
            continue
        email = next((p for p in parts[1:] if "@" in p), None)
        records.append(CenterRecord(canonical_name=name, borough="NY", email=email))
    return records


def build_alias_index(centers: list) -> dict:
    """normalized alias text -> canonical center name."""
    index = {}
    for c in centers:
        index[_normalize(c.canonical_name)] = c.canonical_name
        for alias in c.aliases:
            index[_normalize(alias)] = c.canonical_name
    for alias, canonical in CURATED_ALIASES.items():
        index[_normalize(alias)] = canonical
    return index


@dataclass
class CenterMatch:
    query_text: str
    matched_center: Optional[str] = None
    matched_borough: Optional[str] = None
    method: Optional[str] = None       # "exact" | "fuzzy" | "borough" | None
    confidence: float = 0.0


def resolve_center_query(query_text: str, alias_index: dict, centers: list) -> CenterMatch:
    """Resolves free text to a canonical center (or borough fallback).
    First hit wins: exact alias -> fuzzy -> borough keyword."""
    norm = _normalize(query_text)
    if not norm:
        return CenterMatch(query_text=query_text)

    # 1. Exact — check the whole normalized query, then each individual
    #    alias key as a substring (handles "2 RNs nights new franklin").
    if norm in alias_index:
        return CenterMatch(query_text=query_text, matched_center=alias_index[norm],
                            method="exact", confidence=1.0)
    for alias_key, canonical in alias_index.items():
        if alias_key and alias_key in norm:
            return CenterMatch(query_text=query_text, matched_center=canonical,
                                method="exact", confidence=1.0)

    # 2. Fuzzy — catches typos not already curated in.
    best_ratio, best_canonical = 0.0, None
    words = norm.split()
    candidates_to_try = [norm] + words + [
        " ".join(words[i:i + 2]) for i in range(len(words) - 1)
    ]  # also try 2-word windows, since a full free-text query is noisy
    for chunk in candidates_to_try:
        matches = difflib.get_close_matches(chunk, alias_index.keys(), n=1, cutoff=FUZZY_LOG_THRESHOLD)
        if not matches:
            continue
        ratio = difflib.SequenceMatcher(None, chunk, matches[0]).ratio()
        if ratio > best_ratio:
            best_ratio, best_canonical = ratio, alias_index[matches[0]]

    if best_canonical:
        if best_ratio >= FUZZY_ACCEPT_THRESHOLD:
            return CenterMatch(query_text=query_text, matched_center=best_canonical,
                                method="fuzzy", confidence=round(best_ratio, 3))
        log.info(
            f"Near-miss center match NOT accepted: '{query_text}' ~ "
            f"'{best_canonical}' (confidence {best_ratio:.2f}, below "
            f"{FUZZY_ACCEPT_THRESHOLD} accept threshold). If this is a real "
            f"typo, add it to CURATED_ALIASES in center_alias.py."
        )

    # 3. Borough fallback.
    for borough, keywords in BOROUGH_KEYWORDS.items():
        if any(kw in norm for kw in keywords):
            return CenterMatch(query_text=query_text, matched_borough=borough,
                                method="borough", confidence=0.5)

    return CenterMatch(query_text=query_text)


def verify_against_real_file(config: ClientConfig = BLUELINE_CONFIG) -> None:
    """Not part of the automated test suite — run this by hand, once, on
    Aditya's Mac, where the real BLUELINE_CENTER_DIRECTORY.md actually lives:

        cd ~/Downloads/BlueLine && python3.11 -c \\
          "import sys; sys.path.insert(0,'.'); from center_alias import verify_against_real_file; verify_against_real_file()"

    Prints how many centers parsed and a sample, so a human can eyeball
    whether the parser actually understood the real file before this is
    trusted for real vacancy matching."""
    centers = load_centers(config)
    print(f"Parsed {len(centers)} center(s) from {config.center_directory_path}")
    for c in centers[:10]:
        print(f"  - {c.canonical_name}  [{c.borough}]" + (f"  <{c.email}>" if c.email else ""))
    if len(centers) > 10:
        print(f"  ... and {len(centers) - 10} more")
    if len(centers) == len(_SEED_CENTER_BOROUGHS):
        print(
            "WARNING: parsed count matches the fallback seed list size exactly — "
            "this may mean the real file wasn't found/parsed and you're looking "
            "at the degraded fallback, not the real 34-center directory."
        )


if __name__ == "__main__":
    verify_against_real_file()
