"""
Memory MCP Server — exposes ST recall / add_turn / procedural lookup.

Adapted from Week 13 ``mcp_servers/memory_server.py`` for tenant-scoped Axiom MVP.
"""

from __future__ import annotations

import os
import sys

_SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from dotenv import load_dotenv

load_dotenv()

from loguru import logger
from mcp.server.fastmcp import FastMCP

from agents.tools.memory_tool import MemoryTool

mcp = FastMCP("axiom-memory")
_tool: MemoryTool | None = None


def _init() -> MemoryTool:
    global _tool
    if _tool is None:
        logger.info("Initialising memory MCP server...")
        _tool = MemoryTool()
    return _tool


@mcp.tool()
def recall_turns(
    tenant_id: str,
    session_id: str,
    user_id: str,
    limit: int = 10,
) -> str:
    """Fetch recent conversation turns for a tenant session."""
    return _init().recall_turns(
        tenant_id=tenant_id,
        session_id=session_id,
        user_id=user_id,
        limit=limit,
    )


@mcp.tool()
def add_turn(
    tenant_id: str,
    session_id: str,
    user_id: str,
    role: str,
    content: str,
) -> str:
    """Append a conversation turn to short-term memory."""
    return _init().add_turn(
        tenant_id=tenant_id,
        session_id=session_id,
        user_id=user_id,
        role=role,
        content=content,
    )


@mcp.tool()
def get_procedural(tenant_id: str, name: str | None = None) -> str:
    """Lookup tenant onboarding / workflow procedures."""
    return _init().get_procedural(tenant_id=tenant_id, name=name)


if __name__ == "__main__":
    logger.info("Starting axiom-memory MCP server on stdio...")
    mcp.run()
