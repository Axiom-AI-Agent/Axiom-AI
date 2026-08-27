"""Regression tests for entity extraction and registration validation.

Covers A7 (typo-tolerant class references, and telling "no such class" apart
from "class exists but isn't yours") and C1 (emoji-only registration answers).
"""

from __future__ import annotations

import pytest

from services.nlu.entities import (
    extract_grade,
    extract_subject,
    resolve_class_reference,
    validate_registration_value,
)

CLASSES = [
    {
        "id": "class-physics-al-2026",
        "name": "A/L Physics 2026",
        "subject": "Physics",
        "grade": "A/L",
    },
    {
        "id": "class-chem-al-2026",
        "name": "A/L Chemistry 2026",
        "subject": "Chemistry",
        "grade": "A/L",
    },
    {
        "id": "class-maths-ol-2026",
        "name": "O/L Mathematics 2026",
        "subject": "Mathematics",
        "grade": "O/L",
    },
]


# ── A7: typos in the subject or the word "class" still resolve ───────────────
@pytest.mark.parametrize(
    "message",
    [
        "What is the schedule for my physics clss",
        "What is the schedule for my phyiscs class",
        "whats the timetable for phisics",
        "when is my Physics class",
    ],
)
def test_a7_typos_resolve_to_the_real_class(message: str):
    reference = resolve_class_reference(message, classes=CLASSES)
    assert reference.subject == "Physics"
    assert reference.resolved
    assert reference.only_match is not None
    assert reference.only_match["id"] == "class-physics-al-2026"


def test_a7_typo_correction_is_reported_so_it_can_be_echoed_back():
    reference = resolve_class_reference("my phyiscs class schedule", classes=CLASSES)
    assert reference.corrected_terms == {"phyiscs": "Physics"}


def test_a7_unknown_subject_is_distinguishable_from_no_class_mentioned():
    """"No such class" and "you named no class" need different replies."""
    named_but_missing = resolve_class_reference("when is my biology class", classes=CLASSES)
    assert named_but_missing.mentions_a_class
    assert not named_but_missing.resolved

    nothing_named = resolve_class_reference("when is my next class", classes=CLASSES)
    assert not nothing_named.mentions_a_class


def test_class_name_resolves_without_a_subject_keyword():
    reference = resolve_class_reference("A/L Physics 2026", classes=CLASSES)
    assert reference.only_match is not None
    assert reference.only_match["id"] == "class-physics-al-2026"


def test_grade_narrows_an_otherwise_ambiguous_subject():
    assert extract_grade("A/L physics") == "A/L"
    assert extract_grade("ordinary level maths") == "O/L"
    assert extract_grade("grade 10 science") == "Grade 10"
    assert extract_grade("send me the notes") is None


def test_subject_aliases_and_local_spellings():
    assert extract_subject("how much is chem")[0] == "Chemistry"
    assert extract_subject("maths class fee")[0] == "Mathematics"
    assert extract_subject("send me the tutes")[0] is None


def test_the_word_class_is_never_mistaken_for_a_subject():
    assert extract_subject("what classes are available")[0] is None
    assert extract_subject("clss list please")[0] is None


# ── C1: registration answers must be real values ─────────────────────────────
@pytest.mark.parametrize("value", ["💅💅💅", "🙂", "...", "!!!", "   ", "", "-"])
def test_c1_emoji_and_punctuation_are_rejected_as_names(value: str):
    assert not validate_registration_value(value, field_kind="name")


@pytest.mark.parametrize(
    "value",
    ["Mirco Fernando", "Amaya", "St John Paul II", "නිමල් පෙරේරා", "O'Brien", "Ravi K."],
)
def test_c1_real_names_are_accepted(value: str):
    assert validate_registration_value(value, field_kind="name")


def test_c1_emoji_next_to_a_real_name_is_still_a_name():
    assert validate_registration_value("Mirco 🙂", field_kind="name")


@pytest.mark.parametrize("value", ["94771234567", "+94 77 123 4567", "0771234567"])
def test_c1_phone_fields_accept_dialable_numbers(value: str):
    assert validate_registration_value(value, field_kind="phone")


@pytest.mark.parametrize("value", ["12", "not a number", "💅", "1234567890123456789"])
def test_c1_phone_fields_reject_everything_else(value: str):
    assert not validate_registration_value(value, field_kind="phone")
