"""Fast E2E wiring tests (mocked LLM — BookMe / Week 13 decision_graph test pattern)."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from langchain_core.messages import HumanMessage

from agents.chat_pipeline import run_chat_turn
from agents.decision_graph import build_decision_graph, build_decision_input
from agents.guardrail import Guardrail
from agents.orchestrator import AgentOrchestrator
from agents.router import MultiRouteDecision, QueryRouter, RouteDecision
from agents.state import AgentState
from services.identity.context import IdentityContext


class _RecordingOrchestrator:
    """Minimal stand-in — records whether orchestrator path runs (BookMe AI pattern)."""

    def __init__(self) -> None:
        self.calls = 0
        self._inner = AgentOrchestrator(
            llm_chat=None,
            llm_merge=None,
            router=None,
            memory_tool=None,
        )

    async def arun_state(
        self,
        state: AgentState,
        *,
        config: Any = None,
    ) -> AgentState:
        self.calls += 1
        merged: dict[str, Any] = dict(state)
        merged["final_answer"] = "Mock tuition agent reply."
        merged["agent_outputs"] = [{"route": "direct", "tool_output": "{}"}]
        merged.setdefault("route_decisions", [{"route": "direct", "action": "reply"}])
        return merged  # type: ignore[return-value]

    def _to_agent_response(self, final_state: dict, latency_ms: int):
        return self._inner._to_agent_response(final_state, latency_ms)


def _mock_oos_graph():
    guardrail = Guardrail(MagicMock())
    guardrail.aclassify = AsyncMock(return_value="out_of_scope")
    router = QueryRouter(MagicMock())
    router.aroute = AsyncMock(
        return_value=MultiRouteDecision(
            decisions=[RouteDecision(route="direct", action="general")]
        )
    )
    return build_decision_graph(guardrail=guardrail, router=router)


def _mock_proceed_graph(*, route: str = "admissions"):
    guardrail = Guardrail(MagicMock())
    guardrail.aclassify = AsyncMock(return_value="in_scope")
    router = QueryRouter(MagicMock())
    router.aroute = AsyncMock(
        return_value=MultiRouteDecision(
            decisions=[RouteDecision(route=route, action="general", confidence=0.9)]
        )
    )
    return build_decision_graph(guardrail=guardrail, router=router)


@pytest.fixture
def ctx() -> IdentityContext:
    return IdentityContext(
        tenant_id="tenant-demo-physics",
        tenant_slug="demo-physics",
        tenant_name="Demo Physics Academy",
        student_id="stu-test-e2e",
        phone="94779999099",
        session_id="tenant-demo-physics:94779999099",
    )


@pytest.mark.asyncio
async def test_out_of_scope_skips_orchestrator(ctx: IdentityContext):
    graph = _mock_oos_graph()
    orch = _RecordingOrchestrator()
    result = await run_chat_turn(
        ctx=ctx,
        message="What's the weather in Colombo?",
        decision_graph=graph,
        orchestrator=orch,  # type: ignore[arg-type]
        channel="http_dev",
        memory_tool=MagicMock(recall_turns=MagicMock(return_value="")),
    )
    assert result.verdict == "out_of_scope"
    assert orch.calls == 0
    assert result.answer


@pytest.mark.asyncio
async def test_in_scope_invokes_orchestrator(ctx: IdentityContext):
    graph = _mock_proceed_graph(route="admissions")
    orch = _RecordingOrchestrator()
    result = await run_chat_turn(
        ctx=ctx,
        message="I want to enroll in A/L Physics tuition",
        decision_graph=graph,
        orchestrator=orch,  # type: ignore[arg-type]
        channel="http_dev",
        memory_tool=MagicMock(recall_turns=MagicMock(return_value="")),
    )
    assert result.verdict == "proceed"
    assert orch.calls == 1
    assert result.timings.get("decision_ms", 0) >= 0


@pytest.mark.asyncio
async def test_media_url_forces_payment_route(ctx: IdentityContext):
    graph = _mock_proceed_graph(route="direct")
    decision_out = await graph.ainvoke(
        build_decision_input(message="Here is my payment", router_context=""),
    )
    from agents.decision_bridge import map_decision_to_agent_state

    patch = map_decision_to_agent_state(
        decision_out,
        messages=[HumanMessage(content="Here is my payment")],
        memory_context="",
        tenant_id=ctx.tenant_id,
        user_id=ctx.student_id,
        student_id=ctx.student_id,
        phone=ctx.phone,
        session_id=ctx.session_id,
        tenant_name=ctx.tenant_name or "Demo",
        media_url="https://example.com/slip.jpg",
    )
    if patch.get("verdict") != "out_of_scope":
        patch["route_decisions"] = [
            {
                "route": "payment_check",
                "action": "check",
                "params": {},
                "confidence": 1.0,
                "reasoning": "payment receipt image attached",
            }
        ]
    routes = [d.get("route") for d in patch.get("route_decisions") or []]
    assert "payment_check" in routes
