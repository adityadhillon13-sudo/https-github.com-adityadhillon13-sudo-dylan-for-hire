# DYLAN PRODUCT CONSTITUTION
## The Operating Manual for Building Dylan — Not Just Selling It
**Version:** 1.0 | **Added:** 2026-07-03 | **Owner:** Aditya

---

## WHY THIS FILE EXISTS

Every other doc in this project (`00_INDEX.md` through `12_SCHEDULING_SETUP_GUIDE.md`,
`SAAS_PROJECT_HEALTHCARE_RECRUITMENT_MASTER_CONTEXT.md`) already states, correctly, that
**BlueLine is the reference client, not the product** (`00_INDEX.md`, "Important framing,"
2026-07-01). That line is true and has been true since v3.0. This file exists because that
one line was living as a footnote, not a governing rule — and a separate, fuller version of
this same idea (identity, mission, architecture principles, a "Golden Rule") had been drafted
in conversation at some point and was sitting **only** in this Cowork project's auto-loaded
custom-instructions snapshot — which is not a real, version-controlled file, cannot be edited
from inside a session, and was independently confirmed stale (`DYLAN_FOR_HIRE_EXHAUSTIVE_AUDIT_2026-07-03.md`
§1) — it does not reflect Rule 0 through 0E, the numbered-doc structure, or the v3.x
architecture at all. A rule that only exists in an ephemeral settings snapshot is not a rule
that survives contact with a new session. This file makes it a permanent, versioned,
git-tracked part of the project instead.

**Nothing in this file changes product behavior.** It is a decision framework and a naming/
identity boundary — the thing every session (Claude or Aditya) checks before a product
decision, a doc edit, or a customer conversation risks quietly treating BlueLine's specific
setup as Dylan's architecture.

---

## 1. IDENTITY

Dylan for Hire is an independent software product. Its purpose is to become the operating
system for healthcare staffing agencies.

BlueLine Staffing (Allendale, NJ) is Dylan's **first production customer, design partner, and
validation partner** — see `00_INDEX.md`, `01_PRODUCT_OVERVIEW.md`, and §12A of the master
context doc for the technical detail of that relationship.

**BlueLine is never the reference architecture. BlueLine is one customer among many that
just happens to be the only one live today.** Every product decision should be made assuming
there will eventually be many agencies using Dylan, not assuming BlueLine's setup is what
"normal" looks like.

## 2. MISSION

Build software that lets healthcare staffing agencies grow placements without growing
operational headcount: more recruiter capacity, less operational friction, better compliance,
preserved institutional knowledge, real operational intelligence.

Dylan does not exist to automate BlueLine specifically. BlueLine automation is the current
*proof*, not the *goal*.

## 3. THE ATS RULE

An ATS records what happened. Dylan drives what happens next. Dylan complements ATS
platforms — it is not trying to replace one. This distinction should shape architecture and
integrations, not just sales language. (See `10_CLIENT_INTAKE_AND_ADAPTER_SPEC.md` for where
this already matters technically.)

## 4. THE FEATURE ACCEPTANCE TEST

Before building or documenting anything as a permanent product feature (not a one-off
BlueLine accommodation), it should pass most of these:

1. Would at least three different agencies plausibly buy this?
2. Would this get built if BlueLine weren't a customer at all?
3. Can another agency configure this without custom code, once the adapter layer
   (`10_CLIENT_INTAKE_AND_ADAPTER_SPEC.md`) exists?
4. Does this still make sense with 500 agencies on the platform, not one?

If the honest answer to more than one of these is "no," it's BlueLine-specific configuration
or a one-off consulting favor — not core product, and it should be built/documented that way
explicitly (e.g. flagged as BlueLine-only in code comments and in
`10_CLIENT_INTAKE_AND_ADAPTER_SPEC.md`), not silently absorbed into `src/` as if it were
general.

## 5. CURRENT REALITY CHECK (do not let this file overclaim)

