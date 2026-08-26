from __future__ import annotations

from typing import Literal

from agents.tools.memory_tool import (
    MemoryTool,
)
from services.language import t

ConfirmationDecision = Literal[
    "yes",
    "no",
    "none",
]


CONFIRMATION_TEXT = (
    "Would you like me to send this "
    "question to your tutor?"
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

    if (
        CONFIRMATION_TEXT.lower() not in assistant_message.lower()
        and t("escalation_confirm", "si").lower() not in assistant_message.lower()
        and t("escalation_confirm", "ta").lower() not in assistant_message.lower()
    ):
        return None

    return user_message
