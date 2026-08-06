"""RAG helper utilities."""

from __future__ import annotations


def format_docs(docs: list) -> str:
    """Format LangChain documents into a single context block."""
    formatted = []
    for i, doc in enumerate(docs, 1):
        meta = doc.metadata or {}
        title = meta.get("title", "Untitled")
        lesson = meta.get("lesson", "")
        source = meta.get("url", "N/A")
        lesson_tag = f" [lesson: {lesson}]" if lesson else ""
        content = doc.page_content[:800]
        formatted.append(
            f"[Source {i}{lesson_tag}]\nTitle: {title}\nRef: {source}\nContent: {content}\n"
        )
    return "\n---\n".join(formatted)
