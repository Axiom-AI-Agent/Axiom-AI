"""
Decision LangGraph — guardrail and router subgraph for Axiom AI.

Ported from BookMe AI ``agents/decision_graph.py`` (no CAG/CRAG nodes).

Topology::

    START → guardrail ∥ router → decide → END
"""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from typing import Any

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from loguru import logger

from agents.decision_state import DecisionState, DecisionVerdict, GuardrailVerdict
from agents.guardrail import Guardrail, get_guardrail
from agents.prompts import get_out_of_scope_reply
from agents.router import SPECIALIST_ROUTES, QueryRouter, _fallback_multi, get_query_router

EmitFn = Callable[[dict[str, Any]], Awaitable[None]]


def _ms(t0: float) -> int:
    return int((time.perf_counter() - t0) * 1000)


def _emit_from_config(config: RunnableConfig | None) -> EmitFn:
    if config and (cfg := config.get("configurable")):
        fn = cfg.get("emit")
        if fn is not None:
            return fn

    async def _noop(_: dict[str, Any]) -> None:
        return None

    return _noop


def make_guardrail_node(guardrail: Guardrail):
    async def guardrail_node(
        state: DecisionState,
        config: RunnableConfig | None = None,
    ) -> dict[str, Any]:
        emit = _emit_from_config(config)
        t0 = time.perf_counter()
        await emit({"type": "stage_start", "stage": "guardrail"})
        try:
            verdict: GuardrailVerdict = await guardrail.aclassify(
                state["message"],
                state.get("router_context", "") or "",
            )
        except Exception as exc:
            logger.warning("Guardrail node failed (defaulting in_scope): {}", exc)
            verdict = "in_scope"
        ms = _ms(t0)
        await emit({"type": "stage_done", "stage": "guardrail", "ms": ms, "detail": {"verdict": verdict}})
        return {"guardrail": verdict, "guardrail_ms": ms}

    return guardrail_node


def make_router_node(router: QueryRouter):
    async def router_node(
        state: DecisionState,
        config: RunnableConfig | None = None,
    ) -> dict[str, Any]:
        emit = _emit_from_config(config)
        t0 = time.perf_counter()
        await emit({"type": "stage_start", "stage": "route"})
        try:
            decision = await router.aroute(
                state["message"],
                state.get("router_context", ""),
            )
        except Exception as exc:
            logger.warning("Router node failed (defaulting direct): {}", exc)
            decision = _fallback_multi(f"Router node error: {exc}")
        ms = _ms(t0)
        primary = decision.primary
        await emit(
            {
                "type": "stage_done",
                "stage": "route",
                "ms": ms,
                "detail": {"route": primary.route, "action": primary.action},
            }
        )
        return {"decision": decision, "route_ms": ms}

    return router_node


def decide_node(
    state: DecisionState,
    config: RunnableConfig | None = None,
) -> dict[str, Any]:
    _ = config
    guardrail_v = state.get("guardrail", "in_scope")
    decision = state.get("decision")
    primary = decision.primary if decision else None
    primary_route = primary.route if primary else "direct"

    if guardrail_v == "out_of_scope":
        if primary_route in SPECIALIST_ROUTES:
            logger.info(
                "Guardrail out_of_scope but router chose {}; proceeding",
                primary_route,
            )
            return {"verdict": "proceed", "primary_route": primary_route}
        return {
            "verdict": "out_of_scope",
            "primary_route": primary_route,
            "final_answer": get_out_of_scope_reply(),
        }

    verdict: DecisionVerdict = "proceed"
    return {"verdict": verdict, "primary_route": primary_route}


def build_decision_graph(
    *,
    guardrail: Guardrail | None = None,
    router: QueryRouter | None = None,
):
    guardrail = guardrail or get_guardrail()
    router = router or get_query_router()

    g = StateGraph(DecisionState)
    g.add_node("guardrail", make_guardrail_node(guardrail))
    g.add_node("router", make_router_node(router))
    g.add_node("decide", decide_node)

    g.add_edge(START, "guardrail")
    g.add_edge(START, "router")
    g.add_edge("guardrail", "decide")
    g.add_edge("router", "decide")
    g.add_edge("decide", END)

    return g.compile()


def build_decision_input(*, message: str, router_context: str = "") -> DecisionState:
    return {"message": message, "router_context": router_context}
