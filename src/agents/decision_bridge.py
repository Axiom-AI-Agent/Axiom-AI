"""Bridge decision graph output into orchestrator input."""

from __future__ import annotations

from agents.decision_state import DecisionState
from domain.routing import DecisionVerdict, GuardrailVerdict, RouterIntent, SPECIALIST_INTENTS
from services.prompts.langfuse_prompts import prompt_service


def decide(state: DecisionState) -> DecisionState:
    """Rule-based gate — OOS short-circuit with router override for specialists."""
    guardrail = state.get("guardrail_verdict", GuardrailVerdict.IN_SCOPE.value)
    intent = state.get("router_intent", RouterIntent.DIRECT.value)

    if guardrail == GuardrailVerdict.OUT_OF_SCOPE.value:
        try:
            intent_enum = RouterIntent(intent)
        except ValueError:
            intent_enum = RouterIntent.DIRECT

        if intent_enum in SPECIALIST_INTENTS:
            return {
                "verdict": DecisionVerdict.PROCEED.value,
                "router_intent": intent_enum.value,
            }

        reply = prompt_service.get_text("axiom/out_of_scope_reply")
        return {
            "verdict": DecisionVerdict.OUT_OF_SCOPE.value,
            "reply": reply,
        }

    return {"verdict": DecisionVerdict.PROCEED.value}


def decision_to_orchestrator(state: DecisionState) -> dict[str, object]:
    """Map decision state into orchestrator kwargs."""
    return {
        "intent": state.get("router_intent", RouterIntent.DIRECT.value),
        "message": state.get("message", ""),
        "chat_history": state.get("chat_history", ""),
    }
