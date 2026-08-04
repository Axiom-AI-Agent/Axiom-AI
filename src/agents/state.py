"""
AgentState — shared LangGraph state for the Axiom orchestrator.

Ported from BookMe AI ``agents/state.py``; travel slots replaced with tuition routing.
"""

from __future__ import annotations

import operator
from typing import Annotated, Optional

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    messages: Annotated[list[AnyMessage], add_messages]

    tenant_id: str
    user_id: str
    session_id: str
    tenant_name: str

    memory_context: Optional[str]

    guardrail: Optional[str]
    verdict: Optional[str]

    route_decisions: Optional[list[dict]]
    agent_outputs: Annotated[list[dict], operator.add]

    final_answer: Optional[str]
    tool_output: str
