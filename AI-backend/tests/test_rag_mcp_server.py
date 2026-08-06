"""RAG MCP server — tool surface (same logic as axiom-rag stdio server)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from agents.tools.rag_tool import RagTool


def test_rag_mcp_kb_search_empty_collection():
    import mcp_servers.rag_server as rag_server

    rag_server._tool = RagTool(embedder=MagicMock(), llm=MagicMock())
    with patch("agents.tools.rag_tool.count_points", return_value=0):
        raw = rag_server.kb_search(tenant_id="tenant-demo-physics", query="explain velocity")
    payload = json.loads(raw)
    assert payload["ok"] is True
    assert payload["num_docs"] == 0


def test_rag_mcp_kb_search_with_citations():
    import mcp_servers.rag_server as rag_server

    rag_server._tool = RagTool(embedder=MagicMock(), llm=MagicMock())
    mock_result = {
        "answer": "Velocity is displacement over time.",
        "citations": [{"title": "Lesson 5 — Velocity", "lesson": "5", "score": 0.9}],
        "num_docs": 1,
    }
    with patch("agents.tools.rag_tool.count_points", return_value=2):
        with patch("agents.tools.rag_tool.RAGService") as mock_cls:
            mock_cls.return_value.generate.return_value = mock_result
            raw = rag_server.kb_search(
                tenant_id="tenant-demo-physics",
                query="Explain velocity from the tutor notes",
            )
    payload = json.loads(raw)
    assert payload["ok"] is True
    assert "velocity" in payload["answer"].lower()
    assert payload["citations"][0]["lesson"] == "5"


def test_rag_mcp_kb_ingest_status():
    import mcp_servers.rag_server as rag_server

    rag_server._tool = RagTool()
    with patch("agents.tools.rag_tool.count_points", return_value=4):
        with patch(
            "agents.tools.rag_tool.collection_info",
            return_value={"collection": "axiom_kb_tenant_demo_physics", "points_count": 4},
        ):
            raw = rag_server.kb_ingest_status(tenant_id="tenant-demo-physics")
    payload = json.loads(raw)
    assert payload["ok"] is True
    assert payload["ready"] is True
    assert payload["points_count"] == 4


def test_rag_mcp_tenant_collections_differ():
    import mcp_servers.rag_server as rag_server

    from infrastructure.config import qdrant_collection_for_tenant

    assert qdrant_collection_for_tenant("tenant-demo-physics") != qdrant_collection_for_tenant(
        "tenant-demo-chemistry"
    )

    rag_server._tool = RagTool()
    with patch("agents.tools.rag_tool.count_points", side_effect=[2, 5]):
        with patch(
            "agents.tools.rag_tool.collection_info",
            side_effect=[
                {"collection": "axiom_kb_tenant_demo_physics", "points_count": 2},
                {"collection": "axiom_kb_tenant_demo_chemistry", "points_count": 5},
            ],
        ):
            raw_physics = rag_server.kb_ingest_status(tenant_id="tenant-demo-physics")
            raw_chemistry = rag_server.kb_ingest_status(tenant_id="tenant-demo-chemistry")

    assert json.loads(raw_physics)["points_count"] == 2
    assert json.loads(raw_chemistry)["points_count"] == 5
