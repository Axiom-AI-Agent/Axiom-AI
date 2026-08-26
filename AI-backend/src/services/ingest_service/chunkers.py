"""Text chunking strategies — fixed + parent-child, markdown structure aware.

Parent-child exists because the two jobs pull in opposite directions: a small
chunk has a focused embedding and matches precisely, while a large chunk is
better context for the LLM to answer from. So children are embedded and parents
are what retrieval returns.

The catch with small children is that a ~250-token slice out of the middle of a
document often never names its own topic — "substituting gives 9.81" says
nothing about gravity. Each child is therefore embedded with its heading
breadcrumb prefixed, which is the single largest retrieval win available here.
Heading structure only exists because the extractors emit markdown.
"""

from __future__ import annotations

import re
from typing import Any

from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from infrastructure.config import (
    CHILD_CHUNK_OVERLAP,
    CHILD_CHUNK_SIZE,
    CHUNK_CONTEXTUALIZE_CHILDREN,
    CHUNK_RESPECT_MARKDOWN_HEADERS,
    CHUNK_TOKEN_ENCODING,
    FIXED_CHUNK_OVERLAP,
    FIXED_CHUNK_SIZE,
    PARENT_CHUNK_SIZE,
)

# Emitted by the PDF extractor so chunks can be traced back to a page.
_PAGE_MARKER_RE = re.compile(r"<!--\s*page:(\d+)\s*-->")

_HEADER_LEVELS = [("#", "h1"), ("##", "h2"), ("###", "h3")]
_MAX_BREADCRUMB_CHARS = 80
_TABLE_LINE_RE = re.compile(r"^\|.+\|\s*$")

_encoder = None


def _token_len(text: str) -> int:
    """Token count via tiktoken, falling back to a chars/4 estimate.

    The previous implementation multiplied configured token budgets by 4 to get
    character budgets, which under-fills chunks for prose and overfills them for
    tables and formulae.
    """
    global _encoder
    if _encoder is None:
        try:
            import tiktoken

            _encoder = tiktoken.get_encoding(CHUNK_TOKEN_ENCODING)
        except Exception:  # pragma: no cover - offline / missing encoding
            _encoder = False
    if _encoder is False:
        return max(1, len(text) // 4)
    return len(_encoder.encode(text, disallowed_special=()))


def _strip_page_markers(text: str) -> str:
    return _PAGE_MARKER_RE.sub("", text).strip()


def _page_of(text: str, carried: int | None) -> tuple[int | None, int | None]:
    """Return (page this text starts on, page it ends on).

    A chunk belongs to the page that was open when it started, so a marker in the
    middle only affects what the *next* chunk inherits.
    """
    markers = [int(m) for m in _PAGE_MARKER_RE.findall(text)]
    if not markers:
        return carried, carried
    starts_on = carried if carried is not None else markers[0]
    return starts_on, markers[-1]


def _breadcrumb(metadata: dict[str, str]) -> str:
    """Build a "H1 > H2 > H3" trail, trimmed to stay a prefix rather than a passage.

    Document titles used as H1 can run long, and the breadcrumb is repeated on
    every child chunk — an untrimmed trail can eat a tenth of the embedding
    budget with text that is identical across the whole document. The deepest
    heading is the most discriminating, so drop from the front when over budget.
    """
    parts = [metadata[key] for _, key in _HEADER_LEVELS if metadata.get(key)]
    while len(parts) > 1 and len(" > ".join(parts)) > _MAX_BREADCRUMB_CHARS:
        parts.pop(0)
    trail = " > ".join(parts)
    return trail[:_MAX_BREADCRUMB_CHARS].rstrip() if len(trail) > _MAX_BREADCRUMB_CHARS else trail


def _splitter(chunk_tokens: int, overlap_tokens: int) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_tokens,
        chunk_overlap=overlap_tokens,
        length_function=_token_len,
    )


def _is_table_line(line: str) -> bool:
    return bool(_TABLE_LINE_RE.match(line.strip()))


def _segment_preserving_tables(text: str) -> list[str]:
    """Split prose from markdown pipe tables so tables are never cut mid-row."""
    segments: list[str] = []
    buffer: list[str] = []
    in_table = False

    for line in text.split("\n"):
        if _is_table_line(line):
            if not in_table and buffer:
                segment = "\n".join(buffer).strip()
                if segment:
                    segments.append(segment)
                buffer = []
            in_table = True
            buffer.append(line)
            continue

        if in_table:
            segment = "\n".join(buffer).strip()
            if segment:
                segments.append(segment)
            buffer = []
            in_table = False
        buffer.append(line)

    tail = "\n".join(buffer).strip()
    if tail:
        segments.append(tail)
    return segments


def _split_preserving_tables(text: str, splitter: RecursiveCharacterTextSplitter, max_tokens: int) -> list[str]:
    """Recursive split that keeps each markdown table block intact when possible."""
    parts: list[str] = []
    for segment in _segment_preserving_tables(text):
        if _token_len(segment) <= max_tokens:
            parts.append(segment)
            continue
        if segment.lstrip().startswith("|") and _is_table_line(segment.split("\n", 1)[0]):
            parts.append(segment)
            continue
        parts.extend(splitter.split_text(segment))
    return parts


