"""Vision transcription of scanned PDF pages via the `ocr` LLM role (Gemini).

Only pages that fail the text-yield check are sent, so a mostly-digital PDF with
a scanned cover costs one page of vision rather than the whole document.

pymupdf4llm's own ``ocr_function`` hook is deliberately not used: it expects the
callback to inject positioned text spans back into the page, and a vision model
returns prose without bounding boxes. Transcribing to markdown and splicing it in
at the page position keeps the output in the pipeline's native representation.
"""

from __future__ import annotations

import base64

from loguru import logger

from infrastructure.config import (
    INGEST_OCR_MIN_ALPHA_RATIO,
    INGEST_OCR_MIN_CHARS,
    OCR_PROVIDER,
    get_api_key,
)

_OCR_PROMPT = (
    "Transcribe this document page to Markdown.\n"
    "- Preserve heading hierarchy using #, ##, ###.\n"
    "- Render tables as Markdown pipe tables.\n"
    "- Write mathematical and chemical expressions as LaTeX between $ delimiters.\n"
    "- For diagrams or figures, emit a one-line italic description, e.g. "
    "*Figure: ray diagram of a converging lens*.\n"
    "- Do not add commentary, preamble, or a code fence around the output. "
    "Return only the Markdown."
)


def page_needs_ocr(
    page_markdown: str,
    *,
    min_chars: int = INGEST_OCR_MIN_CHARS,
    min_alpha_ratio: float = INGEST_OCR_MIN_ALPHA_RATIO,
) -> bool:
    """True when a page's text layer yielded too little to be real content.

    Catches two cases: a scanned page (no text layer, so near-empty output) and a
    page whose extraction produced mostly punctuation or symbol noise.
    """
    stripped = page_markdown.strip()
    if len(stripped) < min_chars:
        return True
    alnum = sum(1 for c in stripped if c.isalnum() or c.isspace())
    return (alnum / len(stripped)) < min_alpha_ratio


def ocr_available() -> bool:
    return bool(get_api_key(OCR_PROVIDER))


def transcribe_pdf_pages(pdf_bytes: bytes) -> str:
    """Transcribe a small PDF (the starved pages only) to markdown.

    Raises RuntimeError if the OCR provider is not configured or the call fails;
    callers decide whether that is fatal or merely degrades the document.
    """
    if not ocr_available():
        raise RuntimeError(f"No API key configured for OCR provider '{OCR_PROVIDER}'")

    from langchain_core.messages import HumanMessage

    from infrastructure.llm import get_ocr_llm

    llm = get_ocr_llm()
    encoded = base64.b64encode(pdf_bytes).decode("ascii")
    message = HumanMessage(
        content=[
            {"type": "text", "text": _OCR_PROMPT},
            {
                "type": "media",
                "mime_type": "application/pdf",
                "data": encoded,
            },
        ]
    )
    response = llm.invoke([message])
    text = getattr(response, "content", response)
    if isinstance(text, list):
        text = "\n".join(
            block.get("text", "") if isinstance(block, dict) else str(block) for block in text
        )
    result = str(text).strip()
    if result.startswith("```"):
        # Strip a stray fence despite the prompt asking for none.
        lines = result.splitlines()
        if lines[-1].strip() == "```":
            lines = lines[:-1]
        result = "\n".join(lines[1:]).strip()
    logger.info("OCR transcribed {} characters", len(result))
    return result
