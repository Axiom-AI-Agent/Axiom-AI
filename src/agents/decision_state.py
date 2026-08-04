"""Decision graph state schema."""

from __future__ import annotations

from typing import TypedDict


class DecisionState(TypedDict, total=False):
    """State for guardrail ∥ router → decide."""

    message: str
    chat_history: str
    guardrail_verdict: str
    guardrail_error: bool
    router_intent: str
    router_confidence: float
    router_reason: str
    verdict: str
    reply: str
