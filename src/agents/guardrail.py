"""Binary in-scope / out-of-scope classifier for tuition messages."""

from __future__ import annotations

import re

from langchain_core.messages import HumanMessage, SystemMessage
from loguru import logger

from domain.routing import GuardrailVerdict
from infrastructure.llm.llm_provider import get_guardrail_llm
from infrastructure.observability import observe
from services.prompts.langfuse_prompts import PromptService, prompt_service


class Guardrail:
    """Fast LLM scope check — fails open on provider errors."""

    def __init__(self, *, prompts: PromptService | None = None) -> None:
        self.prompts = prompts or prompt_service
        self.llm = get_guardrail_llm()

    @observe(name="guardrail")
    def classify(self, message: str, *, chat_history: str = "") -> GuardrailVerdict:
        try:
            return self._classify(message, chat_history=chat_history)
        except Exception as exc:
            logger.warning("Guardrail failed open: {}", exc)
            return GuardrailVerdict.IN_SCOPE

    async def aclassify(self, message: str, *, chat_history: str = "") -> GuardrailVerdict:
        return self.classify(message, chat_history=chat_history)

    def _classify(self, message: str, *, chat_history: str = "") -> GuardrailVerdict:
        system = self.prompts.get_text("axiom/guardrail")
        history_block = f"\nRecent chat:\n{chat_history}" if chat_history else ""
        user_content = f"Message: {message}{history_block}"

        response = self.llm.invoke(
            [
                SystemMessage(content=system),
                HumanMessage(content=user_content),
            ]
        )
        raw = str(response.content).strip().lower()
        if "out_of_scope" in raw or raw == "out_of_scope":
            return GuardrailVerdict.OUT_OF_SCOPE
        if "in_scope" in raw or raw == "in_scope":
            return GuardrailVerdict.IN_SCOPE

        token = re.sub(r"[^a-z_]", "", raw.split()[0] if raw.split() else "")
        if token == "outofscope":
            return GuardrailVerdict.OUT_OF_SCOPE
        return GuardrailVerdict.IN_SCOPE
