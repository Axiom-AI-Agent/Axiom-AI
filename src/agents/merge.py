"""Gemini merge — synthesise agent fragments into one WhatsApp reply."""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from infrastructure.llm.llm_provider import get_merge_llm
from infrastructure.observability import observe
from services.prompts.langfuse_prompts import PromptService, prompt_service


class ResponseMerger:
    """Combine specialist fragments into a single student-facing reply."""

    def __init__(self, *, prompts: PromptService | None = None) -> None:
        self.prompts = prompts or prompt_service
        self.llm = get_merge_llm()

    @observe(name="merge_response")
    def merge(
        self,
        *,
        fragments: list[str],
        chat_history: str = "",
        tenant_name: str | None = None,
    ) -> str:
        cleaned = [fragment.strip() for fragment in fragments if fragment and fragment.strip()]
        if not cleaned:
            return "Thanks for your message — how can I help with your class today?"
        if len(cleaned) == 1:
            return cleaned[0]

        fragment_block = "\n\n---\n\n".join(cleaned)
        if tenant_name:
            fragment_block = f"Tutor centre: {tenant_name}\n\n{fragment_block}"

        messages = self.prompts.get_messages(
            "axiom/merge_response",
            fragments=fragment_block,
            chat_history=chat_history or "(no prior turns)",
        )
        lc_messages = []
        for item in messages:
            role = item["role"]
            content = item["content"]
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            else:
                lc_messages.append(HumanMessage(content=content))

        response = self.llm.invoke(lc_messages)
        merged = str(response.content).strip()
        return merged or cleaned[-1]
