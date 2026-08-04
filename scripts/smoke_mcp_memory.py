#!/usr/bin/env python3
"""Live E2E: MCP memory_server recall_turns / add_turn via build_agent_mcp()."""

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

from agents.tools.memory_tool import MemoryTool

TENANT_ID = "tenant-demo-physics"
USER_ID = "stu-physics-001"
SESSION_ID = f"{TENANT_ID}:mcp-smoke-{int(time.time())}"


def _seed_memory() -> MemoryTool:
    memory = MemoryTool()
    memory.add_turn(
        tenant_id=TENANT_ID,
        session_id=SESSION_ID,
        user_id=USER_ID,
        role="user",
        content="MCP smoke marker: secret word is nebula",
    )
    memory.add_turn(
        tenant_id=TENANT_ID,
        session_id=SESSION_ID,
        user_id=USER_ID,
        role="assistant",
        content="Got it — I'll remember nebula for this session.",
    )
    return memory


async def _run_mcp_adapter_path() -> int:
    from agents.orchestrator import build_agent_mcp

    _seed_memory()
    orchestrator = await build_agent_mcp()
    adapter = orchestrator.mcp_memory
    if adapter is None:
        print("FAIL: orchestrator has no MCP memory adapter")
        return 1

    recalled = await adapter.recall_turns(
        tenant_id=TENANT_ID,
        session_id=SESSION_ID,
        user_id=USER_ID,
        limit=10,
    )
    tool_names = sorted(getattr(orchestrator, "mcp_tools", {}).keys())
    print("MCP tools loaded:", tool_names)
    print("MCP recall snippet:", recalled[:200])

    expected_tools = {"recall_turns", "add_turn", "get_procedural"}
    tools_ok = expected_tools.issubset(set(tool_names))
    recall_ok = "nebula" in recalled.lower()
    return 0 if tools_ok and recall_ok else 1


def _run_memory_tool_fallback() -> int:
    """Same business logic memory_server exposes — valid when Python < 3.10."""
    memory = _seed_memory()
    recalled = memory.recall_turns(
        tenant_id=TENANT_ID,
        session_id=SESSION_ID,
        user_id=USER_ID,
        limit=10,
    )
    print("MemoryTool recall snippet:", recalled[:200])
    return 0 if "nebula" in recalled.lower() else 1


async def main() -> int:
    if not (os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_KEY")):
        print("SKIP: SUPABASE_URL / SUPABASE_SERVICE_KEY not set")
        return 0

    print("=== Phase 2 MCP memory E2E ===")
    print(f"Session: {SESSION_ID}")

    if sys.version_info < (3, 10):
        print(
            f"SKIP MCP adapter path: langchain-mcp-adapters needs Python 3.10+ "
            f"(running {sys.version_info.major}.{sys.version_info.minor})"
        )
        if _run_memory_tool_fallback() == 0:
            print("OK fallback: MemoryTool recall (memory_server uses same code)")
            print("PASS (fallback)")
            return 0
        print("FAIL fallback: MemoryTool recall")
        return 1

    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient  # noqa: F401
    except ImportError:
        print("SKIP MCP adapter path: langchain-mcp-adapters not installed")
        if _run_memory_tool_fallback() == 0:
            print("OK fallback: MemoryTool recall")
            print("PASS (fallback)")
            return 0
        return 1

    if await _run_mcp_adapter_path() == 0:
        print("OK MCP tools: recall_turns, add_turn, get_procedural")
        print("OK MCP recall_turns returned seeded turn")
        print("PASS")
        return 0

    print("FAIL MCP adapter path")
    return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
