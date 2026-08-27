"""Semantic NLU layer — intent classification, entity extraction, validation."""

from services.nlu.classifier import aclassify, classify, score_intents, vocabulary
from services.nlu.entities import (
    ClassReference,
    ValidationResult,
    extract_grade,
    extract_subject,
    resolve_class_reference,
    validate_registration_value,
)
from services.nlu.intents import (
    ADMISSIONS_INTENTS,
    INTENT_TO_ACTION,
    INTENT_TO_ROUTE,
    TASK_INTENTS,
    IntentResult,
    StudentIntent,
)

__all__ = [
    "ADMISSIONS_INTENTS",
    "INTENT_TO_ACTION",
    "INTENT_TO_ROUTE",
    "TASK_INTENTS",
    "ClassReference",
    "IntentResult",
    "StudentIntent",
    "ValidationResult",
    "aclassify",
    "classify",
    "extract_grade",
    "extract_subject",
    "resolve_class_reference",
    "score_intents",
    "validate_registration_value",
    "vocabulary",
]
