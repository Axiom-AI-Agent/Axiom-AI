"""Multi-format ingest upload endpoint tests."""

from __future__ import annotations

import io
import zipfile
from unittest.mock import patch


def _ingest_result(**overrides):
    result = {
        "ok": True,
        "tenant_id": "tenant-demo-physics",
        "strategy": "parent_child",
        "documents": 0,
        "chunks_upserted": 0,
        "collection": "axiom_kb_tenant_demo_physics",
        "document_title": "Lesson 7 Notes",
        "source_filename": "lesson7.pdf",
        "warnings": [],
        "document_id": "abc123",
        "skipped": False,
        **{"async": True},
        "status": "pending",
    }
    result.update(overrides)
    return result


def _post(client, *, filename, content, content_type, tenant_id="tenant-demo-physics"):
    return client.post(
        f"/tools/ingest/upload?tenant_id={tenant_id}",
        data={
            "tenant_id": tenant_id,
            "class_id": "class-physics-al-2026",
        },
        files={"file": (filename, content, content_type)},
        headers={"X-Tenant-ID": tenant_id},
    )


def _minimal_docx() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("[Content_Types].xml", "<Types/>")
        z.writestr("word/document.xml", "<document/>")
    return buf.getvalue()


@patch("api.routers.tools.ingest.process_upload_ingest")
@patch("api.routers.tools.ingest.prepare_upload_ingest")
def test_ingest_upload_pdf(mock_prepare, _process, client):
    mock_prepare.return_value = _ingest_result()
    response = client.post(
        "/tools/ingest/upload?tenant_id=tenant-demo-physics",
        data={
            "tenant_id": "tenant-demo-physics",
            "class_id": "class-physics-al-2026",
            "title": "Lesson 7 Notes",
            "lesson": "7",
        },
        files={"file": ("lesson7.pdf", b"%PDF-1.4 test content", "application/pdf")},
        headers={"X-Tenant-ID": "tenant-demo-physics"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["strategy"] == "parent_child"
    assert body["status"] == "pending"
    assert body["async"] is True
    assert body["document_id"] == "abc123"
    assert body["document_title"] == "Lesson 7 Notes"


@patch("api.routers.tools.ingest.process_upload_ingest")
@patch("api.routers.tools.ingest.prepare_upload_ingest")
def test_ingest_upload_skipped_sync(mock_prepare, _process, client):
    mock_prepare.return_value = _ingest_result(
        skipped=True,
        **{"async": False},
        status="ready",
        documents=0,
        chunks_upserted=12,
        source_type="pdf",
    )
    response = client.post(
        "/tools/ingest/upload?tenant_id=tenant-demo-physics",
        data={
            "tenant_id": "tenant-demo-physics",
            "class_id": "class-physics-al-2026",
        },
        files={"file": ("lesson7.pdf", b"%PDF-1.4 test content", "application/pdf")},
        headers={"X-Tenant-ID": "tenant-demo-physics"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["skipped"] is True
    assert body["async"] is False
    _process.assert_not_called()


@patch("api.routers.tools.ingest.process_upload_ingest")
@patch("api.routers.tools.ingest.prepare_upload_ingest")
def test_ingest_upload_docx(mock_prepare, _process, client):
    mock_prepare.return_value = _ingest_result(
        source_filename="lesson8.docx",
        warnings=["No Word heading styles found"],
    )
    response = _post(
        client,
        filename="lesson8.docx",
        content=_minimal_docx(),
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    assert response.status_code == 200
    body = response.json()
    assert body["warnings"] == ["No Word heading styles found"]


@patch("api.routers.tools.ingest.process_upload_ingest")
@patch("api.routers.tools.ingest.prepare_upload_ingest")
def test_ingest_upload_markdown(mock_prepare, _process, client):
    mock_prepare.return_value = _ingest_result(source_filename="notes.md")
    response = _post(
        client,
        filename="notes.md",
        content=b"# Kinematics\n\nVelocity is displacement over time.",
        content_type="text/markdown",
    )
    assert response.status_code == 200
    assert response.json()["source_filename"] == "notes.md"


@patch("services.ingest_service.pipeline.kb_registry.mark_failed")
@patch("services.ingest_service.pipeline.kb_registry.upsert_document")
@patch("services.ingest_service.pipeline.kb_registry.get_document", return_value=None)
def test_ingest_upload_rejects_legacy_doc(_get, _upsert, _fail, client):
    response = _post(
        client,
        filename="notes.doc",
        content=b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 64,
        content_type="application/msword",
    )
    assert response.status_code == 422
    assert ".docx" in response.json()["detail"]


@patch("services.ingest_service.pipeline.kb_registry.mark_failed")
@patch("services.ingest_service.pipeline.kb_registry.upsert_document")
@patch("services.ingest_service.pipeline.kb_registry.get_document", return_value=None)
def test_ingest_upload_rejects_unknown_binary(_get, _upsert, _fail, client):
    response = _post(
        client,
        filename="image.png",
        content=b"\x89PNG\r\n\x1a\n" + b"\x00\x01\x02\x03" * 16,
        content_type="image/png",
    )
    assert response.status_code == 422


def test_ingest_upload_rejects_empty_file(client):
    response = _post(client, filename="empty.pdf", content=b"", content_type="application/pdf")
    assert response.status_code == 422


def test_ingest_upload_rejects_tenant_mismatch(client):
    response = client.post(
        "/tools/ingest/upload?tenant_id=tenant-demo-physics",
        data={
            "tenant_id": "tenant-other",
            "class_id": "class-physics-al-2026",
        },
        files={"file": ("notes.pdf", b"%PDF-1.4 test", "application/pdf")},
        headers={"X-Tenant-ID": "tenant-demo-physics"},
    )
    assert response.status_code == 403


@patch("api.routers.tools.ingest.process_upload_ingest")
@patch("api.routers.tools.ingest.prepare_upload_ingest")
def test_ingest_upload_trusts_content_over_extension(mock_prepare, _process, client):
    mock_prepare.return_value = _ingest_result(source_filename="mislabelled.docx")
    response = _post(
        client,
        filename="mislabelled.docx",
        content=b"%PDF-1.4 test content",
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    assert response.status_code == 200


@patch("api.routers.tools.ingest.kb_registry.get_document")
def test_get_ingest_document(mock_get, client):
    mock_get.return_value = {
        "id": "row-1",
        "tenant_id": "tenant-demo-physics",
        "class_id": "class-physics-al-2026",
        "document_id": "abc123",
        "filename": "lesson7.pdf",
        "title": "Lesson 7",
        "lesson": "7",
        "source_type": "pdf",
        "byte_size": 1000,
        "page_count": 3,
        "ocr_pages": 0,
        "chunks_upserted": 12,
        "status": "embedding",
        "error": None,
        "warnings": [],
    }
    response = client.get(
        "/tools/ingest/documents/abc123?tenant_id=tenant-demo-physics",
        headers={"X-Tenant-ID": "tenant-demo-physics"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["document"]["status"] == "embedding"


@patch("api.routers.tools.ingest.kb_registry.list_documents")
def test_list_ingest_documents(mock_list, client):
    mock_list.return_value = [
        {
            "id": "row-1",
            "tenant_id": "tenant-demo-physics",
            "class_id": "class-physics-al-2026",
            "document_id": "abc123",
            "filename": "lesson7.pdf",
            "title": "Lesson 7",
            "lesson": "7",
            "source_type": "pdf",
            "byte_size": 1000,
            "page_count": 3,
            "ocr_pages": 0,
            "chunks_upserted": 12,
            "status": "ready",
            "error": None,
            "warnings": [],
        }
    ]
    response = client.get(
        "/tools/ingest/documents?tenant_id=tenant-demo-physics",
        headers={"X-Tenant-ID": "tenant-demo-physics"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert len(body["documents"]) == 1
    assert body["documents"][0]["document_id"] == "abc123"


@patch("api.routers.tools.ingest.delete_document_ingest")
def test_delete_ingest_document(mock_delete, client):
    mock_delete.return_value = {
        "ok": True,
        "tenant_id": "tenant-demo-physics",
        "document_id": "abc123",
        "chunks_deleted": 12,
        "registry_deleted": True,
        "points_count": 0,
    }
    response = client.delete(
        "/tools/ingest/documents/abc123?tenant_id=tenant-demo-physics",
        headers={"X-Tenant-ID": "tenant-demo-physics"},
    )
    assert response.status_code == 200
    assert response.json()["chunks_deleted"] == 12
