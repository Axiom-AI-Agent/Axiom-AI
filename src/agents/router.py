"""
Query Router — LLM intent classification for tuition agents.

Ported from BookMe AI ``agents/router.py``; routes adapted for Axiom MVP SRS.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from loguru import logger

from agents.prompts import build_router_prompt
from agents.state import AgentState
from infrastructure.llm import get_router_llm
from infrastructure.observability import observe, update_current_observation

VALID_ROUTES = frozenset({"admissions", "resource", "payment_check", "escalation", "direct"})
VALID_ACTIONS = frozenset({"general", "search", "check", "escalate"})
MAX_ROUTES = 3

_default_router: QueryRouter | None = None

SPECIALIST_ROUTES = frozenset({"admissions", "resource", "payment_check", "escalation"})

_RESOURCE_PATTERNS = (
    r"\bpast paper",
    r"\bmodel paper",
    r"\btextbook\b",
    r"\bsyllabus\b",
    r"\bnotes?\b",
    r"\buploaded\b",
    r"\blesson\b",
    r"\bexplain\b",
    r"\bunderstand\b",
    r"what did",
    r"what is",
    r"what are",
    r"help me with",
    r"how does",
    r"how do",
)
_ESCALATION_PATTERNS = (
    r"speak to (?:a |the )?(?:tutor|human|person|teacher|sir|madam)",
    r"talk to (?:a |the )?(?:tutor|human|person|teacher|sir|madam)",
    r"\bcomplaint\b",
    r"\burgent\b",
    r"need (?:a )?human",
)
_ADMISSIONS_PATTERNS = (
    r"\benroll",
    r"\bregister",
    r"want to join",
    r"join (?:the )?class",
    r"join (?:a |an )?",
    r"new student",
    r"sign up",
)
_PAYMENT_PATTERNS = (
    r"bank slip",
    r"\bpayment\b",
    r"\bfee\b",
    r"\breceipt\b",
    r"paid my",
)
_DIRECT_PATTERNS = (
    r"^(hi|hello|hey|thanks|thank you|ok|okay|bye)[!.?\s]*$",
)


def _pattern_score(text: str, patterns: tuple[str, ...]) -> int:
    return sum(1 for p in patterns if re.search(p, text))


def heuristic_route(message: str) -> MultiRouteDecision | None:
    """Deterministic routing for unambiguous tuition intents (before LLM)."""
    text = message.lower().strip()
    if not text:
        return None

    scores = {
        "resource": _pattern_score(text, _RESOURCE_PATTERNS),
        "escalation": _pattern_score(text, _ESCALATION_PATTERNS),
        "admissions": _pattern_score(text, _ADMISSIONS_PATTERNS),
        "payment_check": _pattern_score(text, _PAYMENT_PATTERNS),
    }
    best_route = max(scores, key=lambda k: scores[k])
    best_score = scores[best_route]

    if best_score == 0:
        if _pattern_score(text, _DIRECT_PATTERNS):
            return MultiRouteDecision(
                decisions=[
                    RouteDecision(
                        route="direct",
                        action="general",
                        confidence=0.95,
                        reasoning="greeting or social message",
                    )
                ]
            )
        return None

    if best_score > 0 and sum(1 for v in scores.values() if v == best_score) > 1:
        return None

    action = _normalize_action(best_route, None)
    return MultiRouteDecision(
        decisions=[
            RouteDecision(
                route=best_route,
                action=action,
                confidence=0.95,
                reasoning=f"keyword heuristic ({best_score} match(es))",
            )
        ]
    )


@dataclass
class RouteDecision:
    route: str = "direct"
    confidence: float = 0.0
    reasoning: str = ""
    action: str | None = "general"
    params: dict[str, Any] = field(default_factory=dict)


@dataclass
class MultiRouteDecision:
    decisions: list[RouteDecision] = field(default_factory=list)

    @property
    def is_multi_route(self) -> bool:
        return len(self.decisions) > 1

    @property
    def primary(self) -> RouteDecision:
        return self.decisions[0] if self.decisions else RouteDecision()


def _normalize_action(route: str, action: str | None) -> str:
    if route == "direct":
        return "general"
    if action in VALID_ACTIONS:
        return action
    defaults = {
        "admissions": "general",
        "resource": "search",
        "payment_check": "check",
        "escalation": "escalate",
    }
    return defaults.get(route, "general")


def _fallback_multi(reasoning: str) -> MultiRouteDecision:
    return MultiRouteDecision(
        decisions=[
            RouteDecision(
                route="direct",
                action="general",
                confidence=0.0,
                reasoning=reasoning,
            )
        ]
    )


def get_query_router() -> QueryRouter:
    global _default_router
    if _default_router is None:
        _default_router = QueryRouter(get_router_llm())
    return _default_router


def router_node(state: AgentState) -> dict:
    user_message = _last_user_text(state)
    memory_context = state.get("memory_context") or ""
    result = get_query_router().route(user_message, memory_context=memory_context)
    return {"route_decisions": [asdict(d) for d in result.decisions]}


def _last_user_text(state: AgentState) -> str:
    messages = state.get("messages") or []
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            content = msg.content
            return content if isinstance(content, str) else str(content)
        if isinstance(msg, dict) and msg.get("role") == "user":
            return str(msg.get("content") or "")
    return ""


class QueryRouter:
    def __init__(self, llm: Any) -> None:
        self.llm = llm

    @observe(name="router", as_type="generation")
    def route(self, user_message: str, memory_context: str = "") -> MultiRouteDecision:
        return self._call(user_message, memory_context)

    @observe(name="router", as_type="generation")
    async def aroute(self, user_message: str, memory_context: str = "") -> MultiRouteDecision:
        return await self._acall(user_message, memory_context)

    def _build_messages(self, user_message: str, memory_context: str):
        system_prompt, user_prompt = build_router_prompt(user_message, memory_context)
        update_current_observation(
            input=user_prompt[:1000],
            model=self._model_name(),
        )
        return [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

    def _record_usage(self, content: str, response) -> None:
        usage = {}
        if hasattr(response, "response_metadata"):
            meta = response.response_metadata or {}
            token_usage = meta.get("token_usage") or meta.get("usage", {})
            if token_usage:
                usage = {
                    "input": token_usage.get("prompt_tokens", 0),
                    "output": token_usage.get("completion_tokens", 0),
                    "total": token_usage.get("total_tokens", 0),
                }
        update_current_observation(output=content[:500], usage=usage if usage else None)

    @staticmethod
    def _content(response) -> str:
        return response.content if hasattr(response, "content") else str(response)

    def _call(self, user_message: str, memory_context: str) -> MultiRouteDecision:
        heuristic = heuristic_route(user_message)
        if heuristic is not None:
            return heuristic
        try:
            response = self.llm.invoke(self._build_messages(user_message, memory_context))
            content = self._content(response)
            self._record_usage(content, response)
        except Exception as exc:
            logger.error("Router LLM call failed: {}", exc)
            return _fallback_multi(f"Router LLM error: {exc}")
        return self._parse_response(content)

    async def _acall(self, user_message: str, memory_context: str) -> MultiRouteDecision:
        heuristic = heuristic_route(user_message)
        if heuristic is not None:
            return heuristic
        try:
            response = await self.llm.ainvoke(
                self._build_messages(user_message, memory_context)
            )
            content = self._content(response)
            self._record_usage(content, response)
        except Exception as exc:
            logger.error("Router LLM async call failed: {}", exc)
            return _fallback_multi(f"Router LLM error: {exc}")
        return self._parse_response(content)

    def _model_name(self) -> str:
        if hasattr(self.llm, "model_name"):
            return self.llm.model_name
        if hasattr(self.llm, "model"):
            return self.llm.model
        return "unknown"

    def _parse_response(self, raw: str) -> MultiRouteDecision:
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[-1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        text = text.strip()

        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            logger.warning("Router output is not JSON; falling back to direct.")
            return _fallback_multi("Failed to parse router output as JSON.")

        try:
            data = json.loads(text[start : end + 1])
        except json.JSONDecodeError as exc:
            logger.warning("Router JSON parse error: {}", exc)
            return _fallback_multi(f"JSON parse error: {exc}")

        if "routes" in data and isinstance(data["routes"], list):
            route_dicts = data["routes"][:MAX_ROUTES]
        elif "intent" in data:
            route_dicts = [{"route": data["intent"], **data}]
        else:
            route_dicts = [data]

        decisions: list[RouteDecision] = []
        seen_routes: set[str] = set()

        for rd in route_dicts:
            if not isinstance(rd, dict):
                continue
            route = rd.get("route") or rd.get("intent") or "direct"
            if route not in VALID_ROUTES:
                logger.warning("Invalid route '{}'; skipping.", route)
                continue
            if route in seen_routes:
                continue
            seen_routes.add(route)

            decisions.append(
                RouteDecision(
                    route=route,
                    confidence=float(rd.get("confidence", 0.5)),
                    reasoning=rd.get("reasoning", "") or rd.get("reason", "") or "",
                    action=_normalize_action(route, rd.get("action")),
                    params=rd.get("params") or {},
                )
            )

        if not decisions:
            return _fallback_multi("No valid routes parsed.")

        return MultiRouteDecision(decisions=decisions)
