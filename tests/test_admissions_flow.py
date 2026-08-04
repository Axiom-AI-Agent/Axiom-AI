"""Onboarding flow unit tests."""

from __future__ import annotations

from services.admissions.onboarding_flow import OnboardingFlow


def test_onboarding_first_step_is_name():
    flow = OnboardingFlow()
    state = flow.load_from_student(None)
    assert state.next_step == "name"


def test_onboarding_extracts_name_school_district():
    flow = OnboardingFlow()
    state = flow.load_from_student({"id": "stu-1", "phone": "94770000001"})
    state = flow.apply_message(state, "Amaya Perera")
    assert state.slots.name == "Amaya Perera"
    assert state.next_step == "school"

    state = flow.apply_message(state, "Visakha Vidyalaya")
    assert state.slots.school == "Visakha Vidyalaya"
    assert state.next_step == "district"

    state = flow.apply_message(state, "Colombo")
    assert state.slots.district == "Colombo"
    assert state.next_step == "class"


def test_class_disambiguation_for_physics():
    flow = OnboardingFlow()
    classes = [
        {"id": "class-al", "subject": "Physics", "grade": "A/L", "name": "A/L Physics 2026"},
        {"id": "class-ol", "subject": "Physics", "grade": "O/L", "name": "O/L Physics 2026"},
    ]
    state = flow.load_from_student(
        {"id": "s1", "name": "Test", "school": "School", "district": "Colombo"}
    )
    state = flow.apply_message(state, "Physics", classes=classes)
    assert len(state.ambiguous_classes) == 2
    assert state.next_step == "class"


def test_class_match_al_physics():
    flow = OnboardingFlow()
    classes = [
        {"id": "class-al", "subject": "Physics", "grade": "A/L", "name": "A/L Physics 2026"},
        {"id": "class-ol", "subject": "Physics", "grade": "O/L", "name": "O/L Physics 2026"},
    ]
    state = flow.load_from_student(
        {"id": "s1", "name": "Test", "school": "School", "district": "Colombo"}
    )
    state = flow.apply_message(state, "A/L Physics", classes=classes)
    assert state.slots.class_id == "class-al"


def test_consent_capture():
    flow = OnboardingFlow()
    state = flow.load_from_student(
        {
            "id": "s1",
            "name": "Test",
            "school": "School",
            "district": "Colombo",
        }
    )
    state.slots.class_id = "class-al"
    state.next_step = "consent"
    state = flow.apply_message(state, "YES")
    assert state.slots.consent is True
    assert state.complete is True


def test_pending_enrollment_state():
    flow = OnboardingFlow()
    state = flow.load_from_student(
        {"id": "s1", "name": "Test", "school": "School", "district": "Colombo", "consent_at": "x"},
        pending_enrollment={"id": "enr-1", "class_id": "class-al", "status": "pending"},
    )
    assert state.pending_payment is True
    assert state.next_step == "payment_receipt"


def test_awaiting_review_state():
    flow = OnboardingFlow()
    state = flow.load_from_student(
        {"id": "s1", "name": "Test", "school": "School", "district": "Colombo", "consent_at": "x"},
        pending_enrollment={"id": "enr-1", "class_id": "class-al", "status": "pending"},
        open_escalation={"id": "esc-1", "status": "open"},
    )
    assert state.awaiting_review is True
    assert state.pending_payment is False
