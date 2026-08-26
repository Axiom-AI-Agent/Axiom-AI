"""Onboarding flow unit tests."""

from __future__ import annotations

from services.admissions.onboarding_flow import OnboardingFlow


def test_onboarding_first_step_is_name():
    flow = OnboardingFlow()
    state = flow.start_collection()
    assert state.next_step == "name"


def test_onboarding_extracts_name_school_district():
    flow = OnboardingFlow()
    state = flow.start_collection()
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
    state = flow.start_collection()
    state.slots.name = "Test"
    state.slots.school = "School"
    state.slots.district = "Colombo"
    state.next_step = "class"
    state = flow.apply_message(state, "Physics", classes=classes)
    assert len(state.ambiguous_classes) == 2
    assert state.next_step == "class"


def test_class_match_al_physics():
    flow = OnboardingFlow()
    classes = [
        {"id": "class-al", "subject": "Physics", "grade": "A/L", "name": "A/L Physics 2026"},
        {"id": "class-ol", "subject": "Physics", "grade": "O/L", "name": "O/L Physics 2026"},
    ]
    state = flow.start_collection()
    state.slots.name = "Test"
    state.slots.school = "School"
    state.slots.district = "Colombo"
    state.next_step = "class"
    state = flow.apply_message(state, "A/L Physics", classes=classes)
    assert state.slots.class_id == "class-al"
    assert state.awaiting_confirmation is True


def test_review_step_after_all_fields():
    flow = OnboardingFlow()
    classes = [
        {"id": "class-al", "subject": "Physics", "grade": "A/L", "name": "A/L Physics 2026"},
    ]
    state = flow.start_collection()
    state.slots.name = "Test"
    state.slots.school = "School"
    state.slots.district = "Colombo"
    state.next_step = "class"
    state = flow.apply_message(state, "A/L Physics", classes=classes)
    assert state.awaiting_confirmation is True
    assert state.next_step == "confirm"


def test_confirm_yes_completes_onboarding():
    flow = OnboardingFlow()
    state = flow.start_collection()
    state.slots.name = "Test"
    state.slots.school = "School"
    state.slots.district = "Colombo"
    state.slots.class_id = "class-al"
    state.awaiting_confirmation = True
    state.next_step = "confirm"
    state = flow.apply_message(state, "YES")
    assert state.slots.confirmed is True
    assert state.complete is True


def test_confirm_yes_not_treated_as_class_selection():
    flow = OnboardingFlow()
    classes = [
        {"id": "class-al", "subject": "Physics", "grade": "A/L", "name": "A/L Physics 2026"},
        {"id": "class-ol", "subject": "Physics", "grade": "O/L", "name": "O/L Physics 2026"},
    ]
    state = flow.start_collection()
    state.slots.name = "Test"
    state.slots.school = "School"
    state.slots.district = "Colombo"
    state.slots.class_id = "class-al"
    state.awaiting_confirmation = True
    state.next_step = "confirm"
    state = flow.apply_message(state, "yes", classes=classes)
    assert state.slots.confirmed is True
    assert not state.ambiguous_classes


def _awaiting_confirmation_state(flow: OnboardingFlow):
    state = flow.start_collection()
    state.slots.name = "Test"
    state.slots.school = "School"
    state.slots.district = "Colombo"
    state.slots.class_id = "class-al"
    state.awaiting_confirmation = True
    state.next_step = "confirm"
    return state


def _assert_collection_restarted(state) -> None:
    assert state.restarted is True
    assert state.awaiting_confirmation is False
    assert state.next_step == "name"
    assert state.slots.name is None
    assert state.slots.school is None
    assert state.slots.district is None
    assert state.slots.class_id is None
    assert state.slots.confirmed is False
    assert state.complete is False


def test_confirm_reject_change_number_restarts_collection():
    flow = OnboardingFlow()
    state = _awaiting_confirmation_state(flow)
    state = flow.apply_message(state, "no I need to change the number")
    _assert_collection_restarted(state)


def test_confirm_plain_no_restarts_collection():
    flow = OnboardingFlow()
    state = _awaiting_confirmation_state(flow)
    state = flow.apply_message(state, "no")
    _assert_collection_restarted(state)


def test_confirm_sinhala_no_restarts_collection():
    flow = OnboardingFlow()
    state = _awaiting_confirmation_state(flow)
    state = flow.apply_message(state, "නෑ")
    _assert_collection_restarted(state)


def test_confirm_reject_wins_over_ok_overlap():
    flow = OnboardingFlow()
    state = _awaiting_confirmation_state(flow)
    state = flow.apply_message(state, "no it's not ok")
    _assert_collection_restarted(state)


