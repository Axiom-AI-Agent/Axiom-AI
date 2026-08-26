"""Multi-format document extraction — PDF, DOCX and Markdown to markdown.

Every extractor returns an :class:`ExtractedDoc`, so adding a format (or swapping
PyMuPDF4LLM for a heavier engine like Docling on a bigger host) is a change in
this package only — the ingest pipeline and chunkers are unaffected.
"""

from __future__ import annotations

from pathlib import Path

from infrastructure.config import INGEST_MAX_UPLOAD_MB
from services.ingest_service.extractors.base import (
    ExtractedDoc,
    ExtractionError,
    PageText,
    SourceType,
)
from services.ingest_service.extractors.docx import extract_docx
from services.ingest_service.extractors.markdown import extract_markdown
from services.ingest_service.extractors.pdf import extract_pdf
from services.ingest_service.extractors.sniff import SUPPORTED_FORMATS, sniff_format

# Advertised to clients so the upload UI and the API agree on one list.
SUPPORTED_EXTENSIONS: tuple[str, ...] = (".pdf", ".docx", ".md", ".markdown", ".txt")


def max_upload_bytes(source_type: SourceType) -> int:
    return INGEST_MAX_UPLOAD_MB.get(source_type, 20) * 1024 * 1024


def extract_document(
    content: bytes,
    *,
    filename: str = "",
) -> ExtractedDoc:
    """Sniff the format of ``content`` and extract it to markdown.

    Raises ExtractionError (a ValueError) for unsupported or unreadable input.
    """
    source_type = sniff_format(content, filename=filename)

    limit = max_upload_bytes(source_type)
    if len(content) > limit:
        raise ExtractionError(
            f"{source_type.upper()} exceeds the {limit // (1024 * 1024)} MB limit "
            f"({len(content) // (1024 * 1024)} MB)"
        )

    if source_type == "pdf":
        return extract_pdf(content, filename=filename)
    if source_type == "docx":
        return extract_docx(content, filename=filename)
    return extract_markdown(content, filename=filename)


def title_from_filename(filename: str) -> str:
    stem = Path(filename).stem
    return stem.replace("_", " ").replace("-", " ").strip().title() or stem


__all__ = [
    "ExtractedDoc",
    "ExtractionError",
    "PageText",
    "SourceType",
    "SUPPORTED_EXTENSIONS",
    "SUPPORTED_FORMATS",
    "extract_document",
    "extract_docx",
    "extract_markdown",
    "extract_pdf",
    "max_upload_bytes",
    "sniff_format",
    "title_from_filename",
]
