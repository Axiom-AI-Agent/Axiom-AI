"""Runtime MCP fallback tests."""

from __future__ import annotations

import pytest

from agents.runtime import configure_agent_runtime, get_orchestrator, reset_agent_runtime


@pytest.mark.asyncio
async def test_orchestrator_falls_back_when_mcp_unavailable(monkeypatch):
    reset_agent_runtime()
    configure_agent_runtime(use_mcp=True)
    monkeypatch.setattr("agents.runtime.ALLOW_INPROCESS_TOOLS", True)

    async def _fail_mcp(**kwargs):
        raise ImportError("No module named 'langchain_mcp_adapters'")

    monkeypatch.setattr("agents.orchestrator.build_agent_mcp", _fail_mcp)
    orch = await get_orchestrator()
    assert orch is not None
    assert orch.mcp_drive is None or orch.mcp_rag is None


@pytest.mark.asyncio
async def test_orchestrator_raises_when_mcp_unavailable_and_no_fallback(monkeypatch):
    reset_agent_runtime()
    configure_agent_runtime(use_mcp=True)
    monkeypatch.setattr("agents.runtime.ALLOW_INPROCESS_TOOLS", False)

    async def _fail_mcp(**kwargs):
        raise ImportError("No module named 'langchain_mcp_adapters'")

    monkeypatch.setattr("agents.orchestrator.build_agent_mcp", _fail_mcp)
    with pytest.raises(RuntimeError, match="ALLOW_INPROCESS_TOOLS=false"):
        await get_orchestrator()
