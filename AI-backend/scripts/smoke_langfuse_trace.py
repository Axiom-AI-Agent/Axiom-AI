#!/usr/bin/env python3
"""Send one real chat turn and print the Langfuse trace id (requires valid .env keys)."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env", override=True)

from agents.chat_pipeline import run_chat_turn
from agents.runtime import configure_agent_runtime, get_decision_graph, get_orchestrator
from infrastructure.observability import flush, get_langfuse_client, is_langfuse_enabled
from services.identity.context import IdentityContext


async def main() -> None:
    configure_agent_runtime(use_mcp=False)
    client = get_langfuse_client()
    if client is None or not is_langfuse_enabled():
        print("FAIL: Langfuse not connected — check LANGFUSE_* in .env")
        sys.exit(1)

    ctx = IdentityContext(
        tenant_id="tenant-demo-physics",
        tenant_slug="demo-physics",
        tenant_name="Demo Physics Academy",
        student_id="stu-physics-001",
        phone="94771234567",
        session_id="tenant-demo-physics:94771234567",
    )

    result = await run_chat_turn(
        ctx=ctx,
        message="Hello — langfuse trace smoke test",
        decision_graph=get_decision_graph(),
        orchestrator=await get_orchestrator(),
        channel="http_dev",
    )
    flush()

    print("=== Langfuse trace smoke ===")
    print("Answer:", (result.answer or "")[:120])
    print("Route:", result.route, "| Verdict:", result.verdict)
    print("Trace ID:", result.trace_id or "(none — check @observe wiring)")
    if not result.trace_id:
        sys.exit(1)
    print("PASS — open this trace in Langfuse UI")


if __name__ == "__main__":
    asyncio.run(main())
