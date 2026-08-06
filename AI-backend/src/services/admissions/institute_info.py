"""Institute info inquiry detection and reply formatting (classes, fees, staff, centre)."""

from __future__ import annotations

import re
from typing import Any, Literal

InfoInquiryKind = Literal["classes", "tenant", "staff", "class_detail"]

_TUTORING_EXCLUSION = re.compile(
    r"\b(explain|understand|help me with|past paper|model paper|homework|lesson notes?|from the notes)\b",
    re.IGNORECASE,
)

_INFO_INQUIRY_PATTERNS: tuple[tuple[InfoInquiryKind, re.Pattern[str]], ...] = (
    (
        "classes",
        re.compile(
            r"\b("
            r"what.*(classes?|courses?|subjects?).*(available|offer|have|current|running)|"
            r"which.*(classes?|courses?|subjects?).*(available|offer|have|do you)|"
            r"(list|show|tell me).*(classes?|courses?|subjects?|offer|available)|"
            r"available.*(classes?|courses?|subjects?)|"
            r"what do you offer|"
            r"what can i join|"
            r"classes?.*available"
            r")\b",
            re.IGNORECASE,
        ),
    ),
    (
        "class_detail",
        re.compile(
            r"\b("
            r"class.*(fee|fees|cost|price|detail|details|schedule|time)|"
            r"how much.*(class|fee|fees|cost|physics|chemistry|a/?l|o/?l)|"
            r"fee.*(class|physics|chemistry|a/?l|o/?l)|"
            r"tell me about.*(class|physics|chemistry|a/?l|o/?l)"
            r")\b",
            re.IGNORECASE,
        ),
    ),
    (
        "staff",
        re.compile(
            r"\b("
            r"who.*(tutor|teacher|teach|staff|sir|madam|principal)|"
            r"who is (?:the )?(tutor|teacher|staff)|"
            r"tell me about (?:the )?(tutor|teacher|staff|team)|"
            r"(teaching team|office team)|"
            r"who runs|who owns"
            r")\b",
            re.IGNORECASE,
        ),
    ),
    (
        "tenant",
        re.compile(
            r"\b("
            r"about.*(academy|institute|centre|center|tuition|school)|"
            r"tell me about.*(you|this place|demo physics)|"
            r"contact.*(number|office|whatsapp|phone)|"
            r"where.*(located|location|based)|"
            r"what is.*(academy|institute|centre|center)"
            r")\b",
            re.IGNORECASE,
        ),
    ),
)

_GRADE_AL = re.compile(r"\b(a/?l|advanced level)\b", re.IGNORECASE)
_GRADE_OL = re.compile(r"\b(o/?l|ordinary level)\b", re.IGNORECASE)


def looks_like_institute_info(message: str) -> bool:
    text = message.strip()
    if not text or _TUTORING_EXCLUSION.search(text):
        return False
    return classify_info_inquiry(text) is not None


def classify_info_inquiry(message: str) -> InfoInquiryKind | None:
    text = message.strip()
    if not text:
        return None
    for kind, pattern in _INFO_INQUIRY_PATTERNS:
        if pattern.search(text):
            return kind
    return None


def extract_class_filters(message: str) -> tuple[str | None, str | None]:
    """Return (subject_hint, grade_hint) parsed from a user message."""
    lowered = message.lower()
    grade = None
    if _GRADE_AL.search(lowered):
        grade = "A/L"
    elif _GRADE_OL.search(lowered):
        grade = "O/L"

    subject = None
    for candidate in ("physics", "chemistry", "biology", "maths", "mathematics"):
        if candidate in lowered:
            subject = candidate.title() if candidate != "maths" else "Mathematics"
            break
    return subject, grade


def format_tenant_info(
    *,
    tenant: dict[str, Any],
    classes: list[dict[str, Any]],
    staff: list[dict[str, Any]],
) -> str:
    name = tenant.get("name") or "our tuition centre"
    whatsapp = tenant.get("whatsapp_number") or ""
    contact_line = f"\nWhatsApp: {whatsapp}" if whatsapp else ""

    class_count = len(classes)
    class_line = (
        f"We currently offer **{class_count}** class{'es' if class_count != 1 else ''}."
        if class_count
        else "Class listings are being updated — please ask again shortly."
    )

    staff_names = [s.get("name") for s in staff if s.get("name")]
    team_line = ""
    if staff_names:
        team_line = f"\nOur team includes: {', '.join(staff_names)}."

    return (
        f"**{name}** is a tuition centre on WhatsApp.{contact_line}\n\n"
        f"{class_line}{team_line}\n\n"
        f"Ask me **what classes are available** or **class fees** for more detail."
    )


def format_staff_list(*, staff: list[dict[str, Any]], tenant_name: str) -> str:
    if not staff:
        return (
            f"I don't have staff details on file for {tenant_name} right now. "
            f"Please contact the office on WhatsApp for help."
        )

    lines = [f"Here's the team at **{tenant_name}**:", ""]
    for member in staff:
        name = member.get("name") or "Staff member"
        role = str(member.get("role") or "staff").replace("_", " ").title()
        lines.append(f"• **{name}** — {role}")
    lines.append("")
    lines.append("For urgent academic help, say **speak to a tutor**.")
    return "\n".join(lines)


def format_class_details(
    *,
    classes: list[dict[str, Any]],
    tenant_name: str,
    subject: str | None = None,
    grade: str | None = None,
) -> str:
    if not classes:
        hint = ""
        if subject or grade:
            parts = [p for p in (grade, subject) if p]
            hint = f" for {' '.join(parts)}"
        return (
            f"I couldn't find any classes{hint} at **{tenant_name}** right now. "
            f"Try asking **what classes are available**."
        )

    if len(classes) == 1:
        cls = classes[0]
        return _format_single_class(cls, tenant_name=tenant_name, header="Here are the details:")

    header = f"Here are the matching classes at **{tenant_name}**:"
    lines = [header, ""]
    for idx, cls in enumerate(classes, start=1):
        label = cls.get("name") or f"{cls.get('grade', '')} {cls.get('subject', '')}".strip()
        fee = cls.get("fee_amount")
        fee_line = f" — LKR {fee}/month" if fee is not None else ""
        cycle = cls.get("fee_cycle") or "monthly"
        lines.append(f"{idx}. **{label}**{fee_line} ({cycle})")
    lines.append("")
    lines.append("Reply with a **class name** if you'd like to enroll.")
    return "\n".join(lines)


def _format_single_class(
    cls: dict[str, Any],
    *,
    tenant_name: str,
    header: str,
) -> str:
    label = cls.get("name") or f"{cls.get('grade', '')} {cls.get('subject', '')}".strip()
    subject = cls.get("subject") or "—"
    grade = cls.get("grade") or "—"
    fee = cls.get("fee_amount")
    cycle = cls.get("fee_cycle") or "monthly"
    fee_line = f"LKR {fee}/{cycle}" if fee is not None else "Contact office for fees"

    return (
        f"{header}\n\n"
        f"**{label}** at {tenant_name}\n"
        f"• Subject: {subject}\n"
        f"• Grade: {grade}\n"
        f"• Fee: {fee_line}\n\n"
        f"Say **I'd like to enroll** when you're ready to join."
    )
