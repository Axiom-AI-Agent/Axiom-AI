#!/usr/bin/env python3
"""Phase 6 perf smoke — 10 concurrent ChatPipeline turns (unique sessions).

Uses in-process pipeline (no Twilio). Adapted from ``scripts/smoke_st_memory.py``.
"""

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

TENANT_ID = "tenant-demo-physics"
CONCURRENCY = 10


async def _one_turn(idx: int) -> tuple[int, str, float]:
    from domain.enums import ChatChannel
    from services.identity.resolver import build_session_id, normalize_phone
    from services.messaging.pipeline import ChatPipeline
    from services.messaging.schemas import InboundMessage

    phone = f"9477088{idx:04d}"
    session_id = build_session_id(TENANT_ID, normalize_phone(phone))
    pipeline = ChatPipeline()
    started = time.perf_counter()
    result = await pipeline.aprocess_message(
        InboundMessage(
            channel=ChatChannel.HTTP_DEV,
            tenant_id=TENANT_ID,
            phone=phone,
            body=f"Hello from concurrent worker {idx}",
        )
    )
    elapsed_ms = (time.perf_counter() - started) * 1000
    return idx, session_id, elapsed_ms


async def main() -> int:
    if not os.getenv("OPENAI_API_KEY"):
        print("SKIP: OPENAI_API_KEY not set")
        return 0
    if not (os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_KEY")):
        print("SKIP: SUPABASE_URL / SUPABASE_SERVICE_KEY not set")
        return 0

    from agents.runtime import configure_agent_runtime

    configure_agent_runtime(use_mcp=os.getenv("AGENT_USE_MCP", "false").lower() == "true")

    print(f"=== Concurrent chat smoke ({CONCURRENCY} workers) ===")
    results = await asyncio.gather(*[_one_turn(i) for i in range(CONCURRENCY)])

    session_ids = {r[1] for r in results}
    latencies = [r[2] for r in results]
    p95 = sorted(latencies)[int(len(latencies) * 0.95) - 1]

    print(f"Sessions: {len(session_ids)} unique (expected {CONCURRENCY})")
    print(f"Latency ms — min={min(latencies):.0f} p95={p95:.0f} max={max(latencies):.0f}")

    if len(session_ids) != CONCURRENCY:
        print("FAIL: session id collision")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
