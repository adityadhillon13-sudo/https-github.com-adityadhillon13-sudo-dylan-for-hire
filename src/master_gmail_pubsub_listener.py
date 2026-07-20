#!/usr/bin/env python3
"""
BlueLine Staffing — Real-Time Gmail Listener (24/7 Service)
=============================================================
Version: 1.0 | 2026-07-01

WHAT THIS REPLACES:
    Before this file existed, email got checked ONCE — whenever you manually
    ran `python3.11 master_gmail_reviewer.py`, or whenever you remembered to.
    There was no scheduled or continuous email checking at all (confirmed:
    no cron entry, no loop, anywhere in the old code for the Gmail side).

WHAT THIS IS:
    A long-running background process (NOT a cron job — cron runs something
    once and exits; this is meant to stay running 24/7, like a service).
    It uses Gmail's push-notification system (via Google Cloud Pub/Sub) so
    that within seconds of a new email arriving at info@bluelinestaffing.com,
    this process finds out and processes it — instead of waiting for the
    next scheduled check.

HOW IT WORKS (PULL, not PUSH — this matters for your setup):
    Gmail's push notifications normally go to a public HTTPS webhook. You
    don't have a public server — everything runs on your Mac. So instead of
    "push", this uses a Pub/Sub PULL subscription: Gmail tells Pub/Sub
    "something changed", and this script asks Pub/Sub "anything new for
    me?" every few seconds. From the outside this behaves exactly like
    real-time (few-second latency) — it just doesn't require you to run a
    public web server on your Mac.

SETUP REQUIRED BEFORE THIS WILL RUN:
    See 09_GO_LIVE_READINESS.md and 03_SETUP_GUIDE.md — you need a Google
    Cloud project, a Pub/Sub topic + pull subscription, and Gmail's push
    service account granted Publisher rights on that topic. This is a
    one-time setup (~20 minutes, exact click-by-click steps in the guide).
    This script cannot do that part for you — it requires your Google
    account and Google Cloud Console access.

WHAT NEVER CHANGES:
    Same non-negotiable rule as every other part of this system: nothing
    is ever auto-sent. This script calls process_new_message_by_id() in
    master_gmail_reviewer.py, which only ever creates Gmail Drafts or
    flags for human review. See 07_COMPLIANCE.md rule #3.

RUNNING THIS:
    Do not run this with `python3.11 master_gmail_pubsub_listener.py` and
    then close the terminal — it will stop. Run it as a launchd service so
    it survives reboots and terminal closes and auto-restarts on crash.
    Exact plist + commands are in 09_GO_LIVE_READINESS.md.
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from googleapiclient.errors import HttpError
# [CLEANED 2026-07-02, Round 14 audit] `build` (googleapiclient.discovery) was
# imported but never called here — Gmail service construction is delegated to
# get_gmail_service() (imported from master_gmail_reviewer.py, used below).
# Confirmed via grep for `build(` returning no call sites before removing.

load_dotenv(os.path.expanduser("~/Downloads/.env"))

try:
    from google.cloud import pubsub_v1
except ImportError:
    print(
        "Missing dependency: google-cloud-pubsub\n"
        "Install with: pip3.11 install google-cloud-pubsub --break-system-packages\n"
        "(also added to master_requirements.txt)"
    )
    sys.exit(1)

# Reuse the SAME Gmail auth + the SAME per-message processor used by the
# batch reviewer — no separate/duplicate email-handling logic exists.
from master_gmail_reviewer import get_gmail_service, get_claude_client, process_new_message_by_id

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("master.gmail_listener")

# ── Config ──────────────────────────────────────────────────────────────────
GCP_PROJECT_ID   = os.getenv("GCP_PROJECT_ID")                    # e.g. "dylan-for-hire-prod"
PUBSUB_TOPIC     = os.getenv("GMAIL_PUBSUB_TOPIC", "gmail-dylan-notify")
PUBSUB_SUB       = os.getenv("GMAIL_PUBSUB_SUBSCRIPTION", "gmail-dylan-notify-sub")

STATE_DIR             = Path.home() / "Downloads"
HISTORY_ID_PATH        = STATE_DIR / "master_last_gmail_history_id.txt"
WATCH_EXPIRATION_PATH  = STATE_DIR / "master_gmail_watch_expiration.txt"

PULL_TIMEOUT_SECONDS   = 20     # how long each pull request waits for a message
IDLE_SLEEP_SECONDS     = 3      # pause between pull attempts when nothing arrives
WATCH_RENEW_MARGIN_HRS = 24     # renew watch() this many hours before it expires
WATCH_LIFETIME_DAYS    = 7      # Gmail's hard limit on watch() validity


# ================================================================================
# SECTION 1: STATE FILES
# ================================================================================

def read_state(path: Path) -> str:
    return path.read_text().strip() if path.exists() else ""


def write_state(path: Path, value: str):
    path.write_text(str(value))


# ================================================================================
# SECTION 2: GMAIL WATCH() SETUP + RENEWAL
# ================================================================================

def start_or_renew_watch(service) -> None:
    """
    Tells Gmail to publish a Pub/Sub notification to our topic every time
    something changes in the inbox. Must be renewed at least every 7 days
    (Gmail's hard limit) — this function checks the stored expiration and
    renews automatically if we're within WATCH_RENEW_MARGIN_HRS of it.
    """
    if not GCP_PROJECT_ID:
        raise RuntimeError(
            "GCP_PROJECT_ID not set in ~/Downloads/.env — required for Gmail watch(). "
            "See 09_GO_LIVE_READINESS.md setup section."
        )

    expiration_str = read_state(WATCH_EXPIRATION_PATH)
    if expiration_str:
        expires_at = datetime.fromtimestamp(int(expiration_str) / 1000, tz=timezone.utc)
        if datetime.now(timezone.utc) < expires_at - timedelta(hours=WATCH_RENEW_MARGIN_HRS):
            log.info(f"  Gmail watch() still valid until {expires_at.isoformat()} — no renewal needed")
            return

    topic_name = f"projects/{GCP_PROJECT_ID}/topics/{PUBSUB_TOPIC}"
    log.info(f"  Calling Gmail watch() -> topic {topic_name}")
    try:
        response = service.users().watch(
            userId="me",
            body={"topicName": topic_name, "labelIds": ["INBOX"], "labelFilterAction": "include"},
        ).execute()
    except HttpError as e:
        log.error(f"  Gmail watch() failed: {e}")
        raise

    history_id = response.get("historyId")
    expiration = response.get("expiration")  # epoch ms string
    write_state(WATCH_EXPIRATION_PATH, expiration)

    # Only seed the history cursor if we don't already have one — we do NOT
    # want to overwrite a cursor that's ahead of this response's historyId,
    # which would cause us to silently miss messages that arrived between
    # the previous watch() call and this one.
    if not read_state(HISTORY_ID_PATH):
        write_state(HISTORY_ID_PATH, history_id)

    exp_readable = datetime.fromtimestamp(int(expiration) / 1000, tz=timezone.utc).isoformat()
    log.info(f"  Gmail watch() active. Expires: {exp_readable} (historyId cursor: {read_state(HISTORY_ID_PATH)})")


# ================================================================================
# SECTION 3: PUB/SUB PULL LOOP
# ================================================================================

def get_subscriber_and_path():
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(GCP_PROJECT_ID, PUBSUB_SUB)
    return subscriber, subscription_path


def pull_once(subscriber, subscription_path, max_messages: int = 10) -> list:
    """Synchronous pull — waits up to PULL_TIMEOUT_SECONDS for messages, then
    returns whatever arrived (possibly empty). This is the 'few seconds of
    latency instead of a public webhook' tradeoff described at the top of
    this file."""
    try:
        response = subscriber.pull(
            request={"subscription": subscription_path, "max_messages": max_messages},
            timeout=PULL_TIMEOUT_SECONDS,
        )
        return response.received_messages
    except Exception as e:
        # Pub/Sub pull times out with no messages fairly often under normal
        # operation — that's not an error, just "nothing happened."
        if "DeadlineExceeded" in type(e).__name__ or "504" in str(e):
            return []
        log.warning(f"  Pub/Sub pull error: {e}")
        return []


def handle_notification(gmail_service, claude_client, notification: dict) -> None:
    """
    notification = {"emailAddress": "info@bluelinestaffing.com", "historyId": "123456"}
    Fetches everything that changed since our last known historyId and
    processes each new message through the exact same logic as batch mode.
    """
    new_history_id = notification.get("historyId")
    last_history_id = read_state(HISTORY_ID_PATH)

    if not last_history_id:
        log.warning("  No stored historyId cursor — seeding from this notification, skipping delta fetch this cycle")
        write_state(HISTORY_ID_PATH, new_history_id)
        return

    try:
        history_response = gmail_service.users().history().list(
            userId="me",
            startHistoryId=last_history_id,
            historyTypes=["messageAdded"],
        ).execute()
    except HttpError as e:
        if e.resp.status == 404:
            # historyId too old (Gmail only retains ~7 days of history) —
            # cursor is stale, resync forward without reprocessing everything.
            log.warning("  historyId too old (404) — resyncing cursor to current notification, no backfill")
            write_state(HISTORY_ID_PATH, new_history_id)
            return
        log.error(f"  Gmail history.list() failed: {e}")
        return

    changes = history_response.get("history", [])
    new_message_ids = set()
    for change in changes:
        for added in change.get("messagesAdded", []):
            msg = added.get("message", {})
            if "INBOX" in (msg.get("labelIds") or []):
                new_message_ids.add(msg["id"])

    if new_message_ids:
        log.info(f"  {len(new_message_ids)} new message(s) since last check")
    for msg_id in new_message_ids:
        try:
            result = process_new_message_by_id(gmail_service, claude_client, msg_id)
            log.info(f"    {msg_id} -> {result['outcome']}")
        except Exception as e:
            log.error(f"    Failed processing {msg_id}: {e}")

    write_state(HISTORY_ID_PATH, new_history_id)


def run_forever():
    log.info("=== GMAIL REAL-TIME LISTENER: starting (DRAFT MODE — nothing auto-sends) ===")

    gmail_service = get_gmail_service()
    claude_client = get_claude_client()
    start_or_renew_watch(gmail_service)

    subscriber, subscription_path = get_subscriber_and_path()
    log.info(f"  Pulling from: {subscription_path}")

    last_watch_check = time.time()
    consecutive_errors = 0

    while True:
        try:
            # Re-check watch() expiration roughly once an hour (cheap no-op
            # if not near expiry yet — see start_or_renew_watch()).
            if time.time() - last_watch_check > 3600:
                start_or_renew_watch(gmail_service)
                last_watch_check = time.time()

            messages = pull_once(subscriber, subscription_path)
            if not messages:
                time.sleep(IDLE_SLEEP_SECONDS)
                continue

            ack_ids = []
            for received in messages:
                try:
                    # [FIX 2026-07-02] google-cloud-pubsub's client library already base64-decodes
                    # message.data into raw bytes as part of its gRPC/protobuf handling — this is
                    # different from the raw REST API, where "data" appears as a base64 string in
                    # JSON. Double-decoding raw bytes as base64 text produced:
                    # "Invalid base64-encoded string: number of data characters (N) cannot be 1
                    # more than a multiple of 4" — confirmed live against a real Gmail
                    # notification on 2026-07-02. message.data does not need b64decode() here.
                    payload = json.loads(received.message.data.decode("utf-8"))
                    handle_notification(gmail_service, claude_client, payload)
                except Exception as e:
                    log.error(f"  Failed to process Pub/Sub message: {e}")
                ack_ids.append(received.ack_id)

            if ack_ids:
                subscriber.acknowledge(request={"subscription": subscription_path, "ack_ids": ack_ids})

            consecutive_errors = 0

        except KeyboardInterrupt:
            log.info("  Shutting down (KeyboardInterrupt)")
            break
        except Exception as e:
            consecutive_errors += 1
            backoff = min(60, 2 ** consecutive_errors)
            log.error(f"  Unexpected error in main loop (attempt {consecutive_errors}): {e} — retrying in {backoff}s")
            time.sleep(backoff)


if __name__ == "__main__":
    run_forever()
