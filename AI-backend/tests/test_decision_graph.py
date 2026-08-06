"""Decision graph routing tests — ported from BookMe scripts/test_decision_graph.py."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from langchain_core.messages import HumanMessage

from agents.decision_bridge import map_decision_to_agent_state
from agents.decision_graph import build_decision_graph, build_decision_input, decide_node
from agents.decision_state import DecisionState
from agents.guardrail import Guardrail
from agents.router import MultiRouteDecision, QueryRouter, RouteDecision
from agents.prompts import get_out_of_scope_reply


@pytest.mark.asyncio
async def test_decide_out_of_scope_short_circuit():
    state: DecisionState = {
        "guardrail": "out_of_scope",
        "decision": MultiRouteDecision(
            decisions=[RouteDecision(route="direct", action="general")]
        ),
    }
    out = decide_node(state)
    assert out["verdict"] == "out_of_scope"
    assert out["final_answer"] == get_out_of_scope_reply()


@pytest.mark.asyncio
async def test_decide_router_override_on_borderline_guardrail():
    state: DecisionState = {
        "guardrail": "out_of_scope",
        "decision": MultiRouteDecision(
            decisions=[RouteDecision(route="admissions", action="general")]
        ),
    }
    out = decide_node(state)
    assert out["verdict"] == "proceed"
    assert out["primary_route"] == "admissions"


@pytest.mark.asyncio
async def test_decision_graph_off_topic_with_mocked_llm():
    mock_llm = MagicMock()
    guardrail = Guardrail(mock_llm)
    guardrail.aclassify = AsyncMock(return_value="out_of_scope")

    mock_router_llm = MagicMock()
    router = QueryRouter(mock_router_llm)
    router.aroute = AsyncMock(
        return_value=MultiRouteDecision(
            decisions=[RouteDecision(route="direct", action="general")]
        )
    )

    graph = build_decision_graph(guardrail=guardrail, router=router)
    decision_out = await graph.ainvoke(
        build_decision_input(message="What is the capital of France?")
    )
    assert decision_out["verdict"] == "out_of_scope"

    patch = map_decision_to_agent_state(
        decision_out,
        messages=[HumanMessage(content="What is the capital of France?")],
    )
    assert patch.get("final_answer")


@pytest.mark.asyncio
async def test_decision_graph_enrollment_proceeds():
    mock_guardrail = Guardrail(MagicMock())
    mock_guardrail.aclassify = AsyncMock(return_value="in_scope")

    router = QueryRouter(MagicMock())
    router.aroute = AsyncMock(
        return_value=MultiRouteDecision(
            decisions=[
                RouteDecision(route="admissions", action="general", confidence=0.9)
            ]
        )
    )

    graph = build_decision_graph(guardrail=mock_guardrail, router=router)
    decision_out = await graph.ainvoke(
        build_decision_input(message="I want to join A/L Physics")
    )
    assert decision_out["verdict"] == "proceed"

    patch = map_decision_to_agent_state(
        decision_out,
        messages=[HumanMessage(content="I want to join A/L Physics")],
    )
    routes = {r["route"] for r in patch.get("route_decisions", [])}
    assert "admissions" in routes


def test_router_parses_json_routes():
    llm = MagicMock()
    response = MagicMock()
    response.content = json.dumps(
        {
            "routes": [
                {
                    "route": "resource",
                    "action": "search",
                    "params": {"topic": "past papers"},
                    "confidence": 0.9,
                    "reasoning": "past papers request",
                }
            ]
        }
    )
    llm.invoke.return_value = response
    router = QueryRouter(llm)
    result = router.route("Do you have 2023 past papers?", "")
    assert result.primary.route == "resource"


@pytest.mark.asyncio
async def test_guardrail_fail_open():
    llm = MagicMock()
    llm.ainvoke = AsyncMock(side_effect=RuntimeError("provider down"))
    guardrail = Guardrail(llm)
    verdict = await guardrail.aclassify("Hello")
    assert verdict == "in_scope"
