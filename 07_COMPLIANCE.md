# DYLAN FOR HIRE — COMPLIANCE PROTOCOL
**Version:** 2.0 | **Last Updated:** 2026-07-01
**Purpose:** TCPA compliance, opt-out management, PII handling, and what NEVER to do.
**Risk level:** Non-compliance with TCPA costs $1,500 per violation. This document is not optional.
**What's new:** Email now has its own automated decision-making (general inquiries,
not just document review) — rule #3 below already covered this in spirit, but v2.0
makes explicit what "sensitive" means for email specifically, since that's now a
live decision the system makes many times a day instead of once.

---

## CRITICAL: NEVER VIOLATE THESE RULES

These are structural invariants in the system. They are not options. They are not context-dependent.

1. **`master_permanent_optouts.txt` MUST NEVER BE DELETED.** Every phone number in this file belongs to a person who explicitly asked to be removed. Deleting this file means re-contacting opted-out people. That is an illegal TCPA violation.

2. **BLOCKED_NUMBERS must never be removed or bypassed.** Current blocked numbers:
   ```
   +13473572031  (Vanessa Ratcliff)
   ```
   This number must stay blocked at the code level and in your Quo contacts.

3. **No email is ever sent automatically.** The Gmail reviewer saves DRAFTS ONLY — this now covers BOTH document-review replies AND general-inquiry replies (new, v2.0). Aditya reviews every draft before clicking Send. No exceptions. No "send it for me" automation.

4. **No contact is ever re-messaged after opting out.** Not after a CSV re-import, not after a database reset, not after a system restart. The opt-out file is the authoritative source. The system checks it before every send.

---

## EMAIL COMPLIANCE GATE (NEW, v2.0) — WHAT GETS FLAGGED INSTEAD OF DRAFTED

The general-inquiry email flow (`email_context_bridge.py`) is instructed to
choose FLAG_HUMAN over DRAFT whenever any of these appear — this is not a
suggestion to the model, it's the first thing checked in its decision
prompt:

- Any opt-out / removal / "stop contacting me" language, in any wording
- Legal threats, mentions of an attorney, lawsuit, discrimination, harassment,
  or a regulatory body (DOH, DOL, EEOC, etc.)
- Pricing, rate negotiation, or contract terms — anything that would commit
  BlueLine to specific terms
- Emails from a nursing home / facility / client (not a candidate)
- Anything the model isn't confident it understands correctly

**⚠️ KNOWN GAP — email opt-outs are NOT auto-added to the SMS opt-out file.**
`master_permanent_optouts.txt` is phone-keyed and only ever written to by the
SMS opt-out flow (Step 3, `step3_sms_reply_handler`). If a candidate emails
"please stop contacting me," that email gets FLAG_HUMAN'd correctly — but
**you must manually check whether the same person has a Quo/phone record and
add them to the opt-out file yourself** if so. The system does not currently
cross-reference an email-based opt-out into the phone-based do-not-contact
list automatically. Treat every email-side opt-out flag as a prompt to check
Quo, not just to stop emailing. This is the single most important open item
in `09_GO_LIVE_READINESS.md` — do not represent this as an already-closed
loop to a customer.

---

## TCPA — WHAT IT IS AND WHY IT MATTERS

The Telephone Consumer Protection Act (TCPA) governs commercial text messaging in the US.

**Relevant rules for this system:**
- You must stop contacting anyone who says STOP, UNSUBSCRIBE, or any equivalent
- You must provide an opt-out mechanism in first-contact messages ("Reply STOP to opt out")
- You must identify yourself (Dylan from BlueLine Staffing) in every first message
- Violations carry statutory damages of $500–$1,500 per message sent to an opted-out number

**At volume (30 leads/day × 30 days = 900 messages/month):** A single compliance failure with mass re-contact could mean $1.3M+ in exposure. This is not theoretical.

---

## OPT-OUT PROTOCOL

### When a candidate texts STOP, UNSUBSCRIBE, or any opt-out keyword:

**What the system does automatically:**
1. Detects the keyword in the inbound message (Step 3)
2. Renames the Quo contact: `firstName = "DO NOT MESSAGE - {original_name}"`
3. Clears the Quo contact's `lastName` field
4. Deletes the Quo conversation (removes from active pipeline)
5. Adds the phone number to `master_permanent_optouts.txt`
6. Logs the action with timestamp

**What you do after the agent runs:**
- Nothing. The opt-out is handled.
- If the contact also emailed → do not reply to their email
- If you later get a new CSV with this phone number → system will skip it (opt-out check runs before every send)

### Opt-out keywords the system recognises:
```
stop, unsubscribe, remove, opt out, optout,
dont text, do not text, dont contact, do not contact,
wrong number, take me off, please stop, no thanks,
not interested, leave me alone
```

### What to do if system misses an opt-out:

If a candidate sends something the system doesn't recognise as an opt-out (e.g. "pls stop texting me" or "get me off your list"):

1. The message goes to `master_needs_human_review.txt`
2. You review it and recognise it as an opt-out
3. Manually:
   ```bash
   # Add to opt-out file
   echo "+1XXXXXXXXXX" >> ~/Downloads/master_permanent_optouts.txt
   ```
4. Open Quo → find contact → rename to "DO NOT MESSAGE - {name}" → clear lastName
5. Do not send any reply

---

## BLOCKED NUMBERS — HARDCODED IN CODE

