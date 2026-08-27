from __future__ import annotations

from typing import Literal

from loguru import logger

from agents.escalation_pending import peek_pending_question
from agents.tools.memory_tool import MemoryTool
from services.language import t
from services.nlu import StudentIntent, classify

ConfirmationDecision = Literal[
    "yes",
    "no",
    "none",
]


#: The exact question the agent asks before escalating. Derived from the
#: template rather than restated here — the two drifted apart once already, and
#: a one-word difference silently stopped every "Yes" from escalating (B4).
CONFIRMATION_TEXT = t("escalation_confirm", "en")

#: Every localized form of that question, so the match does not depend on which
#: language the previous turn was answered in.
_CONFIRMATION_TEXTS = tuple(
    t("escalation_confirm", language).lower() for language in ("en", "si", "ta")
)


YES_REPLIES = {
    "yes",
    "y",
    "yeah",
    "yep",
    "yea",
    "sure",
    "ok",
    "okay",
    "please",
    "yes please",
    "go ahead",
    "do it",
    "send it",
    "yup",
    "yuph",
    "yas",
    "ye",
    "oww",
    "hari",
    "ඔව්",
    "ඔව්වා",
    "හරි",
    "ஆம்",
    "ஆமாம்",
    "சரி",
}


NO_REPLIES = {
    "no",
    "n",
    "nope",
    "nah",
    "no thanks",
    "don't",
    "dont",
    "cancel",
    "it's okay",
    "its okay",
    "never mind",
    "nevermind",
    "නෑ",
    "එපා",
    "இல்லை",
    "வேண்டாம்",
}


def classify_confirmation(
    message: str,
) -> ConfirmationDecision:
    normalized = (
        message
        .strip()
        .lower()
        .rstrip(".!?")
    )

    if normalized in YES_REPLIES:
        return "yes"

    if normalized in NO_REPLIES:
        return "no"

    # The literal sets above only cover replies typed exactly as listed. The
    # classifier handles the rest ("yeah go ahead", "ඔව් හරි") without needing
    # every phrasing enumerated.
    intent = classify(message).intent
    if intent is StudentIntent.AFFIRM:
        return "yes"
    if intent is StudentIntent.DENY:
        return "no"

    return "none"


def get_pending_low_confidence_question(
    *,
    memory_tool: MemoryTool,
    tenant_id: str,
    user_id: str,
    session_id: str,
) -> str | None:
    """The academic question waiting on a yes/no tutor-handoff, if any.

    Prefers the in-process flag written when the agent asked, then falls back
    to the last short-term turns so a restart can still recover the prompt.
    """
    pending = peek_pending_question(session_id)
    if pending:
        return pending

    try:
        pairs = (
            memory_tool.recent_pairs(
                tenant_id=tenant_id,
                user_id=user_id,
                session_id=session_id,
                k=5,
            )
        )
    except Exception as exc:
        logger.warning("pending-escalation ST lookup failed: {}", exc)
        return None

    if not pairs:
        return None

    # Newest complete pair first. A trailing unpaired "Yes" (already logged as
    # inbound before this lookup) is ignored by the pairer, so the last pair
    # should be the RAG ask — but scan a few in case a filler turn landed in
    # between.
    for user_message, assistant_message in reversed(pairs):
        if assistant_message and is_confirmation_prompt(assistant_message):
            return user_message
    return None


def is_confirmation_prompt(assistant_message: str) -> bool:
    """True when the assistant just asked whether to send the question to the tutor."""
    lowered = (assistant_message or "").lower()
    return any(text in lowered for text in _CONFIRMATION_TEXTS)
