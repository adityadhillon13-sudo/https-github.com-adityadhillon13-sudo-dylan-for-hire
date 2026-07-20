"""
Dylan for Hire — Client Configuration
====================================================
Version: 1.0 | 2026-07-09
STATUS: NEW. Written to support Vacancy Matcher, the candidate index, outreach
drafts, and pipeline-depth lookup — see those modules for what actually uses this.

PURPOSE
  Every one of those four new modules needs the same handful of client-specific
  facts: which Quo/OpenPhone account to hit, where that client's center
  directory file lives, where to write the candidate index and outreach
  drafts, and which pipeline-stage tag scheme to read. Today only ONE real
  client config exists (BlueLine) because BlueLine is Dylan's only real
  customer. This module exists so that stays a one-line addition instead of a
  code change when a second client shows up — the four feature modules import
  a ClientConfig object and never hardcode a BlueLine path or env var name
  directly.

HONESTY NOTE — read before assuming this makes the whole product multi-tenant
  This file does NOT retrofit master_daily_agent.py, master_gmail_reviewer.py,
  or any of the existing BlueLine-hardcoded production scripts into being
  multi-client. Per 10_CLIENT_INTAKE_AND_ADAPTER_SPEC.md and the 2026-07-08
  SaaS launch-readiness finding, that is real, separate, multi-week
  architecture work — no doc update or single new module makes it true. What
  this file DOES do is make the five NEW features requested on 2026-07-09
  (Vacancy Matcher, alias table, candidate index, outreach drafts, pipeline
  depth) client-agnostic from day one, so onboarding a second client onto
  JUST these features means writing a new ClientConfig instance below, not
  editing the matching/ranking/drafting logic itself.

USAGE
  from client_config import BLUELINE_CONFIG
  centers = load_centers(BLUELINE_CONFIG)   # (center_alias.py)
  build_candidate_index(BLUELINE_CONFIG)    # (candidate_index.py)
"""

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ClientConfig:
    # Identity
    client_id: str

    # Quo / OpenPhone — same API this whole project already uses. Values are
    # ENV VAR NAMES to read at call time, not the secrets themselves, so this
    # dataclass is safe to import anywhere (including tests) without leaking
    # credentials into a frozen object.
    quo_api_key_env: str = "QUO_API_KEY"
    quo_phone_id_env: str = "QUO_PHONE_NUMBER_ID"
    quo_base_url: str = "https://api.openphone.com/v1"

    # Where this client's center/facility directory lives. Real format is
    # free-form markdown maintained by hand — see center_alias.py's parser
    # and its documented gap (this file is not reachable from a Cowork
    # session; verify the parser against the real file's actual formatting
    # on the machine that runs it before trusting it broadly, same caveat
    # master_candidate_file_consolidator.py already carries for this exact
    # file).
    center_directory_path: Path = field(
        default_factory=lambda: Path.home() / "Downloads" / "BlueLine" / "BLUELINE_CENTER_DIRECTORY.md"
    )

    # Nightly candidate index output (candidate_index.py writes here,
    # vacancy_matcher.py / pipeline_depth.py read from here).
    candidate_index_path: Path = field(
        default_factory=lambda: Path.home() / "Downloads" / "BlueLine" / "candidate_index.json"
    )

    # Where outreach_drafts.py writes review files. Never auto-sent — see
    # that module's docstring for the invariant this preserves.
    outreach_drafts_dir: Path = field(
        default_factory=lambda: Path.home() / "Downloads" / "BlueLine" / "VacancyOutreachDrafts"
    )

    # Phone-based permanent opt-out file, same one master_daily_agent.py and
    # email_context_bridge.py already read/write.
    optouts_path: Path = field(
        default_factory=lambda: Path.home() / "Downloads" / "master_permanent_optouts.txt"
    )

    # Valid license/role tokens for this client (mirrors master_daily_agent.py's
    # VALID_ROLES — duplicated here rather than imported so a future client
    # with a different role set doesn't have to touch BlueLine's code).
    valid_roles: frozenset = frozenset({"RN", "LPN", "CNA", "HHA", "RNS", "MA", "CMA"})

    # How many days back "active" means when nothing else is specified.
    default_active_window_days: int = 45


# ── The one real client config that exists today ────────────────────────────
BLUELINE_CONFIG = ClientConfig(client_id="blueline")


def get_quo_api_key(config: ClientConfig) -> str:
    return os.getenv(config.quo_api_key_env, "")


def get_quo_phone_id(config: ClientConfig) -> str:
    return os.getenv(config.quo_phone_id_env, "")


# ── Extension point for a second client ─────────────────────────────────────
# When a real second Dylan for Hire client exists, add:
#
#   SECOND_CLIENT_CONFIG = ClientConfig(
#       client_id="second-client-slug",
#       quo_api_key_env="SECOND_CLIENT_QUO_API_KEY",
#       quo_phone_id_env="SECOND_CLIENT_QUO_PHONE_NUMBER_ID",
#       center_directory_path=Path.home() / "Downloads" / "SecondClient" / "CENTER_DIRECTORY.md",
#       candidate_index_path=Path.home() / "Downloads" / "SecondClient" / "candidate_index.json",
#       outreach_drafts_dir=Path.home() / "Downloads" / "SecondClient" / "VacancyOutreachDrafts",
#       optouts_path=Path.home() / "Downloads" / "SecondClient" / "permanent_optouts.txt",
#   )
#
# and pass it explicitly via each script's --client flag instead of the
# BLUELINE_CONFIG default. Nothing in center_alias.py, candidate_index.py,
# vacancy_matcher.py, outreach_drafts.py, or pipeline_depth.py needs to change.
