"""
BlueLine Staffing -- Candidate Center/Borough Index Builder
====================================================
Version: 1.0 | 2026-07-09

Scans every active LPN/RN/CNA candidate's SMS history and matches mentions
of known centers/boroughs, writing the result to a single JSON file. This is
what makes the Vacancy Matcher fast -- instead of live-querying Quo's
/messages endpoint per candidate at match time (slow, rate-limit-prone, and
exactly what caused the 429/timeout errors seen across cron_output.log),
the matcher reads this precomputed index.

RUN NOW to build the first index; wire into cron nightly once verified on a
real run:
  cd ~/Downloads/BlueLine
  python3.11 blueline_candidate_index_builder.py

OUTPUT: ~/Downloads/BlueLine/candidate_center_index.json

NOT AI-dependent -- uses only regex/alias matching (blueline_center_aliases.py),
so this works even while the Anthropic credit balance is at zero. A future
upgrade (not built here) could add a second Claude-based pass once credits
are restored, to catch candidates who imply availability without naming a
literal center (e.g. "anywhere in Queens").
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timezone

from blueline_quo_helpers import (
    get_all_contacts, get_recent_conversations, get_messages_for_phone,
    contact_full_name, contact_phones, contact_role_field,
)
from blueline_center_aliases import match_center_mentions, load_alias_index

log = logging.getLogger("blueline.index_builder")

LICENSE_TOKENS = {"RN", "LPN", "CNA"}
INDEX_PATH = Path.home() / "Downloads" / "BlueLine" / "candidate_center_index.json"
ACTIVE_WINDOW_DAYS = 30
SMS_HISTORY_DAYS   = 90


def build_index():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    log.info("Fetching all Quo contacts...")
    contacts = get_all_contacts()
    log.info(f"  {len(contacts)} total contacts")

    log.info(f"Fetching conversations active in the last {ACTIVE_WINDOW_DAYS} days...")
    recent_convos = get_recent_conversations(days=ACTIVE_WINDOW_DAYS)
    active_phones = set()
    for c in recent_convos:
        for p in (c.get("participants") or []):
            active_phones.add(p.strip())
    log.info(f"  {len(active_phones)} unique active phone(s)")

    alias_index = load_alias_index()
    log.info(f"  Loaded {len(alias_index)} center alias(es)")

    entries, skipped = [], []
    for c in contacts:
        full_name = contact_full_name(c)
        tokens = set(full_name.upper().split())
        license_hit = tokens & LICENSE_TOKENS
        if not license_hit:
            continue
        phones = contact_phones(c)
        phone_match = next((p for p in phones if p in active_phones), None)
        if not phone_match:
            continue

        try:
            msgs = get_messages_for_phone(phone_match, days=SMS_HISTORY_DAYS)
        except Exception as e:
            log.warning(f"  SKIPPED {full_name} ({phone_match}) -- {e}")
            skipped.append(f"{full_name} ({phone_match}): {e}")
            continue

        incoming_text = " \n ".join(
            (m.get("text") or "") for m in msgs if m.get("direction") == "incoming"
        )
        matched_centers = match_center_mentions(incoming_text, alias_index)
        last_msg = max(msgs, key=lambda m: m.get("createdAt", ""), default=None)

        entries.append({
            "quo_id": c.get("id"),
            "name": full_name,
            "license": "/".join(sorted(license_hit)),
            "phone": phone_match,
            "quo_role_field": contact_role_field(c),
            "matched_centers": matched_centers,
            "last_message_at": (last_msg or {}).get("createdAt"),
            "last_message_snippet": ((last_msg or {}).get("text") or "")[:200],
        })
        log.info(f"  {full_name} ({license_hit}) -> centers: {matched_centers or '(none)'}")

    output = {
        "built_at": datetime.now(timezone.utc).isoformat(),
        "active_window_days": ACTIVE_WINDOW_DAYS,
        "sms_history_days": SMS_HISTORY_DAYS,
        "candidate_count": len(entries),
        "skipped_count": len(skipped),
        "skipped": skipped,
        "candidates": entries,
    }
    INDEX_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")
    log.info(f"=== DONE -- {len(entries)} candidate(s) indexed, {len(skipped)} skipped. "
              f"Written to {INDEX_PATH} ===")


if __name__ == "__main__":
    build_index()
