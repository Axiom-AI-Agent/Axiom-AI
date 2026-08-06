"""Document ingest — PDF upload → parent-child chunk → Qdrant."""

from __future__ import annotations

import asyncio
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from api.schemas import IngestUploadResponse
from services.ingest_service.pipeline import run_pdf_ingest

router = APIRouter(prefix="/tools/ingest", tags=["Tools — Ingest"])

MAX_PDF_BYTES = 20 * 1024 * 1024  # 20 MB


@router.post("/upload", response_model=IngestUploadResponse)
async def upload_document(
    tenant_id: str = Form(..., description="Tenant id, e.g. tenant-demo-physics"),
    class_id: str = Form(..., description="Subject class id, e.g. class-physics-al-2026"),
    file: UploadFile = File(..., description="Tutor note PDF"),
    title: Optional[str] = Form(None, description="Optional document title"),
    lesson: Optional[str] = Form(None, description="Optional lesson label for citations"),
) -> IngestUploadResponse:
    """
    Upload a tutor PDF, extract text, parent-child chunk, embed, and upsert to Qdrant.

    Chunks are **appended** to the tenant collection (`axiom_kb_{tenant_id}`).
    """
    if not tenant_id.strip():
        raise HTTPException(status_code=422, detail="tenant_id is required")
    if not class_id.strip():
        raise HTTPException(status_code=422, detail="class_id is required")

    filename = file.filename or "upload.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=422, detail="Only PDF files are supported")

    content_type = (file.content_type or "").lower()
    if content_type and content_type not in ("application/pdf", "application/x-pdf", "binary/octet-stream"):
        raise HTTPException(status_code=422, detail=f"Unsupported content type: {content_type}")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=422, detail="Empty file")
    if len(raw) > MAX_PDF_BYTES:
        raise HTTPException(status_code=413, detail=f"PDF exceeds {MAX_PDF_BYTES // (1024 * 1024)} MB limit")

    try:
        result = await asyncio.to_thread(
            run_pdf_ingest,
            tenant_id=tenant_id.strip(),
            class_id=class_id.strip(),
            file_bytes=raw,
            filename=filename,
            title=title.strip() if title else None,
            lesson=lesson.strip() if lesson else None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingest failed: {exc}") from exc

    if not result.get("ok"):
        raise HTTPException(status_code=500, detail=result.get("error", "Ingest failed"))

    return IngestUploadResponse(**result)
