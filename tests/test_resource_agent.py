"""Resource agent node tests (direct tool clients, no MCP)."""

from __future__ import annotations

import json
from typing import Any

import pytest
from langchain_core.messages import HumanMessage

from agents.nodes.resource_agent import DirectDriveClient, DirectRagClient, ResourceAgent


class FakeDrive:
    async def drive_search(self, *, tenant_id: str, query: str, folder: str | None = "papers") -> dict[str, Any]:
        return {
            "ok": True,
            "files": [
                {
                    "name": "2024-model-paper-physics.pdf",
                    "link": "https://drive.example/paper.pdf",
                    "folder": folder or "papers",
                }
            ],
        }


class FakeRag:
    async def kb_search(self, *, tenant_id: str, query: str) -> dict[str, Any]:
        return {
            "ok": True,
            "answer": "Velocity is the rate of change of displacement.",
            "citations": [{"title": "Lesson 5 — Velocity", "lesson": "5", "score": 0.88}],
            "num_docs": 1,
        }


@pytest.mark.asyncio
async def test_resource_agent_drive_path():
    agent = ResourceAgent(drive=FakeDrive(), rag=FakeRag())
    state = {
        "tenant_id": "tenant-demo-physics",
        "tenant_name": "Demo Physics",
        "messages": [HumanMessage(content="Can I get last week's physics paper?")],
    }
    result = await agent.run(state)
    assert result.sub_path == "drive"
    assert "2024-model-paper" in result.answer or "drive.example" in result.answer


@pytest.mark.asyncio
async def test_resource_agent_rag_path():
    agent = ResourceAgent(drive=FakeDrive(), rag=FakeRag())
    state = {
        "tenant_id": "tenant-demo-physics",
        "messages": [HumanMessage(content="Explain velocity from lesson 5")],
    }
    result = await agent.run(state)
    assert result.sub_path == "rag"
    assert "velocity" in result.answer.lower()
