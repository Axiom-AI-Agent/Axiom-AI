"""STT Gemini response parsing tests."""

from types import SimpleNamespace

from services.media.stt_service import _extract_llm_text


def test_extract_llm_text_from_string_content():
    response = SimpleNamespace(content="  hello world  ")
    assert _extract_llm_text(response) == "hello world"


def test_extract_llm_text_from_content_blocks():
    response = SimpleNamespace(
        content=[
            {"type": "text", "text": "What is Newton's first law?"},
            {"type": "text", "text": "Please explain."},
        ]
    )
    assert _extract_llm_text(response) == "What is Newton's first law?\nPlease explain."


def test_extract_llm_text_prefers_text_property():
    response = SimpleNamespace(
        text="plain transcript",
        content=[{"type": "text", "text": "ignored"}],
    )
    assert _extract_llm_text(response) == "plain transcript"


def test_extract_llm_text_empty_blocks():
    response = SimpleNamespace(content=[])
    assert _extract_llm_text(response) == ""
