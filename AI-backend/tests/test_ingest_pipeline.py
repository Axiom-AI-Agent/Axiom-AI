"""Ingest pipeline unit tests."""

from __future__ import annotations

import io
import zipfile
from unittest.mock import patch

from services.ingest_service.chunkers import fixed_chunk, parent_child_chunk
from services.ingest_service.pipeline import load_tenant_docs


def _minimal_docx() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("[Content_Types].xml", "<Types/>")
        z.writestr("word/document.xml", "<document/>")
    return buf.getvalue()


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
            "document_id": "doc-fixed",
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
            "document_id": "doc-pc",
        }
    ]
    children, parents = parent_child_chunk(docs)
    assert len(parents) >= 1
    assert len(children) >= 1
    assert children[0]["strategy"] == "child"
    assert children[0]["parent_id"] == parents[0]["parent_id"]


@patch("services.ingest_service.pipeline.upsert_parent_chunks", return_value=1)
@patch("services.ingest_service.pipeline.delete_chunks_by_document_id", return_value=0)
@patch("services.ingest_service.pipeline.upsert_chunks", return_value=3)
@patch("services.ingest_service.pipeline.embed_texts", return_value=[[0.1] * 3, [0.2] * 3, [0.3] * 3])
@patch("services.ingest_service.pipeline.collection_info", return_value={"points_count": 3})
def test_ingest_documents_parent_child(mock_info, mock_embed, mock_upsert, _delete, mock_parents):
    from services.ingest_service.pipeline import ingest_documents

    docs = [
        {
            "url": "u",
            "title": "T",
            "lesson": "1",
            "class_id": "class-a",
            "content": "word " * 5000,
            "document_id": "doc-test",
        }
    ]
    result = ingest_documents(tenant_id="tenant-a", documents=docs, strategy="parent_child")
    assert result["ok"] is True
    assert result["strategy"] == "parent_child"
    assert result["chunks_upserted"] == 3
    assert result["parents_upserted"] == 1
    mock_upsert.assert_called_once()
    mock_parents.assert_called_once()
    upserted_chunks = mock_upsert.call_args.kwargs["chunks"]
    assert "parent_text" not in upserted_chunks[0]


def _fake_ingest_result():
    return {
        "ok": True,
        "tenant_id": "tenant-a",
        "strategy": "parent_child",
        "documents": 1,
        "chunks_upserted": 5,
        "collection": "axiom_kb_tenant_a",
    }


@patch("services.ingest_service.pipeline.collection_info", return_value={"points_count": 10})
@patch("services.ingest_service.pipeline.process_upload_ingest")
@patch("services.ingest_service.pipeline.kb_registry.get_document")
@patch("services.ingest_service.pipeline.kb_registry.upsert_document")
@patch("services.ingest_service.pipeline.ingest_documents")
@patch("services.ingest_service.pipeline.extract_document")
def test_run_upload_ingest_pdf(mock_extract, mock_ingest, _upsert, mock_get, mock_process, _info):
    from services.ingest_service.extractors import ExtractedDoc
    from services.ingest_service.pipeline import run_upload_ingest

    mock_extract.return_value = ExtractedDoc(
        markdown="# Newton Laws\n\n" + "Newton laws notes " * 100,
        source_type="pdf",
        page_count=4,
        ocr_page_count=1,
        warnings=["OCR used on 1 page"],
    )
    mock_ingest.return_value = {
        **_fake_ingest_result(),
        "chunks_deleted": 0,
        "parents_upserted": 1,
    }
    mock_get.return_value = {
        "status": "ready",
        "chunks_upserted": 5,
        "title": "Newton Laws",
        "filename": "notes.pdf",
        "source_type": "pdf",
        "page_count": 4,
        "ocr_pages": 1,
        "warnings": ["OCR used on 1 page"],
    }

    result = run_upload_ingest(
        tenant_id="tenant-a",
        class_id="class-a",
        file_bytes=b"%PDF-1.4 fake",
        filename="notes.pdf",
        title="Newton Laws",
        save_upload=False,
    )
    assert result["document_title"] == "Newton Laws"
    assert result["chunks_upserted"] == 5
    assert result["source_type"] == "pdf"
    assert result["page_count"] == 4
    assert result["ocr_pages"] == 1
    assert result["warnings"] == ["OCR used on 1 page"]
    mock_process.assert_called_once()


@patch("services.ingest_service.pipeline.collection_info", return_value={"points_count": 10})
@patch("services.ingest_service.pipeline.process_upload_ingest")
@patch("services.ingest_service.pipeline.kb_registry.get_document")
@patch("services.ingest_service.pipeline.kb_registry.upsert_document")
@patch("services.ingest_service.pipeline.ingest_documents")
@patch("services.ingest_service.pipeline.extract_document")
def test_run_upload_ingest_docx_titles_from_filename(mock_extract, mock_ingest, _upsert, mock_get, _process, _info):
    from services.ingest_service.extractors import ExtractedDoc
    from services.ingest_service.pipeline import run_upload_ingest

    mock_extract.return_value = ExtractedDoc(
        markdown="## Redox\n\nOxidation is loss of electrons.",
        source_type="docx",
    )
    mock_ingest.return_value = {**_fake_ingest_result(), "chunks_deleted": 0}
    mock_get.return_value = {
        "status": "ready",
        "title": "Lesson 9 Redox",
        "source_type": "docx",
        "page_count": None,
        "chunks_upserted": 5,
        "warnings": [],
    }

    result = run_upload_ingest(
        tenant_id="tenant-a",
        class_id="class-a",
        file_bytes=_minimal_docx(),
        filename="lesson_9-redox.docx",
        save_upload=False,
    )
    assert result["document_title"] == "Lesson 9 Redox"
    assert result["source_type"] == "docx"
    assert result["page_count"] is None


@patch("services.ingest_service.pipeline.collection_info", return_value={"points_count": 10})
@patch("services.ingest_service.pipeline.process_upload_ingest")
@patch("services.ingest_service.pipeline.kb_registry.get_document")
@patch("services.ingest_service.pipeline.kb_registry.upsert_document")
@patch("services.ingest_service.pipeline.ingest_documents")
@patch("services.ingest_service.pipeline.extract_document")
def test_run_pdf_ingest_alias_delegates(mock_extract, mock_ingest, _upsert, mock_get, _process, _info):
    """The old name is kept for one release; callers should move to run_upload_ingest."""
    from services.ingest_service.extractors import ExtractedDoc
    from services.ingest_service.pipeline import run_pdf_ingest

    mock_extract.return_value = ExtractedDoc(markdown="# Notes\n\nbody", source_type="pdf")
    mock_ingest.return_value = {**_fake_ingest_result(), "chunks_deleted": 0}
    mock_get.return_value = {
        "status": "ready",
        "source_type": "pdf",
        "chunks_upserted": 5,
        "warnings": [],
    }

    result = run_pdf_ingest(
        tenant_id="tenant-a",
        class_id="class-a",
        file_bytes=b"%PDF-1.4 fake",
        filename="notes.pdf",
        save_upload=False,
    )
    assert result["source_type"] == "pdf"
