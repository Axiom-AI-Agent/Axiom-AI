#!/usr/bin/env python3
"""Clear stale st_turns for demo dev-chat sessions."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env", override=True)

from infrastructure.db.supabase_client import get_supabase_client
from services.identity.resolver import build_session_id, normalize_phone

DEMO_SESSIONS: tuple[tuple[str, str], ...] = (
    ("tenant-demo-physics", "94771234567"),
    ("tenant-demo-chemistry", "94779876543"),
)


def main() -> int:
    client = get_supabase_client()
    total = 0

    print("=== Clear demo session memory (st_turns) ===")
    for tenant_id, phone in DEMO_SESSIONS:
        session_id = build_session_id(tenant_id, normalize_phone(phone))
        response = (
            client.table("st_turns")
            .delete()
            .eq("tenant_id", tenant_id)
            .eq("session_id", session_id)
            .execute()
        )
        deleted = len(response.data or [])
        total += deleted
        print(f"  {session_id}: removed {deleted} turn(s)")

    print(f"Done: {total} row(s) deleted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
