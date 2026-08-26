"""Document ingest — PDF/DOCX/Markdown upload → parent-child chunk → Qdrant."""

from __future__ import annotations

import asyncio
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, Query, UploadFile

from api.schemas import (
    IngestDocumentDeleteResponse,
    IngestDocumentListResponse,
    IngestDocumentResponse,
    IngestUploadResponse,
    KbDocumentRecord,
)
from api.tenant_scope import DashboardTenant, assert_form_tenant
from infrastructure.config import INGEST_MAX_UPLOAD_MB
from infrastructure.db import kb_documents as kb_registry
from services.ingest_service.extractors import SUPPORTED_EXTENSIONS, ExtractionError
from services.ingest_service.pipeline import (
    delete_document_ingest,
    prepare_upload_ingest,
    process_upload_ingest,
)

router = APIRouter(prefix="/tools/ingest", tags=["Tools — Ingest"])

MAX_UPLOAD_BYTES = max(INGEST_MAX_UPLOAD_MB.values()) * 1024 * 1024


def _to_record(row: dict) -> KbDocumentRecord:
    warnings = row.get("warnings") or []
    if isinstance(warnings, str):
        warnings = [warnings]
    return KbDocumentRecord(
        id=str(row.get("id") or ""),
        tenant_id=str(row.get("tenant_id") or ""),
        class_id=str(row.get("class_id") or ""),
        document_id=str(row.get("document_id") or ""),
        filename=str(row.get("filename") or ""),
        title=row.get("title"),
        lesson=row.get("lesson"),
        source_type=str(row.get("source_type") or ""),
        byte_size=int(row.get("byte_size") or 0),
        page_count=row.get("page_count"),
        ocr_pages=int(row.get("ocr_pages") or 0),
        chunks_upserted=row.get("chunks_upserted"),
        status=str(row.get("status") or ""),
        error=row.get("error"),
        warnings=list(warnings),
        created_at=row.get("created_at"),
        updated_at=row.get("updated_at"),
    )


@router.get("/documents", response_model=IngestDocumentListResponse)
async def list_documents(
    tenant: DashboardTenant,
    class_id: Optional[str] = Query(None, description="Filter by class id"),
) -> IngestDocumentListResponse:
    """List ingested documents for a tenant from the kb_documents registry."""
    rows = kb_registry.list_documents(
        tenant_id=tenant.tenant_id,
        class_id=class_id.strip() if class_id else None,
    )
    return IngestDocumentListResponse(
        tenant_id=tenant.tenant_id,
        documents=[_to_record(row) for row in rows],
    )


@router.get("/documents/{document_id}", response_model=IngestDocumentResponse)
async def get_document(
    document_id: str,
    tenant: DashboardTenant,
) -> IngestDocumentResponse:
    """Poll ingest status for a single document by content-hash id."""
    row = kb_registry.get_document(tenant_id=tenant.tenant_id, document_id=document_id.strip())
    if not row:
        raise HTTPException(status_code=404, detail=f"Document not found: {document_id}")
    return IngestDocumentResponse(tenant_id=tenant.tenant_id, document=_to_record(row))


@router.delete("/documents/{document_id}", response_model=IngestDocumentDeleteResponse)
async def delete_document(
    document_id: str,
    tenant: DashboardTenant,
) -> IngestDocumentDeleteResponse:
    """Delete a document's Qdrant vectors and registry row."""
    try:
        result = await asyncio.to_thread(
            delete_document_ingest,
            tenant_id=tenant.tenant_id,
            document_id=document_id.strip(),
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return IngestDocumentDeleteResponse(**result)


@router.post("/upload", response_model=IngestUploadResponse)
async def upload_document(
    tenant: DashboardTenant,
    background_tasks: BackgroundTasks,
    tenant_id: str = Form(..., description="Tenant id, e.g. tenant-demo-physics"),
    class_id: str = Form(..., description="Subject class id, e.g. class-physics-al-2026"),
    file: UploadFile = File(..., description="Tutor note — PDF, Word (.docx) or Markdown"),
    title: Optional[str] = Form(None, description="Optional document title"),
    lesson: Optional[str] = Form(None, description="Optional lesson label for citations"),
    force: bool = Form(False, description="Re-ingest even when file bytes are unchanged"),
) -> IngestUploadResponse:
    """
    Upload a tutor document for async ingest.

    Returns immediately with ``status=pending`` while extraction, chunking and
    embedding run in a background task. Poll ``GET /documents/{document_id}`` for progress.
    """
    assert_form_tenant(tenant_id, tenant)

    if not class_id.strip():
        raise HTTPException(status_code=422, detail="class_id is required")

    filename = file.filename or "upload"

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=422, detail="Empty file")
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds the {MAX_UPLOAD_BYTES // (1024 * 1024)} MB limit",
        )

    try:
        result = await asyncio.to_thread(
            prepare_upload_ingest,
            tenant_id=tenant.tenant_id,
            class_id=class_id.strip(),
            file_bytes=raw,
            filename=filename,
            title=title.strip() if title else None,
            lesson=lesson.strip() if lesson else None,
            force=force,
        )
    except ExtractionError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"{exc} (supported: {', '.join(SUPPORTED_EXTENSIONS)})",
        ) from exc
    except ValueError as exc:
        detail = str(exc)
        if "already being ingested" in detail:
            raise HTTPException(status_code=409, detail=detail) from exc
        raise HTTPException(status_code=422, detail=detail) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingest failed: {exc}") from exc

    if result.get("async") and not result.get("skipped"):
        background_tasks.add_task(
            process_upload_ingest,
            tenant_id=tenant.tenant_id,
            class_id=class_id.strip(),
            file_bytes=raw,
            filename=filename,
            title=title.strip() if title else None,
            lesson=lesson.strip() if lesson else None,
        )

    response_payload = dict(result)
    if "async" in response_payload:
        response_payload["async_"] = response_payload.pop("async")
    return IngestUploadResponse(**response_payload)
