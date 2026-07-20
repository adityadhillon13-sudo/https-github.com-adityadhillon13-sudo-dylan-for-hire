# DYLAN FOR HIRE — CLIENT INTAKE & ADAPTER SPEC
**Version:** 1.1 | **Created:** 2026-07-01 | **Audited:** 2026-07-02
**Purpose:** Define what Dylan for Hire needs to ask every new client before building
their instance, and how those answers map to configuration — so the product is
actually system-agnostic instead of "BlueLine's script with the agency name changed."

---

## ⚠️ 2026-07-02 AUDIT FINDING — READ BEFORE USING THE QUESTIONNAIRE WITH A REAL PROSPECT

**The Section 2 questionnaire below asks the right questions. The code cannot
act on most of the answers yet.** Verified directly against `src/` on 2026-07-02:

- `master_daily_agent.py` and `upgrade1_context_aware_messaging.py` call the
  OpenPhone/Quo REST API directly — specific base URL, specific auth header
  format, specific pagination shape. There is no `MessagingAdapter` interface
  and no second implementation. **A client on Twilio, RingCentral, EZTexting,
  Podium, etc. cannot be onboarded today without writing a new adapter from
  scratch** — this is real engineering time, not a config change.
- `master_gmail_reviewer.py`, `master_gmail_setup.py`, and
  `master_gmail_pubsub_listener.py` are Gmail-OAuth2-specific (scopes,
  `watch()`, Pub/Sub). There is no `EmailAdapter` interface and no Microsoft
  365/Outlook/generic-IMAP implementation. **A client on Outlook cannot be
  onboarded today** for the same reason.
- `step2_new_leads()` in `master_daily_agent.py` reads CSV columns named
  exactly `Role` and `Location` (case-insensitive, but the *names* are fixed
  in code) and silently defaults to CNA/blank if they're missing — there is
  no per-client column-mapping config yet, despite §3 of this document
  describing one.
- The NY-specific 9-category credential ruleset (see `05_PIPELINE_REFERENCE.md`)
  is hardcoded into `master_gmail_reviewer.py::validate_documents()`. There is
  no `CredentialRuleset` selection by state — a client outside NY, or one
  needing different documents, gets NY's rules whether they apply or not.

**What this means in practice:** asking a prospect "what SMS platform do you
use?" and "what email provider?" as open, no-consequence questions — the way
Section 2 currently frames them — implies Dylan for Hire flexes to whatever
they answer. It doesn't, today. The honest options are:

1. **Make OpenPhone + Gmail/Google Workspace a stated requirement**, not a
   question with infinite valid answers. If a prospect isn't on either, the
   sales conversation becomes "we'll help you switch during onboarding" (cheap,
   fast, matches the ICP of small agencies with no entrenched tooling) rather
   than "we'll build you a new adapter" (slow, expensive, real dev risk).
   This matches §5's own build order — OpenPhone/Gmail/CSV/NY are the *only*
   adapters that exist even in plan form.
2. Or explicitly quote custom-adapter work as a separate, longer-timeline,
   higher-price Enterprise engagement for anyone who won't switch platforms —
   never as part of the standard $1,500+$750/mo Pro Retainer's 10-day build.

**Recommendation (default assumption used in the client-facing document built
from this spec — override if you disagree):** Option 1. The client-facing
intake document frames OpenPhone and Gmail/Google Workspace as required, with
other platforms routed to a "let's talk" custom-quote path rather than
presented as an equally-supported option. Same treatment for state/credential
rules outside NY — flagged as custom scoping, not a same-day config change.

This does not mean the Section 2 questionnaire below is wrong — the questions
are exactly what you'd need to ask if adapters existed. It means the
*framing* the prospect sees needs updating to match what's buildable today,
and this doc's own "what's actually supported vs. what's a custom quote"
distinction needs to travel with it every time it's reused. Logged in
`DYLAN_AUDIT_2026-07-01_FULL.md` per Rule 0B.

---

## 0. WHY THIS DOCUMENT EXISTS

