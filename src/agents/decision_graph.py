"""Decision graph — parallel guardrail + router, then decide gate."""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from agents.decision_bridge import decide
from agents.decision_state import DecisionState
from agents.guardrail import Guardrail
from agents.router import Router
from domain.routing import GuardrailVerdict
from infrastructure.observability import observe


def _guardrail_node(state: DecisionState) -> DecisionState:
    guardrail = Guardrail()
    verdict = guardrail.classify(
        state.get("message", ""),
        chat_history=state.get("chat_history", ""),
    )
    return {
        "guardrail_verdict": verdict.value,
        "guardrail_error": False,
    }


def _router_node(state: DecisionState) -> DecisionState:
    router = Router()
    decision = router.route(
        state.get("message", ""),
        chat_history=state.get("chat_history", ""),
    )
    return {
        "router_intent": decision.intent.value,
        "router_confidence": decision.confidence,
        "router_reason": decision.reason,
    }


def _decide_node(state: DecisionState) -> DecisionState:
    return decide(state)


@observe(name="decision_graph")
def run_decision_graph(
    *,
    message: str,
    chat_history: str = "",
) -> DecisionState:
    graph = build_decision_graph()
    return graph.invoke(
        {
            "message": message,
            "chat_history": chat_history,
        }
    )


def build_decision_graph():
    graph = StateGraph(DecisionState)
    graph.add_node("guardrail", _guardrail_node)
    graph.add_node("router", _router_node)
    graph.add_node("decide", _decide_node)

    graph.add_edge(START, "guardrail")
    graph.add_edge(START, "router")
    graph.add_edge("guardrail", "decide")
    graph.add_edge("router", "decide")
    graph.add_edge("decide", END)
    return graph.compile()
