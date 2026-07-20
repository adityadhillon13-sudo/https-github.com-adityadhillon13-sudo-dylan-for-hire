#!/usr/bin/env bash
# ============================================================================
# BlueLine <-> Dylan for Hire drift check + sync
# ============================================================================
# WHY THIS EXISTS:
#   BlueLine (~/Downloads/BlueLine/) and Dylan for Hire (this project's src/)
#   both contain copies of the same pipeline .py files. Two things edit them
#   independently: Aditya's Claude Code sessions and this Cowork project.
#   Neither session has live visibility into the other's edits — the only
#   shared truth is the files on disk. Without a routine check, the two
#   copies silently drift apart, which is exactly what caused the confusion
#   on 2026-07-02 (Round 13).
#
# THE RULE THIS SCRIPT ENFORCES:
#   BlueLine is the source of truth for PIPELINE ENGINEERING CODE — it's the
#   live, cron/launchd-run deployment on Aditya's actual Mac, so it's the
#   only place a fix is ever really "proven." When BlueLine and src/ differ
#   on a shared pipeline file, this script copies BlueLine's version into
#   src/ by default (not the reverse) — because src/ is the reference/
#   product copy, not the other way around.
#
#   Exception: one-time setup scripts and shared config (master_gmail_setup.py,
#   master_requirements.txt) sometimes get improved in the product folder
#   first and deployed to BlueLine later — this script flags those instead of
#   auto-resolving them, since the "right direction" isn't always the same.
#
#   BlueLine-specific BUSINESS content (CONFIDENTIAL_candidates.csv, the
#   actual center directory, actual SMS copy addressed as "Dylan from
#   BlueLine Staffing") is NEVER touched by this script and never should be —
#   that content is BlueLine's alone and must not leak into the generic
#   product docs/code as if it were generic.
#
# USAGE:
#   bash scripts/sync_check.sh            # report drift only, no changes
#   bash scripts/sync_check.sh --apply     # sync BlueLine -> src/ for the
#                                          # pipeline files listed below, then
#                                          # run the test suite to confirm
#                                          # nothing broke
#
# WHAT THIS DOES NOT DO:
#   It does not give two live Claude sessions real-time awareness of each
#   other's in-progress work. It only compares what's actually been written
#   to disk, whenever it's run. Run it at the start of any session that will
#   touch these files.
# ============================================================================

set -uo pipefail

BLUELINE_DIR="$HOME/Downloads/BlueLine"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$PROJECT_DIR/src"

# Files where BlueLine (production) always leads -> sync direction is BlueLine -> src/
PIPELINE_FILES=(
  master_daily_agent.py
  master_gmail_reviewer.py
  email_context_bridge.py
  master_gmail_pubsub_listener.py
  master_sms_poll_service.py
  upgrade1_context_aware_messaging.py
)

# Files where either side might legitimately lead -> flagged, never auto-synced
FLAG_ONLY_FILES=(
  master_gmail_setup.py
  master_requirements.txt
)

# [ADDED 2026-07-03] Test suite files. OPPOSITE sync direction from
# PIPELINE_FILES above: this project's tests/ is the source of truth here,
# not BlueLine's. Rationale, from the 2026-07-03 exhaustive audit: BlueLine's
# deployed ~/Downloads/BlueLine/tests/test_pipeline_logic.py had only 16
# `def test_` functions while this project's tests/test_pipeline_logic.py had
# ~79 (150 as of this fix) — because tests/ was never in this script's
# tracked list, so it never got synced like the pipeline files above did.
# Anyone running `pytest` directly inside BlueLine's deployed tests/ dir was
# silently getting the thin, stale suite instead of the one that's actually
# been validating every round of fixes. Since this project's tests/ is where
# the suite is actively developed and immediately re-run every session (per
# Rule 0C in 00_INDEX.md), it leads; BlueLine's copy follows.
TEST_FILES=(
  test_pipeline_logic.py
  conftest.py
)

APPLY=false
if [[ "${1:-}" == "--apply" ]]; then
  APPLY=true
fi

echo "=== BlueLine <-> Dylan for Hire drift check ==="
echo "BlueLine: $BLUELINE_DIR"
echo "src/:     $SRC_DIR"
echo ""

# drift_found:      true if ANY difference was seen this run (for the header report).
# unresolved_drift: true only for drift --apply did NOT (or cannot) fix — a file
#                    missing in BlueLine (no safe auto-copy direction) or a
#                    flag-only file (deliberately never auto-resolved). If --apply
#                    ran and unresolved_drift is still false, everything found was
#                    actually fixed this run — the closing message must say so,
#                    not repeat the pre-apply "drift found" warning as if nothing
#                    happened. [FIX 2026-07-03 — the old version always printed
#                    "Drift was found" even after a successful --apply, which is
#                    exactly the kind of false signal this script exists to prevent.]
drift_found=false
unresolved_drift=false

for f in "${PIPELINE_FILES[@]}"; do
  bl="$BLUELINE_DIR/$f"
  dh="$SRC_DIR/$f"
  if [[ ! -f "$bl" ]]; then
    echo "MISSING IN BLUELINE: $f (no safe auto-copy direction — needs manual review)"
    drift_found=true
    unresolved_drift=true
    continue
  fi
  if [[ ! -f "$dh" ]]; then
    echo "MISSING IN SRC/:     $f (copying from BlueLine)"
    drift_found=true
    if $APPLY; then cp "$bl" "$dh"; else unresolved_drift=true; fi
    continue
  fi
  if ! diff -q "$bl" "$dh" > /dev/null 2>&1; then
    echo "DRIFTED (BlueLine leads): $f"
    drift_found=true
    if $APPLY; then
      cp "$bl" "$dh"
      echo "  -> synced BlueLine to src/"
    else
      unresolved_drift=true
    fi
  else
    echo "IN SYNC:                  $f"
  fi