Every doc in this project through `09_GO_LIVE_READINESS.md` describes **BlueLine's
live implementation**: Quo/OpenPhone for SMS, Gmail for email, a CSV with `Role`
and `Location` columns for leads, NY-specific credential rules, BlueLine's rates
and facility list. `01_PRODUCT_OVERVIEW.md` §8 ("White-Label Parameters") currently
treats turning this into a second agency's system as "go edit these constants by
hand" — that's a manual code edit per customer, not a product.

**The actual requirement (per Aditya, 2026-07-01):** since there is no second
client yet, the product's logic has to start with an exhaustive intake step that
finds out what platforms a given client actually runs — their messaging platform,
their email platform, their lead source, their ATS/CRM if any — and the system
configures itself to that client's answers, rather than assuming everyone looks
like BlueLine.

**How to read what follows:** BlueLine is not special. Treat BlueLine as if it
were the first client to go through this intake process. Everything BlueLine-
specific that's currently hardcoded in `src/` (persona name, agency name, rates,
facility list, credential rules, CSV column names, SMS platform, email platform)
should be expressible as *answers to this questionnaire*, not as edits to the core
agent code.

---

## 1. THE CORE ARCHITECTURAL SHIFT

**Today:** one codebase, one client, hardcoded integrations.
```
master_daily_agent.py ──directly calls──> Quo/OpenPhone API (hardcoded URL, auth format)
master_gmail_reviewer.py ──directly calls──> Gmail API (hardcoded scopes, inbox)
CSV reader ──directly expects──> columns named exactly "Role" and "Location"
Document validator ──directly encodes──> NY-specific credential rules
```

**What it needs to become:** one core engine, N client configs, pluggable adapters.
```
CLIENT CONFIG (per client, e.g. client_blueline.yaml)
  → drives: persona name, agency name, rates, facility list, blocked numbers,
    which state's credential rules apply, daily caps, business hours

MESSAGING ADAPTER (interface) ── implemented by ── OpenPhoneAdapter | TwilioAdapter | ...
EMAIL ADAPTER (interface)     ── implemented by ── GmailAdapter | Microsoft365Adapter | ...
LEAD SOURCE ADAPTER (interface) ── implemented by ── CSVAdapter | IndeedAdapter | ATSAdapter | ...
CREDENTIAL RULESET (per state/config) ── e.g. NYCredentialRules | NJCredentialRules | ...

CORE ENGINE (unchanged per client):
  dedup logic, opt-out tracking, context-aware decision engine, run logging,
  the "never auto-send" invariant, the Step 1/2/3/DEDUP orchestration
```

The core engine is the part that's actually the product. The adapters are what
make it sellable to an agency that isn't BlueLine. The client config is what a
sales call + this intake process produces.

---

## 2. THE INTAKE QUESTIONNAIRE

Ask every one of these before scoping a build. Group A determines which adapters
get selected; the rest populate the client config once adapters are chosen.

### A — Platform selection (determines which adapters to build/reuse)

| # | Question | Why it matters | BlueLine's answer (reference) |
|---|----------|-----------------|-------------------------------|
| A1 | What do you use to send/receive SMS with candidates today? (OpenPhone, Twilio, EZTexting, RingCentral, other/none) | Selects the messaging adapter. Each platform has a different API shape, auth format, and pagination style — this is the single biggest source of "it works for BlueLine but not for client #2" bugs. | OpenPhone (branded "Quo" internally) |
| A2 | What email do candidates/documents come into? Which provider — Gmail, Microsoft 365/Outlook, other IMAP? | Selects the email adapter. OAuth flow, API shape, and draft-creation mechanics differ by provider. | Gmail (`info@bluelinestaffing.com`) |
| A3 | Do you use an ATS/CRM (Bullhorn, Crelate, JobDiva, etc.), or do you track candidates in a spreadsheet/the messaging platform's own contacts? | Determines whether there's a real ATS adapter to build or whether the messaging platform's contact list (like Quo/OpenPhone contacts today) doubles as the candidate record. | No ATS — Quo/OpenPhone contacts double as candidate records |
| A4 | Where do new candidate leads come from? (CSV export, Indeed employer portal, ZipRecruiter, a careers page/web form, referrals only) | Selects the lead-source adapter and what fields it needs to normalize. | CSV export (manual) + Indeed (manual, semi-automated) |
| A5 | Is there a public-facing "apply here" form or page today, or does every lead come in through a portal/manual export? | Determines if a web-intake adapter is needed at all, or if this stays pull-based. | No — manual CSV/Indeed only |

