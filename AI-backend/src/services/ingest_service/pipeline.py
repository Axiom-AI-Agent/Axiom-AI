"""Tenant-scoped tutor-note ingestion into Qdrant."""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Any, Literal

from loguru import logger

from infrastructure.config import EMBEDDING_BATCH_SIZE, KB_DIR, UPLOADS_DIR, qdrant_collection_for_tenant
from infrastructure.db.qdrant_client import collection_info, upsert_chunks
from infrastructure.llm import get_default_embeddings
from services.ingest_service.chunkers import fixed_chunk, parent_child_chunk
from services.ingest_service.pdf_loader import document_from_pdf

_LESSON_RE = re.compile(r"lesson[_\s-]*(\d+)", re.I)
ChunkStrategy = Literal["fixed", "parent_child"]


def load_tenant_docs(*, tenant_id: str, tenant_slug: str, kb_path: Path | None = None) -> list[dict[str, Any]]:
    """Load markdown tutor notes from data/knowledge_base/{tenant_slug}/."""
    root = kb_path or (KB_DIR / tenant_slug)
    if not root.exists():
        raise FileNotFoundError(f"Knowledge-base directory not found: {root}")

    docs: list[dict[str, Any]] = []
    for md_file in sorted(root.glob("*.md")):
        content = md_file.read_text(encoding="utf-8").strip()
        if not content:
            continue
        title = content.split("\n", 1)[0].lstrip("# ").strip() or md_file.stem
        lesson_match = _LESSON_RE.search(md_file.stem) or _LESSON_RE.search(title)
        lesson = lesson_match.group(1) if lesson_match else md_file.stem
        docs.append(
            {
                "url": f"internal://{tenant_id}/{md_file.stem}",
                "title": title,
                "lesson": lesson,
                "content": content,
                "source_type": "markdown",
            }
        )
    logger.info("Loaded {} tutor-note documents from {}", len(docs), root)
    return docs


def embed_texts(texts: list[str], batch_size: int = EMBEDDING_BATCH_SIZE) -> list[list[float]]:
    embedder = get_default_embeddings(batch_size=batch_size)
    all_embeddings: list[list[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        all_embeddings.extend(embedder.embed_documents(batch))
    return all_embeddings


def _build_parent_lookup(parents: list[dict[str, Any]]) -> dict[str, str]:
    return {p["parent_id"]: p["text"] for p in parents}


def _enrich_children_with_parent_text(
    children: list[dict[str, Any]],
    parent_lookup: dict[str, str],
) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for child in children:
        pid = child.get("parent_id", "")
        row = dict(child)
        row["parent_text"] = parent_lookup.get(pid, child["text"])
        enriched.append(row)
    return enriched


def ingest_documents(
    *,
    tenant_id: str,
    documents: list[dict[str, Any]],
    strategy: ChunkStrategy = "parent_child",
) -> dict[str, Any]:
    """
    Chunk, embed, and upsert documents into the tenant Qdrant collection.

    Parent-child: only child chunks are embedded; parent_text is stored in payload.
    """
    if not documents:
        raise ValueError("No documents to ingest")

    if strategy == "parent_child":
        children, parents = parent_child_chunk(documents)
        if not children:
            raise ValueError("Parent-child chunking produced no child chunks")
        parent_lookup = _build_parent_lookup(parents)
        chunks = _enrich_children_with_parent_text(children, parent_lookup)
        logger.info(
            "Parent-child chunking: {} child chunks, {} parent chunks",
            len(children),
            len(parents),
        )
    else:
        chunks = fixed_chunk(documents)
        if not chunks:
            raise ValueError("Fixed chunking produced no chunks")

    texts = [c["text"] for c in chunks]
    t0 = time.time()
    embeddings = embed_texts(texts)
    logger.info("Embedded {} chunks in {:.1f}s", len(chunks), time.time() - t0)

    n = upsert_chunks(tenant_id=tenant_id, chunks=chunks, embeddings=embeddings)
    info = collection_info(tenant_id=tenant_id)
    return {
        "ok": True,
        "tenant_id": tenant_id,
        "strategy": strategy,
        "documents": len(documents),
        "chunks_upserted": n,
        "collection": qdrant_collection_for_tenant(tenant_id),
        "points_count": info.get("points_count"),
    }


def run_tenant_ingest(
    *,
    tenant_id: str,
    tenant_slug: str,
    kb_path: Path | None = None,
    strategy: ChunkStrategy = "parent_child",
) -> int:
    """Load markdown tutor notes and ingest (append — does not wipe collection)."""
    logger.info("Ingesting tutor notes for tenant={} slug={}", tenant_id, tenant_slug)
    docs = load_tenant_docs(tenant_id=tenant_id, tenant_slug=tenant_slug, kb_path=kb_path)
    result = ingest_documents(tenant_id=tenant_id, documents=docs, strategy=strategy)
    logger.success("Ingest complete: {}", result)
    return int(result["chunks_upserted"])


def run_pdf_ingest(
    *,
    tenant_id: str,
    file_bytes: bytes,
    filename: str,
    title: str | None = None,
    lesson: str | None = None,
    save_upload: bool = True,
) -> dict[str, Any]:
    """
    Extract text from PDF, parent-child chunk, embed, and upsert to Qdrant.
    Optionally persist the raw PDF under data/uploads/{tenant_id}/.
    """
    if not filename.lower().endswith(".pdf"):
        raise ValueError("Only PDF uploads are supported")

    if save_upload:
        dest_dir = UPLOADS_DIR / tenant_id
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / Path(filename).name
        dest_path.write_bytes(file_bytes)
        logger.info("Saved upload to {}", dest_path)

    doc = document_from_pdf(
        tenant_id=tenant_id,
        filename=filename,
        content=file_bytes,
        title=title,
        lesson=lesson,
    )
    result = ingest_documents(tenant_id=tenant_id, documents=[doc], strategy="parent_child")
    result["document_title"] = doc["title"]
    result["source_filename"] = filename
    logger.success("PDF ingest complete: {}", result)
    return result