done

echo ""
echo "--- Flagged-only files (do not auto-resolve direction) ---"
for f in "${FLAG_ONLY_FILES[@]}"; do
  bl="$BLUELINE_DIR/$f"
  dh="$SRC_DIR/$f"
  # [FIX 2026-07-03, found while adding TEST_FILES above] If either side is
  # missing (e.g. BlueLine unreachable in a sandbox session, or the file
  # genuinely doesn't exist there yet), the old condition below fell through
  # to the "else" branch and printed "IN SYNC" — a false positive. Missing
  # is not the same claim as identical; report it honestly instead.
  if [[ ! -f "$bl" || ! -f "$dh" ]]; then
    echo "CANNOT COMPARE: $f (missing on one side — bl=$([[ -f "$bl" ]] && echo present || echo MISSING), src=$([[ -f "$dh" ]] && echo present || echo MISSING))"
    drift_found=true
    unresolved_drift=true
  elif ! diff -q "$bl" "$dh" > /dev/null 2>&1; then
    echo "DRIFTED (manual review needed): $f"
    echo "  BlueLine mtime: $(stat -f '%Sm' "$bl" 2>/dev/null || stat -c '%y' "$bl" 2>/dev/null)"
    echo "  src/ mtime:     $(stat -f '%Sm' "$dh" 2>/dev/null || stat -c '%y' "$dh" 2>/dev/null)"
    drift_found=true
    unresolved_drift=true   # flag-only files are NEVER auto-resolved, even with --apply
  else
    echo "IN SYNC: $f"
  fi
done

echo ""
echo "--- Test suite files (src/ leads here — opposite direction, see comment above) ---"
for f in "${TEST_FILES[@]}"; do
  proj="$PROJECT_DIR/tests/$f"
  bl="$BLUELINE_DIR/tests/$f"
  if [[ ! -f "$proj" ]]; then
    echo "MISSING IN PROJECT tests/: $f (this project's tests/ is the source of truth — this needs immediate manual attention, not an auto-sync)"
    drift_found=true
    unresolved_drift=true
    continue
  fi
  if [[ ! -f "$bl" ]]; then
    echo "MISSING IN BLUELINE tests/: $f (copying from project's tests/)"
    drift_found=true
    if $APPLY; then mkdir -p "$BLUELINE_DIR/tests" && cp "$proj" "$bl"; else unresolved_drift=true; fi
    continue
  fi
  if ! diff -q "$proj" "$bl" > /dev/null 2>&1; then
    echo "DRIFTED (project tests/ leads): $f"
    drift_found=true
    if $APPLY; then
      cp "$proj" "$bl"
      echo "  -> synced project tests/ to BlueLine"
    else
      unresolved_drift=true
    fi
  else
    echo "IN SYNC:                  $f"
  fi
done

echo ""
tests_failed=false
if $APPLY && $drift_found; then
  echo "=== Running test suite to confirm the sync didn't break anything ==="
  # [FIX 2026-07-03] Was 'python3', which resolves to Python 3.14 on Aditya's Mac
  # and has no pytest installed there — every real run of this file (crontab,
  # manual) uses python3.11, which does. Prefer python3.11 explicitly; fall back
  # to python3 only if 3.11 genuinely isn't on PATH, and say so plainly rather
  # than silently swallowing a "No module named pytest" failure as if it were a
  # real test result.
  PYBIN="python3.11"
  if ! command -v "$PYBIN" >/dev/null 2>&1; then
    echo "  (python3.11 not found on PATH — falling back to python3; if this fails with"
    echo "   'No module named pytest', that's an environment gap, not a real test failure)"
    PYBIN="python3"
  fi
  test_output="$(cd "$PROJECT_DIR/tests" && "$PYBIN" -m pytest 2>&1)"
  echo "$test_output" | tail -5
  if echo "$test_output" | grep -qE "No module named pytest|ModuleNotFoundError"; then
    echo "  ⚠️  pytest is not installed for $PYBIN — the sync was applied but NOT verified by tests."
    echo "      Run: $PYBIN -m pip install pytest    then re-run this script's test step manually."
    tests_failed=true
  elif ! echo "$test_output" | grep -qE "^[0-9]+ passed" ; then
    echo "  ⚠️  Test suite did not report a clean pass — review the output above before trusting this sync."
    tests_failed=true
  fi
fi

echo ""
if $unresolved_drift; then
  echo "Drift remains that needs manual attention (see MISSING IN BLUELINE / flagged files above)."
  exit 1
elif $drift_found && $APPLY; then
  if $tests_failed; then
    echo "Drift was found and synced, but the test suite could not confirm it — see warning above."
    exit 1
  else
    echo "Drift was found and has been synced (BlueLine -> src/). Tests confirm no regressions."
    exit 0
  fi
elif $drift_found; then
  echo "Drift was found. Re-run with --apply to sync the pipeline files automatically."
  exit 1
else
  echo "No drift. Both copies match."
  exit 0
fi
