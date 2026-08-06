"""PDF text extraction for tutor document uploads."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from loguru import logger


def extract_pdf_text(content: bytes) -> str:
    """Extract plain text from a PDF byte stream."""
    from pypdf import PdfReader

    reader = PdfReader(BytesIO(content))
    pages: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            pages.append(text.strip())
    combined = "\n\n".join(pages).strip()
    if not combined:
        raise ValueError("PDF contains no extractable text")
    logger.info("Extracted {} characters from {} PDF page(s)", len(combined), len(reader.pages))
    return combined


def document_from_pdf(
    *,
    tenant_id: str,
    filename: str,
    content: bytes,
    title: str | None = None,
    lesson: str | None = None,
) -> dict:
    """Build ingest document dict from uploaded PDF bytes."""
    text = extract_pdf_text(content)
    stem = Path(filename).stem
    doc_title = title or stem.replace("_", " ").replace("-", " ").title()
    return {
        "url": f"upload://{tenant_id}/{stem}",
        "title": doc_title,
        "lesson": lesson or stem,
        "content": text,
        "source_filename": filename,
        "source_type": "pdf",
    }
