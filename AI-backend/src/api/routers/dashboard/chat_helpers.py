"""Shared helpers for dashboard chat endpoints."""

from __future__ import annotations

from typing import Any, Literal, Optional

from api.schemas import ChatConversationSummary, ChatTurnRecord
from domain.enums import MessageRole
from services.identity.resolver import build_session_id, normalize_phone

Sender = Literal["student", "bot", "staff"]

_SENDER_BY_ROLE: dict[MessageRole, Sender] = {
    MessageRole.USER: "student",
    MessageRole.ASSISTANT: "bot",
    MessageRole.SYSTEM: "staff",
}


def role_to_sender(role: str | MessageRole) -> Sender:
    if isinstance(role, str):
        try:
            role = MessageRole(role)
        except ValueError:
            return "bot"
    return _SENDER_BY_ROLE.get(role, "bot")


def turn_to_record(row: dict[str, Any]) -> ChatTurnRecord:
    role = MessageRole(str(row["role"]))
    return ChatTurnRecord(
        id=str(row["id"]),
        role=role,
        sender=role_to_sender(role),
        content=str(row["content"]),
        created_at=str(row["created_at"]),
    )


def phone_from_session_id(session_id: str, tenant_id: str) -> str:
    prefix = f"{tenant_id}:"
    if session_id.startswith(prefix):
        return session_id[len(prefix) :]
    return session_id.split(":")[-1] if ":" in session_id else session_id


def build_conversation_summary(
    *,
    tenant_id: str,
    latest_turn: dict[str, Any],
    student: dict[str, Any],
    open_escalation: Optional[dict[str, Any]] = None,
) -> ChatConversationSummary:
    role = str(latest_turn["role"])
    phone = str(student.get("phone") or phone_from_session_id(str(latest_turn["session_id"]), tenant_id))
    content = str(latest_turn["content"])
    preview = content if len(content) <= 120 else f"{content[:117]}..."
    return ChatConversationSummary(
        session_id=str(latest_turn["session_id"]),
        student_id=str(latest_turn["user_id"]),
        student_name=student.get("name"),
        phone=phone,
        last_message=preview,
        last_message_at=str(latest_turn["created_at"]),
        last_sender=role_to_sender(role),
        has_open_escalation=open_escalation is not None,
        open_escalation_reason=(
            str(open_escalation["reason_code"]) if open_escalation else None
        ),
    )


def session_id_for_phone(tenant_id: str, phone: str) -> str:
    return build_session_id(tenant_id, normalize_phone(phone))
