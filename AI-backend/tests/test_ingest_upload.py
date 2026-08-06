"""PDF ingest upload endpoint tests."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@patch("api.routers.tools.ingest.run_pdf_ingest")
def test_ingest_upload_pdf(mock_ingest, client):
    mock_ingest.return_value = {
        "ok": True,
        "tenant_id": "tenant-demo-physics",
        "strategy": "parent_child",
        "documents": 1,
        "chunks_upserted": 12,
        "collection": "axiom_kb_tenant_demo_physics",
        "points_count": 12,
        "document_title": "Lesson 7 Notes",
        "source_filename": "lesson7.pdf",
    }
    response = client.post(
        "/tools/ingest/upload",
        data={"tenant_id": "tenant-demo-physics", "title": "Lesson 7 Notes", "lesson": "7"},
        files={"file": ("lesson7.pdf", b"%PDF-1.4 test content", "application/pdf")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["strategy"] == "parent_child"
    assert body["chunks_upserted"] == 12
    assert body["document_title"] == "Lesson 7 Notes"


def test_ingest_upload_rejects_non_pdf(client):
    response = client.post(
        "/tools/ingest/upload",
        data={"tenant_id": "tenant-demo-physics"},
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 422


def test_ingest_upload_rejects_empty_file(client):
    response = client.post(
        "/tools/ingest/upload",
        data={"tenant_id": "tenant-demo-physics"},
        files={"file": ("empty.pdf", b"", "application/pdf")},
    )
    assert response.status_code == 422
