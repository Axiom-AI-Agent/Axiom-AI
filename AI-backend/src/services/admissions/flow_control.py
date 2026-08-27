"""Per-turn decision: continue an in-progress flow, or interrupt it.

The old behaviour was implicit — once a student had an onboarding session or a
pending enrollment row, every subsequent turn produced that flow's next message
regardless of what the student actually said. A question about the tutor came
back as "send your payment slip".

This module makes the choice explicit and re-evaluates it on *every* message:
the freshly classified intent decides whether the message belongs to the active
flow or supersedes it. An interrupted flow is never lost — it comes back as a
one-line nudge appended to the answer the student actually asked for.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from services.nlu import IntentResult, StudentIntent
from services.nlu.normalize import looks_like_request


class FlowKind(str, Enum):
    """The kind of multi-turn flow a student may be part-way through."""

    NONE = "none"
    ONBOARDING = "onboarding"
    PAYMENT_PENDING = "payment_pending"
    AWAITING_REVIEW = "awaiting_review"
    ESCALATION_CONFIRM = "escalation_confirm"


class FlowAction(str, Enum):
    CONTINUE = "continue"
    """The message is input for the active flow — advance it."""

    INTERRUPT = "interrupt"
    """The message is a different request — answer that instead."""


@dataclass(frozen=True)
class FlowDecision:
    action: FlowAction
    reason: str
    nudge_key: str | None = None

    @property
    def interrupts(self) -> bool:
        return self.action is FlowAction.INTERRUPT


#: Conversational moves that only make sense as a reply to the flow's own
#: question. They can never mean "change the subject".
_FLOW_REPLIES = frozenset(
    {
        StudentIntent.AFFIRM,
        StudentIntent.DENY,
        StudentIntent.GREETING,
        StudentIntent.UNKNOWN,
    }
)

#: Which nudge to append when each flow is interrupted mid-way.
_NUDGE_KEYS = {
    FlowKind.ONBOARDING: "nudge_finish_enrollment",
    FlowKind.PAYMENT_PENDING: "nudge_send_payment_slip",
}

#: Flows whose next expected input is a free-text value the student types
#: (a name, a school, a district). Because the value is arbitrary prose, it can
#: look like almost any intent, so interrupting one needs a request shape too.
_SLOT_COLLECTING_FLOWS = frozenset({FlowKind.ONBOARDING})


def decide_flow_action(
    intent: IntentResult,
    *,
    flow: FlowKind,
    message: str = "",
    expects_media: bool = False,
    has_media: bool = False,
) -> FlowDecision:
    """Decide whether ``intent`` continues the active ``flow`` or replaces it.

    ``expects_media``/``has_media`` cover the payment step, where the awaited
    input is an image rather than a sentence. ``message`` is used only to tell a
    typed slot value apart from a question.
    """
    if flow is FlowKind.NONE:
        return FlowDecision(FlowAction.INTERRUPT, "no active flow")

    if expects_media and has_media:
        return FlowDecision(FlowAction.CONTINUE, "awaited media attachment arrived")

    if intent.intent in _FLOW_REPLIES:
        return FlowDecision(FlowAction.CONTINUE, f"{intent.intent.value} is a reply to the flow")

    # A task intent is a genuine change of subject. Answer it, and remind the
    # student about the unfinished flow rather than silently dropping it.
    if intent.is_task:
        if (
            flow in _SLOT_COLLECTING_FLOWS
            and message
            and not looks_like_request(message)
        ):
            return FlowDecision(
                FlowAction.CONTINUE,
                f"{intent.intent.value} wording, but shaped like a slot answer",
            )
        return FlowDecision(
            FlowAction.INTERRUPT,
            f"new task intent {intent.intent.value} supersedes {flow.value}",
            nudge_key=_NUDGE_KEYS.get(flow),
        )

    # Enrollment talk during onboarding is the flow itself; during a pending
    # payment it means the student wants a *different* class, which the
    # admissions agent answers against real enrollment state.
    if intent.intent is StudentIntent.ENROLL:
        if flow is FlowKind.ONBOARDING:
            return FlowDecision(FlowAction.CONTINUE, "enrollment talk continues onboarding")
        return FlowDecision(
            FlowAction.INTERRUPT,
            "enrollment request while a previous application is pending",
            nudge_key=_NUDGE_KEYS.get(flow),
        )

    if intent.intent in {StudentIntent.PAYMENT_SUBMIT, StudentIntent.PAYMENT_STATUS}:
        if flow in {FlowKind.PAYMENT_PENDING, FlowKind.AWAITING_REVIEW}:
            return FlowDecision(FlowAction.CONTINUE, "payment talk continues the payment flow")
        return FlowDecision(
            FlowAction.INTERRUPT,
            "payment question during onboarding",
            nudge_key=_NUDGE_KEYS.get(flow),
        )

    if intent.intent is StudentIntent.LINK_SHARED:
        return FlowDecision(
            FlowAction.INTERRUPT,
            "a shared link is not valid input for any flow",
            nudge_key=_NUDGE_KEYS.get(flow),
        )

    if intent.intent is StudentIntent.OFF_TOPIC:
        return FlowDecision(FlowAction.INTERRUPT, "off-topic message")

    return FlowDecision(FlowAction.CONTINUE, "no competing intent detected")


def flow_kind_for_student(
    *,
    onboarding_active: bool,
    already_enrolled: bool = False,
    pending_payment: bool = False,
    awaiting_review: bool = False,
) -> FlowKind:
    """Map ground-truth student state onto the flow the student is inside."""
    if already_enrolled:
        return FlowKind.NONE
    if awaiting_review:
        return FlowKind.AWAITING_REVIEW
    if pending_payment:
        return FlowKind.PAYMENT_PENDING
    if onboarding_active:
        return FlowKind.ONBOARDING
    return FlowKind.NONE
