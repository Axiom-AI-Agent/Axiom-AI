"""Escalation reason codes for dashboard inbox filtering."""

from __future__ import annotations


PAYMENT_RECEIPT = "payment_receipt"

TALK_TO_TUTOR = "talk_to_tutor"

LOW_RAG_CONFIDENCE = (
    "low_rag_confidence"
)

# Legacy Phase 3 alias.
ENROLLMENT_PAYMENT_REASON = (
    "enrollment_payment_review"
)


PAYMENT_REASON_CODES = frozenset(
    {
        PAYMENT_RECEIPT,
        ENROLLMENT_PAYMENT_REASON,
    }
)


def is_payment_reason(
    reason_code: str | None,
) -> bool:
    return (
        reason_code
        in PAYMENT_REASON_CODES
    )