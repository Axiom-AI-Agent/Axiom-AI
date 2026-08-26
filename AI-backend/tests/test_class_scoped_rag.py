"""Class-scoped RAG retrieval tests."""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import HumanMessage

from agents.nodes.resource_agent import ResourceAgent
from agents.tools.rag_tool import RagTool


class TrackingRag:
    def __init__(self) -> None:
        self.last_class_ids: list[str] | None = None

    async def kb_search(
        self,
        *,
        tenant_id: str,
        query: str,
        class_ids: list[str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        self.last_class_ids = class_ids
        return {"ok": True, "answer": "Physics only.", "citations": []}


class FakeDrive:
    async def drive_search(self, **kwargs) -> dict[str, Any]:
        return {"ok": True, "files": []}

    async def drive_list(self, **kwargs) -> dict[str, Any]:
        return {"ok": True, "files": []}


@pytest.mark.asyncio
async def test_resource_agent_passes_enrolled_class_ids_to_rag():
    rag = TrackingRag()
    agent = ResourceAgent(drive=FakeDrive(), rag=rag)
    state = {
        "tenant_id": "tenant-demo-physics",
        "is_enrolled": True,
        "enrolled_class_ids": ["class-physics-al-2026"],
        "messages": [HumanMessage(content="Explain velocity")],
    }
    await agent.run(state)
    assert rag.last_class_ids == ["class-physics-al-2026"]


@pytest.mark.asyncio
async def test_resource_agent_blocks_enrolled_without_class_ids():
    agent = ResourceAgent(drive=FakeDrive(), rag=TrackingRag())
    state = {
        "tenant_id": "tenant-demo-physics",
        "tenant_name": "Demo Physics",
        "is_enrolled": True,
        "enrolled_class_ids": [],
        "messages": [HumanMessage(content="Explain velocity")],
    }
    result = await agent.run(state)
    assert "enrollment" in result.answer.lower()


@patch("infrastructure.db.qdrant_client.get_qdrant_client")
def test_search_chunks_applies_class_id_filter(mock_get_client):
    from infrastructure.config import qdrant_collection_for_tenant
    from infrastructure.db.qdrant_client import search_chunks

    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_client.query_points.return_value = MagicMock(points=[])
    collection = MagicMock()
    collection.name = qdrant_collection_for_tenant("tenant-demo-physics")
    mock_client.get_collections.return_value = MagicMock(collections=[collection])

    search_chunks(
        tenant_id="tenant-demo-physics",
        query_vector=[0.1, 0.2],
        class_ids=["class-physics-al-2026"],
    )

    call_kwargs = mock_client.query_points.call_args.kwargs
    assert call_kwargs["query_filter"] is not None
    indexed_fields = [
        call.kwargs["field_name"] for call in mock_client.create_payload_index.call_args_list
    ]
    assert indexed_fields == ["strategy", "class_id"]
    assert all(
        call.kwargs["field_schema"] == "keyword"
        for call in mock_client.create_payload_index.call_args_list
    )


@patch("infrastructure.db.qdrant_client.get_qdrant_client")
def test_search_chunks_ensures_strategy_index_without_class_filter(mock_get_client):
    from infrastructure.config import qdrant_collection_for_tenant
    from infrastructure.db.qdrant_client import search_chunks

    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_client.query_points.return_value = MagicMock(points=[])
    collection = MagicMock()
    collection.name = qdrant_collection_for_tenant("tenant-demo-physics")
    mock_client.get_collections.return_value = MagicMock(collections=[collection])

    search_chunks(
        tenant_id="tenant-demo-physics",
        query_vector=[0.1, 0.2],
    )

    indexed_fields = [
        call.kwargs["field_name"] for call in mock_client.create_payload_index.call_args_list
    ]
    assert indexed_fields == ["strategy"]


def test_kb_search_forwards_class_ids_to_rag_service():
    tool = RagTool(embedder=MagicMock(), llm=MagicMock())
    with patch("agents.tools.rag_tool.RAGService") as mock_cls:
        mock_cls.return_value.generate.return_value = {
            "answer": "Scoped answer.",
            "citations": [],
            "num_docs": 1,
        }
        raw = tool.kb_search(
            tenant_id="tenant-a",
            query="explain velocity",
            class_ids=["class-physics-al-2026"],
        )
    payload = json.loads(raw)
    assert payload["ok"] is True
    assert mock_cls.call_args.kwargs["class_ids"] == ["class-physics-al-2026"]
