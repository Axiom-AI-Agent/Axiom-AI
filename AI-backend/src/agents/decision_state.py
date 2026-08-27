"""
Decision subgraph state — separate from orchestrator AgentState.

Ported from BookMe AI ``agents/decision_state.py``.
"""

from __future__ import annotations

from typing import Literal, Optional

from typing_extensions import TypedDict

from agents.router import MultiRouteDecision
from services.nlu import IntentResult

GuardrailVerdict = Literal["in_scope", "out_of_scope", "flagged_abusive"]
DecisionVerdict = Literal["out_of_scope", "flagged_abusive", "proceed"]


class DecisionState(TypedDict, total=False):
    message: str
    router_context: str

    guardrail: GuardrailVerdict
    decision: MultiRouteDecision
    intent: Optional[IntentResult]

    guardrail_ms: int
    route_ms: int

    verdict: DecisionVerdict
    primary_route: str
    final_answer: Optional[str]
