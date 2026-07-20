#!/usr/bin/env python3
"""
BlueLine Staffing — Real-Time SMS Reply Service (24/7 Companion to Gmail Listener)
=====================================================================================
Version: 1.0 | 2026-07-01

WHY THIS EXISTS:
    Before this file, an inbound "YES" or "STOP" from a candidate only got
    handled once a day, at the 9:00 AM cron run — even though the code that
    handles it (step3_sms_reply_handler) responds in under 10 seconds ONCE
    IT RUNS. The gap wasn't the response speed, it was the check frequency.
    This closes that gap by running the exact same, already-proven
    step3_sms_reply_handler() function on a short loop instead of once a day.

WHAT THIS DOES NOT CHANGE:
    Steps 1 (re-engage stalled), 2 (new leads), and DEDUP stay on the 9:00 AM
    daily cron exactly as before. Those are deliberately daily-paced —
    96-hour stall windows and a 30/day new-lead cap don't benefit from
    tighter polling, and re-running them every 90 seconds would just waste
    API calls. Only Step 3 (inbound reply handling) needs to be continuous.

WHAT NEVER CHANGES:
    Zero new logic. This file does not reimplement anything — it imports
    and calls the real, already-tested step3_sms_reply_handler() from
    master_daily_agent.py, unmodified. Opt-out handling, interest-keyword
    handling, and the human-review flag-queue all behave exactly as
    documented in 05_PIPELINE_REFERENCE.md and 07_COMPLIANCE.md.

RUNNING THIS:
    Same as the Gmail listener — run as a launchd service, not manually in
    a terminal you might close. See 09_GO_LIVE_READINESS.md.
"""

import csv
import time
import logging
from pathlib import Path
from datetime import datetime

import master_daily_agent as mda  # reuse step3 + its module-level state, unmodified

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("master.sms_poll")

POLL_INTERVAL_SECONDS = 90   # how often to check Quo for new inbound replies


def flush_log_for_today():
    """mda.run_log accumulates in memory across every call in this process.
    Flush it to a day-stamped CSV and clear it, so a 24/7 process doesn't
    hold an ever-growing list in memory or silently lose entries."""
    if not mda.run_log:
        return
    today_path = Path.home() / "Downloads" / f"master_sms_poll_log_{datetime.now().strftime('%Y%m%d')}.csv"
    file_exists = today_path.exists()
    with open(today_path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["timestamp", "step", "contact", "action", "detail"])
        if not file_exists:
            w.writeheader()
        w.writerows(mda.run_log)
    mda.run_log.clear()


def run_forever():
    log.info(f"=== SMS REPLY SERVICE: starting — checking Quo every {POLL_INTERVAL_SECONDS}s ===")
    consecutive_errors = 0

    while True:
        try:
            mda.step3_sms_reply_handler()  # [FIX 2026-07-01] was step3_handle_sms_replies — that name never existed in master_daily_agent.py; this call would have crashed with AttributeError on first run.
            flush_log_for_today()
            consecutive_errors = 0
        except KeyboardInterrupt:
            log.info("  Shutting down (KeyboardInterrupt)")
            break
        except Exception as e:
            consecutive_errors += 1
            backoff = min(60, 2 ** consecutive_errors)
            log.error(f"  Poll cycle error (attempt {consecutive_errors}): {e} — retrying in {backoff}s")
            time.sleep(backoff)
            continue

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_forever()
