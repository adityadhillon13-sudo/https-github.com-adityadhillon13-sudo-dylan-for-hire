"""
BlueLine Staffing -- Center/Borough Alias Matching
====================================================
Version: 1.0 | 2026-07-09

Candidates describe centers in free text, not structured data -- "New
Franklin", "fort tyrone" (typo for Fort Tryon), "forest view", "split rock
center". This module normalizes that into canonical center names so the
Vacancy Matcher and Index Builder can reliably answer "who mentioned this
center" regardless of exact phrasing.

Two layers:
  1. SEED_ALIASES below -- derived from KNOWN_CENTER_DOMAINS in
     master_gmail_reviewer.py (e.g. "forttryonrehab.com" -> "Fort Tryon"),
     cross-checked against real candidate SMS text seen this session.
     THESE ARE INFERRED FROM DOMAIN NAMES, NOT VERIFIED against the real
     BLUELINE_CENTER_DIRECTORY.md formal names -- correct them once that
     file's actual center names are confirmed. "PGC" -> "Palm Gardens"
     specifically matches Aditya's known biz dev target (Palm Gardens is
     named directly in the BlueLine project instructions), which is the
     strongest cross-check available -- the rest are best-effort and
     should be treated as unverified until checked against the real
     directory.
  2. DYNAMIC parsing of BLUELINE_CENTER_DIRECTORY.md at runtime for NEW
     names not already in the seed list -- as that file's real center
     names get confirmed, this list improves automatically.

Matching is regex/normalization based -- NOT an AI/Claude call, so this
works even during an Anthropic credit outage.
"""

import re
from pathlib import Path
from difflib import SequenceMatcher

CENTER_DIRECTORY_PATH = Path.home() / "Downloads" / "BlueLine" / "BLUELINE_CENTER_DIRECTORY.md"

# [INFERRED 2026-07-09 -- see module docstring, UNVERIFIED except Palm
# Gardens] canonical_name -> [aliases/misspellings seen or plausible]
SEED_ALIASES = {
    "Bronx Park":      ["bronx park", "bronxpark"],
    "BQ":              ["bq rehab", "bq"],
    "Morningside":     ["morningside", "morningside nrc"],
    "Fort Tryon":      ["fort tryon", "fort tyrone", "ft tryon", "ft tyrone"],
    "Brooklyn Gardens": ["brooklyn gardens"],
    "Palm Gardens":    ["palm gardens", "pgc"],
    "Split Rock":      ["split rock", "splitrock", "split rock rehab"],
    "Caton Park":      ["caton park"],
    "Franklin":        ["franklin", "new franklin"],
    "Citadel":         ["citadel"],
    "Forest View":     ["forest view", "forestview", "fv rehab"],
    "Cliffside":       ["cliffside"],
    "Park Terrace":    ["park terrace"],
    "Rockaway":        ["rockaway", "rockaway cc"],
    "Midway":          ["midway"],
    "Fordham":         ["fordham", "fordham nrc"],
    "NCHHC":           ["nchhc"],
    "BG Rehab":        ["bg rehab", "bgrehab"],
    "DBN":             ["dbn"],
    "Green Hill":      ["green hill", "greenhill"],
    "Riverside":       ["riverside", "riverside premier", "the riverside"],
    "Beach Terrace":   ["beach terrace"],
    "Grandell":        ["grandell"],
    "WCMC":            ["wcmc"],
    "Rebekah Rehab":   ["rebekah", "rebekah rehab"],
    "Hempstead Park":  ["hempstead park", "hempstead"],
    "VNHSI":           ["vnhsi"],
    "Queens Nassau":   ["queens nassau"],
    "Workmen's":       ["workmen's", "workmens"],
}

_STRIP_SUFFIXES = [
    "rehabilitation and nursing center", "rehab and nursing center",
    "nursing and rehabilitation center", "nursing home", "rehab center",
    "care center", "nursing center", "health center", "center", "centre",
    "rehab", "rehabilitation", "nrc", "nh", "cc", "ltc",
]


def _normalize(text: str) -> str:
    t = text.lower().strip()
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    for suf in _STRIP_SUFFIXES:
        if t.endswith(" " + suf):
            t = t[: -(len(suf) + 1)].strip()
    return t


def load_alias_index() -> dict:
    """Returns {normalized_alias: canonical_name}: seed list first, then
    overlaid with anything new parseable from the real center directory."""
    index = {}
    for canonical, aliases in SEED_ALIASES.items():
        index[_normalize(canonical)] = canonical
        for a in aliases:
            index[_normalize(a)] = canonical

    if CENTER_DIRECTORY_PATH.exists():
        text = CENTER_DIRECTORY_PATH.read_text(encoding="utf-8", errors="replace")
        candidate_lines = re.findall(
            r"^\s*(?:#+\s*|\*\*)?([A-Z][A-Za-z0-9'&.,\- ]{3,60}?)(?:\s*[-—|]|\*\*|\n|$)",
            text, re.MULTILINE,
        )
        for name in candidate_lines:
            name = name.strip()
            if len(name) < 4 or len(name) > 60:
                continue
            norm = _normalize(name)
            if norm and norm not in index:
                index[norm] = name

    return index


def canonicalize_center_name(raw: str) -> str:
    """Best-effort: given free text naming ONE center, return its canonical
    name. Falls back to a title-cased normalized version if unrecognized
    (so an unknown center still gets a stable key rather than failing)."""
    norm = _normalize(raw)
    index = load_alias_index()
    if norm in index:
        return index[norm]
    best, best_score = None, 0.0
    for key, canonical in index.items():
        score = SequenceMatcher(None, norm, key).ratio()
        if score > best_score:
            best, best_score = canonical, score
    if best_score >= 0.82:
        return best
    return raw.strip().title()


def match_center_mentions(text: str, alias_index: dict = None) -> list:
    """Scans a block of free text (e.g. all of one candidate's incoming SMS)
    and returns every canonical center name plausibly mentioned. Deliberately
    conservative (substring on normalized alias phrases, no fuzzy matching
    here unlike canonicalize_center_name) to avoid false positives silently
    mis-tagging a candidate."""
    if alias_index is None:
        alias_index = load_alias_index()
    norm_text = _normalize(text)
    found = set()
    for alias_norm, canonical in alias_index.items():
        if not alias_norm or len(alias_norm) < 3:
            continue
        if re.search(rf"\b{re.escape(alias_norm)}\b", norm_text):
            found.add(canonical)
    return sorted(found)
