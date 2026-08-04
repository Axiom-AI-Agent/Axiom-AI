"""LangChain tools backed by MemoryTool — same surface as memory_server MCP."""

from __future__ import annotations

import os

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from agents.tools.memory_tool import MemoryTool
from mcp_servers.mcp_config import MCP_SERVERS, PHASE2_MCP_SERVERS

_memory_tool = MemoryTool()
_mcp_tools_cache: list[StructuredTool] | None = None


class RecallTurnsInput(BaseModel):
    tenant_id: str = Field(description="Tenant scope")
    session_id: str = Field(description="Conversation session key")
    limit: int = Field(default=10, description="Max turns to recall")


class AddTurnInput(BaseModel):
    tenant_id: str
    session_id: str
    user_id: str
    role: str
    content: str


class GetProceduralInput(BaseModel):
    tenant_id: str
    name: str | None = None


def _build_inprocess_tools() -> list[StructuredTool]:
    return [
        StructuredTool.from_function(
            name="recall_turns",
            description="Recall recent short-term conversation turns for a session.",
            func=lambda tenant_id, session_id, limit=10: _memory_tool.recall_turns(
                tenant_id=tenant_id,
                session_id=session_id,
                limit=limit,
            ),
            args_schema=RecallTurnsInput,
        ),
        StructuredTool.from_function(
            name="add_turn",
            description="Append a turn to short-term memory.",
            func=lambda tenant_id, session_id, user_id, role, content: _memory_tool.add_turn(
                tenant_id=tenant_id,
                session_id=session_id,
                user_id=user_id,
                role=role,
                content=content,
            ),
            args_schema=AddTurnInput,
        ),
        StructuredTool.from_function(
            name="get_procedural",
            description="Fetch procedural workflow definitions for a tenant.",
            func=lambda tenant_id, name=None: _memory_tool.get_procedural(
                tenant_id=tenant_id,
                name=name,
            ),
            args_schema=GetProceduralInput,
        ),
    ]


async def _load_mcp_subprocess_tools() -> list[StructuredTool]:
    from langchain_mcp_adapters.client import MultiServerMCPClient

    client = MultiServerMCPClient(
        {name: MCP_SERVERS[name] for name in PHASE2_MCP_SERVERS}
    )
    return await client.get_tools()


def build_agent_mcp(*, prefer_subprocess: bool | None = None) -> list[StructuredTool]:
    """Return memory MCP tools for the orchestrator."""
    global _mcp_tools_cache

    use_subprocess = prefer_subprocess
    if use_subprocess is None:
        use_subprocess = os.getenv("MCP_USE_SUBPROCESS", "false").lower() == "true"

    if not use_subprocess:
        return _build_inprocess_tools()

    if _mcp_tools_cache is not None:
        return _mcp_tools_cache

    import asyncio

    _mcp_tools_cache = asyncio.run(_load_mcp_subprocess_tools())
    return _mcp_tools_cache


def get_memory_tool() -> MemoryTool:
    """Direct access for orchestrator recall (same logic as MCP server)."""
    return _memory_tool
