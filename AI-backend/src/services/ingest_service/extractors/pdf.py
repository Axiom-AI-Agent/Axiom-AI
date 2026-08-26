"""PDF → markdown via pymupdf4llm, with per-page vision OCR for scanned pages.

Replaces the previous flat `pypdf` extraction, which returned characters in
content-stream order (interleaving columns), lost every heading and table, and
silently dropped scanned pages because ``extract_text()`` returns "" for them.
"""

from __future__ import annotations

from loguru import logger

from infrastructure.config import (
    INGEST_OCR_ENABLED,
    INGEST_OCR_MAX_PAGES,
)
from services.ingest_service.extractors.base import (
    ExtractedDoc,
    ExtractionError,
    PageText,
    normalize_markdown,
)
from services.ingest_service.extractors.ocr import (
    ocr_available,
    page_needs_ocr,
    transcribe_pdf_pages,
)


def _page_marker(page_number: int) -> str:
    return f"<!-- page:{page_number} -->"


def _assemble(pages: list[PageText]) -> str:
    """Join pages with an HTML-comment page marker.

    Markdown renderers and the LLM ignore HTML comments, but they let the chunker
    attribute a chunk back to a page number for citations.
    """
    parts = [f"{_page_marker(p.page_number)}\n{p.markdown.strip()}" for p in pages if p.markdown.strip()]
    return "\n\n".join(parts).strip()


def extract_pdf(content: bytes, *, filename: str = "", enable_ocr: bool | None = None) -> ExtractedDoc:
    """Extract markdown from PDF bytes, OCR-ing only pages with no usable text."""
    # Imported lazily: pymupdf4llm pulls in onnxruntime, which costs ~1s and a
    # chunk of RSS at import time. The API process should not pay that unless a
    # PDF is actually being ingested.
    import pymupdf
    import pymupdf4llm

    use_ocr = INGEST_OCR_ENABLED if enable_ocr is None else enable_ocr
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
        # use_ocr=False: we route starved pages to the vision model ourselves
        # rather than relying on a local OCR engine that is not in the image.
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

    starved = [p.page_number for p in pages if page_needs_ocr(p.markdown)]

    if starved and use_ocr and ocr_available():
        pages, ocr_count, ocr_warnings = _ocr_pages(doc, pages, starved)
        warnings.extend(ocr_warnings)
    else:
        ocr_count = 0
        if starved:
            reason = (
                "OCR is disabled"
                if not use_ocr
                else "no OCR API key is configured"
                if not ocr_available()
                else ""
            )
            warnings.append(
                f"{len(starved)} page(s) have no readable text layer and were skipped "
                f"because {reason}: pages {_summarize(starved)}"
            )
            logger.warning("Skipping {} text-less page(s) — {}", len(starved), reason)

    markdown = _assemble(pages)
    if not markdown:
        raise ExtractionError(
            "PDF contains no extractable text. It is likely a scan — enable OCR "
            "(set a GOOGLE_API_KEY) and try again."
        )

    logger.info(
        "PDF '{}': {} page(s), {} OCR'd, {} chars of markdown",
        filename or "upload.pdf",
        doc.page_count,
        ocr_count,
        len(markdown),
    )
    return ExtractedDoc(
        markdown=markdown,
        source_type="pdf",
        pages=pages,
        page_count=doc.page_count,
        ocr_page_count=ocr_count,
        warnings=warnings,
    )


def _ocr_pages(
    doc,
    pages: list[PageText],
    starved: list[int],
) -> tuple[list[PageText], int, list[str]]:
    """Transcribe starved pages with the vision model and splice results back in."""
    import pymupdf

    warnings: list[str] = []
    targets = starved
    if len(targets) > INGEST_OCR_MAX_PAGES:
        warnings.append(
            f"{len(starved)} pages need OCR but the per-document limit is "
            f"{INGEST_OCR_MAX_PAGES}; only the first {INGEST_OCR_MAX_PAGES} were transcribed"
        )
        targets = starved[:INGEST_OCR_MAX_PAGES]

    by_number = {p.page_number: p for p in pages}
    transcribed = 0

    for page_number in targets:
        sub = pymupdf.open()
        try:
            sub.insert_pdf(doc, from_page=page_number - 1, to_page=page_number - 1)
            page_bytes = sub.tobytes()
        finally:
            sub.close()

        try:
            markdown = transcribe_pdf_pages(page_bytes)
        except Exception as exc:
            logger.warning("OCR failed for page {}: {}", page_number, exc)
            warnings.append(f"OCR failed for page {page_number}: {exc}")
            continue

        if not markdown:
            continue
        by_number[page_number] = PageText(
            page_number=page_number,
            markdown=markdown,
            ocr_used=True,
        )
        transcribed += 1

    if transcribed:
        logger.info("OCR transcribed {} page(s): {}", transcribed, _summarize(targets))
    return [by_number[p.page_number] for p in pages], transcribed, warnings


def _summarize(page_numbers: list[int], *, limit: int = 10) -> str:
    shown = ", ".join(str(n) for n in page_numbers[:limit])
    return shown if len(page_numbers) <= limit else f"{shown}, …"
