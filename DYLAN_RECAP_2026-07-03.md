
# DYLAN FOR HIRE — SAAS PRODUCT RECAP ACROSS ALL COWORK SESSIONS
### Compiled 2026-07-03 · for the new "Dylan" session

---

## WHY THIS DOCUMENT EXISTS

This is the product/sales half of the split — everything about **Dylan for Hire**, the productized AI staffing automation service you're building to sell to other nurse staffing agencies. The companion doc, `BLUELINE_RECAP_2026-07-03.md`, covers BlueLine's own live operational system separately (BlueLine is Dylan's proof-of-concept, but the two shouldn't be managed in the same session). Hand this doc to your new "Dylan" session.

---

## 1. WHERE THE PRODUCT DOCS LIVE — AND THE MESS TO CLEAN UP FIRST

**Two parallel doc sets currently exist and have never been reconciled:**

1. `Dylan_for_Hire_Master_Context.md` (this project's root — was `SAAS_PROJECT_HEALTHCARE_RECRUITMENT_MASTER_CONTEXT.md`, renamed/split by you on 2026-07-02)
2. `~/Downloads/DylanForHire/` — a more complete 10-document set built in a dedicated migration session:

| File | Contents |
|---|---|
| `DFH_CLAUDE_SESSION_BOOTSTRAP.md` | Load-first file for any new Claude session on Dylan — pipeline, invariants, APIs, persona, known bugs, outstanding work |
| `DFH_00_MASTER_INDEX.md` | Project overview, doc map, version log, quick-start commands |
| `DFH_01_PRODUCT_AND_BUSINESS.md` | What Dylan is, BlueLine proof numbers, ICP, pricing, revenue path, tech stack, all 4 Make.com scenarios |
| `DFH_02_SYSTEM_ARCHITECTURE.md` | Technical architecture, execution order, file map, API endpoints, pitch deck spec — **⚠️ see Section 4, a real API key was found here** |
| `DFH_03_PIPELINE_LOGIC.md` | Every pipeline step — classification, branch rules, edge cases, dedup, borough detection |
| `DFH_04_COMMUNICATIONS.md` | Every SMS/email template, keyword triggers, tone guide, sequencing, compliance language |
| `DFH_05_SETUP_AND_COMMANDS.md` | Zero-to-live setup, `.env` config, cron, run commands, troubleshooting |
| `DFH_06_DAILY_OPERATIONS.md` | Your daily 15-30 min routine, what the system does vs. what you do |
| `DFH_07_CENTER_DIRECTORY.md` | All 34 centers, contacts, rates |
| `DFH_08_SALES_AND_OUTREACH.md` | LinkedIn sequence, Loom script, discovery call script, Make.com scenario specs, Carrd copy, Phantombuster setup |

**My recommendation: make the `DylanForHire/` set canonical** (it's more complete and more recently structured) and retire `Dylan_for_Hire_Master_Context.md` — or explicitly merge anything unique from it in first. This single decision removes most of the "which doc do I trust" confusion.

---

## 2. THE PRODUCT, IN ONE PLACE

**What it is:** an AI staffing automation service, built on Dylan (originally BlueLine's internal agent), sold to small US nurse staffing agencies (2–50 employees). BlueLine is the live proof of concept.

**Pricing:** $497 DIY template · **$1,500 setup + $750/month retainer (primary tier)** · Enterprise custom.

**Revenue path:** Month 1 (2 clients, $3K setup) → Month 2 ($3K/mo MRR) → Month 3 ($4.5K/mo, referrals) → Month 4+ ($5.3K/mo, 7 clients — the anchor milestone).

**Phase 1 cost/P&L (built in the file-migration session):**
- Tool stack: $132/month fixed
- Month 0 (setup): –$132 (only negative month)
- Month 1: +$2,868 (first 2 clients)
- Month 4+: +$5,868/month steady state
- Cash-flow positive from day one of actual sales; one setup fee covers 11 months of tools.

**Sales assets, current status:**
- Pitch deck (`dylan_for_hire_pitch_deck.html`): pitch-ready. Fixed a branding miss on slide 6 (was still saying "BlueLine" instead of "Dylan for Hire"). One structural suggestion still open: consider moving the BlueLine proof numbers before the mechanism explanation for a stronger arc (not done yet).
- Architecture doc (`dylan_for_hire_architecture.html`): assessed as the strongest asset in the folder — 6-stage manual-vs-AI time breakdown, hidden recruiter cost analysis ($8,910 wasted + $99K missed margin, sourced from ASHHRA/SHRM/BLS/HBR/NYS DOH/CTIA), interactive CPP calculator. **One unresolved issue:** the calculator's pricing labels ("$800/mo Starter / $1,500/mo Professional") don't cleanly match the real pricing structure ($1,500 one-time + $750/mo). Align these before the next prospect sees it.
- System-agnostic client-intake spec (`10_CLIENT_INTAKE_AND_ADAPTER_SPEC.md`): built to make Dylan sellable beyond BlueLine — covers platform selection (SMS/email/ATS/lead source), regulatory scope (state/license/credential rules vary — NY's aren't universal), persona/voice, volume/ops, and how each answer maps to a config-driven adapter. BlueLine's current hardcoded setup is mapped as what "client #1's" intake answers would look like.

---

## 3. PRODUCT CLAIMS THAT WERE CORRECTED (don't let these regress)

- **"11-point document audit"** — accurate only as **8 required + 3 recommended = 11 tracked categories**. Hepatitis B and flu vaccine were added as *recommended, not mandatory* (both accept a signed declination as a valid compliance path — the system can't yet tell "unvaccinated, non-compliant" from "unvaccinated, validly declined," so making either blocking would wrongly flag compliant candidates). **Never say "11-point" again without the 8/3 split in the same breath** — this was flagged hard in four places specifically because it's dangerously close to a claim that already had to be corrected twice.
- The customer-facing product overview doc was **deliberately left unchanged** pending real-world verification — send a real flu-declination form and Hep B card through the actual pipeline, confirm Claude Vision extracts both correctly and the email shows them as non-blocking notes, *then* update that doc. Don't update it on the strength of the code change alone.

---

## 4. SECURITY — HANDLE BEFORE ANYTHING ELSE PRODUCT-SIDE

**A real ElevenLabs API key was committed in plaintext** into `DFH_02_SYSTEM_ARCHITECTURE.md` (line 398, git commit `3e936f5`). The working file has been redacted, but the key is still recoverable from git history. Two options, your call: rotate the key on ElevenLabs (simpler, recommended) or do a destructive git history rewrite. **Neither has been done yet** — do this before sharing this repo or doc set with anyone else.

---

## 5. THE ONE THING THIS SESSION CAN'T DO ALONE

A prior Dylan session tried to physically move BlueLine-specific code out of this project into its own space and hit a wall: *"I have no way to switch to or write into a separate 'BlueLine' Cowork project from this session — that's a UI action on your end."* That's exactly what you're doing now by creating the two sessions. Once "BlueLine" exists as its own session, point it at `~/Downloads/BlueLine/` (the real files already live there) rather than recreating anything.

**Dependency to remember:** every proof number in the Dylan pitch deck (37 nurses, payroll, billing, response times) comes from BlueLine's real, live data. If BlueLine's numbers change materially, the pitch deck needs a refresh — this session should periodically ask the BlueLine session for current stats rather than assuming the deck's numbers stay accurate indefinitely.

---

## 6. OUTSTANDING TASKS (not yet started as of this recap)

- Reconcile the two doc sets (Section 1) — decide canonical, retire the other.
- Rotate the ElevenLabs key or rewrite git history (Section 4).
- Align the CPP calculator's pricing labels with the real pricing structure (Section 2).
- Verify Hep B / flu vaccine doc extraction against a real submitted document before updating the customer-facing overview (Section 3).
- Consider reordering the pitch deck to lead with BlueLine proof before mechanism (Section 2, minor/optional).
