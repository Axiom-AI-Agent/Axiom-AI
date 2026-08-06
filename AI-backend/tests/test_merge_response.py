"""Merge response node tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from langchain_core.messages import HumanMessage

from agents.orchestrator import AgentOrchestrator


@pytest.mark.asyncio
async def test_merge_single_fragment_passthrough():
    llm = MagicMock()
    merge_llm = MagicMock()
    orchestrator = AgentOrchestrator(llm, llm_merge=merge_llm)

    state = {
        "messages": [HumanMessage(content="Hello")],
        "agent_outputs": [
            {"route": "direct", "answer": "Hi! How can I help?", "tool_output": ""}
        ],
    }
    out = await orchestrator.merge_responses_node(state)
    assert out["final_answer"] == "Hi! How can I help?"
    merge_llm.ainvoke.assert_not_called()


@pytest.mark.asyncio
async def test_merge_multiple_fragments_uses_gemini():
    llm = MagicMock()
    merge_llm = MagicMock()
    merged = MagicMock()
    merged.content = "Combined tuition reply"
    merge_llm.ainvoke = AsyncMock(return_value=merged)
    orchestrator = AgentOrchestrator(llm, llm_merge=merge_llm)

    state = {
        "messages": [HumanMessage(content="I want papers and to enroll")],
        "memory_context": "(none)",
        "agent_outputs": [
            {"route": "admissions", "answer": "Admissions stub", "tool_output": ""},
            {"route": "resource", "answer": "Resource stub", "tool_output": ""},
        ],
    }
    out = await orchestrator.merge_responses_node(state)
    assert out["final_answer"] == "Combined tuition reply"
    merge_llm.ainvoke.assert_called_once()
