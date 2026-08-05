"""Institute info inquiry tests."""

from __future__ import annotations

from services.admissions.institute_info import (
    classify_info_inquiry,
    looks_like_institute_info,
)


def test_class_availability_is_institute_info():
    msg = "what are the classes that are available currently"
    assert looks_like_institute_info(msg)
    assert classify_info_inquiry(msg) == "classes"


def test_class_fees_is_class_detail():
    assert classify_info_inquiry("how much is A/L Physics?") == "class_detail"


def test_staff_question_is_staff():
    assert classify_info_inquiry("who is the tutor?") == "staff"


def test_explain_velocity_is_not_institute_info():
    assert not looks_like_institute_info("Explain velocity from the tutor notes")
