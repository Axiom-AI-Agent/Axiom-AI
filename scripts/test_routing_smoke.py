#!/usr/bin/env python3
"""Live smoke: 10 messages through the decision subgraph (Phase 2 gate)."""

from __future__ import annotations

import asyncio
import os
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env", override=True)

from langchain_core.messages import HumanMessage

from agents.decision_bridge import map_decision_to_agent_state
from agents.decision_graph import build_decision_graph, build_decision_input


@dataclass(frozen=True)
class RoutingCase:
    label: str
    message: str
    verdict: str
    routes: tuple[str, ...] | None = None  # None = skip route check (out_of_scope)


# Phase 2 acceptance: 10 sample messages → correct intent / verdict
ROUTING_CASES: tuple[RoutingCase, ...] = (
    RoutingCase("off-topic trivia", "What is the capital of France?", "out_of_scope"),
    RoutingCase("off-topic joke", "Tell me a joke about quantum physics", "out_of_scope"),
    RoutingCase("enrollment", "I want to join A/L Physics", "proceed", ("admissions",)),
    RoutingCase("class inquiry", "What classes do you offer for Grade 12?", "proceed", ("admissions", "direct")),
    RoutingCase("past papers", "Do you have past papers for 2024?", "proceed", ("resource",)),
    RoutingCase("syllabus", "Where can I find the physics syllabus?", "proceed", ("resource",)),
    RoutingCase("bank slip", "I sent my bank slip yesterday", "proceed", ("payment_check",)),
    RoutingCase("fee status", "Has my fee payment been received?", "proceed", ("payment_check",)),
    RoutingCase("escalation", "Can I speak to the tutor please?", "proceed", ("escalation",)),
    RoutingCase("chitchat", "hi", "proceed", ("direct",)),
)


async def _run(graph, message: str) -> dict:
    decision_out = await graph.ainvoke(build_decision_input(message=message))
    agent_patch = map_decision_to_agent_state(
        decision_out,
        messages=[HumanMessage(content=message)],
        memory_context="",
    )
    return {"decision": decision_out, "agent": agent_patch}


def _primary_route(decision: dict) -> str:
    route = decision.get("primary_route")
    if route:
        return str(route)
    decisions = decision.get("decision")
    if decisions and decisions.decisions:
        return str(decisions.decisions[0].route)
    patch_routes = decision.get("route_decisions") or []
    if patch_routes:
        return str(patch_routes[0].get("route", "direct"))
    return "direct"


async def main() -> int:
    if not os.getenv("OPENAI_API_KEY"):
        print("SKIP: OPENAI_API_KEY not set — routing smoke needs live LLM")
        return 0

    graph = build_decision_graph()
    passed = 0
    failed = 0

    print("=== Phase 2 routing smoke (10 messages) ===")
    for case in ROUTING_CASES:
        result = await _run(graph, case.message)
        decision = result["decision"]
        verdict = decision.get("verdict")
        route = _primary_route(decision)

        ok = verdict == case.verdict
        if ok and case.routes is not None:
            ok = route in case.routes

        status = "OK" if ok else "FAIL"
        if case.routes:
            detail = f"verdict={verdict} route={route} (want {case.verdict}, one of {case.routes})"
        else:
            detail = f"verdict={verdict} (want {case.verdict})"

        print(f"{status} {case.label}: {detail}")
        if ok:
            passed += 1
        else:
            failed += 1

    print(f"\nResult: {passed}/{len(ROUTING_CASES)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