As of the 2026-07-03 exhaustive audit, the product is **not yet system-agnostic** —
confirmed by direct read of `src/`: no `MessagingAdapter` / `EmailAdapter` / `LeadSourceAdapter`
/ `CredentialRuleset` interface exists anywhere. Every integration (OpenPhone auth/pagination,
Gmail-OAuth-specific scopes, CSV columns literally named `Role`/`Location`, NY-specific
credential rules) is hardcoded to BlueLine's actual setup. This is not a violation of this
Constitution — it's the honest current state, and `10_CLIENT_INTAKE_AND_ADAPTER_SPEC.md`
already recommends the correct build order (adapter interfaces first, then BlueLine's
integrations refactored out into concrete implementations of those interfaces, then a
client-config schema with BlueLine as the first populated config). This file is the reason
that refactor matters, not a claim that it's already done.

**Sales framing, already adopted correctly in the spec:** OpenPhone + Gmail/Google Workspace
is a stated requirement for now, not an open question. Anything else routes to a custom
Enterprise quote rather than being presented as equally supported.

## 6. NAMING (LOW-COST, HIGH-VALUE — DO THIS CONSISTENTLY)

- Product-facing files, docs, and code comments describing Dylan-the-product (architecture,
  pitch assets, the numbered doc set, `src/`) should read as agency-agnostic wherever the
  content genuinely is — e.g. "the agency's Gmail" not "BlueLine's Gmail" in places where the
  logic would work identically for any client, even though today there's only one client.
- BlueLine-specific operational facts (real candidate data, the real center directory, real
  SMS copy, real rates) stay in BlueLine's own docs (`BLUELINE_*.md`,
  `~/Downloads/BlueLine/CLAUDE.md`) and in §12A of the master context doc — never invented or
  duplicated into the generic product docs.
- This is already the working convention (`BLUELINE_` vs `DYLAN_`/numbered-doc filenames) —
  this section just states it as a rule rather than an emergent pattern.

## 7. THE GOLDEN RULE

> **BlueLine informs Dylan. Dylan never becomes BlueLine.**

Every fact, number, or default gets tested against this. If Dylan starts accumulating
BlueLine-specific assumptions, terminology, or hardcoded values as if they were the platform's
permanent shape, the product is drifting into "a customized internal system for one agency,"
not the SaaS company `SAAS_PROJECT_HEALTHCARE_RECRUITMENT_MASTER_CONTEXT.md` describes.

## 8. FOUNDER DECISION FILTER

Read before any meaningful product decision:

1. Am I solving a market problem, or a BlueLine problem?
2. Would I ship this if BlueLine weren't a customer?
3. Can another agency configure this without custom code?
4. Does this increase Dylan's long-term defensibility?
5. Does this move Dylan closer to being the operating system for healthcare staffing agencies,
   not just a better internal tool for one?

If the answer to #5 is no, it probably doesn't belong in the core product — it belongs in
BlueLine's own ops docs, or in a scoped custom-implementation line item.

## 9. HOW A SESSION USES THIS FILE

- Read this alongside `00_INDEX.md` Rule 0 at the start of any Dylan for Hire session —
  Rule 0 governs *where* work happens; this file governs *what kind of thing* Dylan is while
  that work happens.
- If a request would hardcode a new BlueLine-specific assumption into shared `src/` code
  (not a client-config value, an actual hardcoded assumption), flag it against §4 and §6
  before writing it, the same way Rule 0D already requires flagging unverified claims.
- This file does not replace or outrank Rule 0 / 0B / 0C / 0D / 0E in `00_INDEX.md` — it
  answers a different question (identity/scope, not process) and sits alongside them.

---

*Cross-references: `00_INDEX.md` (Rule 0 family, document map), `01_PRODUCT_OVERVIEW.md`
(honest gap list), `10_CLIENT_INTAKE_AND_ADAPTER_SPEC.md` (the actual adapter build order this
Constitution assumes), `SAAS_PROJECT_HEALTHCARE_RECRUITMENT_MASTER_CONTEXT.md` §12A (BlueLine
technical reference, explicitly scoped as "proof of concept — production system," not the
product itself).*
