"""Qdrant client — tenant-scoped tutor-note collections (no CAG cache)."""

from __future__ import annotations

import uuid
from typing import Any

from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

from infrastructure.config import EMBEDDING_DIM, QDRANT_API_KEY, QDRANT_URL, qdrant_collection_for_tenant

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
        return collection_name
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=distance, on_disk=True),
    )
    logger.info("Created Qdrant collection {}", collection_name)
    return collection_name


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
        for chunk, vec in zip(batch_chunks, batch_embeds):
            payload = {
                "tenant_id": tenant_id,
                "chunk_text": chunk.get("text", ""),
                "url": chunk.get("url", ""),
                "title": chunk.get("title", ""),
                "lesson": chunk.get("lesson", ""),
                "strategy": chunk.get("strategy", "fixed"),
                "chunk_index": chunk.get("chunk_index", 0),
            }
            if chunk.get("parent_id"):
                payload["parent_id"] = chunk["parent_id"]
            if chunk.get("parent_text"):
                payload["parent_text"] = chunk["parent_text"]
            if chunk.get("child_id"):
                payload["child_id"] = chunk["child_id"]
            if chunk.get("source_filename"):
                payload["source_filename"] = chunk["source_filename"]
            points.append(PointStruct(id=str(uuid.uuid4()), vector=vec, payload=payload))
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
) -> list[dict[str, Any]]:
    collection_name = qdrant_collection_for_tenant(tenant_id)
    client = get_qdrant_client()
    # Collection is already tenant-scoped by name — no payload filter needed
    # (avoids requiring a keyword index on tenant_id in managed Qdrant Cloud).
    response = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=top_k,
        score_threshold=score_threshold,
    )
    results: list[dict[str, Any]] = []
    seen_parents: set[str] = set()
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
            "strategy": payload.get("strategy", "fixed"),
            "chunk_index": payload.get("chunk_index", 0),
            "score": hit.score,
            "tenant_id": payload.get("tenant_id", tenant_id),
        }
        if payload.get("parent_text"):
            row["parent_text"] = payload["parent_text"]
        if parent_id:
            row["parent_id"] = parent_id
        results.append(row)
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
