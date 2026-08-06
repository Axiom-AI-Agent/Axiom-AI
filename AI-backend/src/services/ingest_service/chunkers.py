"""Text chunking strategies — fixed + parent-child (Week 13 pattern)."""

from __future__ import annotations

from typing import Any

from langchain_text_splitters import RecursiveCharacterTextSplitter

from infrastructure.config import (
    CHILD_CHUNK_OVERLAP,
    CHILD_CHUNK_SIZE,
    FIXED_CHUNK_OVERLAP,
    FIXED_CHUNK_SIZE,
    PARENT_CHUNK_SIZE,
)


def fixed_chunk(documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Split documents into fixed-size chunks with overlap."""
    chunks: list[dict[str, Any]] = []
    chunk_idx = 0
    size = FIXED_CHUNK_SIZE
    overlap = FIXED_CHUNK_OVERLAP

    for doc in documents:
        content = doc.get("content", "")
        url = doc.get("url", "")
        title = doc.get("title", "")
        lesson = doc.get("lesson", "")
        class_id = doc.get("class_id", "")
        if not content.strip():
            continue

        start = 0
        while start < len(content):
            end = min(start + size, len(content))
            text = content[start:end].strip()
            if text:
                chunks.append(
                    {
                        "url": url,
                        "title": title,
                        "lesson": lesson,
                        "class_id": class_id,
                        "text": text,
                        "strategy": "fixed",
                        "chunk_index": chunk_idx,
                    }
                )
                chunk_idx += 1
            if end >= len(content):
                break
            start = max(end - overlap, start + 1)

    return chunks


def parent_child_chunk(
    documents: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Two-tier chunking: small child chunks indexed in Qdrant, parent text stored
    in payload for richer LLM context on retrieval (Week 13 pattern).
    """
    parent_chunks: list[dict[str, Any]] = []
    child_chunks: list[dict[str, Any]] = []
    parent_idx = 0
    child_idx = 0

    parent_size_chars = PARENT_CHUNK_SIZE * 4
    child_size_chars = CHILD_CHUNK_SIZE * 4
    child_overlap_chars = CHILD_CHUNK_OVERLAP * 4

    parent_splitter = RecursiveCharacterTextSplitter(
        chunk_size=parent_size_chars,
        chunk_overlap=200,
        length_function=len,
    )
    child_splitter = RecursiveCharacterTextSplitter(
        chunk_size=child_size_chars,
        chunk_overlap=child_overlap_chars,
        length_function=len,
    )

    for doc in documents:
        content = doc.get("content", "")
        url = doc.get("url", "")
        title = doc.get("title", "")
        lesson = doc.get("lesson", "")
        class_id = doc.get("class_id", "")
        if not content.strip():
            continue

        for parent_text in parent_splitter.split_text(content):
            if not parent_text.strip():
                continue
            parent_id = f"{url}::parent::{parent_idx}"
            parent_chunks.append(
                {
                    "parent_id": parent_id,
                    "url": url,
                    "title": title,
                    "lesson": lesson,
                    "class_id": class_id,
                    "text": parent_text.strip(),
                    "strategy": "parent",
                    "chunk_index": parent_idx,
                }
            )
            for child_text in child_splitter.split_text(parent_text):
                if not child_text.strip():
                    continue
                child_chunks.append(
                    {
                        "child_id": f"{parent_id}::child::{child_idx}",
                        "parent_id": parent_id,
                        "url": url,
                        "title": title,
                        "lesson": lesson,
                        "class_id": class_id,
                        "text": child_text.strip(),
                        "strategy": "child",
                        "chunk_index": child_idx,
                    }
                )
                child_idx += 1
            parent_idx += 1

    return child_chunks, parent_chunks
