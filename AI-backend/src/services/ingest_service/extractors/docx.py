"""DOCX → markdown via mammoth (HTML) → markdownify.

mammoth keys off Word's *semantic* styles in ``styles.xml`` rather than visual
formatting, so a heading someone faked by bolding 16pt text is correctly not
promoted. That is the right default, but plenty of real tutor documents —
Google Docs exports in particular — carry no paragraph styles at all, leaving a
completely flat document. `_promote_bold_headings` recovers section boundaries
in that case so heading-breadcrumb contextualization still has something to work
with.
"""

from __future__ import annotations

import re
from io import BytesIO

from loguru import logger

from infrastructure.config import INGEST_DOCX_PROMOTE_BOLD_HEADINGS
from services.ingest_service.extractors.base import (
    ExtractedDoc,
    ExtractionError,
    normalize_markdown,
)

# Word style names that should become headings but are not part of mammoth's
# default map (it already handles "Heading 1".."Heading 6").
_STYLE_MAP = """
p[style-name='Title'] => h1:fresh
p[style-name='Subtitle'] => h2:fresh
p[style-name='Section Title'] => h1:fresh
p[style-name='Subsection Title'] => h2:fresh
"""

# A whole-line bold run, e.g. "**1. The Core Problem**".
_BOLD_LINE_RE = re.compile(r"^\*\*(?P<text>.+?)\*\*:?$")
# Leading section numbers tell us the depth: "1." -> h2, "1.2" -> h3.
_NUMBER_PREFIX_RE = re.compile(r"^(?P<digits>\d+(?:\.\d+)*)[.)]?\s+")

_MAX_HEADING_CHARS = 120


def _looks_like_heading(text: str) -> bool:
    if len(text) > _MAX_HEADING_CHARS:
        return False
    # Real headings do not end in sentence punctuation.
    if text.rstrip().endswith((".", "!", "?", ";", ",")):
        return False
    # Needs at least one word character, and should not be a bare number.
    return bool(re.search(r"[A-Za-z]", text))


def _heading_level(text: str, *, is_first: bool) -> int:
    match = _NUMBER_PREFIX_RE.match(text)
    if match:
        return min(2 + match.group("digits").count("."), 6)
    return 1 if is_first else 2


def _promote_bold_headings(markdown: str) -> tuple[str, int]:
    """Turn standalone whole-line bold paragraphs into markdown headings."""
    lines = markdown.split("\n")
    out: list[str] = []
    promoted = 0
    seen_heading = False

    for index, line in enumerate(lines):
        stripped = line.strip()
        match = _BOLD_LINE_RE.match(stripped)
        if not match:
            if stripped.startswith("#"):
                seen_heading = True
            out.append(line)
            continue

        text = match.group("text").strip()
        # Must be a standalone paragraph, not one bold line inside a block.
        prev_blank = index == 0 or not lines[index - 1].strip()
        next_blank = index == len(lines) - 1 or not lines[index + 1].strip()
        if not (prev_blank and next_blank and _looks_like_heading(text)):
            out.append(line)
            continue

        level = _heading_level(text, is_first=not seen_heading)
        seen_heading = True
        promoted += 1
        out.append(f"{'#' * level} {text}")

    return "\n".join(out), promoted


def extract_docx(content: bytes, *, filename: str = "") -> ExtractedDoc:
    """Extract markdown from .docx bytes."""
    import mammoth
    from markdownify import markdownify

    try:
        result = mammoth.convert_to_html(BytesIO(content), style_map=_STYLE_MAP)
    except Exception as exc:
        raise ExtractionError(f"Could not read Word document: {exc}") from exc

    warnings = [str(m) for m in result.messages if getattr(m, "type", "") == "warning"]

    markdown = markdownify(result.value, heading_style="ATX").strip()
    if not markdown:
        raise ExtractionError("Word document contains no extractable text")

    has_headings = any(line.startswith("#") for line in markdown.splitlines())
    if not has_headings and INGEST_DOCX_PROMOTE_BOLD_HEADINGS:
        markdown, promoted = _promote_bold_headings(markdown)
        if promoted:
            logger.info("Recovered {} heading(s) from bold paragraphs in {}", promoted, filename)
            warnings.append(
                f"No Word heading styles found; inferred {promoted} heading(s) from "
                "bold paragraphs. For best retrieval, apply Word's Heading styles."
            )
        else:
            warnings.append(
                "No headings found in this document — retrieval quality will be lower. "
                "Apply Word's Heading 1/2/3 styles and re-upload."
            )

    markdown = normalize_markdown(markdown)

    logger.info("DOCX '{}': {} chars of markdown", filename or "upload.docx", len(markdown))
    return ExtractedDoc(
        markdown=markdown,
        source_type="docx",
        pages=None,  # .docx has no fixed pagination until it is rendered
        page_count=None,
        warnings=warnings,
    )