```python
# master_daily_agent.py — module level
BLOCKED_NUMBERS = {'+13473572031'}  # Vanessa Ratcliff
```

This set is checked before every SMS in every step. Even if this number appears in the CSV, was in Quo, or replied with YES — it will never receive another message from this system.

**To add a new blocked number:**
1. Open `master_daily_agent.py`
2. Find `BLOCKED_NUMBERS = {`
3. Add the number: `BLOCKED_NUMBERS = {'+13473572031', '+1XXXXXXXXXX'}`
4. Document the reason in a comment on the same line

---

## STATE FILE SAFETY

| File | Safe to delete? | Consequence |
|------|----------------|-------------|
| `master_permanent_optouts.txt` | **NEVER** | TCPA violation — opted-out numbers re-messaged |
| `master_processed_contacts.txt` | No | Duplicate intro SMS to all past contacts |
| `master_handled_interest_replies.txt` | No | Interest replies responded to twice (double checklist send) |
| `master_processed_email_ids.txt` | No | Duplicate Gmail drafts created |
| `master_needs_human_review.txt` | Yes (after reviewing all items) | Loses pending review log |
| `master_last_run_timestamp.txt` | Yes | Next run calculates as if many days missed (catch-up fires) |
| `master_run_log_*.csv` | Yes | Loses audit trail for that run |

---

## FIRST-MESSAGE REQUIREMENTS

Every first contact with a candidate must include:
1. Agent identity: "this is Dylan from BlueLine Staffing"
2. Purpose: what you're offering (nursing shifts, placements)
3. Opt-out instruction: "Reply STOP to opt out" (exact wording preferred but any clear instruction works)

The DYLAN_INTRO template already includes all three. Do not remove any of these elements when customising the intro.

---

## PII HANDLING — CANDIDATE DATA

**What is PII in this system:**
- Candidate names
- Phone numbers
- Email addresses
- Resume content
- License numbers
- Addresses

**Rules:**
- `CONFIDENTIAL_candidates.csv` must NEVER be committed to git, uploaded to any cloud service, or shared with anyone outside the organisation
- `gmail_credentials.json` and `gmail_token.json` must stay local — they authorise access to the agency email account
- API keys (`.env`) must never be shared or committed
- If any of the above are accidentally exposed → rotate immediately (see Emergency Procedures)

**Indeed-specific rules:**
- Never use, store, or text to `@indeedmail.com` proxy addresses
- Only store and use the candidate's personal email if visible in their resume
- Multi-application rule: If a candidate applied to multiple positions, one record only — do not duplicate

---

## EMAIL DRAFT REVIEW REQUIREMENTS

Before sending any Gmail draft created by the document reviewer:

1. **Confirm the checklist is accurate:** Read each ✓ and ✗. Claude reads documents well, but verify any unusual findings.
2. **Check the PDF attachment:** Confirm the right PDF is attached (RN vs LPN vs CNA).
3. **Add your signature:** The draft is written by Claude. Add your Gmail signature block before sending.
4. **Do not auto-forward:** Never set up Gmail filters or automation that would send these drafts without your review.

**One human review always stands between the AI and the candidate inbox.** This is intentional and non-negotiable.

---

## EMERGENCY PROCEDURES

### Accidental re-contact of opted-out number

1. Stop the agent immediately: kill any running process
2. Send a genuine apology from Quo manually:
   ```
   Hi [name], I sincerely apologise for contacting you again. 
   Your number has been permanently removed. We won't reach out again.
   ```
3. Confirm the phone number is in `master_permanent_optouts.txt`
4. Document: date, number, how it happened, what was sent

### API key exposed (committed to git, pasted in Slack, etc.)

1. Immediately revoke the exposed key:
   - Anthropic: console.anthropic.com → API Keys → Revoke
   - OpenPhone: openphone.com → Settings → API → Revoke
2. Generate new keys
3. Update `~/Downloads/.env` with new values
4. Verify agent still works: `python3.11 master_daily_agent.py`
5. If git was involved: contact whoever has access to that repo

### Gmail credentials exposed

1. Go to Google Cloud Console → OAuth 2.0 → revoke the client credentials
2. Generate new credentials
3. Replace `gmail_credentials.json` in `~/Downloads/BlueLine/`
4. Re-run `python3.11 master_gmail_setup.py` to get a new token

### Candidate data (CSV) exposed

1. Immediately remove from wherever it was exposed
2. Notify Aditya
3. Do not send further messages to any candidate whose data was exposed until situation is assessed
4. Consider whether candidates need to be informed per applicable state data breach notification laws

---

## AUDIT TRAIL

Every run generates: `~/Downloads/master_run_log_YYYYMMDD_HHMMSS.csv`

**Contents:**
- Timestamp of every action
- Candidate name and phone
- Action type (INTRO_SMS, INTEREST_REPLY, REENGAGE, OPT_OUT, DEDUP_MERGE, etc.)
- Result (SENT, SKIPPED, FAILED, FLAGGED)
- Notes (reason for skip, error message, etc.)

**Retention:** Keep all run logs. They are your paper trail if a TCPA complaint is ever filed. Archive monthly but do not delete.

**What the log proves:**
- You sent opt-out instructions with first contact (DYLAN_INTRO)
- You processed opt-outs immediately (OPT_OUT action)
- You did not re-contact after opt-out (phone absent from all subsequent INTRO_SMS rows)
