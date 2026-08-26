"""RAG helper utilities."""

from __future__ import annotations


def _format_citation_label(meta: dict) -> str:
    title = meta.get("title") or "Untitled"
    parts: list[str] = [title]
    heading = meta.get("heading_path") or ""
    if heading and heading != title:
        parts.append(heading)
    page = meta.get("page_number")
    if page is not None:
        parts.append(f"p. {page}")
    source_type = meta.get("source_type") or ""
    if source_type:
        parts.append(source_type.upper())
    return " · ".join(parts)


def format_docs(docs: list) -> str:
    """Format LangChain documents into a single context block."""
    formatted = []
    for i, doc in enumerate(docs, 1):
        meta = doc.metadata or {}
        label = _format_citation_label(meta)
        lesson = meta.get("lesson", "")
        source = meta.get("url", "N/A")
        lesson_tag = f" [lesson: {lesson}]" if lesson else ""
        content = doc.page_content[:800]
        formatted.append(
            f"[Source {i}{lesson_tag}]\n{label}\nRef: {source}\nContent: {content}\n"
        )
    return "\n---\n".join(formatted)
