"""
Bridge decision subgraph output → orchestrator AgentState.

Ported from BookMe AI ``agents/decision_bridge.py``.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from langchain_core.messages import AnyMessage

from agents.decision_state import DecisionState
from agents.prompts import get_flagged_abusive_reply, get_out_of_scope_reply
from agents.state import AgentState
from services.language import normalize_language_pref


def map_decision_to_agent_state(
    decision_out: DecisionState,
    *,
    messages: list[AnyMessage],
    memory_context: str = "",
    tenant_id: str = "",
    user_id: str = "",
    student_id: str = "",
    student_name: str = "",
    phone: str = "",
    session_id: str = "",
    tenant_name: str = "",
    is_enrolled: bool = False,
    enrolled_class_ids: list[str] | None = None,
    student_profile_context: str = "",
    media_url: str | None = None,
    language_pref: str = "en",
) -> AgentState:
    patch: dict[str, Any] = {
        "messages": messages,
        "memory_context": memory_context or decision_out.get("router_context") or "",
        "tenant_id": tenant_id,
        "user_id": user_id,
        "student_id": student_id or user_id,
        "student_name": student_name,
        "phone": phone,
        "session_id": session_id,
        "tenant_name": tenant_name,
        "is_enrolled": is_enrolled,
        "enrolled_class_ids": list(enrolled_class_ids or []),
        "student_profile_context": student_profile_context,
        "media_url": media_url,
        "language_pref": normalize_language_pref(language_pref),
        "guardrail": decision_out.get("guardrail", "in_scope"),
        "verdict": decision_out.get("verdict", "proceed"),
    }

    if patch["verdict"] == "out_of_scope":
        patch["final_answer"] = get_out_of_scope_reply(
            language=patch["language_pref"]
        )
        return patch  # type: ignore[return-value]

    if patch["verdict"] == "flagged_abusive":
        patch["final_answer"] = get_flagged_abusive_reply(
            language=patch["language_pref"]
        )
        return patch  # type: ignore[return-value]

    decision = decision_out.get("decision")
    if decision and decision.decisions:
        patch["route_decisions"] = [asdict(d) for d in decision.decisions]
    else:
        patch["route_decisions"] = []

    return patch  # type: ignore[return-value]
