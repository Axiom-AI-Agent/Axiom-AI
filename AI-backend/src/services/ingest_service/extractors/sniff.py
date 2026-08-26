"""Detect upload format from content, not from the filename.

Both the filename and the ``Content-Type`` header are supplied by the client, so
neither is evidence of what the bytes are. Browsers also report `.docx`
inconsistently (``application/vnd.openxmlformats-...``, ``application/zip`` or
``application/octet-stream`` depending on OS), which makes a MIME allowlist a
maintenance burden that sniffing avoids entirely.
"""

from __future__ import annotations

import zipfile
from io import BytesIO

from services.ingest_service.extractors.base import ExtractionError, SourceType

_PDF_MAGIC = b"%PDF-"
_ZIP_MAGIC = b"PK\x03\x04"
# OLE2 compound file — legacy .doc/.xls/.ppt.
_OLE2_MAGIC = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"

# OOXML formats are all zip archives, so the PK header alone is ambiguous;
# the part name inside the archive is what identifies the format.
_OOXML_MARKERS: tuple[tuple[str, SourceType], ...] = (
    ("word/document.xml", "docx"),
    ("ppt/presentation.xml", "pptx"),
    ("xl/workbook.xml", "xlsx"),
)

SUPPORTED_FORMATS: frozenset[SourceType] = frozenset({"pdf", "docx", "markdown"})


def _zip_format(content: bytes) -> SourceType:
    try:
        names = set(zipfile.ZipFile(BytesIO(content)).namelist())
    except zipfile.BadZipFile as exc:
        raise ExtractionError("File looks like a zip archive but could not be read") from exc

    for marker, source_type in _OOXML_MARKERS:
        if marker in names:
            if source_type == "docx":
                return "docx"
            raise ExtractionError(
                f"{source_type.upper()} files are not supported yet — "
                "upload a PDF or Word (.docx) document"
            )
    raise ExtractionError("Unsupported zip archive — upload a PDF, Word (.docx) or Markdown file")


def _looks_like_text(content: bytes) -> bool:
    """Heuristic: decodable as UTF-8 and free of NUL bytes."""
    if b"\x00" in content[:8192]:
        return False
    try:
        content[:8192].decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def sniff_format(content: bytes, *, filename: str = "") -> SourceType:
    """Return the source type for ``content``, or raise ExtractionError.

    ``filename`` is used only to disambiguate plain text, never to override what
    the bytes say.
    """
    if not content:
        raise ExtractionError("Empty file")

    if content.startswith(_PDF_MAGIC):
        return "pdf"
    if content.startswith(_ZIP_MAGIC):
        return _zip_format(content)
    if content.startswith(_OLE2_MAGIC):
        raise ExtractionError(
            "Legacy .doc files are not supported — open the file in Word and "
            "'Save As' .docx, then upload again"
        )
    if _looks_like_text(content):
        return "markdown"

    suffix = filename.rsplit(".", 1)[-1].lower() if "." in filename else "?"
    raise ExtractionError(
        f"Unrecognised file format (.{suffix}) — upload a PDF, Word (.docx) or Markdown file"
    )
