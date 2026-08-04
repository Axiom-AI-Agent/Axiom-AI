"""Routing enums for the decision graph and orchestrator."""

from enum import StrEnum


class GuardrailVerdict(StrEnum):
    IN_SCOPE = "in_scope"
    OUT_OF_SCOPE = "out_of_scope"


class RouterIntent(StrEnum):
    ADMISSIONS = "admissions"
    RESOURCE = "resource"
    PAYMENT_CHECK = "payment_check"
    ESCALATION = "escalation"
    DIRECT = "direct"


class DecisionVerdict(StrEnum):
    PROCEED = "proceed"
    OUT_OF_SCOPE = "out_of_scope"


SPECIALIST_INTENTS = frozenset(
    {
        RouterIntent.ADMISSIONS,
        RouterIntent.RESOURCE,
        RouterIntent.PAYMENT_CHECK,
        RouterIntent.ESCALATION,
    }
)
