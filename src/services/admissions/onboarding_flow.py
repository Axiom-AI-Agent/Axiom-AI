"""Multi-turn admissions onboarding — slot tracking and class disambiguation."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

_CONSENT_YES = re.compile(
    r"\b(yes|yeah|yep|agree|ok|okay|confirm|i agree|sure)\b",
    re.IGNORECASE,
)
_GRADE_AL = re.compile(r"\b(a/?l|advanced level|al)\b", re.IGNORECASE)
_GRADE_OL = re.compile(r"\b(o/?l|ordinary level|ol)\b", re.IGNORECASE)


@dataclass
class OnboardingSlots:
    name: str | None = None
    school: str | None = None
    district: str | None = None
    class_id: str | None = None
    consent: bool = False


@dataclass
class OnboardingState:
    slots: OnboardingSlots = field(default_factory=OnboardingSlots)
    next_step: str | None = None
    complete: bool = False
    already_enrolled: bool = False
    pending_payment: bool = False
    awaiting_review: bool = False
    ambiguous_classes: list[dict[str, Any]] = field(default_factory=list)


class OnboardingFlow:
    """Determine onboarding progress and extract slots from user messages."""

    STEPS = ("name", "school", "district", "class", "consent")

    def load_from_student(
        self,
        student: dict[str, Any] | None,
        *,
        enrollments: list[dict[str, Any]] | None = None,
        pending_enrollment: dict[str, Any] | None = None,
        open_escalation: dict[str, Any] | None = None,
    ) -> OnboardingState:
        state = OnboardingState()
        if not student:
            state.next_step = "name"
            return state

        slots = state.slots
        slots.name = student.get("name") or None
        slots.school = student.get("school") or None
        slots.district = student.get("district") or None
        slots.consent = bool(student.get("consent_at"))

        active_enrollments = [
            e for e in (enrollments or []) if e.get("status") == "active"
        ]
        if active_enrollments:
            state.already_enrolled = True
            slots.class_id = active_enrollments[0].get("class_id")
            state.complete = True
            return state

        if pending_enrollment:
            slots.class_id = pending_enrollment.get("class_id")
            if open_escalation:
                state.awaiting_review = True
                state.pending_payment = False
            else:
                state.pending_payment = True
                state.next_step = "payment_receipt"
            return state

        state.next_step = self._first_missing_step(slots)
        return state

    def apply_message(
        self,
        state: OnboardingState,
        message: str,
        *,
        classes: list[dict[str, Any]] | None = None,
    ) -> OnboardingState:
        text = message.strip()
        if not text:
            return state

        step = state.next_step
        slots = state.slots

        if step == "name" and not slots.name:
            if self._looks_like_enrollment_intent(text):
                pass
            elif len(text.split()) >= 1 and not self._looks_like_consent(text):
                slots.name = text.title()
        elif step == "school" and not slots.school:
            slots.school = text.title()
        elif step == "district" and not slots.district:
            slots.district = text.title()
        elif step == "class" and not slots.class_id and classes:
            numbered = self._match_class_by_number(text, classes)
            if numbered:
                slots.class_id = numbered["id"]
                state.ambiguous_classes = []
            else:
                match = self._match_class(text, classes)
                if isinstance(match, list):
                    state.ambiguous_classes = match
                elif match:
                    slots.class_id = match["id"]
                    state.ambiguous_classes = []
        elif step == "consent" and not slots.consent:
            slots.consent = bool(_CONSENT_YES.search(text))

        if state.ambiguous_classes:
            state.next_step = "class"
            return state

        state.next_step = self._first_missing_step(slots)
        state.complete = self._profile_complete(slots) and bool(slots.class_id)
        return state

    def prompt_for_step(self, step: str | None, *, tenant_name: str = "our centre") -> str:
        prompts = {
            "name": f"Welcome to {tenant_name}! To get started, what is your full name?",
            "school": "Great! Which school do you attend?",
            "district": "Thanks. Which district are you from?",
            "class": "Which class would you like to join? (e.g. A/L Physics or O/L Physics)",
            "consent": (
                "Before we confirm your enrollment, do you agree to our data policy? "
                "Reply YES to confirm."
            ),
        }
        return prompts.get(step or "name", prompts["name"])

    def disambiguation_prompt(self, classes: list[dict[str, Any]]) -> str:
        lines = ["I found a few classes — which one would you like?"]
        for idx, cls in enumerate(classes, start=1):
            label = cls.get("name") or f"{cls.get('grade', '')} {cls.get('subject', '')}".strip()
            fee = cls.get("fee_amount")
            fee_line = f" (LKR {fee}/month)" if fee is not None else ""
            lines.append(f"{idx}. {label}{fee_line}")
        return "\n".join(lines)

    def payment_pending_message(
        self,
        *,
        slots: OnboardingSlots,
        class_row: dict[str, Any] | None,
        tenant_name: str,
    ) -> str:
        class_label = (
            (class_row or {}).get("name")
            or f"{(class_row or {}).get('grade', '')} {(class_row or {}).get('subject', '')}".strip()
            or "your selected class"
        )
        fee = (class_row or {}).get("fee_amount")
        fee_line = f"\nClass fee: LKR {fee}/month." if fee is not None else ""
        return (
            f"Thanks, {slots.name}! Your application for **{class_label}** at "
            f"{tenant_name} is almost complete.{fee_line}\n\n"
            f"Please send a photo of your **payment receipt / bank slip** on WhatsApp "
            f"to confirm your enrollment."
        )

    def receipt_received_message(self, *, tenant_name: str) -> str:
        return (
            f"Thanks! We received your payment receipt for {tenant_name}. "
            f"Our team is reviewing it now — you'll get a confirmation message once "
            f"your enrollment is approved."
        )

    def awaiting_review_message(self, *, tenant_name: str) -> str:
        return (
            f"Your payment receipt is already with our team at {tenant_name}. "
            f"We'll message you as soon as your enrollment is confirmed."
        )

    def enrollment_success_message(
        self,
        *,
        student: dict[str, Any],
        class_row: dict[str, Any] | None,
        tenant_name: str,
    ) -> str:
        name = student.get("name") or "there"
        class_label = (
            (class_row or {}).get("name")
            or f"{(class_row or {}).get('grade', '')} {(class_row or {}).get('subject', '')}".strip()
            or "your class"
        )
        return (
            f"Great news, {name}! 🎉\n"
            f"You are **successfully enrolled** in {class_label} at {tenant_name}.\n"
            f"Welcome — class details and fee info will follow shortly."
        )

    def confirmation_message(
        self,
        *,
        slots: OnboardingSlots,
        class_row: dict[str, Any] | None,
        tenant_name: str,
    ) -> str:
        class_label = (
            (class_row or {}).get("name")
            or f"{(class_row or {}).get('grade', '')} {(class_row or {}).get('subject', '')}".strip()
            or "your selected class"
        )
        return (
            f"You're all set, {slots.name}! 🎉\n"
            f"Enrolled in **{class_label}** at {tenant_name}.\n"
            f"School: {slots.school} | District: {slots.district}\n"
            f"We'll send class details and fee info shortly."
        )

    def already_registered_message(
        self,
        *,
        student: dict[str, Any],
        class_row: dict[str, Any] | None,
        tenant_name: str,
    ) -> str:
        name = student.get("name") or "there"
        class_label = (class_row or {}).get("name") or "your class"
        return (
            f"Hi {name}! You're already registered at {tenant_name} "
            f"for {class_label}. How can I help you today?"
        )

    def _first_missing_step(self, slots: OnboardingSlots) -> str | None:
        for step in self.STEPS:
            if step == "name" and not slots.name:
                return "name"
            if step == "school" and not slots.school:
                return "school"
            if step == "district" and not slots.district:
                return "district"
            if step == "class" and not slots.class_id:
                return "class"
            if step == "consent" and not slots.consent:
                return "consent"
        return None

    def _profile_complete(self, slots: OnboardingSlots) -> bool:
        return bool(slots.name and slots.school and slots.district and slots.consent)

    def _looks_like_consent(self, text: str) -> bool:
        return bool(_CONSENT_YES.fullmatch(text.strip()))

    def _looks_like_enrollment_intent(self, text: str) -> bool:
        lowered = text.lower()
        keywords = ("join", "enroll", "register", "sign up", "admission", "class")
        return any(k in lowered for k in keywords)

    def _match_class_by_number(
        self,
        text: str,
        classes: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        stripped = text.strip()
        if stripped.isdigit():
            idx = int(stripped) - 1
            if 0 <= idx < len(classes):
                return classes[idx]
        return None

    def _match_class(
        self,
        text: str,
        classes: list[dict[str, Any]],
    ) -> dict[str, Any] | list[dict[str, Any]] | None:
        if not classes:
            return None

        lowered = text.lower()
        grade_hint = None
        if _GRADE_AL.search(lowered):
            grade_hint = "A/L"
        elif _GRADE_OL.search(lowered):
            grade_hint = "O/L"

        subject_hints: list[str] = []
        for cls in classes:
            subject = str(cls.get("subject") or "").lower()
            if subject and subject in lowered:
                subject_hints.append(subject)

        candidates = classes
        if grade_hint:
            candidates = [
                c
                for c in candidates
                if str(c.get("grade") or "").upper() == grade_hint.upper()
            ]
        if subject_hints:
            candidates = [
                c
                for c in candidates
                if str(c.get("subject") or "").lower() in subject_hints
            ]

        if len(candidates) == 1:
            return candidates[0]
        if len(candidates) > 1:
            return candidates

        if len(classes) == 1:
            return classes[0]
        return None