### B — Regulatory & credential scope (determines which credential ruleset applies)

| # | Question | Why it matters |
|---|----------|-----------------|
| B1 | What state(s) do you operate in? | Credential requirements are NOT universal — NY's rules (used today) don't automatically apply elsewhere. This is the single biggest "silently wrong" risk if skipped: shipping NY rules to a New Jersey or Florida agency without checking. |
| B2 | What license types do you place? (RN, LPN, CNA, HHA, other — e.g. PT, OT, RT) | Determines which document-validation schema fields are even relevant. |
| B3 | What documents does your state/facility contracts actually require for onboarding? (physical, titers, TB test, background check/fingerprinting, specific vaccines, BLS/CPR, other) | The current code checks 9 categories tuned to NY (see `05_PIPELINE_REFERENCE.md`'s corrected validation table) — a different state may require different items (e.g. a different background-check process) or have different date windows. |
| B4 | Do you have existing onboarding/application PDFs per license type that should be auto-attached? | Determines whether the "attach the right PDF" step (currently hardcoded to 3 BlueLine PDFs at a fixed Desktop path) has anything to attach, and what the per-license mapping should be. |

### C — Persona, voice, and compliance posture

| # | Question | Why it matters |
|---|----------|-----------------|
| C1 | What name should the AI agent use when texting/emailing candidates? | Drives the persona substitution everywhere (today: "Dylan"). |
| C2 | What's your agency's legal/trade name as candidates should see it? | Same — persona + agency name pair drives every template. |
| C3 | What phone number and monitored inbox should be used? | Config values, not code changes — but need to exist before build. |
| C4 | Any phrases, tone, or claims your compliance/legal function wants to forbid or require (beyond standard TCPA STOP language)? | Some agencies may have stricter internal compliance requirements than the TCPA floor this system currently implements. |
| C5 | Who reviews Gmail drafts before sending — one person, a team, a shared inbox? | Doesn't change the engine (still never auto-sends) but affects the daily-operations doc for that client. |

### D — Volume & operations

| # | Question | Why it matters |
|---|----------|-----------------|
| D1 | Roughly how many new leads per day/week, and how many active candidates at once? | Sets the client's `NEW_LEAD_ROLLING_CAP`-equivalent value. **[UPDATED 2026-07-02, Round 14 audit]** BlueLine itself no longer uses a fixed daily cap — as of Round 11/12 it sends unlimited new-lead intros per run, gated only by a rolling 75-messages/trailing-24h safety cap (with a notification when hit) and the hard duplicate-send guard. The old "30/day, 150-catchup" numbers referenced here are retired even for BlueLine, not just non-universal — use the rolling-cap model as the template for new clients instead. |
| D2 | What are your pay rates by role and shift (if you want them quoted automatically)? | Populates the rates section of the document-checklist/interest-reply templates. |
| D3 | What facilities/clients should be mentioned in candidate-facing messaging, if any? | Populates the facility-list section of templates. |
| D4 | Where will this run — the agency's own machine (cron/launchd, like BlueLine today) or does it need to be hosted centrally? | Determines whether the "everything runs on Aditya's Mac" assumption throughout `03_SETUP_GUIDE.md` holds for this client, or whether a hosted/multi-tenant deployment model is needed. |

---

## 3. WHAT THIS MEANS FOR THE EXISTING CODEBASE

None of `src/` needs to be thrown away — BlueLine's implementation is the reference
adapter for OpenPhone + Gmail + CSV + NY rules. What changes is where the
BlueLine-specific values live:

| Currently hardcoded as... | Should become... |
|---|---|
| `DYLAN_INTRO`, `DOCUMENT_CHECKLIST_MSG` string literals in `master_daily_agent.py` | Templates parameterized by client config (persona, agency name, rates, facility list) |
| `QUO_BASE_URL`, OpenPhone-specific auth/pagination logic | `OpenPhoneMessagingAdapter` implementing a generic `MessagingAdapter` interface (`send`, `get_recent_conversations`, `get_contact_by_phone`, `create_contact`, `rename_contact`) |
| Gmail-specific OAuth/token logic in `master_gmail_setup.py`/`master_gmail_reviewer.py` | `GmailEmailAdapter` implementing a generic `EmailAdapter` interface (`get_unread`, `get_thread_history`, `save_draft`) |
| `row.get("Role")` / `row.get("Location")` CSV column assumptions | `CSVLeadAdapter` with a per-client column-mapping config (answers to A4 above determine which adapter; the mapping answers B1-ish questions about field names) |
| The 9-category NY-tuned validation schema in `master_gmail_reviewer.py::validate_documents()` | A `CredentialRuleset` selected by state (answers to B1-B3), with NY as the first implemented ruleset |
| `BLOCKED_NUMBERS`, daily cap constants | Per-client config values, not module-level constants in shared code |

**What stays exactly as-is:** the dedup 3-pass algorithm, the opt-out state-file
pattern, the context-aware decision engine's *logic* (the Claude prompt structure
for SKIP/SEND decisions), the "drafts only, human sends" invariant, and the run-log
audit trail. These are the actual reusable product — they don't reference any
platform specifics.

