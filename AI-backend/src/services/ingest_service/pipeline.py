"""Tenant-scoped tutor-note ingestion into Qdrant."""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Any, Literal

from loguru import logger

from infrastructure.config import EMBEDDING_BATCH_SIZE, KB_DIR, UPLOADS_DIR, qdrant_collection_for_tenant
from infrastructure.db import kb_documents as kb_registry
from infrastructure.db.qdrant_client import (
    collection_info,
    delete_chunks_by_document_id,
    upsert_chunks,
    upsert_parent_chunks,
)
from infrastructure.llm import get_default_embeddings
from services.ingest_service.chunkers import fixed_chunk, parent_child_chunk
from infrastructure.db.ingest_ids import compute_document_id
from services.ingest_service.extractors import extract_document, title_from_filename, ExtractionError, sniff_format

_LESSON_RE = re.compile(r"lesson[_\s-]*(\d+)", re.I)
_KB_SUFFIXES = frozenset({".md", ".markdown", ".txt", ".pdf", ".docx"})
ChunkStrategy = Literal["fixed", "parent_child"]

_IN_PROGRESS_STATUSES = frozenset({"pending", "extracting", "embedding"})

TENANT_DEFAULT_CLASS: dict[str, str] = {
    "tenant-demo-physics": "class-physics-al-2026",
    "tenant-demo-chemistry": "class-chemistry-al-2026",
}


def load_tenant_docs(
    *,
    tenant_id: str,
    tenant_slug: str,
    kb_path: Path | None = None,
    class_id: str | None = None,
) -> list[dict[str, Any]]:
    """Load tutor notes (markdown, PDF or DOCX) from data/knowledge_base/{tenant_slug}/."""
    root = kb_path or (KB_DIR / tenant_slug)
    if not root.exists():
        raise FileNotFoundError(f"Knowledge-base directory not found: {root}")

    resolved_class_id = (class_id or TENANT_DEFAULT_CLASS.get(tenant_id) or "").strip()
    if not resolved_class_id:
        raise ValueError(
            f"class_id is required for ingest (no default for tenant {tenant_id}). "
            "Pass --class-id or use TENANT_DEFAULT_CLASS."
        )

    paths = sorted(p for p in root.iterdir() if p.suffix.lower() in _KB_SUFFIXES and p.is_file())

    docs: list[dict[str, Any]] = []
    for path in paths:
        raw = path.read_bytes()
        try:
            extracted = extract_document(raw, filename=path.name)
        except ValueError as exc:
            logger.warning("Skipping {}: {}", path.name, exc)
            continue

        content = extracted.markdown
        if not content:
            continue
        first_line = content.split("\n", 1)[0].lstrip("# ").strip()
        title = first_line or title_from_filename(path.name)
        lesson_match = _LESSON_RE.search(path.stem) or _LESSON_RE.search(title)
        lesson = lesson_match.group(1) if lesson_match else path.stem
        docs.append(
            {
                "url": f"internal://{tenant_id}/{path.stem}",
                "title": title,
                "lesson": lesson,
                "class_id": resolved_class_id,
                "content": content,
                "source_filename": path.name,
                "source_type": extracted.source_type,
                "document_id": compute_document_id(raw),
                "byte_size": len(raw),
                "page_count": extracted.page_count,
                "ocr_pages": extracted.ocr_page_count,
                "warnings": extracted.warnings,
            }
        )
    logger.info("Loaded {} tutor-note documents from {} (class_id={})", len(docs), root, resolved_class_id)
    return docs


