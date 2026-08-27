"""Canonical student intents and their mapping onto agent routes."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class StudentIntent(str, Enum):
    """What the student is actually asking for on this turn."""

    CLASS_LIST = "class_list"
    CLASS_DETAIL = "class_detail"
    ENROLL = "enroll"
    MY_ENROLLMENTS = "my_enrollments"
    CANCEL_ENROLLMENT = "cancel_enrollment"
    TUTOR_INFO = "tutor_info"
    CENTRE_INFO = "centre_info"
    SCHEDULE = "schedule"
    RESOURCE_FILES = "resource_files"
    LESSON_HELP = "lesson_help"
    PAYMENT_SUBMIT = "payment_submit"
    PAYMENT_STATUS = "payment_status"
    ESCALATION = "escalation"
    AFFIRM = "affirm"
    DENY = "deny"
    GREETING = "greeting"
    PROFILE_LOOKUP = "profile_lookup"
    LINK_SHARED = "link_shared"
    OFF_TOPIC = "off_topic"
    UNKNOWN = "unknown"


#: Intents that name a concrete task rather than a conversational move. Only
#: these are strong enough to interrupt an in-progress flow.
TASK_INTENTS = frozenset(
    {
        StudentIntent.CLASS_LIST,
        StudentIntent.CLASS_DETAIL,
        StudentIntent.MY_ENROLLMENTS,
        StudentIntent.CANCEL_ENROLLMENT,
        StudentIntent.TUTOR_INFO,
        StudentIntent.CENTRE_INFO,
        StudentIntent.SCHEDULE,
        StudentIntent.RESOURCE_FILES,
        StudentIntent.LESSON_HELP,
        StudentIntent.PAYMENT_STATUS,
        StudentIntent.ESCALATION,
        StudentIntent.PROFILE_LOOKUP,
    }
)

#: Intents the admissions agent owns end to end.
ADMISSIONS_INTENTS = frozenset(
    {
        StudentIntent.CLASS_LIST,
        StudentIntent.CLASS_DETAIL,
        StudentIntent.ENROLL,
        StudentIntent.MY_ENROLLMENTS,
        StudentIntent.TUTOR_INFO,
        StudentIntent.CENTRE_INFO,
    }
)

INTENT_TO_ROUTE: dict[StudentIntent, str] = {
    StudentIntent.CLASS_LIST: "admissions",
    StudentIntent.CLASS_DETAIL: "admissions",
    StudentIntent.ENROLL: "admissions",
    StudentIntent.MY_ENROLLMENTS: "admissions",
    StudentIntent.CENTRE_INFO: "admissions",
    StudentIntent.TUTOR_INFO: "admissions",
    StudentIntent.CANCEL_ENROLLMENT: "escalation",
    StudentIntent.SCHEDULE: "resource",
    StudentIntent.RESOURCE_FILES: "resource",
    StudentIntent.LESSON_HELP: "resource",
    StudentIntent.PAYMENT_SUBMIT: "payment_check",
    StudentIntent.PAYMENT_STATUS: "payment_check",
    StudentIntent.ESCALATION: "escalation",
    StudentIntent.GREETING: "direct",
    StudentIntent.AFFIRM: "direct",
    StudentIntent.DENY: "direct",
    StudentIntent.PROFILE_LOOKUP: "direct",
    StudentIntent.LINK_SHARED: "direct",
    StudentIntent.OFF_TOPIC: "direct",
    StudentIntent.UNKNOWN: "direct",
}

INTENT_TO_ACTION: dict[StudentIntent, str] = {
    StudentIntent.CLASS_LIST: "search",
    StudentIntent.CLASS_DETAIL: "search",
    StudentIntent.ENROLL: "general",
    StudentIntent.MY_ENROLLMENTS: "check",
    StudentIntent.CENTRE_INFO: "search",
    StudentIntent.TUTOR_INFO: "search",
    StudentIntent.CANCEL_ENROLLMENT: "escalate",
    StudentIntent.SCHEDULE: "search",
    StudentIntent.RESOURCE_FILES: "search",
    StudentIntent.LESSON_HELP: "search",
    StudentIntent.PAYMENT_SUBMIT: "general",
    StudentIntent.PAYMENT_STATUS: "check",
    StudentIntent.ESCALATION: "escalate",
}


@dataclass
class IntentResult:
    """Outcome of classifying one incoming message."""

    intent: StudentIntent = StudentIntent.UNKNOWN
    confidence: float = 0.0
    source: str = "none"
    entities: dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""

    @property
    def route(self) -> str:
        return INTENT_TO_ROUTE.get(self.intent, "direct")

    @property
    def action(self) -> str:
        return INTENT_TO_ACTION.get(self.intent, "general")

    @property
    def is_task(self) -> bool:
        return self.intent in TASK_INTENTS
