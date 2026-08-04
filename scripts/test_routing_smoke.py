#!/usr/bin/env python3
"""Smoke test: decision subgraph routing (BookMe AI pattern)."""

from __future__ import annotations

import asyncio
import sys
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
from agents.router import get_query_router


async def _run(message: str) -> dict:
    graph = build_decision_graph()
    decision_out = await graph.ainvoke(build_decision_input(message=message))
    agent_patch = map_decision_to_agent_state(
        decision_out,
        messages=[HumanMessage(content=message)],
        memory_context="",
    )
    return {"decision": decision_out, "agent": agent_patch}


async def main() -> int:
    off = await _run("What is the capital of France?")
    if off["decision"].get("verdict") != "out_of_scope":
        print("FAIL: expected out_of_scope for trivia, got", off["decision"].get("verdict"))
        return 1
    print("OK off-topic:", off["decision"].get("verdict"))

    enroll = await _run("I want to join A/L Physics")
    if enroll["decision"].get("verdict") != "proceed":
        print("FAIL: expected proceed for enrollment, got", enroll["decision"].get("verdict"))
        return 1
    routes = {r.get("route") for r in enroll["agent"].get("route_decisions") or []}
    print("OK enrollment: verdict=proceed routes=", routes)

    hi = (await get_query_router().aroute("hi", "")).primary.route
    print("OK router chitchat: hi →", hi)

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
