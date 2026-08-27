"""Entity extraction over real tenant data, with typo tolerance.

Students write "phyiscs clss" and "AL fisics". Matching those against a fixed
list of hardcoded subject spellings fails silently and the agent then reports
"you have no upcoming classes" — indistinguishable, from the student's side,
from a class that genuinely doesn't exist. Everything here resolves references
against the tenant's *actual* class rows so the caller can tell "no such class"
apart from "class exists, but you aren't enrolled/approved yet".
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Any

from services.nlu.normalize import has_word_characters, raw_tokens, strip_emoji

#: Canonical subject spellings, and the misspellings/short forms seen in the QA
#: log. Fuzzy matching handles the rest.
_SUBJECT_ALIASES: dict[str, str] = {
    "physics": "Physics",
    "phy": "Physics",
    "fizik": "Physics",
    "chemistry": "Chemistry",
    "chem": "Chemistry",
    "biology": "Biology",
    "bio": "Biology",
    "maths": "Mathematics",
    "math": "Mathematics",
    "mathematics": "Mathematics",
    "combined": "Combined Maths",
    "ict": "ICT",
    "english": "English",
    "science": "Science",
    "සිංහල": "Sinhala",
    "භෞතික": "Physics",
    "රසායන": "Chemistry",
    "ජීව": "Biology",
    "ගණිත": "Mathematics",
    "இயற்பியல்": "Physics",
    "வேதியியல்": "Chemistry",
    "உயிரியல்": "Biology",
    "கணிதம்": "Mathematics",
}

_GRADE_AL = re.compile(r"\b(a\s*/?\s*l|advanced\s+level|al)\b", re.IGNORECASE)
_GRADE_OL = re.compile(r"\b(o\s*/?\s*l|ordinary\s+level|ol)\b", re.IGNORECASE)
_GRADE_NUMERIC = re.compile(r"\b(?:grade|year)\s*(\d{1,2})\b", re.IGNORECASE)

#: Tokens that look like subjects to a fuzzy matcher but never are. Without this
#: guard "class" scores 0.8 against "chemistry"-adjacent noise.
_NEVER_A_SUBJECT = frozenset(
    {"class", "classes", "clss", "clas", "claas", "subject", "grade", "exam", "paper", "tute"}
)


@dataclass
class ClassReference:
    """What a student's mention of a class resolved to."""

    subject: str | None = None
    grade: str | None = None
    matches: list[dict[str, Any]] = field(default_factory=list)
    corrected_terms: dict[str, str] = field(default_factory=dict)

    @property
    def resolved(self) -> bool:
        return bool(self.matches)

    @property
    def ambiguous(self) -> bool:
        return len(self.matches) > 1

    @property
    def mentions_a_class(self) -> bool:
        """The student referred to *some* class, whether or not it exists."""
        return bool(self.subject or self.grade)

    @property
    def only_match(self) -> dict[str, Any] | None:
        return self.matches[0] if len(self.matches) == 1 else None


def extract_grade(message: str) -> str | None:
    text = strip_emoji(message or "")
    if _GRADE_AL.search(text):
        return "A/L"
    if _GRADE_OL.search(text):
        return "O/L"
    numeric = _GRADE_NUMERIC.search(text)
    if numeric:
        return f"Grade {numeric.group(1)}"
    return None


def extract_subject(
    message: str,
    *,
    known_subjects: list[str] | None = None,
) -> tuple[str | None, str | None]:
    """Return ``(subject, corrected_from)`` for the subject named in ``message``.

    ``corrected_from`` is the student's original spelling when it only matched
    fuzzily, so the caller can echo the correction back ("I read that as
    Physics") rather than silently answering about something else.
    """
    candidates = {alias: canon for alias, canon in _SUBJECT_ALIASES.items()}
    for subject in known_subjects or []:
        cleaned = (subject or "").strip()
        if cleaned:
            candidates[cleaned.lower()] = cleaned

    tokens = raw_tokens(message)
    for token in tokens:
        if token in candidates:
            return candidates[token], None

    for token in tokens:
        if token in _NEVER_A_SUBJECT or len(token) < 4:
            continue
        match = _closest(token, candidates.keys(), cutoff=0.78)
        if match:
            return candidates[match], token
    return None, None


