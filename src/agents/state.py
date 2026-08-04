"""LangGraph orchestrator state."""

from __future__ import annotations

from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class AgentState(TypedDict, total=False):
    """State carried through the orchestrator graph."""

    message: str
    tenant_id: str
    session_id: str
    student_id: str
    tenant_name: str | None
    intent: str
    chat_history: str
    fragments: list[str]
    reply: str
    messages: Annotated[list, add_messages]
