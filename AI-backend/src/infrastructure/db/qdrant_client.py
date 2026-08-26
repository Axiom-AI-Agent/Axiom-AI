"""Qdrant client — tenant-scoped tutor-note collections (no CAG cache)."""

from __future__ import annotations

import uuid
from typing import Any

from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    FieldCondition,
    Filter,
    FilterSelector,
    MatchAny,
    MatchValue,
    PointStruct,
    VectorParams,
)

from infrastructure.config import EMBEDDING_DIM, QDRANT_API_KEY, QDRANT_URL, qdrant_collection_for_tenant
from infrastructure.db.ingest_ids import point_id_for_chunk, point_id_for_parent

# Fetch extra hits before parent dedup so dense PDF pages still return diverse results.
RETRIEVAL_OVERFETCH_FACTOR = 3

_parent_dummy_vector: list[float] | None = None


def _dummy_vector() -> list[float]:
    """Placeholder vector for parent-context points that are never searched."""
    global _parent_dummy_vector
    if _parent_dummy_vector is None:
        _parent_dummy_vector = [0.0] * EMBEDDING_DIM
    return _parent_dummy_vector


def _search_filter(*, class_ids: list[str] | None) -> Filter:
    """Exclude parent-context points from vector search — they are joined by id."""
    must: list[FieldCondition] = [
        FieldCondition(
            key="strategy",
            match=MatchAny(any=["child", "fixed"]),
        )
    ]
    if class_ids:
        allowed = [cid.strip() for cid in class_ids if cid and cid.strip()]
        if allowed:
            must.append(FieldCondition(key="class_id", match=MatchAny(any=allowed)))
    return Filter(must=must)

_qdrant_client: QdrantClient | None = None


def get_qdrant_client() -> QdrantClient:
    global _qdrant_client
    if _qdrant_client is not None:
        return _qdrant_client
    if not QDRANT_URL:
        raise RuntimeError("QDRANT_URL is not set")
    if not QDRANT_API_KEY:
        raise RuntimeError("QDRANT_API_KEY is not set")
    _qdrant_client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        timeout=30,
        check_compatibility=False,
    )
    logger.info("Connected to Qdrant at {}", QDRANT_URL)
    return _qdrant_client


def ensure_collection(
    *,
    tenant_id: str,
    vector_size: int = EMBEDDING_DIM,
    distance: Distance = Distance.COSINE,
) -> str:
    """Create tenant collection if missing; return collection name."""
    collection_name = qdrant_collection_for_tenant(tenant_id)
    client = get_qdrant_client()
    existing = [c.name for c in client.get_collections().collections]
    if collection_name in existing:
        ensure_payload_indexes(tenant_id=tenant_id)
        return collection_name
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=distance, on_disk=True),
    )
    client.create_payload_index(
        collection_name=collection_name,
        field_name="class_id",
        field_schema="keyword",
    )
    client.create_payload_index(
        collection_name=collection_name,
        field_name="document_id",
        field_schema="keyword",
    )
    logger.info("Created Qdrant collection {} with payload indexes", collection_name)
    return collection_name


def ensure_payload_indexes(*, tenant_id: str) -> None:
    """Create keyword indexes used by retrieval filters and document deletion."""
    ensure_class_id_index(tenant_id=tenant_id)
    ensure_document_id_index(tenant_id=tenant_id)


def ensure_document_id_index(*, tenant_id: str) -> None:
    """Keyword index on document_id for idempotent delete-before-upsert."""
    collection_name = qdrant_collection_for_tenant(tenant_id)
    client = get_qdrant_client()
    if collection_name not in [c.name for c in client.get_collections().collections]:
        return
    try:
        client.create_payload_index(
            collection_name=collection_name,
            field_name="document_id",
            field_schema="keyword",
        )
    except Exception as exc:
        logger.debug("document_id index on {} (may already exist): {}", collection_name, exc)


def ensure_class_id_index(*, tenant_id: str) -> None:
    """Create class_id payload index on existing collections (idempotent)."""
    collection_name = qdrant_collection_for_tenant(tenant_id)
    client = get_qdrant_client()
    if collection_name not in [c.name for c in client.get_collections().collections]:
        return
    try:
        client.create_payload_index(
            collection_name=collection_name,
            field_name="class_id",
            field_schema="keyword",
        )
    except Exception as exc:
        logger.debug("class_id index on {} (may already exist): {}", collection_name, exc)


