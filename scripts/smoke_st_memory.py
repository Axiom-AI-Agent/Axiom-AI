#!/usr/bin/env python3
"""Live E2E: short-term memory persists across two POST /chat-style turns."""

from __future__ import annotations

import asyncio
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env", override=True)

from domain.enums import ChatChannel
from services.identity.resolver import build_session_id, normalize_phone
from services.messaging.persistence import MessagePersistence
from services.messaging.pipeline import ChatPipeline
from services.messaging.schemas import InboundMessage

TENANT_ID = "tenant-demo-physics"
# Unique phone per run avoids stale turns from earlier smoke tests
SMOKE_PHONE = f"9477099{int(time.time()) % 10000:04d}"


async def main() -> int:
    if not os.getenv("OPENAI_API_KEY"):
        print("SKIP: OPENAI_API_KEY not set")
        return 0
    if not (os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_KEY")):
        print("SKIP: SUPABASE_URL / SUPABASE_SERVICE_KEY not set")
        return 0

    pipeline = ChatPipeline()
    persistence = MessagePersistence()
    session_id = build_session_id(TENANT_ID, normalize_phone(SMOKE_PHONE))

    print("=== Phase 2 ST memory E2E ===")
    print(f"Session: {session_id}")

    turn1 = InboundMessage(
        channel=ChatChannel.HTTP_DEV,
        tenant_id=TENANT_ID,
        phone=SMOKE_PHONE,
        body="I want to enroll in A/L Physics — my preferred lesson time is 4pm on weekdays.",
    )
    result1 = await pipeline.aprocess_message(turn1)
    print("Turn 1 reply:", result1.reply[:120])

    turn2 = InboundMessage(
        channel=ChatChannel.HTTP_DEV,
        tenant_id=TENANT_ID,
        phone=SMOKE_PHONE,
        body="What lesson time did I say I prefer for my A/L Physics enrollment?",
    )
    result2 = await pipeline.aprocess_message(turn2)
    print("Turn 2 reply:", result2.reply[:200])

    rows = persistence.get_turns(tenant_id=TENANT_ID, session_id=session_id, limit=20)
    user_rows = [r for r in rows if r.get("role") == "user"]
    assistant_rows = [r for r in rows if r.get("role") == "assistant"]

    print(f"st_turns rows: {len(rows)} ({len(user_rows)} user, {len(assistant_rows)} assistant)")

    memory_ok = len(rows) >= 4 and ("4pm" in result2.reply.lower() or "4 pm" in result2.reply.lower())
    persist_ok = len(user_rows) >= 2 and len(assistant_rows) >= 2

    if persist_ok:
        print("OK persistence: st_turns has both turns")
    else:
        print("FAIL persistence: expected >=2 user and >=2 assistant rows")

    if memory_ok:
        print("OK recall: turn 2 references 4pm from turn 1")
    else:
        print("FAIL recall: turn 2 did not reference 4pm from turn 1")

    if persist_ok and memory_ok:
        print("PASS")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
