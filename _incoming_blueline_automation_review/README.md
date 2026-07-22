# BlueLine Automation — Recruitment & Sourcing Pipeline Systems
==============================================================
**Version 1.0** | *Production-Ready Client-Specific Deployment*

This directory contains the custom-built, high-efficiency Python automation suite designed specifically for **BlueLine Staffing**. It streamlines candidate matching, resolves facility-name variations, and builds a robust local pipeline cache without hitting OpenPhone API rate limits or incurring artificial delays.

---

## 📂 System Architecture & Files

The suite is comprised of five highly focused, modular scripts designed to run on your local Mac under `~/Downloads/BlueLine/`.

### 1. Central API Helper (`blueline_quo_helpers.py`)
- **What it does**: Serves as the single, centralized gateway for all communication with the OpenPhone (Quo) API (`/contacts`, `/conversations`, and `/messages`).
- **Why it is critical**: It completely resolves previous production bugs (such as the 400 Bad Request error caused by a missing `phoneNumberId` parameter). It incorporates built-in retry logic (up to 3 attempts), handles API rate limiting (`429`), and implements automatic pagination for infinite list loads.
- **Dependency**: Free of heavy, applet-wide startup checks to ensure it is lightweight and safe to import.

### 2. Location Normalizer (`blueline_center_aliases.py`)
- **What it does**: Standardizes free-form text input and candidate messages. Normalizes variations like `"New Franklin"`, `"fort tyrone"` (with typos), `"forestview rehab"`, or `"PGC"` into canonical facility names (e.g., *Franklin*, *Fort Tryon*, *Forest View*, *Palm Gardens*).
- **Why it is critical**: Candidates do not communicate using structured databases. This regex-based utility ensures exact matching by stripping extraneous noise (e.g., "rehab and nursing center") and executing lookup checks against pre-defined facility seeds, as well as dynamically loading new names added to `BLUELINE_CENTER_DIRECTORY.md`.

### 3. High-Performance Indexer (`blueline_candidate_index_builder.py`)
- **What it does**: Crawls the last 90 days of incoming candidate SMS history and active OpenPhone contacts, normalizes locations, and compiles a fast JSON index (`candidate_center_index.json`).
- **Why it is critical**: Eliminates slow, rate-limit-prone live API requests during matching. Instead of querying OpenPhone for every candidate during a lookup (which triggers `429` errors), other scripts read this pre-compiled index instantly.
- **Frequency**: Intended to be run nightly.

### 4. Direct Vacancy Matcher (`blueline_vacancy_matcher.py`)
- **What it does**: Queries the local JSON index to retrieve candidates matching a specific facility and license type (RN, LPN, CNA), sorted by paperwork readiness.
- **Why it is critical**: Instantly finds who is ready to work. Running it with the `--draft` flag generates ready-to-use SMS outreach messages and appends them directly to `vacancy_outreach_drafts.txt` for fast copy-pasting.

### 5. Sales & Biz Dev Pipeline Tracker (`blueline_pipeline_depth.py`)
- **What it does**: Provides quick, reliable metrics on candidate depth (e.g., *"How many LPNs do we have who want to work at Split Rock?"*).
- **Why it is critical**: Gives your business development team real, immediate numbers of eligible candidates to close deals with new facilities during sales calls.

---

## ⚙️ Environment & Requirements

### 1. Python Environment
The scripts are optimized to run with **Python 3.11** or higher.
Ensure you have the required `requests` and `python-dotenv` libraries installed:
```bash
pip install requests python-dotenv
```

### 2. Secrets & Configuration (`.env`)
The suite reads configuration settings from your local environment file located at `~/Downloads/.env`. Verify that this file contains your active credentials:
```env
QUO_API_KEY="Bearer your_openphone_api_key_here"
QUO_PHONE_NUMBER_ID="your_phone_number_id_here"
```

---

## 🚀 How to Run the Scripts

Always change your working directory to the BlueLine folder on your Mac before executing:
```bash
cd ~/Downloads/BlueLine
```

### A. Compile/Build the Candidate Index (Perform Nightly)
Before executing search queries or sales lookups, ensure your local database is up to date:
```bash
python3.11 blueline_candidate_index_builder.py
```
*This generates or updates `candidate_center_index.json` in your local directory.*

### B. Find Candidates for a Vacancy & Auto-Draft Messages
Search for active **RNs** who want to work at **Franklin**, and automatically create SMS drafts:
```bash
python3.11 blueline_vacancy_matcher.py --center "Franklin" --license RN --draft
```
*The generated templates are appended directly to your local workspace file `vacancy_outreach_drafts.txt`.*

### C. Check Pipeline Depth for Sales/Biz Dev
Instantly check the number of candidates who mentioned availability for **Split Rock**:
```bash
python3.11 blueline_pipeline_depth.py --center "Split Rock"
```

---

## 🕒 Automated Scheduling (Nightly Cron Job)

To keep the candidate search index perfectly fresh, wire the builder script into your local system crontab.

1. Open your terminal and edit your crontab:
   ```bash
   crontab -e
   ```
2. Insert the following entry (configured to run automatically every night at 3:00 AM Eastern Time):
   ```cron
   0 3 * * * cd /Users/Aditya/Downloads/BlueLine && set -a && source ../.env && set +a && /usr/local/bin/python3.11 blueline_candidate_index_builder.py >> /Users/Aditya/Downloads/BlueLine/cron_output.log 2>&1
   ```
3. Save and close the editor. Your Mac will now rebuild the search index silently in the background each night, ensuring instantaneous lookups during the workday.
