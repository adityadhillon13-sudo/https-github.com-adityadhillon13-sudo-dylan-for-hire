"""
BlueLine Staffing — Master Gmail OAuth Setup
=============================================
Run this ONCE before using the master agent.
Opens a browser to authorise access to info@bluelinestaffing.com.

Usage:
  python3.11 master_gmail_setup.py

You need gmail_credentials.json in ~/Downloads/ first.
Instructions printed below if it is missing.
"""

import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES           = ["https://www.googleapis.com/auth/gmail.modify"]
TOKEN_PATH       = os.path.expanduser("~/Downloads/gmail_token.json")
CREDENTIALS_PATH = os.path.expanduser("~/Downloads/gmail_credentials.json")

SETUP_INSTRUCTIONS = """
=============================================================
HOW TO GET gmail_credentials.json (one-time setup)
=============================================================
1. Go to: https://console.cloud.google.com/
2. Create a new project (or select an existing one)
3. APIs & Services → Enable APIs → search "Gmail API" → Enable
4. APIs & Services → Credentials
5. Click "Create Credentials" → "OAuth 2.0 Client IDs"
6. Application type: Desktop app
7. Click Download JSON
8. Rename the file to: gmail_credentials.json
9. Move it to: ~/Downloads/gmail_credentials.json
10. Run this script again
=============================================================
"""

def main():
    if not os.path.exists(CREDENTIALS_PATH):
        print(f"ERROR: {CREDENTIALS_PATH} not found.")
        print(SETUP_INSTRUCTIONS)
        exit(1)

    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            print("Token refreshed successfully.")
        else:
            flow  = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
            print("Authorisation successful!")
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
        print(f"Token saved to: {TOKEN_PATH}")
    else:
        print("Already authorised — token is valid.")

    print("\nSetup complete. You can now run master_daily_agent.py")


# [FIX 2026-07-02, Round 6 audit] This script used to run its OAuth setup flow
# as bare top-level module code, which meant simply `import master_gmail_setup`
# (e.g. from a test suite checking TOKEN_PATH/CREDENTIALS_PATH consistency
# against the other files that use them) would launch a real OAuth flow or
# sys.exit(1) if gmail_credentials.json wasn't present — an untestable,
# side-effecting module. Wrapped in main() + guard so importing this file is
# now safe and inert; `python3.11 master_gmail_setup.py` behaves identically
# to before. See DYLAN_AUDIT_2026-07-01_FULL.md Round 6.
if __name__ == "__main__":
    main()
