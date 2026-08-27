"""Prompt service tests."""

from services.prompts.langfuse_prompts import PromptService


def test_local_prompt_fallback_text():
    service = PromptService()
    text = service.get_text("axiom/out_of_scope_reply")
    assert "tuition" in text.lower()
    abusive = service.get_text("axiom/flagged_abusive_reply")
    assert "abusive" in abusive.lower() or "offensive" in abusive.lower()


def test_local_prompt_fallback_messages():
    service = PromptService()
    text = service.get_text("axiom/router-user", memory_context="prior chat", user_message="Hello")
    assert "Hello" in text
    assert "prior chat" in text
