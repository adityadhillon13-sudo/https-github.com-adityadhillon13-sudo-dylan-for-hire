# DYLAN FOR HIRE
## Scheduling & Discovery Call Setup Guide

**Version:** 1.1 | **Last Updated:** 2026-07-01
**Supersedes:** `Dylan_for_Hire_Calendly_Setup_Guide.md` (referenced in the master context doc §10 but not
present in this project folder as of this audit — this file is the current version of that deliverable,
renamed to describe the process rather than one specific tool).

**Audit note:** checked against `SAAS_PROJECT_HEALTHCARE_RECRUITMENT_MASTER_CONTEXT.md` §8 (the record
of the actual live Calendly configuration). All process values below (buffers, hours, call length, max/day,
notice) match §8 exactly as of 2026-07-01 — no corrections needed to this file's content.

**Important — avoid duplicating live values in two places.** This file intentionally does **not** hardcode
the actual account name, email address, phone number, or booking URL — those live in one place only:
`SAAS_PROJECT_HEALTHCARE_RECRUITMENT_MASTER_CONTEXT.md` §8. If those specifics ever change, update §8 and
treat this file as the process, not the record of current values.

This guide walks through setting up the discovery call booking system used in the Dylan for Hire sales funnel.

---

## STEP 1 — Create the Company Inbox

Create a dedicated business email account for customer-facing communication under the company brand (e.g., a `dylanforhire.com` address or a branded Gmail account).

Set up mail forwarding from the dedicated inbox to your internal operations inbox so booking notifications are never missed, and optionally configure "Send As" so replies can go out from the branded address without switching inboxes.

---

## STEP 2 — Create the Scheduling Account (Calendly)

Sign up at calendly.com using the company inbox created in Step 1.

| Field | Value |
|---|---|
| Name | Dylan for Hire |
| Welcome message | *"Book your free 30-min Dylan demo. I'll show you exactly how the system works — and whether it's the right fit for your agency."* |
| Time zone | Eastern Time (US & Canada) |

---

## STEP 3 — Configure Availability

| Day | Hours |
|---|---|
| Monday–Friday | 9:00 AM – 6:00 PM ET |
| Saturday–Sunday | Off |

- Buffer before: **10 minutes**
- Buffer after: **15 minutes**
- Maximum bookings per day: **4**

---

## STEP 4 — Create the Event Type

### Basic Info
| Field | Value |
|---|---|
| Event name | Free 30-Min Dylan Demo |
| Location | Zoom / Google Meet |
| Duration | 30 minutes |
| Description | *"See Dylan live — the AI staffing agent that runs intake, document audits, shift matching, and placement alerts for nurse staffing agencies. No pressure. Just a live walkthrough."* |

### Scheduling Rules
| Setting | Value |
|---|---|
| Date range | 60 rolling days |
| Start time increments | 30 minutes |
| Minimum notice | 4 hours |
| Max invitees | 1 |

### Required Invitee Questions
1. Agency name (short answer)
2. State(s) you operate in (short answer)
3. Nurses currently on your bench (dropdown: Under 10 / 10–25 / 26–50 / 50+)
4. What are you currently using to manage candidate intake? (short answer)

### Confirmation Message
> *"You're booked. Before the call, check your email — I'll send a short walkthrough showing Dylan running live in production. You'll see the full intake-to-alert pipeline before we speak.*
>
> *Talk soon — the Dylan for Hire team."*

---

## STEP 5 — Notification Emails

Turn on invitee reminders: 1 day before, 1 hour before.

**Reminder message (1 hour before):**
> *"Your Dylan demo is in 1 hour. Link: [meeting link]. Questions before we start? Reply to this email."*

Turn on internal reminder: 15 minutes before.

---

## STEP 6 — Booking Link

Publish the booking link and route it consistently across every customer touchpoint: sales deck CTA, outreach sequence, marketing automation, and the company website CTA button.

Current live booking URL is recorded in `SAAS_PROJECT_HEALTHCARE_RECRUITMENT_MASTER_CONTEXT.md` §8 — do not duplicate it here; that section is the single source of truth so it only needs to be updated in one place if it ever changes.

---

## STEP 7 — Connect to Automation Platform

Configure the automation platform to watch for new booking events (`invitee.created`). On trigger:
1. Add the prospect to the sales pipeline (tag: Discovery Call Booked)
2. Alert the sales team with the prospect's pre-call intake answers
3. Queue the AI-drafted proposal for after the call

**Cross-reference:** this is Make.com Scenario 2 in the master context doc §3/§4 — not "Scenario 1" (Scenario 1 is the Loom follow-up automation, triggered earlier in the funnel). This numbering has been a recurring source of confusion across earlier drafts of this guide — do not renumber it again.

---

## QUICK REFERENCE

| Item | Value |
|---|---|
| Availability | Mon–Fri, 9am–6pm ET |
| Call duration | 30 minutes |
| Buffer before | 10 minutes |
| Buffer after | 15 minutes |
| Max calls/day | 4 |
| Min booking notice | 4 hours |

---

*Dylan for Hire — an Indo-US SaaS product built for the US healthcare staffing agency market. Process guide only — for live account values (name, email, phone, booking URL), see `SAAS_PROJECT_HEALTHCARE_RECRUITMENT_MASTER_CONTEXT.md` §8.*