def delete_collection(*, tenant_id: str) -> None:
    client = get_qdrant_client()
    client.delete_collection(qdrant_collection_for_tenant(tenant_id))


def collection_info(*, tenant_id: str) -> dict[str, Any]:
    client = get_qdrant_client()
    name = qdrant_collection_for_tenant(tenant_id)
    info = client.get_collection(name)
    return {
        "collection": name,
        "tenant_id": tenant_id,
        "points_count": info.points_count,
        "vector_size": info.config.params.vectors.size,  # type: ignore[union-attr]
        "status": info.status.name,
    }


def delete_chunks_by_document_id(*, tenant_id: str, document_id: str) -> int:
    """Remove all Qdrant points belonging to one ingested document."""
    collection_name = qdrant_collection_for_tenant(tenant_id)
    client = get_qdrant_client()
    if collection_name not in [c.name for c in client.get_collections().collections]:
        return 0
    ensure_document_id_index(tenant_id=tenant_id)
    before = client.count(
        collection_name=collection_name,
        count_filter=Filter(
            must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
        ),
        exact=True,
    ).count
    if not before:
        return 0
    client.delete(
        collection_name=collection_name,
        points_selector=FilterSelector(
            filter=Filter(
                must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
            )
        ),
    )
    logger.info("Deleted {} points for document_id={} in {}", before, document_id, collection_name)
    return before


def upsert_parent_chunks(*, tenant_id: str, parents: list[dict[str, Any]]) -> int:
    """Store each parent section once — children reference it by ``parent_id`` at read time."""
    if not parents:
        return 0
    collection_name = ensure_collection(tenant_id=tenant_id)
    client = get_qdrant_client()
    dummy = _dummy_vector()
    points: list[PointStruct] = []
    for parent in parents:
        parent_id = str(parent.get("parent_id") or "")
        if not parent_id:
            continue
        document_id = str(parent.get("document_id") or "")
        payload = {
            "tenant_id": tenant_id,
            "class_id": parent.get("class_id", ""),
            "chunk_text": parent.get("text", ""),
            "url": parent.get("url", ""),
            "title": parent.get("title", ""),
            "lesson": parent.get("lesson", ""),
            "strategy": "parent",
            "parent_id": parent_id,
            "chunk_index": int(parent.get("chunk_index", 0)),
            "source_type": parent.get("source_type", ""),
        }
        if document_id:
            payload["document_id"] = document_id
        if parent.get("heading_path"):
            payload["heading_path"] = parent["heading_path"]
        if parent.get("page_number") is not None:
            payload["page_number"] = parent["page_number"]
        points.append(
            PointStruct(
                id=point_id_for_parent(tenant_id=tenant_id, parent_id=parent_id),
                vector=dummy,
                payload=payload,
            )
        )
    if points:
        client.upsert(collection_name=collection_name, points=points)
    logger.info("Upserted {} parent-context point(s) into {}", len(points), collection_name)
    return len(points)


def retrieve_parent_texts(*, tenant_id: str, parent_ids: list[str]) -> dict[str, str]:
    """Batch-fetch parent section text by logical ``parent_id``."""
    unique = [pid for pid in dict.fromkeys(parent_ids) if pid]
    if not unique:
        return {}
    collection_name = qdrant_collection_for_tenant(tenant_id)
    client = get_qdrant_client()
    if collection_name not in [c.name for c in client.get_collections().collections]:
        return {}
    point_ids = [point_id_for_parent(tenant_id=tenant_id, parent_id=pid) for pid in unique]
    records = client.retrieve(collection_name=collection_name, ids=point_ids, with_payload=True)
    lookup: dict[str, str] = {}
    for record in records:
        payload = record.payload or {}
        parent_id = payload.get("parent_id")
        text = payload.get("chunk_text", "")
        if parent_id and text:
            lookup[str(parent_id)] = str(text)
    return lookup


