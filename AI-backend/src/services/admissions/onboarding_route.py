"""Route-lock helpers — keep mid-onboarding turns on the admissions agent.

The lock exists so that a student answering "Kandy" to "which district?" isn't
routed to the resource agent as a geography question. It used to be close to
absolute: anything that wasn't an obvious resource/escalation/payment keyword
was fed back into the slot collector, which is why questions about the tutor or
the class list during onboarding came back as the next onboarding prompt (B3).

Now the lock is evaluated against the turn's classified intent, and breaking it
suspends the onboarding session instead of deleting it, so the student can be
nudged back to where they left off.
"""

from __future__ import annotations

from services.admissions.flow_control import FlowKind, decide_flow_action
from services.admissions.onboarding_session_store import get_onboarding_session_store
from services.nlu import IntentResult, classify


def should_break_onboarding_lock(message: str, *, intent: IntentResult | None = None) -> bool:
    """True when the message is a different request, not onboarding input."""
    resolved = intent or classify(message)
    return decide_flow_action(resolved, flow=FlowKind.ONBOARDING, message=message).interrupts


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
    intent: IntentResult | None = None,
) -> bool:
    """Force proceed + admissions when mid-onboarding. Returns True if applied."""
    if patch.get("verdict") == "flagged_abusive":
        return False
    if not is_onboarding_active(
        tenant_id=tenant_id, phone=phone, student_exists=student_exists
    ):
        return False
    if message and should_break_onboarding_lock(message, intent=intent):
        # Keep the collected slots. The student is answering a different
        # question this turn, not abandoning enrollment.
        _suspend_session(tenant_id=tenant_id, phone=phone)
        patch["flow_nudge_key"] = "nudge_finish_enrollment"
        return False
    patch["verdict"] = "proceed"
    patch.pop("final_answer", None)
    patch["route_decisions"] = [
        admissions_route_decision(
            reasoning="active onboarding session — keep on admissions agent",
        )
    ]
    return True


def _suspend_session(*, tenant_id: str, phone: str) -> None:
    store = get_onboarding_session_store()
    session = store.get(tenant_id=tenant_id, phone=phone)
    if session is None:
        return
    session.active = False
    store.save(tenant_id=tenant_id, phone=phone, session=session)


def resume_onboarding_session(*, tenant_id: str, phone: str) -> bool:
    """Reactivate a suspended session when the student comes back to it."""
    store = get_onboarding_session_store()
    session = store.get(tenant_id=tenant_id, phone=phone)
    if session is None or session.active:
        return False
    session.active = True
    store.save(tenant_id=tenant_id, phone=phone, session=session)
    return True


def admissions_route_decision(*, reasoning: str) -> dict:
    return {
        "route": "admissions",
        "action": "general",
        "params": {},
        "confidence": 1.0,
        "reasoning": reasoning,
    }