def _sections(content: str) -> list[tuple[str, str]]:
    """Split markdown into (breadcrumb, text) sections on headings.

    Falls back to a single unlabelled section for documents with no headings, so
    plain-text sources still flow through unchanged.
    """
    if not CHUNK_RESPECT_MARKDOWN_HEADERS or not re.search(r"^#{1,3} ", content, re.M):
        return [("", content)]

    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=_HEADER_LEVELS,
        strip_headers=False,  # keep the heading in parent text for LLM context
    )
    sections: list[tuple[str, str]] = []
    for doc in splitter.split_text(content):
        text = doc.page_content.strip()
        if text:
            sections.append((_breadcrumb(doc.metadata or {}), text))
    return sections or [("", content)]


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
        source_type = doc.get("source_type", "")
        document_id = doc.get("document_id", "")
        if not content.strip():
            continue

        page: int | None = None
        start = 0
        while start < len(content):
            end = min(start + size, len(content))
            raw = content[start:end]
            page, page_end = _page_of(raw, page)
            text = _strip_page_markers(raw)
            if text:
                chunks.append(
                    {
                        "url": url,
                        "title": title,
                        "lesson": lesson,
                        "class_id": class_id,
                        "source_type": source_type,
                        "document_id": document_id,
                        "page_number": page,
                        "text": text,
                        "strategy": "fixed",
                        "chunk_index": chunk_idx,
                    }
                )
                chunk_idx += 1
            page = page_end
            if end >= len(content):
                break
            start = max(end - overlap, start + 1)

    return chunks


def parent_child_chunk(
    documents: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Two-tier chunking: small child chunks indexed in Qdrant, parent text stored
    in payload for richer LLM context on retrieval.

    Children carry an ``embed_text`` field — the heading breadcrumb plus the chunk
    — which is what gets embedded. ``text`` stays clean for display and citation.
    """
    parent_chunks: list[dict[str, Any]] = []
    child_chunks: list[dict[str, Any]] = []
    parent_idx = 0
    child_idx = 0

    parent_splitter = _splitter(PARENT_CHUNK_SIZE, min(200, PARENT_CHUNK_SIZE // 6))
    child_splitter = _splitter(CHILD_CHUNK_SIZE, CHILD_CHUNK_OVERLAP)

    for doc in documents:
        content = doc.get("content", "")
        url = doc.get("url", "")
        title = doc.get("title", "")
        lesson = doc.get("lesson", "")
        class_id = doc.get("class_id", "")
        source_type = doc.get("source_type", "")
        document_id = doc.get("document_id", "")
        if not content.strip():
            continue

        page: int | None = None

        for breadcrumb, section in _sections(content):
            # A section shorter than the parent budget stays whole; only
            # oversized sections are cut, so parents follow the document's own
            # structure wherever it fits.
            parent_texts = (
                [section]
                if _token_len(section) <= PARENT_CHUNK_SIZE
                else parent_splitter.split_text(section)
            )

            for parent_text in parent_texts:
                page, page_end = _page_of(parent_text, page)
                clean_parent = _strip_page_markers(parent_text)
                if not clean_parent:
                    page = page_end
                    continue

                parent_id = f"{url}::parent::{parent_idx}"
                parent_chunks.append(
                    {
                        "parent_id": parent_id,
                        "url": url,
                        "title": title,
                        "lesson": lesson,
                        "class_id": class_id,
                        "source_type": source_type,
                        "heading_path": breadcrumb,
                        "page_number": page,
                        "text": clean_parent,
                        "strategy": "parent",
                        "chunk_index": parent_idx,
                    }
                )

                child_page = page
                for child_text in _split_preserving_tables(
                    parent_text, child_splitter, CHILD_CHUNK_SIZE
                ):
                    child_page, child_page_end = _page_of(child_text, child_page)
                    clean_child = _strip_page_markers(child_text)
                    if not clean_child:
                        child_page = child_page_end
                        continue
                    child_chunks.append(
                        {
                            "child_id": f"{parent_id}::child::{child_idx}",
                            "parent_id": parent_id,
                            "url": url,
                            "title": title,
                            "lesson": lesson,
                            "class_id": class_id,
                            "source_type": source_type,
                            "document_id": document_id,
                            "heading_path": breadcrumb,
                            "page_number": child_page,
                            "text": clean_child,
                            "embed_text": _contextualize(clean_child, breadcrumb, title),
                            "strategy": "child",
                            "chunk_index": child_idx,
                        }
                    )
                    child_idx += 1
                    child_page = child_page_end

                page = page_end
                parent_idx += 1

    return child_chunks, parent_chunks


def _contextualize(text: str, breadcrumb: str, title: str) -> str:
    """Prefix a child chunk with the headings it sits under, for embedding."""
    if not CHUNK_CONTEXTUALIZE_CHILDREN:
        return text
    prefix = breadcrumb or title
    if not prefix or text.lstrip().startswith(prefix):
        return text
    return f"{prefix}\n{text}"
