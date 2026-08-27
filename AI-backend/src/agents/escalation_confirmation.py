from __future__ import annotations

from typing import Literal

from agents.tools.memory_tool import (
    MemoryTool,
)
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
    """
    Detect whether the immediately preceding
    completed exchange asked the student to
    confirm a low-confidence tutor handoff.
    """

    try:
        pairs = (
            memory_tool.recent_pairs(
                tenant_id=tenant_id,
                user_id=user_id,
                session_id=session_id,
                k=3,
            )
        )
    except Exception:
        return None

    if not pairs:
        return None

    last = pairs[-1]
    if not isinstance(last, (tuple, list)) or len(last) < 2:
        return None
    user_message, assistant_message = last[0], last[1]
    if not assistant_message:
        return None

    lowered = assistant_message.lower()
    if not any(text in lowered for text in _CONFIRMATION_TEXTS):
        return None

    return user_message
