"""Normalize student-facing chat text for WhatsApp and Telegram."""

from __future__ import annotations

import re

_BOLD_MARKERS = re.compile(r"\*\*(.+?)\*\*", re.DOTALL)


def strip_markdown_markers(text: str) -> str:
    """Remove markdown ``**bold**`` markers so they do not show as raw asterisks."""
    if not text:
        return text
    cleaned = _BOLD_MARKERS.sub(r"\1", text)
    return cleaned.replace("**", "")
