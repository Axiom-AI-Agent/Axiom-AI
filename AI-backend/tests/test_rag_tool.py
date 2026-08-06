"""RAG tool unit tests."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from agents.tools.rag_tool import RagTool


def test_kb_search_empty_collection():
    tool = RagTool(embedder=MagicMock(), llm=MagicMock())
    with patch("agents.tools.rag_tool.count_points", return_value=0):
        raw = tool.kb_search(tenant_id="tenant-a", query="explain velocity")
    payload = json.loads(raw)
    assert payload["ok"] is True
    assert "don't have tutor notes" in payload["answer"].lower()


def test_kb_search_requires_tenant():
    tool = RagTool()
    raw = tool.kb_search(tenant_id="", query="velocity")
    payload = json.loads(raw)
    assert payload["ok"] is False


def test_kb_search_with_mock_service():
    tool = RagTool(embedder=MagicMock(), llm=MagicMock())
    mock_result = {
        "answer": "Velocity is displacement over time.",
        "citations": [{"title": "Lesson 5", "lesson": "5", "score": 0.9}],
        "num_docs": 1,
    }
    with patch("agents.tools.rag_tool.count_points", return_value=3):
        with patch("agents.tools.rag_tool.RAGService") as mock_cls:
            mock_cls.return_value.generate.return_value = mock_result
            raw = tool.kb_search(tenant_id="tenant-a", query="explain velocity")
    payload = json.loads(raw)
    assert payload["ok"] is True
    assert "velocity" in payload["answer"].lower()
    assert payload["citations"][0]["lesson"] == "5"


def test_kb_ingest_status():
    tool = RagTool()
    with patch("agents.tools.rag_tool.count_points", return_value=12):
        with patch(
            "agents.tools.rag_tool.collection_info",
            return_value={"collection": "axiom_kb_tenant_a", "points_count": 12},
        ):
            raw = tool.kb_ingest_status(tenant_id="tenant-a")
    payload = json.loads(raw)
    assert payload["ok"] is True
    assert payload["points_count"] == 12
    assert payload["ready"] is True
