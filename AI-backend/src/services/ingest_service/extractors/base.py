"""Shared types for document extraction.

Every extractor converts source bytes into markdown. Markdown is the pipeline's
intermediate representation because it carries structure in-band (``#`` headings,
pipe tables), which lets the chunkers split on semantic boundaries without a
separate structural model.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

SourceType = str  # "pdf" | "docx" | "markdown"

_HEADING_RE = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<text>.*?)\s*#*\s*$")
_EMPHASIS_RE = re.compile(r"(\*\*|__|\*|_)")
_BLANK_RUN_RE = re.compile(r"\n{3,}")


def normalize_markdown(markdown: str) -> str:
    """Clean up extractor output so headings are usable as breadcrumbs.

    Layout-derived headings often arrive wrapped in emphasis (``# **Title**``)
    because the source styled them bold as well as large. Left in place, that
    punctuation ends up inside every child chunk's heading prefix.
    """
    lines: list[str] = []
    for line in markdown.split("\n"):
        match = _HEADING_RE.match(line)
        if match:
            text = _EMPHASIS_RE.sub("", match.group("text")).strip()
            lines.append(f"{match.group('hashes')} {text}" if text else "")
        else:
            lines.append(line.rstrip())
    return _BLANK_RUN_RE.sub("\n\n", "\n".join(lines)).strip()


class ExtractionError(ValueError):
    """Raised when a document cannot be turned into usable markdown.

    Subclasses ValueError so the API layer keeps mapping it to HTTP 422.
    """


@dataclass(frozen=True)
class PageText:
    """One page of a paginated source document."""

    page_number: int  # 1-based, matches what a reader sees
    markdown: str
    ocr_used: bool = False


@dataclass(frozen=True)
class ExtractedDoc:
    """Normalized extraction result handed to the ingest pipeline."""

    markdown: str
    source_type: SourceType
    pages: list[PageText] | None = None  # None for formats without pagination
    page_count: int | None = None
    ocr_page_count: int = 0
    warnings: list[str] = field(default_factory=list)

    @property
    def has_headings(self) -> bool:
        return any(line.startswith("#") for line in self.markdown.splitlines())
