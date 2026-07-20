"""
Test bootstrap for the Dylan for Hire pipeline test suite.

Sets dummy environment variables BEFORE any src/ module is imported (several
modules read os.environ[...] directly at import time and will raise KeyError
without this), and adds src/ to sys.path so tests can `import master_daily_agent`
etc. the same way the real scripts do on Aditya's Mac.

These are fake credentials for logic-level testing only. No network call in
this suite is allowed to actually reach api.openphone.com, Gmail, or the
Claude API — every test that exercises a function which would make a real
call either mocks that call out or is testing a pure function that doesn't
make one. See DYLAN_AUDIT_2026-07-01_FULL.md Round 6 for what this suite
does and does not prove.
"""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

# Dummy creds — required so module-level `os.environ["QUO_API_KEY"]` etc.
# in master_daily_agent.py don't raise KeyError on import. NEVER real keys.
os.environ.setdefault("QUO_API_KEY", "test-fake-quo-key")
os.environ.setdefault("QUO_PHONE_NUMBER_ID", "test-fake-phone-id")
os.environ.setdefault("CLAUDE_API_KEY", "test-fake-claude-key")
os.environ.setdefault("GCP_PROJECT_ID", "test-fake-gcp-project")
