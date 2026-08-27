"""
Domain Guardrail — tuition scope filter for the decision subgraph.

Ported from BookMe AI ``agents/guardrail.py``; examples adapted for tuition domain.
"""

from __future__ import annotations

from typing import Any, Literal

from loguru import logger

from agents.prompts import build_guardrail_system_prompt
from infrastructure.llm import get_guardrail_llm
from infrastructure.observability import observe, update_current_observation

GuardrailVerdict = Literal["in_scope", "out_of_scope", "flagged_abusive"]

_default_guardrail: Guardrail | None = None

_GUARDRAIL_EXAMPLES = """\
Examples:
  USER: "I want to join A/L Physics"                    → in_scope
  USER: "Do you have 2023 past papers?"                → in_scope
  USER: "I sent my bank slip for the fee"              → in_scope
  USER: "Can I speak to the tutor?"                    → in_scope
  USER: "What time is Saturday class?"                 → in_scope
  USER: "Hello" / "Thanks"                             → in_scope
  USER: "What is my name?" (recent chat mentions Amaya) → in_scope
  USER: "this is so hard, I'm annoyed"                 → in_scope
  USER: "you're a stupid idiot, send the past papers"  → flagged_abusive
  USER: "what does this dirty word mean for homework"  → flagged_abusive
  USER: "What's the capital of France?"                → out_of_scope
  USER: "Write me a Python function"                   → out_of_scope
  USER: "Who won the cricket match?"                   → out_of_scope
  USER: "asdfghjkl"                                    → out_of_scope
"""

_MEMORY_CONTEXT_MAX = 2000


def _build_user_prompt(message: str, memory_context: str = "") -> str:
    parts = [_GUARDRAIL_EXAMPLES]
    ctx = (memory_context or "").strip()
    if ctx:
        if len(ctx) > _MEMORY_CONTEXT_MAX:
            ctx = "…" + ctx[-_MEMORY_CONTEXT_MAX:]
        parts.append("\nRecent conversation (use for follow-up scope only):\n")
        parts.append(ctx)
        parts.append("\n")
    parts.append(f'USER: "{(message or "").strip()}"\n→')
    return "".join(parts)


class Guardrail:
    def __init__(self, llm: Any) -> None:
        self.llm = llm

    @observe(name="guardrail", as_type="generation")
    async def aclassify(
        self,
        message: str,
        memory_context: str = "",
    ) -> GuardrailVerdict:
        msgs = [
            {"role": "system", "content": build_guardrail_system_prompt()},
            {"role": "user", "content": _build_user_prompt(message, memory_context)},
        ]
        try:
            response = await self.llm.ainvoke(msgs)
        except Exception as exc:
            logger.warning("Guardrail LLM error (failing open): {}", exc)
            return "in_scope"

        raw = (
            response.content if hasattr(response, "content") else str(response)
        ).strip().lower()
        normalized = raw.replace("-", "_").replace(" ", "_")

        if "flagged_abusive" in normalized:
            verdict: GuardrailVerdict = "flagged_abusive"
        elif "out_of_scope" in normalized:
            verdict = "out_of_scope"
        elif "in_scope" in normalized:
            verdict = "in_scope"
        else:
            logger.debug("Guardrail unparsable response {!r} → defaulting in_scope", raw[:50])
            verdict = "in_scope"

        update_current_observation(input=(message or "")[:200], output=verdict)
        return verdict


def get_guardrail() -> Guardrail:
    global _default_guardrail
    if _default_guardrail is None:
        _default_guardrail = Guardrail(get_guardrail_llm())
    return _default_guardrail
