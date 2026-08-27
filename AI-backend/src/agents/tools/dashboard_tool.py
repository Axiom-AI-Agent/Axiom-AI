"""Read-only dashboard analytics for the staff Dashboard Agent.

tenant_id is bound at construction from StaffContext — never from message text
or LLM tool arguments.
"""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from domain.escalation_reasons import PAYMENT_RECEIPT, TALK_TO_TUTOR
from infrastructure.db.supabase_client import get_supabase_client

_PAGE = 1000
_MAX_ROWS = 8000
_PHONE_RE = re.compile(r"\d{9,}")


class DashboardQueryTool:
    def __init__(self, tenant_id: str, *, client: Any | None = None) -> None:
        scoped = (tenant_id or "").strip()
        if not scoped:
            raise ValueError("tenant_id is required for dashboard queries")
        self._tenant_id = scoped
        self._client = client

    @property
    def tenant_id(self) -> str:
        return self._tenant_id

    def get_overview(self) -> dict[str, Any]:
        tenant_id = self._tenant_id
        open_escalations = self._count("escalations", filters={"status": "open"})
        payment = self._count_in(
            "escalations",
            status="open",
            column="reason_code",
            values=[PAYMENT_RECEIPT, "enrollment_payment_review"],
        )
        tutor = self._count("escalations", filters={"status": "open", "reason_code": TALK_TO_TUTOR})
        pending = self._count("enrollments", filters={"status": "pending"})
        students = self._count("students")
        classes = self._count("subject_classes")
        return {
            "tenant_id": tenant_id,
            "open_escalations": open_escalations,
            "open_payment_receipts": payment,
            "open_talk_to_tutor": tutor,
            "pending_enrollments": pending,
            "students": students,
            "classes": classes,
        }

    def get_analytics(self) -> dict[str, Any]:
        return _build_analytics(
            tenant_id=self._tenant_id,
            turns=self._fetch_all("st_turns", "session_id, user_id, role, created_at"),
            escalations=self._fetch_all(
                "escalations",
                "id, student_id, reason_code, status, created_at",
            ),
            students=self._fetch_all("students", "id, name"),
        )

    def get_class_analytics(self) -> dict[str, Any]:
        return _build_class_analytics(
            tenant_id=self._tenant_id,
            classes=self._fetch_all("subject_classes", "id, name, subject, grade"),
            enrollments=self._fetch_all("enrollments", "id, class_id, student_id, status"),
            turns=self._fetch_all("st_turns", "session_id, user_id, role, created_at"),
            escalations=self._fetch_all(
                "escalations",
                "id, student_id, reason_code, status, created_at",
            ),
        )

    def get_escalation_summary(self, *, limit: int = 15) -> dict[str, Any]:
        cap = max(1, min(int(limit), 25))
        rows = self._fetch_all(
            "escalations",
            "id, student_id, reason_code, status, student_message, created_at",
        )
        open_rows = [row for row in rows if row.get("status") == "open"]
        open_rows.sort(key=lambda row: str(row.get("created_at") or ""), reverse=True)
        student_ids = [str(row["student_id"]) for row in open_rows[:cap] if row.get("student_id")]
        names = self._student_names(student_ids)
        recent = []
        for row in open_rows[:cap]:
            student_id = str(row.get("student_id") or "")
            recent.append(
                {
                    "id": row.get("id"),
                    "reason_code": row.get("reason_code"),
                    "status": row.get("status"),
                    "student_name": names.get(student_id),
                    "created_at": row.get("created_at"),
                }
            )
        by_reason: dict[str, int] = defaultdict(int)
        for row in open_rows:
            by_reason[str(row.get("reason_code") or "unknown")] += 1
        return {
            "tenant_id": self._tenant_id,
            "open_count": len(open_rows),
            "open_by_reason": dict(by_reason),
            "recent_open": recent,
        }

    def lookup_student_by_phone(self, phone: str) -> dict[str, Any]:
        digits = re.sub(r"\D", "", phone or "")
        if len(digits) < 9:
            return {"ok": False, "error": "A phone number is required"}
        client = self._db()
        response = (
            client.table("students")
            .select("id, name, phone, language_pref")
            .eq("tenant_id", self._tenant_id)
            .eq("phone", digits)
            .limit(1)
            .execute()
        )
        rows = response.data or []
        if not rows:
            return {"ok": True, "student": None}
        student = rows[0]
        enrollments = (
            client.table("enrollments")
            .select("id, class_id, status")
            .eq("tenant_id", self._tenant_id)
            .eq("student_id", student["id"])
            .execute()
        )
        open_esc = (
            client.table("escalations")
            .select("id, reason_code, status")
            .eq("tenant_id", self._tenant_id)
            .eq("student_id", student["id"])
            .eq("status", "open")
            .execute()
        )
        return {
            "ok": True,
            "student": {
                "id": student["id"],
                "name": student.get("name"),
                "phone": student.get("phone"),
                "enrollments": enrollments.data or [],
                "open_escalations": open_esc.data or [],
            },
        }

    def _db(self) -> Any:
        return self._client or get_supabase_client()

    def _count(self, table: str, *, filters: dict[str, str] | None = None) -> int:
        query = self._db().table(table).select("id", count="exact").eq("tenant_id", self._tenant_id)
        for key, value in (filters or {}).items():
            query = query.eq(key, value)
        response = query.execute()
        return int(response.count or 0)

    def _count_in(self, table: str, *, status: str, column: str, values: list[str]) -> int:
        response = (
            self._db()
            .table(table)
            .select("id", count="exact")
            .eq("tenant_id", self._tenant_id)
            .eq("status", status)
            .in_(column, values)
            .execute()
        )
        return int(response.count or 0)

    def _fetch_all(self, table: str, columns: str) -> list[dict[str, Any]]:
        client = self._db()
        rows: list[dict[str, Any]] = []
        start = 0
        while start < _MAX_ROWS:
            end = start + _PAGE - 1
            response = (
                client.table(table)
                .select(columns)
                .eq("tenant_id", self._tenant_id)
                .range(start, end)
                .execute()
            )
            batch = response.data or []
            rows.extend(batch)
            if len(batch) < _PAGE:
                break
            start += _PAGE
        return rows

    def _student_names(self, student_ids: list[str]) -> dict[str, str | None]:
        unique = [sid for sid in dict.fromkeys(student_ids) if sid]
        if not unique:
            return {}
        response = (
            self._db()
            .table("students")
            .select("id, name")
            .eq("tenant_id", self._tenant_id)
            .in_("id", unique[:50])
            .execute()
        )
        return {str(row["id"]): row.get("name") for row in (response.data or []) if row.get("id")}


