"""Format sniffing, DOCX/markdown extraction, and PDF text-layer routing."""

from __future__ import annotations

import io
import zipfile

import pytest

from services.ingest_service.extractors import (
    ExtractionError,
    extract_document,
    sniff_format,
    title_from_filename,
)
from services.ingest_service.extractors.base import normalize_markdown
from services.ingest_service.extractors.docx import _promote_bold_headings
from services.ingest_service.extractors.pdf import _page_lacks_text

_OLE2 = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"


def _ooxml(part: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("[Content_Types].xml", "<Types/>")
        z.writestr(part, "<x/>")
    return buf.getvalue()


class TestSniffFormat:
    def test_detects_pdf(self):
        assert sniff_format(b"%PDF-1.7\nrest") == "pdf"

    def test_detects_docx_by_part_name(self):
        assert sniff_format(_ooxml("word/document.xml")) == "docx"

    def test_detects_markdown(self):
        assert sniff_format(b"# Heading\n\nbody") == "markdown"

    def test_extension_does_not_override_content(self):
        """A PDF named .docx is a PDF — filename is client-controlled."""
        assert sniff_format(b"%PDF-1.4 x", filename="mislabelled.docx") == "pdf"

    def test_legacy_doc_gets_actionable_error(self):
        with pytest.raises(ExtractionError, match=r"\.docx"):
            sniff_format(_OLE2 + b"\x00" * 32, filename="old.doc")

    def test_pptx_rejected_by_name(self):
        with pytest.raises(ExtractionError, match="PPTX"):
            sniff_format(_ooxml("ppt/presentation.xml"))

    def test_empty_rejected(self):
        with pytest.raises(ExtractionError, match="Empty"):
            sniff_format(b"")

    def test_unknown_binary_rejected(self):
        with pytest.raises(ExtractionError, match="Unrecognised"):
            sniff_format(b"\x89PNG\r\n\x1a\n" + bytes(range(64)), filename="x.png")


class TestPageLacksText:
    def test_empty_page(self):
        assert _page_lacks_text("") is True

    def test_short_page(self):
        assert _page_lacks_text("Figure 1") is True

    def test_prose_page_does_not(self):
        assert _page_lacks_text("Velocity is the rate of change of displacement. " * 5) is False

    def test_symbol_noise(self):
        assert _page_lacks_text("|/\\-_=+*&^%$#@!" * 20) is True


class TestNormalizeMarkdown:
    def test_strips_emphasis_from_headings(self):
        assert normalize_markdown("# **Kinematics** ") == "# Kinematics"

    def test_leaves_body_emphasis_alone(self):
        assert normalize_markdown("Some **bold** body") == "Some **bold** body"

    def test_collapses_blank_runs(self):
        assert normalize_markdown("a\n\n\n\n\nb") == "a\n\nb"


class TestPromoteBoldHeadings:
    def test_promotes_standalone_bold_paragraph(self):
        md, count = _promote_bold_headings("**Kinematics**\n\nBody text here.")
        assert count == 1
        assert md.startswith("# Kinematics")

    def test_infers_depth_from_section_numbers(self):
        md, _ = _promote_bold_headings("# Doc\n\n**1. Intro**\n\nx\n\n**1.2 Detail**\n\ny")
        assert "## 1. Intro" in md
        assert "### 1.2 Detail" in md

    def test_ignores_bold_sentences(self):
        text = "**This is a full sentence that ends with a period.**\n\nBody."
        _, count = _promote_bold_headings(text)
        assert count == 0

    def test_ignores_inline_bold(self):
        _, count = _promote_bold_headings("Body with **bold** inline.\n\nMore.")
        assert count == 0


class TestExtractDocument:
    def test_markdown_roundtrip(self):
        doc = extract_document(b"# Kinematics\n\nVelocity is displacement over time.")
        assert doc.source_type == "markdown"
        assert doc.has_headings
        assert doc.page_count is None

    def test_markdown_strips_front_matter(self):
        doc = extract_document(b"---\ntitle: x\n---\n# Real Heading\n\nbody")
        assert doc.markdown.startswith("# Real Heading")

    def test_oversized_upload_rejected(self):
        oversized = b"# h\n" + b"a" * (6 * 1024 * 1024)
        with pytest.raises(ExtractionError, match="limit"):
            extract_document(oversized, filename="big.md")


def test_title_from_filename():
    assert title_from_filename("lesson_5-velocity.pdf") == "Lesson 5 Velocity"
