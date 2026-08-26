"""Route-lock helpers — keep mid-onboarding turns on the admissions agent."""

from __future__ import annotations

from agents.router import heuristic_route
from services.admissions.onboarding_session_store import get_onboarding_session_store

_BREAKOUT_ROUTES = frozenset({"resource", "escalation", "payment_check"})


def should_break_onboarding_lock(message: str) -> bool:
    """True when a clear specialist intent should override active onboarding."""
    decision = heuristic_route(message)
    if decision is None:
        return False
    return decision.primary.route in _BREAKOUT_ROUTES


def is_onboarding_active(*, tenant_id: str, phone: str, student_exists: bool) -> bool:
    """True when an in-memory onboarding session is collecting details."""
    if student_exists:
        return False
    session = get_onboarding_session_store().get(tenant_id=tenant_id, phone=phone)
    return session is not None and session.active


def onboarding_router_context_hint(*, tenant_id: str, phone: str, student_exists: bool) -> str:
    if not is_onboarding_active(
        tenant_id=tenant_id, phone=phone, student_exists=student_exists
    ):
        return ""
    session = get_onboarding_session_store().get(tenant_id=tenant_id, phone=phone)
    if session and session.awaiting_confirmation:
        return (
            "[ONBOARDING AWAITING CONFIRMATION — user YES/confirm completes enrollment "
            "— NO/change restarts collection — always in_scope, route to admissions]"
        )
    step = (session.next_step if session else None) or "name"
    return f"[ONBOARDING IN PROGRESS — collecting: {step} — route to admissions]"


def apply_onboarding_patch_overrides(
    patch: dict,
    *,
    tenant_id: str,
    phone: str,
    student_exists: bool,
    message: str = "",
) -> bool:
    """Force proceed + admissions when mid-onboarding. Returns True if applied."""
    if not is_onboarding_active(
        tenant_id=tenant_id, phone=phone, student_exists=student_exists
    ):
        return False
    if message and should_break_onboarding_lock(message):
        get_onboarding_session_store().clear(tenant_id=tenant_id, phone=phone)
        return False
    patch["verdict"] = "proceed"
    patch.pop("final_answer", None)
    patch["route_decisions"] = [
        admissions_route_decision(
            reasoning="active onboarding session — keep on admissions agent",
        )
    ]
    return True


def admissions_route_decision(*, reasoning: str) -> dict:
    return {
        "route": "admissions",
        "action": "general",
        "params": {},
        "confidence": 1.0,
        "reasoning": reasoning,
    }