def test_confirm_unclear_hmm_keeps_review():
    flow = OnboardingFlow()
    state = _awaiting_confirmation_state(flow)
    state = flow.apply_message(state, "hmm")
    assert state.awaiting_confirmation is True
    assert state.next_step == "confirm"
    assert state.restarted is False
    assert state.slots.name == "Test"
    assert state.slots.school == "School"
    assert state.slots.district == "Colombo"
    assert state.slots.class_id == "class-al"


def test_extract_name_from_my_name_is():
    flow = OnboardingFlow()
    state = flow.start_collection()
    state = flow.apply_message(state, "My name is Mirco Fernando")
    assert state.slots.name == "Mirco Fernando"
    assert state.next_step == "school"


def test_extract_school_from_phrase():
    flow = OnboardingFlow()
    state = flow.start_collection()
    state.slots.name = "Mirco Fernando"
    state.next_step = "school"
    state = flow.apply_message(state, "I go to Royal College Colombo")
    assert state.slots.school == "Royal College Colombo"


def test_class_catalog_request_on_class_step():
    flow = OnboardingFlow()
    classes = [
        {"id": "class-al", "subject": "Physics", "grade": "A/L", "name": "A/L Physics 2026", "fee_amount": 5000},
        {"id": "class-ol", "subject": "Physics", "grade": "O/L", "name": "O/L Physics 2026", "fee_amount": 3500},
    ]
    msg = flow.class_catalog_message(
        classes=classes,
        tenant_name="Demo Physics Academy",
        student_name="Mirco Fernando",
        intro="Of course! Here's what we offer:",
    )
    assert "A/L Physics 2026" in msg
    assert "O/L Physics 2026" in msg
    assert "**" not in msg
    assert "LKR 5,000/month" in msg
    assert flow._looks_like_class_catalog_request("what are all the available classes")


def test_review_and_welcome_messages_have_no_markdown_bold():
    flow = OnboardingFlow()
    state = flow.start_collection()
    state.slots.name = "Mirco Fernando"
    state.slots.school = "Royal College"
    state.slots.district = "Colombo"
    class_row = {"name": "A/L Physics 2026", "fee_amount": 5000}
    review = flow.review_confirmation_message(
        slots=state.slots,
        class_row=class_row,
        tenant_name="Demo Physics Academy",
        phone="+94770000000",
    )
    welcome = flow.enrollment_welcome_message(
        slots=state.slots,
        class_row=class_row,
        tenant_name="Demo Physics Academy",
    )
    assert "**" not in review
    assert "**" not in welcome
    assert "Full name: Mirco Fernando" in review
    assert "A/L Physics 2026" in welcome


def test_pending_enrollment_state():
    flow = OnboardingFlow()
    state = flow.load_from_student(
        {"id": "s1", "name": "Test", "school": "School", "district": "Colombo", "consent_at": "x"},
        pending_enrollment={"id": "enr-1", "class_id": "class-al", "status": "pending"},
    )
    assert state.pending_payment is True


def test_awaiting_review_state():
    flow = OnboardingFlow()
    state = flow.load_from_student(
        {"id": "s1", "name": "Test", "school": "School", "district": "Colombo", "consent_at": "x"},
        pending_enrollment={"id": "enr-1", "class_id": "class-al", "status": "pending"},
        open_escalation={"id": "esc-1", "status": "open"},
    )
    assert state.awaiting_review is True
    assert state.pending_payment is False


def test_enrollment_status_query_is_not_enrollment_intent():
    flow = OnboardingFlow()
    assert flow._looks_like_enrollment_status_query("am i enrolled in a class of your academy")
    assert not flow._looks_like_enrollment_intent("am i enrolled in a class of your academy")


def test_tutoring_question_not_extracted_as_name():
    flow = OnboardingFlow()
    state = flow.start_collection()
    state = flow.apply_message(state, "Explain velocity from the tutor notes")
    assert state.slots.name is None
    assert state.next_step == "name"


def test_tutoring_question_not_extracted_as_school():
    flow = OnboardingFlow()
    state = flow.start_collection()
    state.slots.name = "Amaya Perera"
    state.next_step = "school"
    state = flow.apply_message(state, "Explain velocity from the tutor notes")
    assert state.slots.school is None
    assert state.next_step == "school"


def test_off_topic_detected_during_onboarding():
    flow = OnboardingFlow()
    assert flow._looks_like_off_topic_during_onboarding("Explain velocity from the tutor notes")
    assert not flow._looks_like_off_topic_during_onboarding("Royal College Colombo")