def embed_texts(texts: list[str], batch_size: int = EMBEDDING_BATCH_SIZE) -> list[list[float]]:
    embedder = get_default_embeddings(batch_size=batch_size)
    all_embeddings: list[list[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        all_embeddings.extend(embedder.embed_documents(batch))
    return all_embeddings


def _attach_document_ids(chunks: list[dict[str, Any]], document_id: str) -> list[dict[str, Any]]:
    return [{**chunk, "document_id": document_id} for chunk in chunks]


def ingest_documents(
    *,
    tenant_id: str,
    documents: list[dict[str, Any]],
    strategy: ChunkStrategy = "parent_child",
    replace_existing: bool = True,
) -> dict[str, Any]:
    """
    Chunk, embed, and upsert documents into the tenant Qdrant collection.

    Each document must carry a ``document_id`` (content hash). Re-ingesting the same
    id deletes prior points first so corrected uploads replace rather than duplicate.
    """
    if not documents:
        raise ValueError("No documents to ingest")

    for doc in documents:
        if not str(doc.get("class_id") or "").strip():
            raise ValueError("Each document must include class_id for class-scoped retrieval")
        if not str(doc.get("document_id") or "").strip():
            raise ValueError("Each document must include document_id")

    total_deleted = 0
    total_parents = 0
    all_chunks: list[dict[str, Any]] = []

    for doc in documents:
        document_id = str(doc["document_id"])
        if replace_existing:
            total_deleted += delete_chunks_by_document_id(tenant_id=tenant_id, document_id=document_id)

        if strategy == "parent_child":
            children, parents = parent_child_chunk([doc])
            if not children:
                raise ValueError(f"Parent-child chunking produced no child chunks for {document_id}")
            parent_chunks = _attach_document_ids(parents, document_id)
            total_parents += upsert_parent_chunks(tenant_id=tenant_id, parents=parent_chunks)
            chunks = _attach_document_ids(children, document_id)
            logger.info(
                "Parent-child chunking for {}: {} child chunks, {} parent chunks",
                document_id,
                len(children),
                len(parents),
            )
        else:
            chunks = fixed_chunk([doc])
            if not chunks:
                raise ValueError(f"Fixed chunking produced no chunks for {document_id}")

        all_chunks.extend(_attach_document_ids(chunks, document_id))

    texts = [c.get("embed_text") or c["text"] for c in all_chunks]
    t0 = time.time()
    embeddings = embed_texts(texts)
    logger.info("Embedded {} chunks in {:.1f}s", len(all_chunks), time.time() - t0)

    n = upsert_chunks(tenant_id=tenant_id, chunks=all_chunks, embeddings=embeddings)
    info = collection_info(tenant_id=tenant_id)
    return {
        "ok": True,
        "tenant_id": tenant_id,
        "strategy": strategy,
        "documents": len(documents),
        "chunks_upserted": n,
        "parents_upserted": total_parents,
        "chunks_deleted": total_deleted,
        "collection": qdrant_collection_for_tenant(tenant_id),
        "points_count": info.get("points_count"),
    }


def run_tenant_ingest(
    *,
    tenant_id: str,
    tenant_slug: str,
    kb_path: Path | None = None,
    strategy: ChunkStrategy = "parent_child",
    class_id: str | None = None,
) -> int:
    """Load tutor notes and ingest (idempotent per document content hash)."""
    logger.info("Ingesting tutor notes for tenant={} slug={}", tenant_id, tenant_slug)
    docs = load_tenant_docs(
        tenant_id=tenant_id,
        tenant_slug=tenant_slug,
        kb_path=kb_path,
        class_id=class_id,
    )
    total = 0
    for doc in docs:
        kb_registry.upsert_document(
            tenant_id=tenant_id,
            class_id=doc["class_id"],
            document_id=doc["document_id"],
            filename=doc.get("source_filename") or doc["url"],
            title=doc.get("title"),
            lesson=doc.get("lesson"),
            source_type=doc.get("source_type", "markdown"),
            byte_size=int(doc.get("byte_size") or 0),
            page_count=doc.get("page_count"),
            ocr_pages=int(doc.get("ocr_pages") or 0),
            status="embedding",
            warnings=doc.get("warnings") or [],
        )
        result = ingest_documents(tenant_id=tenant_id, documents=[doc], strategy=strategy)
        kb_registry.upsert_document(
            tenant_id=tenant_id,
            class_id=doc["class_id"],
            document_id=doc["document_id"],
            filename=doc.get("source_filename") or doc["url"],
            title=doc.get("title"),
            lesson=doc.get("lesson"),
            source_type=doc.get("source_type", "markdown"),
            byte_size=int(doc.get("byte_size") or 0),
            page_count=doc.get("page_count"),
            ocr_pages=int(doc.get("ocr_pages") or 0),
            chunks_upserted=result["chunks_upserted"],
            status="ready",
            warnings=doc.get("warnings") or [],
        )
        total += int(result["chunks_upserted"])
    logger.success("Ingest complete: {} chunks across {} documents", total, len(docs))
    return total


def prepare_upload_ingest(
    *,
    tenant_id: str,
    file_bytes: bytes,
    filename: str,
    class_id: str,
    title: str | None = None,
    lesson: str | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """
    Validate idempotency and register ``pending`` for async ingest.

    Returns an immediate response dict (skipped short-circuit or async accept).
    """
    if not class_id.strip():
        raise ValueError("class_id is required")

    try:
        source_type = sniff_format(file_bytes, filename=filename)
    except ExtractionError:
        raise

    document_id = compute_document_id(file_bytes)
    existing = kb_registry.get_document(tenant_id=tenant_id, document_id=document_id)
    doc_title = title or title_from_filename(filename)

    if (
        not force
        and existing
        and existing.get("status") == "ready"
        and int(existing.get("byte_size") or 0) == len(file_bytes)
    ):
        logger.info("Skipping unchanged upload {} ({})", filename, document_id)
        info = collection_info(tenant_id=tenant_id)
        return {
            "ok": True,
            "skipped": True,
            "async": False,
            "status": "ready",
            "tenant_id": tenant_id,
            "strategy": "parent_child",
            "documents": 0,
            "chunks_upserted": int(existing.get("chunks_upserted") or 0),
            "collection": qdrant_collection_for_tenant(tenant_id),
            "points_count": info.get("points_count"),
            "document_id": document_id,
            "document_title": existing.get("title") or doc_title,
            "source_filename": existing.get("filename") or filename,
            "source_type": existing.get("source_type"),
            "page_count": existing.get("page_count"),
            "ocr_pages": int(existing.get("ocr_pages") or 0),
            "warnings": existing.get("warnings") or [],
        }

    if not force and existing and existing.get("status") in _IN_PROGRESS_STATUSES:
        raise ValueError(
            f"Document {document_id} is already being ingested (status={existing['status']})"
        )

    kb_registry.upsert_document(
        tenant_id=tenant_id,
        class_id=class_id.strip(),
        document_id=document_id,
        filename=filename,
        title=doc_title,
        lesson=lesson,
        source_type="unknown",
        byte_size=len(file_bytes),
        status="pending",
    )

    return {
        "ok": True,
        "skipped": False,
        "async": True,
        "status": "pending",
        "tenant_id": tenant_id,
        "strategy": "parent_child",
        "documents": 0,
        "chunks_upserted": 0,
        "collection": qdrant_collection_for_tenant(tenant_id),
        "document_id": document_id,
        "document_title": doc_title,
        "source_filename": filename,
        "source_type": source_type,
        "warnings": [],
    }


def process_upload_ingest(
    *,
    tenant_id: str,
    file_bytes: bytes,
    filename: str,
    class_id: str,
    title: str | None = None,
    lesson: str | None = None,
    save_upload: bool = True,
) -> None:
    """Background worker: extract, chunk, embed, and mark registry ready/failed."""
    document_id = compute_document_id(file_bytes)
    doc_title = title or title_from_filename(filename)

    kb_registry.upsert_document(
        tenant_id=tenant_id,
        class_id=class_id.strip(),
        document_id=document_id,
        filename=filename,
        title=doc_title,
        lesson=lesson,
        source_type="unknown",
        byte_size=len(file_bytes),
        status="extracting",
    )

    try:
        extracted = extract_document(file_bytes, filename=filename)
    except Exception as exc:
        kb_registry.mark_failed(tenant_id=tenant_id, document_id=document_id, error=str(exc))
        logger.exception("Extract failed for {} ({})", filename, document_id)
        return

    stem = Path(filename).stem
    doc: dict[str, Any] = {
        "url": f"upload://{tenant_id}/{stem}",
        "title": doc_title,
        "lesson": lesson or stem,
        "class_id": class_id.strip(),
        "content": extracted.markdown,
        "source_filename": filename,
        "source_type": extracted.source_type,
        "document_id": document_id,
        "byte_size": len(file_bytes),
        "page_count": extracted.page_count,
        "ocr_pages": extracted.ocr_page_count,
        "warnings": extracted.warnings,
    }

    kb_registry.upsert_document(
        tenant_id=tenant_id,
        class_id=class_id.strip(),
        document_id=document_id,
        filename=filename,
        title=doc_title,
        lesson=lesson or stem,
        source_type=extracted.source_type,
        byte_size=len(file_bytes),
        page_count=extracted.page_count,
        ocr_pages=extracted.ocr_page_count,
        status="embedding",
        warnings=extracted.warnings,
    )

    try:
        result = ingest_documents(tenant_id=tenant_id, documents=[doc], strategy="parent_child")
    except Exception as exc:
        kb_registry.mark_failed(tenant_id=tenant_id, document_id=document_id, error=str(exc))
        logger.exception("Ingest failed for {} ({})", filename, document_id)
        return

    if save_upload and result.get("ok"):
        dest_dir = UPLOADS_DIR / tenant_id
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / Path(filename).name
        dest_path.write_bytes(file_bytes)
        logger.info("Saved upload to {}", dest_path)

    kb_registry.upsert_document(
        tenant_id=tenant_id,
        class_id=class_id.strip(),
        document_id=document_id,
        filename=filename,
        title=doc_title,
        lesson=lesson or stem,
        source_type=extracted.source_type,
        byte_size=len(file_bytes),
        page_count=extracted.page_count,
        ocr_pages=extracted.ocr_page_count,
        chunks_upserted=result["chunks_upserted"],
        status="ready",
        warnings=extracted.warnings,
    )

    logger.success(
        "Upload ingest complete: {} ({}), {} chunks",
        filename,
        extracted.source_type,
        result["chunks_upserted"],
    )


def run_upload_ingest(
    *,
    tenant_id: str,
    file_bytes: bytes,
    filename: str,
    class_id: str,
    title: str | None = None,
    lesson: str | None = None,
    save_upload: bool = True,
    force: bool = False,
) -> dict[str, Any]:
    """
    Synchronous upload ingest (used in tests and CLI).

    Dashboard uploads use :func:`prepare_upload_ingest` + :func:`process_upload_ingest`.
    """
    prepared = prepare_upload_ingest(
        tenant_id=tenant_id,
        file_bytes=file_bytes,
        filename=filename,
        class_id=class_id,
        title=title,
        lesson=lesson,
        force=force,
    )
    if prepared.get("skipped"):
        return prepared

    process_upload_ingest(
        tenant_id=tenant_id,
        file_bytes=file_bytes,
        filename=filename,
        class_id=class_id,
        title=title,
        lesson=lesson,
        save_upload=save_upload,
    )

    document_id = prepared["document_id"]
    row = kb_registry.get_document(tenant_id=tenant_id, document_id=document_id) or {}
    if row.get("status") == "failed":
        raise ValueError(row.get("error") or "Ingest failed")

    info = collection_info(tenant_id=tenant_id)
    return {
        "ok": True,
        "skipped": False,
        "async": False,
        "status": "ready",
        "tenant_id": tenant_id,
        "strategy": "parent_child",
        "documents": 1,
        "chunks_upserted": int(row.get("chunks_upserted") or 0),
        "collection": qdrant_collection_for_tenant(tenant_id),
        "points_count": info.get("points_count"),
        "document_id": document_id,
        "document_title": row.get("title") or prepared.get("document_title"),
        "source_filename": row.get("filename") or filename,
        "source_type": row.get("source_type"),
        "page_count": row.get("page_count"),
        "ocr_pages": int(row.get("ocr_pages") or 0),
        "warnings": row.get("warnings") or [],
    }


def delete_document_ingest(*, tenant_id: str, document_id: str) -> dict[str, Any]:
    """Remove a document from Qdrant and the registry."""
    deleted_points = delete_chunks_by_document_id(tenant_id=tenant_id, document_id=document_id)
    registry_deleted = kb_registry.delete_document(tenant_id=tenant_id, document_id=document_id)
    if deleted_points == 0 and not registry_deleted:
        raise ValueError(f"Document not found: {document_id}")
    info = collection_info(tenant_id=tenant_id)
    return {
        "ok": True,
        "tenant_id": tenant_id,
        "document_id": document_id,
        "chunks_deleted": deleted_points,
        "registry_deleted": registry_deleted,
        "points_count": info.get("points_count"),
    }


def run_pdf_ingest(**kwargs: Any) -> dict[str, Any]:
    """Deprecated alias for :func:`run_upload_ingest`, kept for one release."""
    return run_upload_ingest(**kwargs)
