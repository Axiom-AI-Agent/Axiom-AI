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
from agents.escalation_pending import remember_pending_question, reset_pending_questions
from agents.router import MultiRouteDecision, RouteDecision
from agents.tools.memory_tool import MemoryTool
from memory.st_store import ShortTermMemoryStore
from services.identity.context import IdentityContext
from services.language import t
from services.nlu import StudentIntent, classify


@pytest.fixture(autouse=True)
def _reset_escalation_pending():
    reset_pending_questions()
    yield
    reset_pending_questions()


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


@pytest.mark.parametrize("reply", ["Yes", "yes please", "sure", "go ahead", "Yup", "yup", "ඔව්"])
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


class _RecallOnlyMemory:
    """What production MemoryTool looked like before recent_pairs existed."""

    def recall_turns(self, **kwargs) -> str:
        return ""

    def recent_pairs(self, **kwargs):
        raise AttributeError("'MemoryTool' object has no attribute 'recent_pairs'")


@pytest.mark.asyncio
@pytest.mark.parametrize("reply", ["Yes", "Yup"])
async def test_b4_yes_escalates_from_in_process_pending_even_without_st(
    ctx: IdentityContext, reply: str
):
    """The live bug: RAG ask, then Yes/Yup, ST lookup throws, student is greeted."""
    memory = _RecallOnlyMemory()
    asked = t("rag_low_confidence_ask", "en")
    first = _RecordingOrchestrator(answer=asked)
    await run_chat_turn(
        ctx=ctx,
        message="What is terminal veloctity",
        decision_graph=_decision_graph("resource"),
        orchestrator=first,  # type: ignore[arg-type]
        memory_tool=memory,  # type: ignore[arg-type]
    )

    second = _RecordingOrchestrator()
    result = await run_chat_turn(
        ctx=ctx,
        message=reply,
        decision_graph=_decision_graph("admissions"),
        orchestrator=second,  # type: ignore[arg-type]
        memory_tool=memory,  # type: ignore[arg-type]
    )

    assert result.routes == ["escalation"]
    assert second.patch is not None
    assert second.patch["pending_escalation_message"] == "What is terminal veloctity"
    assert "welcome" not in result.answer.lower()


def test_b4_pending_question_is_read_from_process_store_before_st():
    remember_pending_question(
        session_id="tenant-demo-physics:94770991234",
        question="What is gravity",
    )
    memory = _RecallOnlyMemory()
    pending = get_pending_low_confidence_question(
        memory_tool=memory,  # type: ignore[arg-type]
        tenant_id="tenant-demo-physics",
        user_id="94770991234",
        session_id="tenant-demo-physics:94770991234",
    )
    assert pending == "What is gravity"


def test_memory_tool_recent_pairs_delegates_to_st_store():
    st = MagicMock()
    st.recent_pairs.return_value = [("What is gravity", t("rag_low_confidence_ask", "en"))]
    tool = MemoryTool(st_store=st)
    pairs = tool.recent_pairs(
        tenant_id="t",
        user_id="u",
        session_id="s",
        k=3,
    )
    assert pairs == [("What is gravity", t("rag_low_confidence_ask", "en"))]
    st.recent_pairs.assert_called_once_with(
        tenant_id="t", user_id="u", session_id="s", k=3
    )


def test_st_recent_pairs_uses_newest_turns_and_skips_trailing_unpaired_user(monkeypatch):
    asked = t("rag_low_confidence_ask", "en")
    # Query is newest-first; inbound "Yes" is already logged so it is first.
    newest_first = [
        {"role": "user", "content": "Yes", "created_at": "2026-08-28T02:15:00"},
        {"role": "assistant", "content": asked, "created_at": "2026-08-28T02:14:00"},
        {"role": "user", "content": "What is gravity", "created_at": "2026-08-28T02:13:00"},
        {"role": "assistant", "content": "Welcome back!", "created_at": "2026-08-28T02:12:00"},
        {"role": "user", "content": "hi", "created_at": "2026-08-28T02:11:00"},
    ]

    class _Query:
        def select(self, *args, **kwargs):
            return self

        def eq(self, *args, **kwargs):
            return self

        def order(self, *args, **kwargs):
            return self

        def limit(self, *args, **kwargs):
            return self

        def execute(self):
            return type("Response", (), {"data": newest_first})()

    class _Client:
        def table(self, _name):
            return _Query()

    monkeypatch.setattr("memory.st_store.get_supabase_client", lambda: _Client())
    pairs = ShortTermMemoryStore().recent_pairs(
        tenant_id="t",
        user_id="u",
        session_id="s",
        k=3,
    )

    assert pairs[-1] == ("What is gravity", asked)


def test_yup_is_an_affirmative_intent():
    assert classify("Yup").intent is StudentIntent.AFFIRM


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
