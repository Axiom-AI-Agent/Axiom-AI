"""Stable document and point identity for idempotent Qdrant ingest."""

from __future__ import annotations

import hashlib
import uuid


def compute_document_id(content: bytes) -> str:
    """Content hash — same bytes always yield the same id within a tenant."""
    return hashlib.sha256(content).hexdigest()[:16]


def point_id_for_chunk(*, tenant_id: str, document_id: str, chunk_index: int) -> str:
    """Deterministic Qdrant point id so re-ingest replaces rather than duplicates."""
    key = f"{tenant_id}:{document_id}:{chunk_index}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, key))


def point_id_for_parent(*, tenant_id: str, parent_id: str) -> str:
    """Deterministic id for a parent-context point (stored once, joined on retrieval)."""
    key = f"{tenant_id}:parent:{parent_id}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, key))
