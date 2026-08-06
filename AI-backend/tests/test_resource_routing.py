"""Resource agent sub-router tests."""

from __future__ import annotations

import pytest

from agents.nodes.resource_agent import classify_resource_subpath, _infer_drive_folder


@pytest.mark.parametrize(
    "message,expected",
    [
        ("Do you have past papers for 2024?", "drive"),
        ("Send me the physics textbook chapter 3", "drive"),
        ("Where is the syllabus?", "drive"),
        ("I don't understand velocity in lesson 5", "rag"),
        ("Explain Newton's laws", "rag"),
        ("Explain momentum from the uploaded notes", "rag"),
        ("What did sir say about friction?", "rag"),
    ],
)
def test_classify_resource_subpath(message, expected):
    assert classify_resource_subpath(message) == expected


def test_infer_drive_folder():
    assert _infer_drive_folder("send me the textbook") == "textbooks"
    assert _infer_drive_folder("where is the syllabus") == "syllabus"
    assert _infer_drive_folder("past paper 2024") == "papers"