def resolve_class_reference(
    message: str,
    *,
    classes: list[dict[str, Any]],
) -> ClassReference:
    """Resolve a class mention against the tenant's real class rows.

    Both the subject and the grade are matched with typo tolerance, and the
    result reports whether the student named a class at all — the distinction
    the "no upcoming classes" reply was missing.
    """
    known_subjects = [str(c.get("subject") or "") for c in classes]
    subject, corrected_from = extract_subject(message, known_subjects=known_subjects)
    grade = extract_grade(message)

    corrections = {corrected_from: subject} if corrected_from and subject else {}

    if not subject and not grade:
        name_match = _match_by_class_name(message, classes)
        if name_match:
            return ClassReference(
                subject=name_match.get("subject"),
                grade=name_match.get("grade"),
                matches=[name_match],
            )
        return ClassReference(corrected_terms=corrections)

    matches = [
        row
        for row in classes
        if (not subject or _same(row.get("subject"), subject))
        and (not grade or _same(row.get("grade"), grade))
    ]
    return ClassReference(
        subject=subject,
        grade=grade,
        matches=matches,
        corrected_terms=corrections,
    )


def _match_by_class_name(
    message: str, classes: list[dict[str, Any]]
) -> dict[str, Any] | None:
    """Fall back to the class's display name ("A/L Physics 2026")."""
    tokens = set(raw_tokens(message))
    if not tokens:
        return None
    for row in classes:
        name_tokens = set(raw_tokens(str(row.get("name") or "")))
        name_tokens -= _NEVER_A_SUBJECT
        if name_tokens and name_tokens <= tokens:
            return row
    return None


def _same(value: Any, expected: str) -> bool:
    return str(value or "").strip().lower() == expected.strip().lower()


def _closest(token: str, options: Any, *, cutoff: float) -> str | None:
    best: str | None = None
    best_score = cutoff
    for option in options:
        if abs(len(option) - len(token)) > 3:
            continue
        score = SequenceMatcher(None, token, option).ratio()
        if score > best_score:
            best_score = score
            best = option
    return best


# ── registration field validation ────────────────────────────────────────

_MIN_NAME_LETTERS = 2
_PHONE_RE = re.compile(r"^\+?[\d\s\-()]{9,15}$")


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    reason: str = ""

    def __bool__(self) -> bool:
        return self.ok


def validate_registration_value(value: str, *, field_kind: str = "text") -> ValidationResult:
    """Reject registration answers that cannot be a real name/school/district.

    Emoji-only and punctuation-only answers were previously stored verbatim,
    producing student records named "💅💅💅".
    """
    text = (value or "").strip()
    if not text:
        return ValidationResult(False, "empty")

    if field_kind == "phone":
        digits = re.sub(r"\D", "", text)
        if not _PHONE_RE.match(text) or not 9 <= len(digits) <= 15:
            return ValidationResult(False, "not a phone number")
        return ValidationResult(True)

    if not has_word_characters(text):
        return ValidationResult(False, "no letters or digits")

    letters = [ch for ch in strip_emoji(text) if unicodedata.category(ch)[0] == "L"]
    if field_kind in {"name", "text"} and len(letters) < _MIN_NAME_LETTERS:
        return ValidationResult(False, "too few letters")

    if field_kind == "name" and any(ch.isdigit() for ch in text) and not letters:
        return ValidationResult(False, "digits only")

    return ValidationResult(True)


__all__ = [
    "ClassReference",
    "ValidationResult",
    "extract_grade",
    "extract_subject",
    "resolve_class_reference",
    "validate_registration_value",
]