---

## 4. HOW THIS RESOLVES THE BLUELINE-VS-DYLAN-FOR-HIRE QUESTION

Treating BlueLine as "client #1" instead of "the product" means:
- **This project** ("Dylan for Hire") should hold: the core engine, the adapter
  interfaces, this intake spec, and (once built) each adapter implementation as a
  reusable module — the sellable product.
- **BlueLine's own project/folder** should hold: BlueLine's filled-out answers to
  Section 2 above (effectively a config file), BlueLine's own operational docs
  (`BLUELINE_MASTER_OPS.md`, `BLUELINE_CANDIDATE_PIPELINE.md`, etc. — already
  referenced at `~/Downloads/BlueLine/` in the master context doc's governing-docs
  table), and BlueLine-specific runtime concerns (its actual cron, its actual
  `.env`, its actual CSV).

**Open item, needs your input, not something I can resolve alone:** I don't have
a way to see or write to a separate "BlueLine" Cowork project from inside this
session — switching projects/folders is a UI action on your end, not something
any tool available to me can do. Practically, that means physically moving
`src/*.py` and the BlueLine-specific parts of the doc set out of this project
folder requires either (a) you opening the BlueLine project yourself and asking me
there to pull this project's BlueLine-specific content in, or (b) you doing a
plain file copy in Finder — these are real files on your Mac at
`/Users/Aditya/Claude/Projects/Dylan for Hire- Saas Product Healthcare recruitment/`.
Let me know which you'd prefer and I'll prepare exactly what should move.

---

## 5. NEXT STEP (PER ADITYA'S DIRECTION: SPEC FIRST, THEN SCAFFOLDING)

This document is the spec. Scaffolding should build, in this order:
1. The four adapter interfaces (Messaging, Email, LeadSource, CredentialRuleset)
   as abstract base classes/protocols — no client-specific logic in them.
2. `OpenPhoneMessagingAdapter`, `GmailEmailAdapter`, `CSVLeadAdapter`, and
   `NYCredentialRuleset` as the first concrete implementations — refactored out
   of BlueLine's existing, proven code, not rewritten from scratch.
3. A client config schema (likely YAML) with BlueLine's own answers to Section 2
   as the first populated config, proving the refactor didn't change BlueLine's
   actual behavior.
4. Re-run BlueLine's existing test/verification steps from `09_GO_LIVE_READINESS.md`
   against the refactored version before touching anything else — BlueLine going
   live on 2026-07-15 should not be put at risk by this refactor.
