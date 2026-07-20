# DYLAN FOR HIRE
## AI-Powered Staffing Automation for Healthcare Agencies
### Product & Company Overview — Customer-Facing

**Version:** 1.1 | **Last Updated:** 2026-07-01
**Status:** Sanitized for external/prospect use — excludes internal operator identity, personal contact info, and agency-specific detail not relevant to general market use.

**What changed from the uploaded v1.0:** The credential-audit table in §6 was corrected. The
previous version listed 11 document categories, including Hepatitis B, annual flu vaccine, and a
background-check/fingerprint item. That list was checked directly against this session's live
source code (`validate_documents()` in `master_gmail_reviewer.py`) rather than assumed — the
system actually implements **9** categories, and Hepatitis B / flu / background-check are **not**
among them. This is not a formatting choice; it's a correction. See the note at the end of §6.

Two things were deliberately **left out** of this version, and Aditya should decide whether to add
them back before this goes to a prospect:
1. **Continuous (24/7) monitoring.** The underlying system has new always-on email/SMS checking
   built (see `09_GO_LIVE_READINESS.md` in the internal doc set), but it has not yet been verified
   running on the live production Mac. Claiming it here before that verification is done would be
   describing something as proven that isn't yet. Once verified live, this should be added back in.
2. **Live metrics** (candidates contacted, active conversations, etc.) — deliberately omitted here.
   Pull current numbers fresh before any customer conversation rather than hardcoding a snapshot
   into a reusable sales document that will go stale the next time someone opens it.

---

## 1. WHAT IS DYLAN FOR HIRE

Dylan for Hire is an Indo-US SaaS product that automates the candidate pipeline for healthcare staffing agencies in the United States — CNAs, LPNs, and RNs. It is engineered by a distributed Indo-US team, pairing US healthcare staffing domain expertise with an India-based automation and AI engineering practice, and sold directly to small and mid-sized US nurse staffing agencies.

Dylan replaces the manual, spreadsheet-driven candidate intake process most small staffing agencies still run with an automated system covering sourcing, credential verification, shift matching, and placement alerts — reducing the primary human-required steps in the funnel to the sales/discovery call and reviewing anything the system flags or drafts for a human decision.

---

## 2. THE PRODUCT

### Pricing Tiers
| Tier | Price | Notes |
|---|---|---|
| DIY Template | $497 one-time | Template bundle, self-setup, no support |
| Pro Retainer (flagship) | $1,500 setup + $750/month | Full custom build, deposit to start |
| Enterprise | Custom quote | Multi-state, white-label, dedicated SLA |

### The 5-Step Pipeline
1. **Candidate Applies** — Web / SMS / email capture
2. **Intake Captured** — Automated form processing
3. **Documents Audited** — 9-category credential check (see §6), zero human review of the audit step itself
4. **Shift Matched** — AM/PM/overnight by borough & role
5. **Client Alerted** — Under 4 minutes from submission

**The only steps that require a human: the sales call, and reviewing anything the system flags or drafts before it goes out.** That human-review gate is a deliberate safety feature, not a gap — see §6 and §8.

---

## 3. PROVEN RESULTS (LIVE DEPLOYMENT CASE STUDY)

Dylan for Hire is proven in production at a live NYC-area healthcare staffing agency:

- 37 active nurses managed (22 CNAs · 9 LPNs · 6 RNs)
- 19 Full-Time · 16 Part-Time · 2 Per Diem
- Monthly payroll generated: $30–35K
- Monthly client billing: $42–48K
- 83% intake time reduction
- 9-category document audit — zero human review of the audit step itself (see §6)
- Candidate-to-placement alert in under 4 minutes
- One operator now runs what previously required a team of three

*These figures are business-reported and should be re-verified as current before quoting them in any specific customer conversation — they are a point-in-time snapshot, not a live feed.*

---

## 4. TECHNOLOGY STACK

| Component | Function |
|---|---|
| LinkedIn sourcing automation | Automated outbound connection requests |
| Workflow automation platform | Orchestrates the end-to-end pipeline |
| Claude API (Anthropic) | Proposal drafting + document audit intelligence |
| Scheduling integration | Discovery calls booked automatically |
| Payment processing | Invoice generation + payment link on proposal sign |
| Live pipeline dashboard | Source-of-truth tracking |
| One-page marketing site | Product offer page |
| Product walkthrough video | Primary sales asset |

### Core Automation Scenarios
1. **Prospect follow-up** — triggered automatically after initial outbound contact; delivers product walkthrough
2. **Booking handler** — triggered on discovery call booking; updates pipeline + alerts sales team with pre-call intake answers
3. **Proposal draft** — triggered after the discovery call; AI generates a personalized proposal
4. **Invoice + onboarding** — triggered on proposal approval; payment link sent + onboarding sequence starts

