"""Abuse detection that does not depend on sentence structure.

"Why do you suck so bad" was blocked while "Man you suck f%$ you" sailed through
to a tutor escalation (A4). The difference was grammatical, not semantic, which
is the signature of a filter keyed on sentence shape. This module normalizes
away the obfuscation students actually use — symbol substitution, repeated
letters, spacing — and then looks for abuse regardless of whether the message is
phrased as a question, a statement, or a fragment.

It is a floor, not a replacement for the guardrail LLM: it catches the blatant
cases deterministically so a single mislabel can't wave them through.
"""

from __future__ import annotations

import re
import unicodedata

#: Characters students substitute to slip past naive filters.
_LEETSPEAK = str.maketrans(
    {
        "0": "o", "1": "i", "!": "i", "|": "i", "3": "e", "4": "a", "@": "a",
        "5": "s", "$": "s", "7": "t", "+": "t", "8": "b", "9": "g",
        "%": "u", "#": "h", "*": "", "^": "", "&": "", "~": "", "_": "",
    }
)

#: Stems, so inflections and compounds are covered without listing each one.
_ABUSE_STEMS = (
    "fuck", "fuk", "fck", "shit", "bitch", "bastard", "asshole", "arsehole",
    "cunt", "dick", "prick", "wanker", "slut", "whore", "retard", "moron",
    "idiot", "stupid", "dumbass", "jackass", "suck", "sucks", "crap",
    "hutta", "pako", "ponnaya", "huttige", "paiya", "thevidiya", "punda",
)

#: Words whose stems appear inside innocent ones. Checked before the stem scan.
_FALSE_POSITIVES = frozenset(
    {"assess", "assessment", "class", "classes", "pass", "password", "assist",
     "assign", "assignment", "massive", "analysis", "shitake", "dickens",
     "cockpit", "scunthorpe", "sucker", "suction"}
)

_REPEAT_RE = re.compile(r"(.)\1{2,}")
_NON_ALNUM_RE = re.compile(r"[^a-z\s]")


def normalize_for_abuse(text: str) -> str:
    """Collapse obfuscation so ``f%$k`` and ``fuuuuck`` reduce to ``fuck``."""
    folded = unicodedata.normalize("NFKD", text or "").lower()
    folded = folded.translate(_LEETSPEAK)
    folded = _NON_ALNUM_RE.sub(" ", folded)
    folded = _REPEAT_RE.sub(r"\1", folded)
    return " ".join(folded.split())


def contains_abuse(message: str) -> bool:
    """True when the message contains abuse, in any sentence form."""
    normalized = normalize_for_abuse(message)
    if not normalized:
        return False

    for word in normalized.split():
        if word in _FALSE_POSITIVES:
            continue
        if any(stem in word for stem in _ABUSE_STEMS):
            return True

    # Also catch abuse split across tokens ("f u c k you", "b i t c h").
    squeezed = normalized.replace(" ", "")
    return any(stem in squeezed for stem in ("fuckyou", "fuckoff", "fucku"))


__all__ = ["contains_abuse", "normalize_for_abuse"]
