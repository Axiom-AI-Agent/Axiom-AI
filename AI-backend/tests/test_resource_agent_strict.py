"""Resource agent — in-process tools blocked when ALLOW_INPROCESS_TOOLS=false."""

from __future__ import annotations

import pytest
from langchain_core.messages import HumanMessage

from agents.nodes.resource_agent import run_resource_agent


@pytest.mark.asyncio
async def test_run_resource_agent_requires_mcp_clients_when_fallback_disabled(monkeypatch):
    monkeypatch.setattr("infrastructure.config.ALLOW_INPROCESS_TOOLS", False)
    state = {
        "tenant_id": "tenant-demo-physics",
        "messages": [HumanMessage(content="past paper")],
    }
    with pytest.raises(RuntimeError, match="MCP drive client required"):
        await run_resource_agent(state, drive=None, rag=None)