---

## 5. CUSTOMER ACQUISITION FUNNEL

```
Outbound prospecting (healthcare staffing agency owners)
  → Connection accepted
  → Automated follow-up: product walkthrough delivered
  → Prospect books discovery call
  → Pipeline updated, sales team alerted
  → Discovery call (30 min — only manual step in the sales process)
  → AI drafts proposal within 60 seconds of call ending
  → Proposal reviewed and sent
  → Prospect pays deposit
  → Onboarding sequence fires automatically
  → 10-day build
  → Go live
  → Recurring monthly revenue begins
```

### Ideal Client Profile (ICP)
- 2–50 employee nurse staffing agency
- Places CNAs / LPNs / RNs (per diem or contract)
- US-based, operating in 1–5 states
- Owner-operator or small founding team
- Currently tracking candidates in spreadsheets
- No dedicated tech or operations hire
- Wants to scale without adding headcount

### Agency Categories Served
- Per Diem Local agencies (major US metros)
- LTC & Nursing Home staffing (CNA/LPN heavy)
- Home Health (recurring aide + nurse shifts)
- Travel staffing boutiques (1–3 state, growing bench)
- New Founders (0–18 months, building operations)

---

## 6. COMPLIANCE & CREDENTIAL AUDIT ENGINE

Dylan's core differentiator is its automated, zero-human-review-of-the-audit-step credential check. The system checks the following categories of healthcare worker documentation, verified directly against the current production code:

| # | Document | Standard Window | Required? |
|---|----------|-------------------|-----------|
| 1 | Updated resume | On file | Required |
| 2 | Nursing license | State-active, correct license type (CNA/LPN/RN) | Required |
| 3 | I-9 identity documents | List A alone OR List B + List C | Required |
| 4 | Physical exam | ≤ 12 months | Required |
| 5 | MMR titer (measles, mumps, rubella) | ≤ 5 years, immunity confirmed | Required |
| 6 | Varicella titer | ≤ 5 years, immunity confirmed | Required |
| 7 | Chest X-ray + PPD (Mantoux), OR Quantiferon-Gold (IGRA) | ≤ 9 months, combined pass/fail | Required |
| 8 | COVID-19 vaccination | Vaccine card, immunization record, or physical-exam record accepted | Required |
| 9 | BLS/CPR certification | ≤ 2 years (AHA or Red Cross accepted) | Preferred, not blocking |

> Regulatory windows are configured at implementation and should be reverified against current state Department of Health guidance for each deployment. Dylan's audit engine is a workflow accelerator — not a substitute for facility-level compliance sign-off.

**Note on scope (do not represent otherwise to a prospect):** Hepatitis B vaccination/titer, annual flu vaccine, and state background-check/fingerprint clearance are **not currently part of the automated audit** — they were in earlier planning material for this system but were never built into the credential-check logic. If a prospect's state or facility requires these, they still need to be tracked manually today. Whether to build them into the automated check is an open product decision, not yet made.

---

## 7. REVENUE MODEL

| Milestone | Clients | Monthly Recurring Revenue |
|---|---|---|
| Early stage | 2 | Setup fees, ramping MRR |
| Growth stage | 4 | MRR building via outreach engine |
| Scale stage | 6 | Referral-driven growth |
| Target stage | 7 | ~$5.3K/month MRR |

---

## 8. QUALITY & GOVERNANCE STANDARDS

- **Automation-first.** Every repeatable step is automated; human time is reserved for sales, relationship-building, and reviewing anything the system flags or drafts.
- **Never auto-sends anything sensitive.** Email replies are always drafts. Both SMS and email flag ambiguous, legal, pricing, or opt-out-adjacent messages for a human to handle directly. This is a permanent safety feature, not a current limitation — sell it as "always watching, always ready, a human approves anything that matters."
- **95th-percentile quality floor** on all client-facing output.
- **No fabricated statistics or invented regulatory requirements.** Anything not independently verified is flagged for confirmation before it reaches a prospect or client.
- **Real deployment data only.** No invented client results.

---

## 9. COMPANY POSITIONING

**Dylan for Hire** is an Indo-US SaaS product: engineered by an India-based automation team, proven on a live US healthcare staffing operation, and sold directly into the US healthcare staffing agency market. It's built for owner-operators who want a modern, automated staffing back office without adding operations headcount.

---

*This document is a sanitized, product-facing overview of Dylan for Hire. It excludes internal operator identity, personal contact information, and agency-specific operational detail not relevant to general market use. Facts in this document are derived from, and must stay in sync with, `SAAS_PROJECT_HEALTHCARE_RECRUITMENT_MASTER_CONTEXT.md` and `09_GO_LIVE_READINESS.md` in the internal Dylan for Hire project — if those change, this document needs a pass too. Do not edit facts here independently of those source documents.*