def upsert_chunks(
    *,
    tenant_id: str,
    chunks: list[dict[str, Any]],
    embeddings: list[list[float]],
    batch_size: int = 100,
) -> int:
    if len(chunks) != len(embeddings):
        raise ValueError(f"Mismatch: {len(chunks)} chunks vs {len(embeddings)} embeddings")
    collection_name = ensure_collection(tenant_id=tenant_id)
    client = get_qdrant_client()
    total = 0
    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i : i + batch_size]
        batch_embeds = embeddings[i : i + batch_size]
        points = []
        for chunk, vec in zip(batch_chunks, batch_embeds, strict=True):
            document_id = chunk.get("document_id", "")
            chunk_index = int(chunk.get("chunk_index", 0))
            point_id = (
                point_id_for_chunk(
                    tenant_id=tenant_id,
                    document_id=document_id,
                    chunk_index=chunk_index,
                )
                if document_id
                else str(uuid.uuid4())
            )
            payload = {
                "tenant_id": tenant_id,
                "class_id": chunk.get("class_id", ""),
                "chunk_text": chunk.get("text", ""),
                "url": chunk.get("url", ""),
                "title": chunk.get("title", ""),
                "lesson": chunk.get("lesson", ""),
                "strategy": chunk.get("strategy", "fixed"),
                "chunk_index": chunk_index,
                "source_type": chunk.get("source_type", ""),
            }
            if document_id:
                payload["document_id"] = document_id
            if chunk.get("heading_path"):
                payload["heading_path"] = chunk["heading_path"]
            if chunk.get("page_number") is not None:
                payload["page_number"] = chunk["page_number"]
            if chunk.get("parent_id"):
                payload["parent_id"] = chunk["parent_id"]
            if chunk.get("child_id"):
                payload["child_id"] = chunk["child_id"]
            if chunk.get("source_filename"):
                payload["source_filename"] = chunk["source_filename"]
            points.append(PointStruct(id=point_id, vector=vec, payload=payload))
        client.upsert(collection_name=collection_name, points=points)
        total += len(points)
    logger.info("Upserted {} points into {}", total, collection_name)
    return total


def search_chunks(
    *,
    tenant_id: str,
    query_vector: list[float],
    top_k: int = 4,
    score_threshold: float = 0.0,
    class_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    collection_name = qdrant_collection_for_tenant(tenant_id)
    client = get_qdrant_client()
    if class_ids:
        ensure_class_id_index(tenant_id=tenant_id)
    query_filter = _search_filter(class_ids=class_ids)
    response = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=max(top_k * RETRIEVAL_OVERFETCH_FACTOR, top_k),
        score_threshold=score_threshold,
        query_filter=query_filter,
    )
    results: list[dict[str, Any]] = []
    seen_parents: set[str] = set()
    parent_ids_to_fetch: list[str] = []
    for hit in response.points:
        payload = hit.payload or {}
        parent_id = payload.get("parent_id")
        if parent_id and parent_id in seen_parents:
            continue
        if parent_id:
            seen_parents.add(parent_id)
        row = {
            "chunk_text": payload.get("chunk_text", ""),
            "url": payload.get("url", ""),
            "title": payload.get("title", ""),
            "lesson": payload.get("lesson", ""),
            "class_id": payload.get("class_id", ""),
            "strategy": payload.get("strategy", "fixed"),
            "chunk_index": payload.get("chunk_index", 0),
            "source_type": payload.get("source_type", ""),
            "heading_path": payload.get("heading_path", ""),
            "page_number": payload.get("page_number"),
            "document_id": payload.get("document_id", ""),
            "score": hit.score,
            "tenant_id": payload.get("tenant_id", tenant_id),
        }
        if parent_id:
            row["parent_id"] = parent_id
        if payload.get("parent_text"):
            # Legacy points written before parent dedup stored text inline.
            row["parent_text"] = payload["parent_text"]
        elif parent_id:
            parent_ids_to_fetch.append(str(parent_id))
        results.append(row)
        if len(results) >= top_k:
            break

    if parent_ids_to_fetch:
        parent_lookup = retrieve_parent_texts(tenant_id=tenant_id, parent_ids=parent_ids_to_fetch)
        for row in results:
            if row.get("parent_text") or not row.get("parent_id"):
                continue
            row["parent_text"] = parent_lookup.get(str(row["parent_id"]), row["chunk_text"])
    return results


def count_points(*, tenant_id: str) -> int:
    client = get_qdrant_client()
    name = qdrant_collection_for_tenant(tenant_id)
    if name not in [c.name for c in client.get_collections().collections]:
        return 0
    info = client.get_collection(name)
    return info.points_count or 0


def collection_exists(*, tenant_id: str) -> bool:
    client = get_qdrant_client()
    return qdrant_collection_for_tenant(tenant_id) in [
        c.name for c in client.get_collections().collections
    ]
