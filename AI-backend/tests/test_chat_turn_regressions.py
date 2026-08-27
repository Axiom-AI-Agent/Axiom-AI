"""Chat-turn regressions for B4 (escalation confirmation) and B5 (bare links)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from agents.chat_pipeline import run_chat_turn
from agents.escalation_confirmation import (
    CONFIRMATION_TEXT,
    classify_confirmation,
    get_pending_low_confidence_question,
)
from agents.router import MultiRouteDecision, RouteDecision
from services.identity.context import IdentityContext
from services.language import t


@pytest.fixture
def ctx() -> IdentityContext:
    return IdentityContext(
        tenant_id="tenant-demo-physics",
        tenant_slug="demo-physics",
        tenant_name="Demo Physics Academy",
        phone="94770991234",
        session_id="tenant-demo-physics:94770991234",
        student_exists=True,
        is_enrolled=True,
    )


class _RecordingOrchestrator:
    def __init__(self, answer: str = "Sent to your tutor.") -> None:
        self.answer = answer
        self.patch: dict | None = None

    async def arun_state(self, patch, config=None):
        self.patch = patch
        return {"agent_outputs": [], "route_decisions": patch.get("route_decisions")}

    def _to_agent_response(self, final_state, latency_ms):
        from agents.orchestrator import AgentResponse

        routes = [d.get("route", "direct") for d in final_state.get("route_decisions") or []]
        return AgentResponse(
            answer=self.answer,
            route=routes[0] if routes else "direct",
            routes=routes or ["direct"],
            latency_ms=latency_ms,
        )


def _decision_graph(route: str = "direct") -> MagicMock:
    graph = MagicMock()
    graph.ainvoke = AsyncMock(
        return_value={
            "guardrail": "in_scope",
            "verdict": "proceed",
            "decision": MultiRouteDecision(
                decisions=[RouteDecision(route=route, action="general", confidence=0.9)]
            ),
        }
    )
    return graph


# ── B4: the "Yes" that escalates must match the question that was asked ─────
def test_b4_the_agents_own_question_is_recognised_as_the_escalation_prompt():
    """The asked question and the matcher used to differ by one word."""
    asked = t("rag_low_confidence_ask", "en")
    assert CONFIRMATION_TEXT in asked

    memory = MagicMock()
    memory.recent_pairs.return_value = [("What is terminal velocity", asked)]

    pending = get_pending_low_confidence_question(
        memory_tool=memory,
        tenant_id="tenant-demo-physics",
        user_id="94770991234",
        session_id="tenant-demo-physics:94770991234",
    )
    assert pending == "What is terminal velocity"


@pytest.mark.parametrize("reply", ["Yes", "yes please", "sure", "go ahead", "ඔව්"])
def test_b4_affirmative_replies_are_recognised(reply: str):
    assert classify_confirmation(reply) == "yes"


@pytest.mark.parametrize("reply", ["No", "no thanks", "nevermind", "නෑ"])
def test_b4_negative_replies_are_recognised(reply: str):
    assert classify_confirmation(reply) == "no"


@pytest.mark.asyncio
async def test_b4_yes_routes_to_escalation_not_the_enrollment_flow(ctx: IdentityContext):
    memory = MagicMock()
    memory.recall_turns.return_value = ""
    memory.recent_pairs.return_value = [
        ("What is terminal velocity", t("rag_low_confidence_ask", "en"))
    ]
    orchestrator = _RecordingOrchestrator()

    result = await run_chat_turn(
        ctx=ctx,
        message="Yes",
        decision_graph=_decision_graph(),
        orchestrator=orchestrator,  # type: ignore[arg-type]
        memory_tool=memory,
    )

    assert result.routes == ["escalation"]
    assert orchestrator.patch is not None
    assert orchestrator.patch["pending_escalation_message"] == "What is terminal velocity"
    assert "payment slip" not in result.answer.lower()


# ── B5: a pasted link is answered as a link, not as a payment slip ──────────
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "message",
    [
        "https://docs.google.com/document/d/abc123/edit",
        "www.example.com/notes",
    ],
)
async def test_b5_bare_link_does_not_trigger_payment_verification(
    ctx: IdentityContext, message: str
):
    memory = MagicMock()
    memory.recall_turns.return_value = ""
    memory.recent_pairs.return_value = []
    orchestrator = _RecordingOrchestrator(answer="should not be reached")

    result = await run_chat_turn(
        ctx=ctx,
        message=message,
        decision_graph=_decision_graph("payment_check"),
        orchestrator=orchestrator,  # type: ignore[arg-type]
        memory_tool=memory,
    )

    assert "bank slip" not in result.answer.lower()
    assert "can't open links" in result.answer.lower()
    assert orchestrator.patch is None


@pytest.mark.asyncio
async def test_a_question_containing_a_link_is_still_the_question(ctx: IdentityContext):
    memory = MagicMock()
    memory.recall_turns.return_value = ""
    memory.recent_pairs.return_value = []
    orchestrator = _RecordingOrchestrator(answer="Here's an explanation.")

    result = await run_chat_turn(
        ctx=ctx,
        message="can you explain velocity from https://example.com/notes",
        decision_graph=_decision_graph("resource"),
        orchestrator=orchestrator,  # type: ignore[arg-type]
        memory_tool=memory,
    )

    assert result.answer == "Here's an explanation."


# ── A5: arithmetic is answered instead of being deflected as off-topic ──────
@pytest.mark.asyncio
async def test_a5_arithmetic_is_answered_in_the_chat_turn(ctx: IdentityContext):
    memory = MagicMock()
    memory.recall_turns.return_value = ""
    memory.recent_pairs.return_value = []
    orchestrator = _RecordingOrchestrator(answer="should not be reached")

    result = await run_chat_turn(
        ctx=ctx,
        message="2+2?",
        decision_graph=_decision_graph(),
        orchestrator=orchestrator,  # type: ignore[arg-type]
        memory_tool=memory,
    )

    assert "4" in result.answer
    assert "outside what I can help with" not in result.answer.lower()
