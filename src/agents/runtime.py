"""Lazy-init agent stack (decision graph + orchestrator) for ChatPipeline."""

from __future__ import annotations

from typing import Any

from loguru import logger

from infrastructure.config import ALLOW_INPROCESS_TOOLS

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
            try:
                from agents.orchestrator import build_agent_mcp

                _orchestrator = await build_agent_mcp()
                logger.info("Orchestrator ready (MCP subprocesses)")
            except Exception as exc:
                if not ALLOW_INPROCESS_TOOLS:
                    raise RuntimeError(
                        "MCP orchestrator failed and ALLOW_INPROCESS_TOOLS=false. "
                        "Fix MCP setup or set ALLOW_INPROCESS_TOOLS=true for local dev."
                    ) from exc
                logger.warning(
                    "MCP orchestrator unavailable ({}); falling back to in-process tools. "
                    "Install langchain-mcp-adapters on Python 3.10+ or set AGENT_USE_MCP=false.",
                    exc,
                )
                from agents.orchestrator import build_orchestrator

                _orchestrator = build_orchestrator()
                logger.info("Orchestrator ready (direct tool fallback)")
        else:
            from agents.orchestrator import build_orchestrator

            _orchestrator = build_orchestrator()
            logger.info("Orchestrator ready (direct MemoryTool)")
    return _orchestrator
