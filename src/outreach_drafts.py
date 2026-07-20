"""
Dylan for Hire — Auto-Draft Outreach On Match
====================================================
Version: 1.0 | 2026-07-09
STATUS: NEW, covered by tests/test_vacancy_matcher.py's
TestOutreachDraftsNeverSend and TestOutreachDraftContent.

PURPOSE
  Once vacancy_matcher.py matches candidates to a vacancy, draft a "we have
  an opening at X, are you still interested" message per matched candidate —
  ready for Aditya to review and fire himself.

DRAFT-ONLY INVARIANT — THE MOST IMPORTANT THING IN THIS FILE
  Nothing in this module sends anything, ever. This project's own Key
  Invariants (SAAS_PROJECT_HEALTHCARE_RECRUITMENT_MASTER_CONTEXT.md §12A)
  state: "Nothing auto-sends — email replies are always drafts; Aditya sends
  manually." Quo/OpenPhone has no native "draft SMS" object the way Gmail has
  drafts (there is no create-draft-message tool in the Quo MCP connector, and
  no such endpoint used anywhere else in this codebase) — so the draft here
  is a local markdown file Aditya reads and copies from, not a Quo API
  object. This module does not import send_sms, send-message, or anything
  that reaches OpenPhone's API at all — see
  TestOutreachDraftsNeverSend::test_module_imports_no_send_capable_function
  for a test that actually checks this by reading the module's own imports,
  not just trusting this comment.

CLIENT-AGNOSTIC BY DESIGN — writes to config.outreach_drafts_dir, never a
  hardcoded BlueLine path.
"""

import logging
from datetime import datetime, timezone
from pathlib import Path

from client_config import ClientConfig, BLUELINE_CONFIG

log = logging.getLogger("master.outreach_drafts")


def draft_message_for_candidate(candidate: dict, resolved_center: str, resolved_borough: str,
                                 shift: str = None) -> str:
    """Plain-text SMS-style draft. No emojis (06_COMMUNICATIONS.md Ground
    Rule #3), includes the standing opt-out line this project puts on every
    first-touch-style message (07_COMPLIANCE.md / DYLAN_INTRO's own "Reply
    STOP to opt out.")."""
    first_name = (candidate.get("name") or "").split(" ")[0] or "there"
    where = resolved_center or resolved_borough or "one of our facilities"
    shift_phrase = f" {shift.lower()} shift" if shift else ""
    return (
        f"Hi {first_name}, this is Dylan from BlueLine Staffing. "
        f"We have a{shift_phrase} opening at {where} for "
        f"{candidate.get('license_type', 'your license type')} — "
        f"are you still interested? Reply YES and I'll send details. "
        f"Reply STOP to opt out."
    )


def write_outreach_drafts(match_result, config: ClientConfig = BLUELINE_CONFIG) -> Path:
    """Takes a vacancy_matcher.MatchResult, writes ONE markdown review file
    listing every matched candidate's drafted message. Returns the file
    path. Writes nothing if there are no matches (nothing to review)."""
    if not match_result.matches:
        log.info("No matches to draft outreach for — no file written.")
        return None

    out_dir = Path(config.outreach_drafts_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = out_dir / f"vacancy_outreach_{timestamp}.md"

    where = match_result.resolved_center or match_result.resolved_borough or "(unresolved location)"
    lines = [
        "# DRAFT — NOT SENT. Review each message, then send manually from Quo.",
        "",
        f"Vacancy: {match_result.request.count or 'any #'} "
        f"{match_result.request.license_type or 'any license'} "
        f"{match_result.request.shift or 'any shift'} @ {where}",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "---",
        "",
    ]
    for i, c in enumerate(match_result.matches, 1):
        message = draft_message_for_candidate(
            c, match_result.resolved_center, match_result.resolved_borough,
            match_result.request.shift,
        )
        lines.append(f"## {i}. {c.get('name')} — {c.get('phone')} — [{c.get('readiness_bucket')}]")
        lines.append("")
        lines.append(f"> {message}")
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    log.info(f"Wrote {len(match_result.matches)} outreach draft(s) to {out_path}")
    return out_path
