"""Prompt service tests."""

from services.prompts.langfuse_prompts import PromptService


def test_local_prompt_fallback_text():
    service = PromptService()
    text = service.get_text("axiom/out_of_scope_reply")
    assert "tuition" in text.lower()


def test_local_prompt_fallback_messages():
    service = PromptService()
    messages = service.get_messages("axiom/direct", message="Hello")
    assert messages[0]["role"] == "system"
    assert messages[-1]["content"] == "Hello"
