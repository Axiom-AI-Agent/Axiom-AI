"""Student-facing language helpers (Sinhala, Tamil, English, code-switching)."""

from services.language.detect import (
    LANGUAGE_NAMES,
    SUPPORTED_LANGUAGES,
    detect_script_language,
    language_policy_block,
    looks_like_singlish,
    looks_like_tanglish,
    normalize_canned_language,
    normalize_language_pref,
    resolve_canned_language,
    resolve_reply_language,
    retrieval_query,
    stt_language_hint,
    with_language_policy,
)
from services.language.templates import t

__all__ = [
    "LANGUAGE_NAMES",
    "SUPPORTED_LANGUAGES",
    "detect_script_language",
    "language_policy_block",
    "normalize_language_pref",
    "resolve_reply_language",
    "stt_language_hint",
    "t",
    "with_language_policy",
    "looks_like_singlish",
    "looks_like_tanglish",
    "normalize_canned_language",
    "resolve_canned_language",
    "retrieval_query",
]
