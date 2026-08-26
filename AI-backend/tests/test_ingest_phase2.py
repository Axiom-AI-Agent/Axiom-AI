"""Phase 2 ingest correctness — idempotency, dedup, document registry."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from infrastructure.db.ingest_ids import compute_document_id, point_id_for_chunk


def test_compute_document_id_is_stable():
    content = b"same bytes every time"
    assert compute_document_id(content) == compute_document_id(content)
    assert len(compute_document_id(content)) == 16


def test_point_id_is_deterministic():
    a = point_id_for_chunk(tenant_id="tenant-a", document_id="doc1", chunk_index=3)
    b = point_id_for_chunk(tenant_id="tenant-a", document_id="doc1", chunk_index=3)
    c = point_id_for_chunk(tenant_id="tenant-a", document_id="doc1", chunk_index=4)
    assert a == b
    assert a != c


@patch("services.ingest_service.pipeline.upsert_parent_chunks", return_value=1)
@patch("services.ingest_service.pipeline.upsert_chunks", return_value=2)
@patch("services.ingest_service.pipeline.embed_texts", return_value=[[0.1], [0.2]])
@patch("services.ingest_service.pipeline.collection_info", return_value={"points_count": 2})
@patch("services.ingest_service.pipeline.delete_chunks_by_document_id", return_value=5)
def test_ingest_documents_deletes_before_upsert(mock_delete, _info, _embed, mock_upsert, _parents):
    from services.ingest_service.pipeline import ingest_documents

    docs = [
        {
            "url": "upload://t/a",
            "title": "A",
            "lesson": "1",
            "class_id": "class-a",
            "content": "word " * 500,
            "document_id": "doc123",
        }
    ]
    result = ingest_documents(tenant_id="tenant-a", documents=docs, strategy="parent_child")
    mock_delete.assert_called_once_with(tenant_id="tenant-a", document_id="doc123")
    assert result["chunks_deleted"] == 5
    upserted = mock_upsert.call_args.kwargs["chunks"]
    assert all(c["document_id"] == "doc123" for c in upserted)


@patch("services.ingest_service.pipeline.collection_info", return_value={"points_count": 10})
@patch("services.ingest_service.pipeline.kb_registry.get_document")
def test_run_upload_ingest_skips_unchanged(mock_get, _info):
    from services.ingest_service.pipeline import run_upload_ingest

    file_bytes = b"%PDF-1.4 unchanged"
    document_id = compute_document_id(file_bytes)
    mock_get.return_value = {
        "status": "ready",
        "byte_size": len(file_bytes),
        "document_id": document_id,
        "chunks_upserted": 8,
        "title": "Existing",
        "filename": "notes.pdf",
        "source_type": "pdf",
        "page_count": 2,
        "ocr_pages": 0,
        "warnings": [],
    }

    result = run_upload_ingest(
        tenant_id="tenant-a",
        class_id="class-a",
        file_bytes=file_bytes,
        filename="notes.pdf",
        save_upload=False,
    )
    assert result["skipped"] is True
    assert result["chunks_upserted"] == 8
    assert result["document_id"] == document_id


@patch("infrastructure.db.qdrant_client.get_qdrant_client")
def test_search_chunks_overfetches_before_parent_dedup(mock_get_client):
    from infrastructure.db.qdrant_client import search_chunks

    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    parent = "upload://t/doc::parent::0"
    points = []
    for idx, score in enumerate([0.95, 0.94, 0.93, 0.92]):
        points.append(
            MagicMock(
                score=score,
                payload={
                    "chunk_text": f"child {idx}",
                    "parent_id": parent,
                    "parent_text": "shared parent",
                    "title": "Notes",
                    "class_id": "class-a",
                    "tenant_id": "tenant-a",
                },
            )
        )
    points.append(
        MagicMock(
            score=0.80,
            payload={
                "chunk_text": "other section",
                "parent_id": "upload://t/doc::parent::1",
                "parent_text": "other parent",
                "title": "Notes",
                "class_id": "class-a",
                "tenant_id": "tenant-a",
            },
        )
    )
    mock_client.query_points.return_value = MagicMock(points=points)
    mock_client.get_collections.return_value = MagicMock(collections=[])

    results = search_chunks(
        tenant_id="tenant-a",
        query_vector=[0.1, 0.2],
        top_k=2,
    )

    assert mock_client.query_points.call_args.kwargs["limit"] == 6
    assert len(results) == 2
    parent_ids = {row.get("parent_id") for row in results}
    assert len(parent_ids) == 2


@patch("infrastructure.db.qdrant_client.get_qdrant_client")
def test_search_chunks_hydrates_parent_text_from_parent_points(mock_get_client):
    from infrastructure.db.ingest_ids import point_id_for_parent
    from infrastructure.db.qdrant_client import search_chunks

    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    parent = "upload://t/doc::parent::0"
    mock_client.query_points.return_value = MagicMock(
        points=[
            MagicMock(
                score=0.95,
                payload={
                    "chunk_text": "child snippet",
                    "parent_id": parent,
                    "title": "Notes",
                    "class_id": "class-a",
                    "tenant_id": "tenant-a",
                    "strategy": "child",
                },
            )
        ]
    )
    collection = MagicMock()
    collection.name = "axiom_kb_tenant_a"
    mock_client.get_collections.return_value = MagicMock(collections=[collection])
    mock_client.retrieve.return_value = [
        MagicMock(
            payload={
                "parent_id": parent,
                "chunk_text": "full parent section text",
            }
        )
    ]

    results = search_chunks(
        tenant_id="tenant-a",
        query_vector=[0.1, 0.2],
        top_k=1,
    )

    assert results[0]["parent_text"] == "full parent section text"
    mock_client.retrieve.assert_called_once()
    assert mock_client.retrieve.call_args.kwargs["ids"] == [
        point_id_for_parent(tenant_id="tenant-a", parent_id=parent)
    ]
