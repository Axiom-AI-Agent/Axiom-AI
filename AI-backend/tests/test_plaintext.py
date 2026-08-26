"""Plain-text sanitizer for student-facing messages."""

from services.messaging.plaintext import strip_markdown_markers


def test_strips_bold_markers():
    assert strip_markdown_markers("Reply **YES** to proceed.") == "Reply YES to proceed."


def test_strips_multiple_bold_spans():
    text = "• **Full name:** Mirco\nWe have **tutes** and **past papers**."
    assert strip_markdown_markers(text) == "• Full name: Mirco\nWe have tutes and past papers."


def test_leaves_plain_text_unchanged():
    assert strip_markdown_markers("Hello there") == "Hello there"


def test_empty_and_none_safe():
    assert strip_markdown_markers("") == ""
