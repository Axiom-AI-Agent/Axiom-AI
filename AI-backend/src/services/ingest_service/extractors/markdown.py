"""Markdown / plain-text passthrough."""

from __future__ import annotations

import re

from loguru import logger

from services.ingest_service.extractors.base import (
    ExtractedDoc,
    ExtractionError,
    normalize_markdown,
)

_FRONT_MATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)


def extract_markdown(content: bytes, *, filename: str = "") -> ExtractedDoc:
    """Decode markdown bytes, stripping YAML front matter if present."""
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = content.decode("latin-1")
        except UnicodeDecodeError as exc:
            raise ExtractionError("Could not decode text file as UTF-8") from exc

    markdown = normalize_markdown(_FRONT_MATTER_RE.sub("", text))
    if not markdown:
        raise ExtractionError("File is empty")

    logger.info("Markdown '{}': {} chars", filename or "upload.md", len(markdown))
    return ExtractedDoc(markdown=markdown, source_type="markdown")