def extract_phone_from_message(message: str) -> str | None:
    match = _PHONE_RE.search(message or "")
    return match.group(0) if match else None


def _parse_dt(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
    text = str(value).replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _build_analytics(
    *,
    tenant_id: str,
    turns: list[dict[str, Any]],
    escalations: list[dict[str, Any]],
    students: list[dict[str, Any]],
    estimated_minutes_per_deflection: int = 2,
) -> dict[str, Any]:
    students_by_id = {str(row["id"]): row for row in students if row.get("id")}
    total_messages = len(turns)
    session_ids = {row.get("session_id") for row in turns if row.get("session_id")}
    total_conversations = len(session_ids)
    escalated_student_ids = {str(row["student_id"]) for row in escalations if row.get("student_id")}
    sessions_by_student: dict[str, set[str]] = defaultdict(set)
    for row in turns:
        user_id = row.get("user_id")
        session_id = row.get("session_id")
        if user_id and session_id:
            sessions_by_student[str(user_id)].add(session_id)
    escalated_conversation_proxy = min(
        sum(len(sessions_by_student.get(sid, set())) for sid in escalated_student_ids),
        total_conversations,
    )
    deflected_conversations = max(total_conversations - escalated_conversation_proxy, 0)
    deflection_rate = (
        round((deflected_conversations / total_conversations) * 100, 1) if total_conversations else 0.0
    )

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in turns:
        grouped[str(row.get("session_id") or "")].append(row)
    response_times: list[float] = []
    for session_turns in grouped.values():
        ordered = sorted(session_turns, key=lambda item: str(item.get("created_at") or ""))
        for index, turn in enumerate(ordered):
            if str(turn.get("role") or "") != "user":
                continue
            for nxt in ordered[index + 1 :]:
                role = str(nxt.get("role") or "")
                if role == "assistant":
                    start = _parse_dt(turn.get("created_at"))
                    end = _parse_dt(nxt.get("created_at"))
                    if start and end:
                        delta = (end - start).total_seconds()
                        if delta >= 0:
                            response_times.append(delta)
                    break
                if role == "user":
                    break

    average_response_seconds = (
        round(sum(response_times) / len(response_times), 2) if response_times else 0.0
    )
    open_escalations = sum(1 for row in escalations if row.get("status") == "open")
    resolved_escalations = sum(1 for row in escalations if row.get("status") == "resolved")
    category_counts: dict[str, int] = defaultdict(int)
    for row in escalations:
        category_counts[str(row.get("reason_code") or "unknown")] += 1
    escalation_categories = [
        {"reason_code": reason, "count": count}
        for reason, count in sorted(category_counts.items(), key=lambda item: item[1], reverse=True)
    ]

    message_counts: dict[str, int] = defaultdict(int)
    conversation_counts: dict[str, set[str]] = defaultdict(set)
    escalation_counts: dict[str, int] = defaultdict(int)
    for row in turns:
        user_id = str(row.get("user_id") or "")
        message_counts[user_id] += 1
        if row.get("session_id"):
            conversation_counts[user_id].add(row["session_id"])
    for row in escalations:
        escalation_counts[str(row.get("student_id") or "")] += 1

    student_metrics = []
    for student_id in set(message_counts) | set(escalation_counts):
        if not student_id:
            continue
        student = students_by_id.get(student_id)
        student_metrics.append(
            {
                "student_id": student_id,
                "student_name": student.get("name") if student else None,
                "messages": message_counts.get(student_id, 0),
                "conversations": len(conversation_counts.get(student_id, set())),
                "escalations": escalation_counts.get(student_id, 0),
            }
        )
    student_metrics.sort(key=lambda row: (row["messages"], row["conversations"]), reverse=True)

    return {
        "tenant_id": tenant_id,
        "total_conversations": total_conversations,
        "total_messages": total_messages,
        "deflected_conversations": deflected_conversations,
        "deflection_rate": deflection_rate,
        "average_response_seconds": average_response_seconds,
        "estimated_minutes_saved": deflected_conversations * estimated_minutes_per_deflection,
        "total_escalations": len(escalations),
        "open_escalations": open_escalations,
        "resolved_escalations": resolved_escalations,
        "escalation_categories": escalation_categories,
        "students": student_metrics[:20],
    }


def _build_class_analytics(
    *,
    tenant_id: str,
    classes: list[dict[str, Any]],
    enrollments: list[dict[str, Any]],
    turns: list[dict[str, Any]],
    escalations: list[dict[str, Any]],
    estimated_minutes_per_deflection: int = 2,
) -> dict[str, Any]:
    class_enrollments: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in enrollments:
        class_enrollments[str(row.get("class_id") or "")].append(row)
    turns_by_student: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in turns:
        turns_by_student[str(row.get("user_id") or "")].append(row)
    escalations_by_student: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in escalations:
        escalations_by_student[str(row.get("student_id") or "")].append(row)

    results = []
    ordered_classes = sorted(
        classes,
        key=lambda row: (str(row.get("subject") or ""), str(row.get("name") or "")),
    )
    for subject_class in ordered_classes:
        class_id = str(subject_class.get("id") or "")
        class_rows = class_enrollments.get(class_id, [])
        student_ids = {str(row.get("student_id") or "") for row in class_rows if row.get("student_id")}
        active_students = sum(1 for row in class_rows if row.get("status") == "active")
        pending_students = sum(1 for row in class_rows if row.get("status") == "pending")
        class_turns: list[dict[str, Any]] = []
        class_escalations: list[dict[str, Any]] = []
        for student_id in student_ids:
            class_turns.extend(turns_by_student.get(student_id, []))
            class_escalations.extend(escalations_by_student.get(student_id, []))
        session_ids = {row.get("session_id") for row in class_turns if row.get("session_id")}
        total_conversations = len(session_ids)
        total_messages = len(class_turns)
        escalated_sessions: set[str] = set()
        for student_id in {str(row.get("student_id") or "") for row in class_escalations}:
            for turn in turns_by_student.get(student_id, []):
                if turn.get("session_id"):
                    escalated_sessions.add(turn["session_id"])
        escalated_conversation_proxy = min(len(escalated_sessions), total_conversations)
        deflected_conversations = max(total_conversations - escalated_conversation_proxy, 0)
        deflection_rate = (
            round((deflected_conversations / total_conversations) * 100, 1)
            if total_conversations
            else 0.0
        )
        results.append(
            {
                "class_id": class_id,
                "class_name": subject_class.get("name"),
                "subject": subject_class.get("subject"),
                "grade": subject_class.get("grade"),
                "enrolled_students": len(student_ids),
                "active_students": active_students,
                "pending_students": pending_students,
                "total_messages": total_messages,
                "total_conversations": total_conversations,
                "deflected_conversations": deflected_conversations,
                "deflection_rate": deflection_rate,
                "estimated_minutes_saved": deflected_conversations * estimated_minutes_per_deflection,
                "total_escalations": len(class_escalations),
                "open_escalations": sum(1 for row in class_escalations if row.get("status") == "open"),
                "resolved_escalations": sum(
                    1 for row in class_escalations if row.get("status") == "resolved"
                ),
            }
        )
    return {
        "tenant_id": tenant_id,
        "attribution_mode": "enrollment_membership",
        "classes": results,
    }


def format_overview_fallback(overview: dict[str, Any], analytics: dict[str, Any] | None = None) -> str:
    lines = [
        f"Open escalations: {overview.get('open_escalations', 0)}",
        f"Payment receipts waiting: {overview.get('open_payment_receipts', 0)}",
        f"Talk-to-tutor: {overview.get('open_talk_to_tutor', 0)}",
        f"Pending enrollments: {overview.get('pending_enrollments', 0)}",
        f"Students: {overview.get('students', 0)}",
        f"Classes: {overview.get('classes', 0)}",
    ]
    if analytics:
        lines.append(f"Deflection rate: {analytics.get('deflection_rate', 0)}%")
        lines.append(f"Conversations: {analytics.get('total_conversations', 0)}")
    return "\n".join(lines)
