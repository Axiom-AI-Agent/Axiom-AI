"""TEMP DEBUG — Google OAuth only (no Drive list, no MCP).

Run:
  PYTHONPATH=src .venv/bin/python tests/debug_google_auth.py
"""

from __future__ import annotations

import os
import sys
import time
import traceback
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env", override=True)
sys.path.insert(0, str(ROOT / "src"))


def main() -> int:
    path = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    print("Authentication started...")
    print(f"GOOGLE_SERVICE_ACCOUNT_JSON exists: {bool(path and Path(path).is_file())}")
    if not path or not Path(path).is_file():
        print("ERROR: service account JSON path missing or file not found")
        return 1

    try:
        from google.auth.transport.requests import Request
        from google.oauth2 import service_account

        scopes = ["https://www.googleapis.com/auth/drive.readonly"]
        t0 = time.perf_counter()
        creds = service_account.Credentials.from_service_account_file(path, scopes=scopes)
        creds.refresh(Request())
        elapsed = time.perf_counter() - t0
        print(f"Authentication completed in {elapsed:.2f} seconds")
        print(f"Token valid: {bool(creds.token) and creds.valid}")
        print(f"Token expiry: {creds.expiry}")
        return 0
    except Exception:
        print("Authentication FAILED")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
