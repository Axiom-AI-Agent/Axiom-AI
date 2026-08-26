"""Multi-turn admissions onboarding — slot tracking and class disambiguation."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from services.language import normalize_language_pref, t

_CONFIRM_YES = re.compile(
    r"\b(yes|yeah|yep|agree|ok|okay|confirm|i agree|sure|looks good|proceed|oww|hari)\b"
    r"|ඔව්|ඔව්වා|හරි|ඔව් හරි"
    r"|ஆம்|ஆமாம்|சரி",
    re.IGNORECASE,
)
_CONFIRM_NO = re.compile(
    r"\b("
    r"no|nope|nah|cancel|wrong|change|incorrect|mistake|"
    r"start over|start again|not right"
    r")\b"
    r"|නෑ|එපා"
    r"|இல்லை|வேண்டாம்",
    re.IGNORECASE,
)
_EDIT_FIELD_PATTERN = re.compile(
    r"^\s*(?:change|edit|update|correct)\s+"
    r"(name|school|district|class|course)\s+"
    r"(?:to\s+)?(.+?)\s*$",
    re.IGNORECASE,
)
_RESTART_PATTERN = re.compile(
    r"\b("
    r"start over|restart|begin again|"
    r"redo|reset"
    r")\b",
    re.IGNORECASE,
)
_GRADE_AL = re.compile(r"\b(a/?l|advanced level|al)\b", re.IGNORECASE)
_GRADE_OL = re.compile(r"\b(o/?l|ordinary level|ol)\b", re.IGNORECASE)
_NAME_PREFIX = re.compile(
    r"^(?:my name is|i'?m|i am|call me|name is|this is)\s+(.+)$",
    re.IGNORECASE,
)
_SCHOOL_PREFIX = re.compile(
    r"^(?:i go to|i study at|my school is|school is|at)\s+(.+)$",
    re.IGNORECASE,
)
_DISTRICT_PREFIX = re.compile(
    r"^(?:i am from|i'?m from|from|my district is|district is)\s+(.+)$",
    re.IGNORECASE,
)
_CLASS_CATALOG = re.compile(
    r"\b("
    r"what.*(classes?|courses?|subjects?)|"
    r"which.*(classes?|courses?|subjects?)|"
    r"(list|show|tell me).*(classes?|courses?|offer|available)|"
    r"available.*(classes?|courses?)|"
    r"all.*(classes?|courses?)|"
    r"what do you offer|"
    r"what can i join"
    r")\b",
    re.IGNORECASE,
)
_ENROLLMENT_STATUS_QUERY = re.compile(
    r"\b("
    r"am i enrolled|"
    r"are you enrolled|"
    r"check my enrollment|"
    r"enrollment status|"
    r"am i registered|"
    r"do i have a class|"
    r"am i in a class|"
    r"is my enrollment"
    r")\b",
    re.IGNORECASE,
)
_ENROLLMENT_INTENT = re.compile(
    r"\b(enroll|register|sign up|admission|new student)\b|"
    r"\bjoin(?:\s+(?:a|an|the))?\s*(?:class|course)?\b|"
    r"want to join|like to join|study here|"
    r"join karanna|enroll wenna|class eka join|"
    r"ලියාපදිංචි|එකතු වෙ|"
    r"பதிவு|சேர|வகுப்பில் சேர",
    re.IGNORECASE,
)
_OFF_TOPIC_SLOT_PATTERNS = (
    r"\bexplain\b",
    r"\bnotes?\b",
    r"\bpast paper",
    r"\bhomework\b",
    r"\blesson\b",
    r"\bunderstand\b",
    r"what is",
    r"what are",
    r"how does",
    r"help me with",
    r"\btutor\b",
    r"\?",
)
_NON_NAME_WORDS = frozenset(
    {
        "explain",
        "what",
        "how",
        "why",
        "when",
        "where",
        "help",
        "yes",
        "no",
        "ok",
        "okay",
        "hello",
        "hi",
        "hey",
        "thanks",
        "velocity",
        "physics",
    }
)


def _format_lkr_amount(amount: Any) -> str:
    try:
        value = float(amount)
    except (TypeError, ValueError):
        return str(amount)
    if value == int(value):
        return f"{int(value):,}"
    return f"{value:,.2f}"


@dataclass
class OnboardingSlots:
    name: str | None = None
    school: str | None = None
    district: str | None = None
    class_id: str | None = None
    confirmed: bool = False


@dataclass
class OnboardingState:
    slots: OnboardingSlots = field(default_factory=OnboardingSlots)
    next_step: str | None = None
    complete: bool = False
    already_enrolled: bool = False
    pending_payment: bool = False
    awaiting_review: bool = False
    awaiting_confirmation: bool = False
    restarted: bool = False
    ambiguous_classes: list[dict[str, Any]] = field(default_factory=list)


class OnboardingFlow:
    """Determine onboarding progress and extract slots from user messages."""

    COLLECTION_STEPS = ("name", "school", "district", "class")

    def __init__(self, *, language: str = "en") -> None:
        self.language = normalize_language_pref(language)

    def _t(self, key: str, **kwargs: Any) -> str:
        return t(key, self.language, **kwargs)

    def load_from_student(
        self,
        student: dict[str, Any] | None,
        *,
        enrollments: list[dict[str, Any]] | None = None,
        pending_enrollment: dict[str, Any] | None = None,
        open_escalation: dict[str, Any] | None = None,
    ) -> OnboardingState:
        """Hydrate state for an existing database student (post-enrollment paths only)."""
        state = OnboardingState()
        if not student:
            return state

        slots = state.slots
        slots.name = student.get("name") or None
        slots.school = student.get("school") or None
        slots.district = student.get("district") or None
        slots.confirmed = bool(student.get("consent_at"))

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
            return state

        return state

    def start_collection(self) -> OnboardingState:
        return OnboardingState(next_step="name")

    def apply_message(
        self,
        state: OnboardingState,
        message: str,
        *,
        classes: list[dict[str, Any]] | None = None,
        phone: str | None = None,
    ) -> OnboardingState:
        text = message.strip()
        if not text:
            return state

        if state.awaiting_confirmation:
            if self._looks_like_reject(text):
                reset = self.start_collection()
                reset.restarted = True
                return reset
            if self._looks_like_confirm(text):
                state.slots.confirmed = True
                state.complete = True
                state.awaiting_confirmation = False
                state.next_step = None
                return state
            state = self._apply_collection_message(state, text, classes=classes)
            if self._collection_complete(state.slots):
                state.awaiting_confirmation = True
                state.next_step = "confirm"
            return state

        state = self._apply_collection_message(state, text, classes=classes)

        if state.ambiguous_classes:
            state.next_step = "class"
            return state

        if self._collection_complete(state.slots):
            state.awaiting_confirmation = True
            state.next_step = "confirm"
        else:
            state.next_step = self._first_missing_step(state.slots)

        return state

    def apply_confirmation_edit(
        self,
        state: OnboardingState,
        message: str,
        *,
        classes: list[dict[str, Any]] | None = None,
    ) -> tuple[OnboardingState, bool]:
        text = message.strip()
        if not text:
            return state, False

        if _RESTART_PATTERN.search(text):
            return OnboardingState(next_step="name"), True

        match = _EDIT_FIELD_PATTERN.match(text)
        if not match:
            return state, False

        field = match.group(1).lower()
        value = match.group(2).strip()
        state.slots.confirmed = False
        state.complete = False

        if field == "name":
            state.slots.name = self._title_name(value)
        elif field == "school":
            state.slots.school = value.title()
        elif field == "district":
            state.slots.district = value.title()
        elif field in {"class", "course"}:
            if not classes:
                return state, False
            numbered = self._match_class_by_number(value, classes)
            if numbered:
                state.slots.class_id = numbered["id"]
                state.ambiguous_classes = []
            else:
                class_match = self._match_class(value, classes)
                if isinstance(class_match, list):
                    state.ambiguous_classes = class_match
                    state.slots.class_id = None
                    state.awaiting_confirmation = False
                    state.next_step = "class"
                    return state, True
                if class_match:
                    state.slots.class_id = class_match["id"]
                    state.ambiguous_classes = []
                else:
                    return state, False

        state.awaiting_confirmation = True
        state.next_step = "confirm"
        return state, True

    def _apply_collection_message(
        self,
        state: OnboardingState,
        text: str,
        *,
        classes: list[dict[str, Any]] | None = None,
    ) -> OnboardingState:
        step = state.next_step or self._first_missing_step(state.slots)
        slots = state.slots

        if step == "name" and not slots.name:
            if self._looks_like_enrollment_intent(text) and not _NAME_PREFIX.match(text):
                pass
            else:
                extracted = self._extract_name(text)
                if extracted:
                    slots.name = extracted
        elif step == "school" and not slots.school:
            extracted = self._extract_labeled_value(text, _SCHOOL_PREFIX)
            if extracted:
                slots.school = extracted
        elif step == "district" and not slots.district:
            extracted = self._extract_labeled_value(text, _DISTRICT_PREFIX)
            if extracted:
                slots.district = extracted
        elif step == "class" and not slots.class_id and classes:
            if self._looks_like_confirm(text):
                pass
            else:
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

        return state

    def prompt_for_step(
        self,
        step: str | None,
        *,
        tenant_name: str = "our centre",
        phone: str | None = None,
        student_name: str | None = None,
        classes: list[dict[str, Any]] | None = None,
    ) -> str:
        first = student_name.split()[0] if student_name else None
        if step == "class" and classes:
            return self.class_catalog_message(
                classes=classes,
                tenant_name=tenant_name,
                student_name=student_name,
            )
        name_suffix = f", {first}" if first else ""
        prompts = {
            "name": self._t("onboarding_ask_name", tenant_name=tenant_name),
            "school": self._t("onboarding_ask_school", name_suffix=name_suffix),
            "district": self._t("onboarding_ask_district"),
        }
        return prompts.get(step or "name", prompts["name"])

    def class_catalog_message(
        self,
        *,
        classes: list[dict[str, Any]],
        tenant_name: str,
        student_name: str | None = None,
        intro: str | None = None,
    ) -> str:
        first = student_name.split()[0] if student_name else None
        if intro:
            header = intro
        elif first:
            header = self._t(
                "class_catalog_header_named",
                first=first,
                tenant_name=tenant_name,
            )
        else:
            header = self._t("class_catalog_header", tenant_name=tenant_name)

        lines = [header, ""]
        lines.extend(self._format_class_lines(classes))
        lines.append("")
        lines.append(self._t("class_catalog_pick"))
        return "\n".join(lines)

    def _format_class_lines(self, classes: list[dict[str, Any]]) -> list[str]:
        if not classes:
            return [self._t("class_catalog_empty")]
        lines: list[str] = []
        for idx, cls in enumerate(classes, start=1):
            label = cls.get("name") or f"{cls.get('grade', '')} {cls.get('subject', '')}".strip()
            fee = cls.get("fee_amount")
            fee_line = f" — LKR {_format_lkr_amount(fee)}/month" if fee is not None else ""
            lines.append(f"{idx}. {label}{fee_line}")
        return lines

    def review_confirmation_message(
        self,
        *,
        slots: OnboardingSlots,
        class_row: dict[str, Any] | None,
        tenant_name: str,
        phone: str | None = None,
    ) -> str:
        class_label = (
            (class_row or {}).get("name")
            or f"{(class_row or {}).get('grade', '')} {(class_row or {}).get('subject', '')}".strip()
            or "your selected class"
        )
        fee = (class_row or {}).get("fee_amount")
        fee_line = self._t("fee_line", fee=fee) if fee is not None else ""
        contact = phone or "your WhatsApp number"
        return self._t(
            "review_confirmation",
            tenant_name=tenant_name,
            name=slots.name,
            contact=contact,
            school=slots.school,
            district=slots.district,
            class_label=class_label,
            fee_line=fee_line,
        )

    def disambiguation_prompt(self, classes: list[dict[str, Any]]) -> str:
        lines = [
            self._t("disambiguation_header"),
            "",
            *self._format_class_lines(classes),
            "",
            self._t("disambiguation_pick"),
        ]
        return "\n".join(lines)

    def enrollment_welcome_message(
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
        return self._t(
            "enrollment_welcome",
            tenant_name=tenant_name,
            class_label=class_label,
        )

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
        fee_line = self._t("fee_line", fee=fee) if fee is not None else ""
        return self._t(
            "payment_pending",
            name=slots.name,
            class_label=class_label,
            tenant_name=tenant_name,
            fee_line=fee_line,
        )

    def receipt_received_message(self, *, tenant_name: str) -> str:
        return self._t("receipt_received", tenant_name=tenant_name)

    def awaiting_review_message(self, *, tenant_name: str) -> str:
        return self._t("awaiting_review", tenant_name=tenant_name)

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
        return self._t(
            "enrollment_success",
            name=name,
            class_label=class_label,
            tenant_name=tenant_name,
        )

    def payment_rejected_message(
        self,
        *,
        student: dict[str, Any],
        tenant_name: str,
    ) -> str:
        name = student.get("name") or "there"
        return self._t("payment_rejected", name=name, tenant_name=tenant_name)

    def already_registered_message(
        self,
        *,
        student: dict[str, Any],
        class_row: dict[str, Any] | None,
        tenant_name: str,
    ) -> str:
        name = student.get("name") or "there"
        class_label = (class_row or {}).get("name") or "your class"
        return self._t(
            "already_registered",
            name=name,
            tenant_name=tenant_name,
            class_label=class_label,
        )

    def not_registered_status_message(self, *, tenant_name: str) -> str:
        return self._t("not_registered", tenant_name=tenant_name)

    def _first_missing_step(self, slots: OnboardingSlots) -> str | None:
        for step in self.COLLECTION_STEPS:
            if step == "name" and not slots.name:
                return "name"
            if step == "school" and not slots.school:
                return "school"
            if step == "district" and not slots.district:
                return "district"
            if step == "class" and not slots.class_id:
                return "class"
        return None

    def _collection_complete(self, slots: OnboardingSlots) -> bool:
        return bool(slots.name and slots.school and slots.district and slots.class_id)

    def _looks_like_confirm(self, text: str) -> bool:
        if self._looks_like_reject(text):
            return False
        return bool(_CONFIRM_YES.search(text.strip()))

    def _looks_like_reject(self, text: str) -> bool:
        return bool(_CONFIRM_NO.search(text.strip()))

    def _looks_like_class_catalog_request(self, text: str) -> bool:
        return bool(_CLASS_CATALOG.search(text.strip()))

    def _looks_like_enrollment_status_query(self, text: str) -> bool:
        return bool(_ENROLLMENT_STATUS_QUERY.search(text.strip()))

    def _looks_like_enrollment_intent(self, text: str) -> bool:
        if self._looks_like_enrollment_status_query(text):
            return False
        return bool(_ENROLLMENT_INTENT.search(text.strip()))

    def _looks_like_off_topic_during_onboarding(self, text: str) -> bool:
        stripped = text.strip()
        if not stripped:
            return False
        if self._looks_like_enrollment_status_query(stripped):
            return True
        from services.admissions.institute_info import looks_like_institute_info

        if looks_like_institute_info(stripped):
            return False
        lowered = stripped.lower()
        return any(re.search(p, lowered) for p in _OFF_TOPIC_SLOT_PATTERNS)

    def _extract_name(self, text: str) -> str | None:
        stripped = text.strip()
        if not stripped or self._looks_like_confirm(stripped):
            return None
        if self._looks_like_off_topic_during_onboarding(stripped):
            return None
        match = _NAME_PREFIX.match(stripped)
        if match:
            return self._title_name(match.group(1))
        if self._looks_like_enrollment_intent(stripped):
            return None
        words = stripped.split()
        if "?" in stripped or not (1 <= len(words) <= 5):
            return None
        if len(words) == 1 and words[0].lower() in _NON_NAME_WORDS:
            return None
        return self._title_name(stripped)

    def _extract_labeled_value(self, text: str, pattern: re.Pattern[str]) -> str | None:
        stripped = text.strip()
        if not stripped or self._looks_like_off_topic_during_onboarding(stripped):
            return None
        match = pattern.match(stripped)
        if match:
            return match.group(1).strip().title()
        words = stripped.split()
        if "?" not in stripped and 1 <= len(words) <= 6:
            return stripped.title()
        return None

    @staticmethod
    def _title_name(value: str) -> str:
        return " ".join(part.capitalize() for part in value.split())

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

        name_matches = [
            c
            for c in classes
            if str(c.get("name") or "").lower() in lowered
            or lowered in str(c.get("name") or "").lower()
        ]

        if not grade_hint and not subject_hints and not name_matches:
            return None

        candidates = name_matches or classes
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
