"""Classify an inbound attachment so each media type gets its own handling.

The inbound path used to ask one question — "is this a voice note?" — and treat
every "no" as a broken voice note. A student photographing their bank slip, the
single most common attachment a tuition centre receives, was answered with
"Sorry, I can only process voice notes" (B6). Naming the media kind explicitly
makes the image path reachable and leaves a real branch for the formats we
genuinely cannot read.
"""

from __future__ import annotations

from enum import Enum

from services.media.stt_service import VOICE_NOTE_EXTENSIONS

_IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".bmp", ".gif"})
_DOCUMENT_EXTENSIONS = frozenset({".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt", ".csv"})
_OTHER_AUDIO_EXTENSIONS = frozenset({".mp3", ".m4a", ".wav", ".aac", ".amr", ".flac"})
_VIDEO_EXTENSIONS = frozenset({".mp4", ".mov", ".3gp", ".avi", ".mkv", ".webm"})


class MediaKind(str, Enum):
    NONE = "none"
    VOICE_NOTE = "voice_note"
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO_FILE = "audio_file"
    VIDEO = "video"
    UNKNOWN = "unknown"

    @property
    def is_payment_slip_candidate(self) -> bool:
        """Formats a bank slip plausibly arrives in."""
        return self in {MediaKind.IMAGE, MediaKind.DOCUMENT}


def classify_media(url: str | None, *, content_type: str | None = None) -> MediaKind:
    """Best-effort media kind from a Content-Type header or URL extension."""
    if not url:
        return MediaKind.NONE

    mime = (content_type or "").split(";")[0].strip().lower()
    if mime:
        if mime in {"audio/ogg", "audio/opus"} or mime.endswith("+opus"):
            return MediaKind.VOICE_NOTE
        if mime.startswith("image/"):
            return MediaKind.IMAGE
        if mime.startswith("video/"):
            return MediaKind.VIDEO
        if mime.startswith("audio/"):
            return MediaKind.AUDIO_FILE
        if mime == "application/pdf" or mime.startswith("application/vnd.") or mime.startswith("text/"):
            return MediaKind.DOCUMENT

    suffix = _suffix(url)
    if suffix in VOICE_NOTE_EXTENSIONS:
        return MediaKind.VOICE_NOTE
    if suffix in _IMAGE_EXTENSIONS:
        return MediaKind.IMAGE
    if suffix in _DOCUMENT_EXTENSIONS:
        return MediaKind.DOCUMENT
    if suffix in _OTHER_AUDIO_EXTENSIONS:
        return MediaKind.AUDIO_FILE
    if suffix in _VIDEO_EXTENSIONS:
        return MediaKind.VIDEO
    return MediaKind.UNKNOWN


def _suffix(url: str) -> str:
    path = url.lower().split("?")[0].split("#")[0]
    _, dot, ext = path.rpartition(".")
    return f".{ext}" if dot else ""


__all__ = ["MediaKind", "classify_media"]
