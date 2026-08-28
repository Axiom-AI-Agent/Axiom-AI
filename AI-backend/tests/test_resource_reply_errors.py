"""User-facing resource agent reply error sanitization."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import HumanMessage

from agents.nodes.resource_agent import ResourceAgent
from agents.prompts.agent_prompts import (
    build_resource_drive_list_reply,
    build_resource_drive_reply,
    build_resource_rag_reply,
)
from agents.tools.rag_tool import RagTool


def test_build_resource_rag_reply_hides_internal_error():
    reply = build_resource_rag_reply(
        answer="",
        error='Unexpected Response: 400 (Bad Request) Raw response content: b\'{"status":{"error":"Bad request"}}\'',
    )
    assert "400" not in reply
    assert "Bad Request" not in reply
    assert "couldn't search the tutor notes" in reply.lower()


def test_build_resource_drive_reply_hides_internal_error():
    reply = build_resource_drive_reply(
        files=[],
        query="physics paper",
        error="Drive API timeout after 30s",
    )
    assert "timeout" not in reply.lower()
    assert "couldn't search for files" in reply.lower()


def test_build_resource_drive_list_reply_omits_links():
    reply = build_resource_drive_list_reply(
        files=[
            {"name": "tute-01.pdf", "link": "https://drive.example/secret", "folder": "papers"},
        ],
        folder="papers",
    )
    assert "1. tute-01.pdf" in reply
    assert "https://drive.example/secret" not in reply
    assert "number" in reply.lower()


def test_build_resource_drive_list_reply_tags_union_classes():
    reply = build_resource_drive_list_reply(
        files=[
            {"name": "phys.pdf", "class_name": "A/L Physics 2026"},
            {"name": "chem.pdf", "class_name": "A/L Chemistry 2026"},
        ],
        folder="papers",
    )
    assert "1. phys.pdf (A/L Physics 2026)" in reply
    assert "2. chem.pdf (A/L Chemistry 2026)" in reply


def test_kb_search_returns_generic_error_code():
    tool = RagTool(embedder=MagicMock(), llm=MagicMock())
    with patch("agents.tools.rag_tool.count_points", return_value=3):
        with patch("agents.tools.rag_tool.RAGService") as mock_cls:
            mock_cls.return_value.generate.side_effect = RuntimeError(
                'Unexpected Response: 400 (Bad Request) class_id index missing'
            )
            raw = tool.kb_search(
                tenant_id="tenant-a",
                query="explain velocity",
                class_ids=["class-physics-al-2026"],
            )
    payload = json.loads(raw)
    assert payload["ok"] is False
    assert payload["error"] == "search_unavailable"
    assert "400" not in payload["error"]


class FakeDrive:
    async def drive_search(self, **kwargs):
        return {"ok": True, "files": []}

    async def drive_list(self, **kwargs):
        return {"ok": True, "files": []}


class ErrorRag:
    async def kb_search(self, **kwargs):
        return {"ok": False, "error": "search_unavailable", "answer": "", "citations": []}


@pytest.mark.asyncio
async def test_resource_agent_rag_path_hides_search_failure():
    agent = ResourceAgent(drive=FakeDrive(), rag=ErrorRag())
    state = {
        "tenant_id": "tenant-demo-physics",
        "is_enrolled": True,
        "enrolled_class_ids": ["class-physics-al-2026"],
        "messages": [HumanMessage(content="Explain velocity from the tutor notes")],
    }
    result = await agent.run(state)
    assert "search_unavailable" not in result.answer
    assert "400" not in result.answer
    assert "tutor" in result.answer.lower()
