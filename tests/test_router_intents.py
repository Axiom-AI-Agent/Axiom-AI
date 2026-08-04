"""Router intent classification tests."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from agents.router import QueryRouter


def _router_with_content(content: str) -> QueryRouter:
    llm = MagicMock()
    response = MagicMock()
    response.content = content
    llm.invoke.return_value = response
    llm.ainvoke = AsyncMock(return_value=response)
    return QueryRouter(llm)


@pytest.mark.parametrize(
    ("message", "expected_route"),
    [
        ("hi", "direct"),
        ("I want to join A/L Physics", "admissions"),
        ("Do you have past papers?", "resource"),
        ("I sent my bank slip", "payment_check"),
        ("Can I speak to the tutor?", "escalation"),
    ],
)
@pytest.mark.asyncio
async def test_router_intents(message: str, expected_route: str):
    payload = json.dumps(
        {
            "routes": [
                {
                    "route": expected_route,
                    "action": "general",
                    "params": {},
                    "confidence": 0.9,
                    "reasoning": "test",
                }
            ]
        }
    )
    router = _router_with_content(payload)
    result = await router.aroute(message, "")
    assert result.primary.route == expected_route
