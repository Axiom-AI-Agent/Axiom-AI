"""Regression tests for sticky flow-state (category B in the QA log).

The reported symptom was always the same: whatever the student typed, the agent
replied with the next step of whichever flow they happened to be inside. These
tests pin the corrected behaviour — every message is classified first, and the
flow only continues when the message actually belongs to it.
"""

from __future__ import annotations

import pytest

from services.admissions.flow_control import (
    FlowAction,
    FlowKind,
    decide_flow_action,
    flow_kind_for_student,
)
from services.nlu import StudentIntent, classify


def decide(message: str, flow: FlowKind, **kwargs):
    return decide_flow_action(classify(message), flow=flow, message=message, **kwargs)


# ── B1/B2/B3: a new request must not be answered with the payment prompt ─────
@pytest.mark.parametrize(
    "message",
    [
        "I want to join another class",
        "I want to join the A Level physics class",
        "Can I get some information on the tutor?",
        "Who are the team at Demo Physics Academy?",
        "What classes do you teach?",
        "When is my next class?",
        "Do you have 2023 past papers?",
    ],
)
def test_b1_b3_new_requests_interrupt_a_pending_payment(message: str):
    decision = decide(message, FlowKind.PAYMENT_PENDING)
    assert decision.interrupts, f"{message!r} was swallowed by the payment flow"


def test_interrupting_a_payment_flow_nudges_the_student_back():
    decision = decide("Can I get some information on the tutor?", FlowKind.PAYMENT_PENDING)
    assert decision.nudge_key == "nudge_send_payment_slip"


# ── The flow must still advance when the message really is its input ─────────
@pytest.mark.parametrize("message", ["Yes", "yes please", "No", "hi"])
def test_conversational_replies_continue_the_flow(message: str):
    assert decide(message, FlowKind.ONBOARDING).action is FlowAction.CONTINUE


@pytest.mark.parametrize(
    "message",
    [
        "My name is Mirco Fernando",
        "Mirco Fernando",
        "St John Paul II",
        "Puttlam",
        "A/L Physics",
        "2",
    ],
)
def test_slot_answers_do_not_interrupt_onboarding(message: str):
    """A typed slot value shares vocabulary with real intents; shape decides."""
    assert decide(message, FlowKind.ONBOARDING).action is FlowAction.CONTINUE


@pytest.mark.parametrize(
    "message",
    [
        "Explain velocity from the tutor notes",
        "Can I get some information on the tutor?",
        "Send me the past papers",
    ],
)
def test_questions_interrupt_onboarding(message: str):
    assert decide(message, FlowKind.ONBOARDING).interrupts


def test_enrollment_talk_continues_onboarding_but_interrupts_payment():
    message = "I want to join the physics class"
    assert decide(message, FlowKind.ONBOARDING).action is FlowAction.CONTINUE
    assert decide(message, FlowKind.PAYMENT_PENDING).interrupts


def test_payment_talk_continues_the_payment_flow():
    assert decide("I sent my bank slip", FlowKind.PAYMENT_PENDING).action is FlowAction.CONTINUE


# ── B5: a bare link is not valid input for any flow ──────────────────────────
def test_b5_shared_link_interrupts_every_flow():
    link = "https://docs.google.com/document/d/abc123/edit"
    assert classify(link).intent is StudentIntent.LINK_SHARED
    for flow in (FlowKind.ONBOARDING, FlowKind.PAYMENT_PENDING, FlowKind.AWAITING_REVIEW):
        assert decide(link, flow).interrupts


# ── B6: an awaited attachment advances the flow rather than being re-read ────
def test_b6_awaited_media_continues_the_payment_flow():
    decision = decide_flow_action(
        classify(""),
        flow=FlowKind.PAYMENT_PENDING,
        expects_media=True,
        has_media=True,
    )
    assert decision.action is FlowAction.CONTINUE


# ── Ground truth, not conversational memory, decides which flow is active ────
def test_flow_kind_follows_database_state():
    assert flow_kind_for_student(onboarding_active=True) is FlowKind.ONBOARDING
    assert (
        flow_kind_for_student(onboarding_active=True, pending_payment=True)
        is FlowKind.PAYMENT_PENDING
    )
    assert (
        flow_kind_for_student(onboarding_active=True, awaiting_review=True)
        is FlowKind.AWAITING_REVIEW
    )
    # Already enrolled outranks everything: there is no flow left to finish.
    assert (
        flow_kind_for_student(
            onboarding_active=True, pending_payment=True, already_enrolled=True
        )
        is FlowKind.NONE
    )
    assert flow_kind_for_student(onboarding_active=False) is FlowKind.NONE


def test_no_active_flow_means_every_message_is_answered_on_its_own_terms():
    assert decide("Who is the tutor?", FlowKind.NONE).interrupts
