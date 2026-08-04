"""Lazy-init agent stack (decision graph + orchestrator) for ChatPipeline."""

from __future__ import annotations

from typing import Any

from loguru import logger

_decision_graph: Any | None = None
_orchestrator: Any | None = None
_use_mcp: bool = False


def configure_agent_runtime(*, use_mcp: bool = False) -> None:
    global _use_mcp
    _use_mcp = use_mcp
    reset_agent_runtime()


def reset_agent_runtime() -> None:
    global _decision_graph, _orchestrator
    _decision_graph = None
    _orchestrator = None


def get_decision_graph():
    global _decision_graph
    if _decision_graph is None:
        from agents.decision_graph import build_decision_graph

        _decision_graph = build_decision_graph()
        logger.info("Decision graph compiled")
    return _decision_graph


async def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        if _use_mcp:
            from agents.orchestrator import build_agent_mcp

            _orchestrator = await build_agent_mcp()
            logger.info("Orchestrator ready (MCP memory)")
        else:
            from agents.orchestrator import build_orchestrator

            _orchestrator = build_orchestrator()
            logger.info("Orchestrator ready (direct MemoryTool)")
    return _orchestrator
