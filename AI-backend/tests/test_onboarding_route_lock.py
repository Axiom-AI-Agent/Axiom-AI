"""Onboarding route lock tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from langchain_core.messages import HumanMessage

from agents.chat_pipeline import run_chat_turn
from agents.router import MultiRouteDecision, RouteDecision
from services.admissions.onboarding_session_store import get_onboarding_session_store
from services.identity.context import IdentityContext


@pytest.fixture(autouse=True)
def clear_onboarding_sessions():
    store = get_onboarding_session_store()
    store._sessions.clear()
    yield
    store._sessions.clear()


@pytest.fixture
def ctx() -> IdentityContext:
    return IdentityContext(
        tenant_id="tenant-demo-physics",
        tenant_slug="demo-physics",
        tenant_name="Demo Physics Academy",
        phone="94770991234",
        session_id="tenant-demo-physics:94770991234",
        student_exists=False,
    )


@pytest.mark.asyncio
async def test_active_onboarding_forces_admissions_route(ctx: IdentityContext):
    store = get_onboarding_session_store()
    store.start(tenant_id=ctx.tenant_id, phone=ctx.phone)

    recorded: dict = {}

    class RecordingOrchestrator:
        async def arun_state(self, patch, config=None):
            recorded["routes"] = [d.get("route") for d in patch.get("route_decisions") or []]
            return {
                "agent_outputs": [
                    {
                        "route": "admissions",
                        "answer": "Great! Which school do you attend?",
                        "tool_output": "",
                        "status": "ok",
                    }
                ],
                "route_decisions": patch.get("route_decisions"),
            }

        def _to_agent_response(self, final_state, latency_ms):
            from agents.orchestrator import AgentResponse

            return AgentResponse(
                answer="Great! Which school do you attend?",
                route="admissions",
                routes=["admissions"],
                latency_ms=latency_ms,
            )

    decision_out = {
        "guardrail": "in_scope",
        "verdict": "proceed",
        "decision": MultiRouteDecision(
            decisions=[
                RouteDecision(
                    route="direct",
                    action="general",
                    confidence=0.9,
                    reasoning="would route direct without lock",
                )
            ]
        ),
    }
    decision_graph = MagicMock()
    decision_graph.ainvoke = AsyncMock(return_value=decision_out)

    result = await run_chat_turn(
        ctx=ctx,
        message="My name is Mirco Fernando",
        decision_graph=decision_graph,
        orchestrator=RecordingOrchestrator(),  # type: ignore[arg-type]
        memory_tool=MagicMock(recall_turns=MagicMock(return_value="")),
    )

    assert recorded["routes"] == ["admissions"]
    assert result.route == "admissions"
    assert "school" in result.answer.lower()


@pytest.mark.asyncio
async def test_onboarding_bypasses_guardrail_oos_on_confirm_yes(ctx: IdentityContext):
    store = get_onboarding_session_store()
    session = store.start(tenant_id=ctx.tenant_id, phone=ctx.phone)
    session.slots.name = "Mirco Fernando"
    session.slots.school = "St John Paul II"
    session.slots.district = "Puttlam"
    session.slots.class_id = "class-physics-al-2026"
    session.awaiting_confirmation = True
    session.next_step = "confirm"
    store.save(tenant_id=ctx.tenant_id, phone=ctx.phone, session=session)

    recorded: dict = {}

    class RecordingOrchestrator:
        async def arun_state(self, patch, config=None):
            recorded["verdict"] = patch.get("verdict")
            recorded["routes"] = [d.get("route") for d in patch.get("route_decisions") or []]
            return {
                "agent_outputs": [
                    {
                        "route": "admissions",
                        "answer": "Welcome to Demo Physics Academy! Thank you for your enrollment.",
                        "tool_output": "",
                        "status": "ok",
                    }
                ],
                "route_decisions": patch.get("route_decisions"),
            }

        def _to_agent_response(self, final_state, latency_ms):
            from agents.orchestrator import AgentResponse

            return AgentResponse(
                answer="Welcome to Demo Physics Academy! Thank you for your enrollment.",
                route="admissions",
                routes=["admissions"],
                latency_ms=latency_ms,
            )

    decision_out = {
        "guardrail": "out_of_scope",
        "verdict": "out_of_scope",
        "final_answer": "I'm here to help with tuition-related questions...",
        "decision": MultiRouteDecision(
            decisions=[
                RouteDecision(
                    route="direct",
                    action="general",
                    confidence=0.9,
                    reasoning="short reply",
                )
            ]
        ),
    }
    decision_graph = MagicMock()
    decision_graph.ainvoke = AsyncMock(return_value=decision_out)

    result = await run_chat_turn(
        ctx=ctx,
        message="YES",
        decision_graph=decision_graph,
        orchestrator=RecordingOrchestrator(),  # type: ignore[arg-type]
        memory_tool=MagicMock(recall_turns=MagicMock(return_value="")),
    )

    assert recorded.get("verdict") == "proceed"
    assert recorded["routes"] == ["admissions"]
    assert result.verdict == "proceed"
    assert "tuition-related" not in result.answer.lower()


@pytest.mark.asyncio
async def test_abusive_not_overridden_by_onboarding_lock(ctx: IdentityContext):
    store = get_onboarding_session_store()
    store.start(tenant_id=ctx.tenant_id, phone=ctx.phone)

    recorded: dict = {}

    class RecordingOrchestrator:
        async def arun_state(self, patch, config=None):
            recorded["called"] = True
            return {
                "agent_outputs": [],
                "route_decisions": patch.get("route_decisions"),
            }

        def _to_agent_response(self, final_state, latency_ms):
            from agents.orchestrator import AgentResponse

            return AgentResponse(
                answer="should not run",
                route="admissions",
                routes=["admissions"],
                latency_ms=latency_ms,
            )

    decision_out = {
        "guardrail": "flagged_abusive",
        "verdict": "flagged_abusive",
        "final_answer": "I can't help with messages that use abusive or offensive language.",
        "decision": MultiRouteDecision(
            decisions=[
                RouteDecision(
                    route="admissions",
                    action="general",
                    confidence=0.9,
                    reasoning="onboarding-looking message",
                )
            ]
        ),
    }
    decision_graph = MagicMock()
    decision_graph.ainvoke = AsyncMock(return_value=decision_out)

    result = await run_chat_turn(
        ctx=ctx,
        message="you're a stupid idiot",
        decision_graph=decision_graph,
        orchestrator=RecordingOrchestrator(),  # type: ignore[arg-type]
        memory_tool=MagicMock(recall_turns=MagicMock(return_value="")),
    )

    assert recorded.get("called") is None
    assert result.verdict == "flagged_abusive"
    assert "abusive" in result.answer.lower() or "offensive" in result.answer.lower()


@pytest.mark.asyncio
async def test_tutoring_question_breaks_onboarding_route_lock(ctx: IdentityContext):
    store = get_onboarding_session_store()
    store.start(tenant_id=ctx.tenant_id, phone=ctx.phone)

    recorded: dict = {}

    class RecordingOrchestrator:
        async def arun_state(self, patch, config=None):
            recorded["routes"] = [d.get("route") for d in patch.get("route_decisions") or []]
            return {
                "agent_outputs": [
                    {
                        "route": "resource",
                        "answer": "Past papers and tutor notes are available to enrolled students only.",
                        "tool_output": "",
                        "status": "ok",
                    }
                ],
                "route_decisions": patch.get("route_decisions"),
            }

        def _to_agent_response(self, final_state, latency_ms):
            from agents.orchestrator import AgentResponse

            return AgentResponse(
                answer="Past papers and tutor notes are available to enrolled students only.",
                route="resource",
                routes=["resource"],
                latency_ms=latency_ms,
            )

    decision_out = {
        "guardrail": "in_scope",
        "verdict": "proceed",
        "decision": MultiRouteDecision(
            decisions=[
                RouteDecision(
                    route="resource",
                    action="search",
                    confidence=0.95,
                    reasoning="tutoring question",
                )
            ]
        ),
    }
    decision_graph = MagicMock()
    decision_graph.ainvoke = AsyncMock(return_value=decision_out)

    result = await run_chat_turn(
        ctx=ctx,
        message="Explain velocity from the tutor notes",
        decision_graph=decision_graph,
        orchestrator=RecordingOrchestrator(),  # type: ignore[arg-type]
        memory_tool=MagicMock(recall_turns=MagicMock(return_value="")),
    )

    assert recorded["routes"] == ["resource"]
    assert result.route == "resource"
    assert store.get(tenant_id=ctx.tenant_id, phone=ctx.phone) is None


def test_router_routes_class_availability_to_admissions():
    from agents.router import heuristic_route

    decision = heuristic_route("what are the classes that are available currently")
    assert decision is not None
    assert decision.primary.route == "admissions"
    assert decision.primary.action == "search"
