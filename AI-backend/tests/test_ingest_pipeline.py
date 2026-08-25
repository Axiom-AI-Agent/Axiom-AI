"""Ingest pipeline unit tests."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from services.ingest_service.chunkers import fixed_chunk, parent_child_chunk
from services.ingest_service.pipeline import load_tenant_docs


def test_load_tenant_docs_demo_physics(
    tmp_path,
):
    (
        tmp_path
        / "lesson_5_velocity.md"
    ).write_text(
        (
            "# Lesson 5 Velocity\n\n"
            "Velocity is the rate of "
            "change of displacement."
        ),
        encoding="utf-8",
    )

    (
        tmp_path
        / "lesson_6_acceleration.md"
    ).write_text(
        (
            "# Lesson 6 Acceleration\n\n"
            "Acceleration is the rate "
            "of change of velocity."
        ),
        encoding="utf-8",
    )

    docs = load_tenant_docs(
        tenant_id=(
            "tenant-demo-physics"
        ),
        tenant_slug=(
            "demo-physics"
        ),
        kb_path=tmp_path,
    )

    assert len(docs) >= 2

    assert any(
        (
            "velocity"
            in d["title"].lower()
            or
            "velocity"
            in d["content"].lower()
        )
        for d in docs
    )
    assert len(docs) >= 2
    assert any("velocity" in d["title"].lower() or "velocity" in d["content"].lower() for d in docs)


def test_fixed_chunk_produces_chunks():
    docs = [
        {
            "url": "internal://test/doc",
            "title": "Test",
            "lesson": "1",
            "content": "A" * 2000,
        }
    ]
    chunks = fixed_chunk(docs)
    assert len(chunks) >= 2
    assert chunks[0]["strategy"] == "fixed"


def test_parent_child_chunk_links_parent_text():
    docs = [
        {
            "url": "internal://test/doc",
            "title": "Lesson Notes",
            "lesson": "5",
            "content": "Velocity is displacement over time. " * 200,
        }
    ]
    children, parents = parent_child_chunk(docs)
    assert len(parents) >= 1
    assert len(children) >= 1
    assert children[0]["strategy"] == "child"
    assert children[0]["parent_id"] == parents[0]["parent_id"]


@patch("services.ingest_service.pipeline.upsert_chunks", return_value=3)
@patch("services.ingest_service.pipeline.embed_texts", return_value=[[0.1] * 3, [0.2] * 3, [0.3] * 3])
@patch("services.ingest_service.pipeline.collection_info", return_value={"points_count": 3})
def test_ingest_documents_parent_child(mock_info, mock_embed, mock_upsert):
    from services.ingest_service.pipeline import ingest_documents

    docs = [{"url": "u", "title": "T", "lesson": "1", "class_id": "class-a", "content": "word " * 5000}]
    result = ingest_documents(tenant_id="tenant-a", documents=docs, strategy="parent_child")
    assert result["ok"] is True
    assert result["strategy"] == "parent_child"
    assert result["chunks_upserted"] == 3
    mock_upsert.assert_called_once()
    upserted_chunks = mock_upsert.call_args.kwargs["chunks"]
    assert upserted_chunks[0].get("parent_text")


@patch("services.ingest_service.pipeline.ingest_documents")
@patch("services.ingest_service.pdf_loader.extract_pdf_text", return_value="Newton laws notes " * 100)
def test_run_pdf_ingest(mock_extract, mock_ingest):
    from services.ingest_service.pipeline import run_pdf_ingest

    mock_ingest.return_value = {
        "ok": True,
        "tenant_id": "tenant-a",
        "strategy": "parent_child",
        "documents": 1,
        "chunks_upserted": 5,
        "collection": "axiom_kb_tenant_a",
    }
    result = run_pdf_ingest(
        tenant_id="tenant-a",
        class_id="class-a",
        file_bytes=b"%PDF-1.4 fake",
        filename="notes.pdf",
        title="Newton Laws",
        save_upload=False,
    )
    assert result["document_title"] == "Newton Laws"
    assert result["chunks_upserted"] == 5
    mock_ingest.assert_called_once()
