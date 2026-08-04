"""LLM intent router — admissions, resource, payment, escalation, direct."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from loguru import logger

from domain.routing import RouterIntent
from infrastructure.llm.llm_provider import get_router_llm
from infrastructure.observability import observe
from services.prompts.langfuse_prompts import PromptService, prompt_service


@dataclass(frozen=True)
class RouteDecision:
    intent: RouterIntent
    confidence: float
    reason: str


class Router:
    """Classify student messages into specialist intents."""

    def __init__(self, *, prompts: PromptService | None = None) -> None:
        self.prompts = prompts or prompt_service
        self.llm = get_router_llm()

    @observe(name="router")
    def route(self, message: str, *, chat_history: str = "") -> RouteDecision:
        try:
            return self._route(message, chat_history=chat_history)
        except Exception as exc:
            logger.warning("Router fallback to direct: {}", exc)
            return RouteDecision(
                intent=RouterIntent.DIRECT,
                confidence=0.0,
                reason="router_parse_error",
            )

    def _route(self, message: str, *, chat_history: str = "") -> RouteDecision:
        messages = self.prompts.get_messages(
            "axiom/router",
            message=message,
            router_context=chat_history or "(no prior turns)",
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
        return self._parse_response(str(response.content))

    @staticmethod
    def _parse_response(raw: str) -> RouteDecision:
        payload = Router._extract_json(raw)
        intent_raw = str(payload.get("intent", RouterIntent.DIRECT.value)).lower()
        try:
            intent = RouterIntent(intent_raw)
        except ValueError:
            intent = RouterIntent.DIRECT

        confidence_raw = payload.get("confidence", 0.5)
        try:
            confidence = float(confidence_raw)
        except (TypeError, ValueError):
            confidence = 0.5

        reason = str(payload.get("reason", "")).strip() or "router_classification"
        return RouteDecision(intent=intent, confidence=confidence, reason=reason)

    @staticmethod
    def _extract_json(raw: str) -> dict[str, object]:
        text = raw.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            text = text[start : end + 1]
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass
        return {"intent": RouterIntent.DIRECT.value, "confidence": 0.0, "reason": "invalid_json"}
