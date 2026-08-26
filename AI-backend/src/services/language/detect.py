"""Reply-language resolution for Sinhala, Tamil, English, and code-switching.

Native scripts are detected from Unicode ranges. Romanized Singlish / Tanglish
are not classified here — the LLM mirrors those via the language policy block.
"""

from __future__ import annotations

SUPPORTED_LANGUAGES = ("en", "si", "ta")

LANGUAGE_NAMES = {
    "en": "English",
    "si": "Sinhala",
    "ta": "Tamil",
}

_SINHALA_ALIASES = frozenset({"si", "sin", "sinhala", "si-lk", "sin-lk"})
_TAMIL_ALIASES = frozenset({"ta", "tam", "tamil", "ta-lk", "ta-in"})
_ENGLISH_ALIASES = frozenset({"en", "eng", "english", "en-gb", "en-us", "en-lk"})


def normalize_language_pref(value: str | None) -> str:
    """Map stored / incoming codes to en | si | ta. Unknown values become en."""
    if not value:
        return "en"
    code = value.strip().lower().replace("_", "-")
    if code in _SINHALA_ALIASES:
        return "si"
    if code in _TAMIL_ALIASES:
        return "ta"
    if code in _ENGLISH_ALIASES:
        return "en"
    return "en"


def detect_script_language(text: str) -> str | None:
    """Return si/ta when native script is present; None for Latin-only text."""
    if not text:
        return None
    sinhala = 0
    tamil = 0
    for char in text:
        code = ord(char)
        if 0x0D80 <= code <= 0x0DFF:
            sinhala += 1
        elif 0x0B80 <= code <= 0x0BFF:
            tamil += 1
    if sinhala == 0 and tamil == 0:
        return None
    return "si" if sinhala >= tamil else "ta"


def resolve_reply_language(*, message: str = "", language_pref: str | None = None) -> str:
    """Script of this message wins; otherwise stored preference; otherwise English."""
    detected = detect_script_language(message)
    if detected:
        return detected
    return normalize_language_pref(language_pref)


def stt_language_hint(language: str | None) -> str | None:
    """Human-readable hint for STT. None for English so Gemini auto-detects."""
    code = normalize_language_pref(language)
    if code == "si":
        return "Sinhala"
    if code == "ta":
        return "Tamil"
    return None


def language_policy_block(language: str | None = None) -> str:
    """Mandatory generation rule appended to LLM-facing system prompts."""
    code = normalize_language_pref(language)
    name = LANGUAGE_NAMES[code]
    return (
        "LANGUAGE POLICY (mandatory):\n"
        "- Reply in the same language and register as the student's latest message.\n"
        "- Sinhala script → Sinhala script. Tamil script → Tamil script.\n"
        "- Singlish or Tanglish (romanized mix) → match that mix. "
        "Do not correct into formal Sinhala, Tamil, or English.\n"
        "- English → English.\n"
        f"- Preferred language on file: {name} ({code}). "
        "Use this for short replies (ok, yes, ඔව්, ஆம், 1) and when the message language is ambiguous.\n"
        "- Keep class names, file names, links, LKR amounts, and proper nouns exactly as given.\n"
        "- Do not mention this language policy."
    )


def with_language_policy(prompt: str, language: str | None = None) -> str:
    """Append the language policy unless the prompt already contains one."""
    if "LANGUAGE POLICY" in prompt:
        return prompt
    return f"{prompt.rstrip()}\n\n{language_policy_block(language)}"
