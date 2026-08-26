"""PDF → markdown via pymupdf4llm (text layer only — no vision OCR)."""

from __future__ import annotations

from loguru import logger

from services.ingest_service.extractors.base import (
    ExtractedDoc,
    ExtractionError,
    PageText,
    normalize_markdown,
)

_MIN_CHARS_PER_PAGE = 100
_MIN_ALPHA_RATIO = 0.5


def _page_marker(page_number: int) -> str:
    return f"<!-- page:{page_number} -->"


def _page_lacks_text(page_markdown: str) -> bool:
    """True when a page's text layer yielded too little to be real content."""
    stripped = page_markdown.strip()
    if len(stripped) < _MIN_CHARS_PER_PAGE:
        return True
    alnum = sum(1 for c in stripped if c.isalnum() or c.isspace())
    return (alnum / len(stripped)) < _MIN_ALPHA_RATIO


def _assemble(pages: list[PageText]) -> str:
    parts = [f"{_page_marker(p.page_number)}\n{p.markdown.strip()}" for p in pages if p.markdown.strip()]
    return "\n\n".join(parts).strip()


def extract_pdf(content: bytes, *, filename: str = "") -> ExtractedDoc:
    """Extract markdown from PDF bytes using the embedded text layer only."""
    import pymupdf
    import pymupdf4llm

    warnings: list[str] = []

    try:
        doc = pymupdf.open(stream=content, filetype="pdf")
    except Exception as exc:
        raise ExtractionError(f"Could not open PDF: {exc}") from exc

    if doc.needs_pass:
        raise ExtractionError("PDF is password-protected — remove the password and re-upload")
    if doc.page_count == 0:
        raise ExtractionError("PDF has no pages")

    try:
        raw_chunks = pymupdf4llm.to_markdown(doc, page_chunks=True, use_ocr=False)
    except Exception as exc:
        raise ExtractionError(f"PDF text extraction failed: {exc}") from exc

    pages: list[PageText] = []
    for index, chunk in enumerate(raw_chunks):
        metadata = chunk.get("metadata") or {}
        pages.append(
            PageText(
                page_number=int(metadata.get("page_number") or index + 1),
                markdown=normalize_markdown(chunk.get("text") or ""),
            )
        )

    starved = [p.page_number for p in pages if _page_lacks_text(p.markdown)]
    if starved:
        warnings.append(
            f"{len(starved)} page(s) have no readable text layer and were skipped: "
            f"pages {_summarize(starved)}. "
            "Upload a searchable PDF, Word (.docx), or Markdown export instead of a raw scan."
        )
        logger.warning("Skipping {} text-less page(s)", len(starved))

    markdown = _assemble(pages)
    if not markdown:
        raise ExtractionError(
            "PDF contains no extractable text — it looks like a scan. "
            "Convert it first (e.g. export as Word or Markdown, or run ocrmypdf to add a "
            "text layer), then upload again."
        )

    logger.info(
        "PDF '{}': {} page(s), {} chars of markdown",
        filename or "upload.pdf",
        doc.page_count,
        len(markdown),
    )
    return ExtractedDoc(
        markdown=markdown,
        source_type="pdf",
        pages=pages,
        page_count=doc.page_count,
        ocr_page_count=0,
        warnings=warnings,
    )


def _summarize(page_numbers: list[int], *, limit: int = 10) -> str:
    shown = ", ".join(str(n) for n in page_numbers[:limit])
    return shown if len(page_numbers) <= limit else f"{shown}, …"
