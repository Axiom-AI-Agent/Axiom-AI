"""Supabase registry for ingested tutor documents."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from loguru import logger

from infrastructure.config import SUPABASE_SERVICE_KEY, SUPABASE_URL
from infrastructure.db.supabase_client import get_supabase_client

TABLE = "kb_documents"


def registry_available() -> bool:
    return bool(SUPABASE_URL and SUPABASE_SERVICE_KEY)


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def get_document(*, tenant_id: str, document_id: str) -> dict[str, Any] | None:
    if not registry_available():
        return None
    client = get_supabase_client()
    response = (
        client.table(TABLE)
        .select("*")
        .eq("tenant_id", tenant_id)
        .eq("document_id", document_id)
        .limit(1)
        .execute()
    )
    rows = response.data or []
    return rows[0] if rows else None


def list_documents(
    *,
    tenant_id: str,
    class_id: str | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    if not registry_available():
        return []
    client = get_supabase_client()
    query = (
        client.table(TABLE)
        .select("*")
        .eq("tenant_id", tenant_id)
        .order("updated_at", desc=True)
        .limit(limit)
    )
    if class_id:
        query = query.eq("class_id", class_id)
    response = query.execute()
    return response.data or []


def upsert_document(
    *,
    tenant_id: str,
    class_id: str,
    document_id: str,
    filename: str,
    title: str | None,
    lesson: str | None,
    source_type: str,
    byte_size: int,
    status: str = "pending",
    page_count: int | None = None,
    ocr_pages: int = 0,
    chunks_upserted: int | None = None,
    error: str | None = None,
    warnings: list[str] | None = None,
) -> dict[str, Any] | None:
    if not registry_available():
        return None
    row = {
        "tenant_id": tenant_id,
        "class_id": class_id,
        "document_id": document_id,
        "filename": filename,
        "title": title,
        "lesson": lesson,
        "source_type": source_type,
        "byte_size": byte_size,
        "page_count": page_count,
        "ocr_pages": ocr_pages,
        "chunks_upserted": chunks_upserted,
        "status": status,
        "error": error,
        "warnings": warnings or [],
        "updated_at": _now_iso(),
    }
    client = get_supabase_client()
    response = client.table(TABLE).upsert(row, on_conflict="tenant_id,document_id").execute()
    rows = response.data or []
    return rows[0] if rows else row


def delete_document(*, tenant_id: str, document_id: str) -> bool:
    if not registry_available():
        return False
    client = get_supabase_client()
    response = (
        client.table(TABLE)
        .delete()
        .eq("tenant_id", tenant_id)
        .eq("document_id", document_id)
        .execute()
    )
    deleted = response.data or []
    logger.info("Deleted kb_documents row tenant={} document_id={}", tenant_id, document_id)
    return bool(deleted)


def mark_failed(*, tenant_id: str, document_id: str, error: str) -> None:
    if not registry_available():
        return
    client = get_supabase_client()
    client.table(TABLE).update(
        {"status": "failed", "error": error[:2000], "updated_at": _now_iso()}
    ).eq("tenant_id", tenant_id).eq("document_id", document_id).execute()
