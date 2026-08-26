"""Keyword heuristic router tests (no LLM)."""

from __future__ import annotations

import pytest

from agents.router import heuristic_route


@pytest.mark.parametrize(
    ("message", "expected_route"),
    [
        ("Explain momentum from the uploaded notes", "resource"),
        ("I don't understand velocity in lesson 5", "resource"),
        ("Do you have past papers for 2024?", "resource"),
        ("any tutes?", "resource"),
        ("send me the papers", "resource"),
        ("I need the syllabus PDF", "resource"),
        ("Can I speak to the tutor please?", "escalation"),
        ("I want to join A/L Physics", "admissions"),
        ("I sent my bank slip yesterday", "payment_check"),
        ("hi", "direct"),
    ],
)
def test_heuristic_route(message: str, expected_route: str):
    result = heuristic_route(message)
    assert result is not None
    assert result.primary.route == expected_route
