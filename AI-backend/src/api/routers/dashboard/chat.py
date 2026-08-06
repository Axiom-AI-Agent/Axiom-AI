"""Dashboard staff chat — conversation list, thread view, staff send."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query

from api.routers.dashboard.chat_helpers import (
    build_conversation_summary,
    session_id_for_phone,
    turn_to_record,
)
from api.schemas import (
    ChatConversationsResponse,
    ChatThreadResponse,
    ChatTurnRecord,
    ChatTurnsResponse,
    DashboardChatSendRequest,
    DashboardChatSendResponse,
)
from api.routers.dashboard.escalations import notify_student
from api.tenant_scope import (
    DashboardTenant,
    assert_body_tenant,
    assert_session_for_tenant,
)
from infrastructure.db.supabase_client import get_supabase_client
from services.identity.resolver import build_session_id, normalize_phone
from services.messaging.persistence import MessagePersistence

router = APIRouter(prefix="/chat", tags=["dashboard-chat"])


def _fetch_students_by_ids(
    client: Any, tenant_id: str, student_ids: list[str]
) -> dict[str, dict[str, Any]]:
    if not student_ids:
        return {}
    response = (
        client.table("students")
        .select("id, name, phone")
        .eq("tenant_id", tenant_id)
        .in_("id", student_ids)
        .execute()
    )
    return {row["id"]: row for row in (response.data or [])}


def _fetch_open_escalations_by_student(
    client: Any, tenant_id: str, student_ids: list[str]
) -> dict[str, dict[str, Any]]:
    if not student_ids:
        return {}
    response = (
        client.table("escalations")
        .select("id, student_id, reason_code, status, created_at")
        .eq("tenant_id", tenant_id)
        .eq("status", "open")
        .in_("student_id", student_ids)
        .execute()
    )
    by_student: dict[str, dict[str, Any]] = {}
    for row in response.data or []:
        sid = row["student_id"]
        existing = by_student.get(sid)
        if existing is None or str(row["created_at"]) > str(existing["created_at"]):
            by_student[sid] = row
    return by_student


def _fetch_open_escalations_for_student(
    client: Any, tenant_id: str, student_id: str
) -> list[dict[str, Any]]:
    response = (
        client.table("escalations")
        .select(
            "id, reason_code, status, media_url, student_message, "
            "created_at, updated_at"
        )
        .eq("tenant_id", tenant_id)
        .eq("student_id", student_id)
        .eq("status", "open")
        .order("created_at", desc=True)
        .execute()
    )
    return response.data or []


@router.get("/conversations", response_model=ChatConversationsResponse)
async def list_conversations(
    tenant: DashboardTenant,
    limit: int = Query(default=50, ge=1, le=200),
    open_escalation_only: bool = Query(
        default=False,
        description="When true, only return students with an open escalation",
    ),
) -> ChatConversationsResponse:
    """
    Sidebar conversation list for the staff chat UI.

    One row per student session, sorted by most recent message. Mirrors the
    BookMe AI session sidebar pattern — the dashboard team polls or refreshes
    this endpoint to populate the left panel.
    """
    tenant_id = tenant.tenant_id
    persistence = MessagePersistence()
    try:
        latest_turns = persistence.list_recent_sessions(tenant_id=tenant_id, limit=limit)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    if not latest_turns:
        return ChatConversationsResponse(tenant_id=tenant_id, conversations=[])

    client = get_supabase_client()
    student_ids = list({str(row["user_id"]) for row in latest_turns})
    students = _fetch_students_by_ids(client, tenant_id, student_ids)
    open_esc = _fetch_open_escalations_by_student(client, tenant_id, student_ids)

    conversations = []
    for turn in latest_turns:
        session_id = str(turn["session_id"])
        assert_session_for_tenant(session_id, tenant)
        student_id = str(turn["user_id"])
        student = students.get(student_id, {"id": student_id, "phone": None, "name": None})
        escalation = open_esc.get(student_id)
        if open_escalation_only and escalation is None:
            continue
        conversations.append(
            build_conversation_summary(
                tenant_id=tenant_id,
                latest_turn=turn,
                student=student,
                open_escalation=escalation,
            )
        )

    return ChatConversationsResponse(tenant_id=tenant_id, conversations=conversations)


@router.get("/conversations/{phone}", response_model=ChatThreadResponse)
async def get_conversation_thread(
    phone: str,
    tenant: DashboardTenant,
    limit: int = Query(default=100, ge=1, le=500),
) -> ChatThreadResponse:
    """
    Full message thread for one student — central panel of the chat UI.

    Returns turns with `sender` labels (`student` | `bot` | `staff`) plus any
    open escalations for context banners in the dashboard.
    """
    tenant_id = tenant.tenant_id
    normalized = normalize_phone(phone)
    session_id = session_id_for_phone(tenant_id, normalized)
    assert_session_for_tenant(session_id, tenant)
    persistence = MessagePersistence()
    client = get_supabase_client()

    try:
        rows = persistence.get_turns(
            tenant_id=tenant_id,
            session_id=session_id,
            limit=limit,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    student_resp = (
        client.table("students")
        .select("id, name, phone")
        .eq("tenant_id", tenant_id)
        .eq("phone", normalized)
        .limit(1)
        .execute()
    )
    student_rows = student_resp.data or []
    if not student_rows:
        raise HTTPException(status_code=404, detail="Student not found")

    student = student_rows[0]
    open_escalations = _fetch_open_escalations_for_student(
        client, tenant_id, str(student["id"])
    )

    return ChatThreadResponse(
        tenant_id=tenant_id,
        session_id=session_id,
        student_id=str(student["id"]),
        student_name=student.get("name"),
        phone=normalized,
        turns=[turn_to_record(row) for row in rows],
        open_escalations=open_escalations,
    )


@router.get("/threads/{phone}", response_model=ChatThreadResponse)
async def get_thread_alias(
    phone: str,
    tenant: DashboardTenant,
    limit: int = Query(default=100, ge=1, le=500),
) -> ChatThreadResponse:
    """Alias for GET /conversations/{phone}."""
    return await get_conversation_thread(phone, tenant=tenant, limit=limit)


@router.get("/turns", response_model=ChatTurnsResponse)
async def get_chat_turns(
    tenant: DashboardTenant,
    phone: str = Query(..., description="Student phone, e.g. 94771234567"),
    limit: int = Query(default=50, ge=1, le=200),
) -> ChatTurnsResponse:
    """Fetch conversation turns (legacy path; prefer GET /conversations/{phone})."""
    tenant_id = tenant.tenant_id
    normalized = normalize_phone(phone)
    session_id = build_session_id(tenant_id, normalized)
    assert_session_for_tenant(session_id, tenant)
    persistence = MessagePersistence()
    try:
        rows = persistence.get_turns(
            tenant_id=tenant_id,
            session_id=session_id,
            limit=limit,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return ChatTurnsResponse(
        tenant_id=tenant_id,
        session_id=session_id,
        turns=[turn_to_record(row) for row in rows],
    )


@router.post("/send", response_model=DashboardChatSendResponse)
async def send_staff_message(
    body: DashboardChatSendRequest,
    tenant: DashboardTenant,
) -> DashboardChatSendResponse:
    """
    Staff reply to a student via WhatsApp.

    Persists the message as role=system (sender=staff) before delivery so the
    dashboard thread stays in sync with what the student receives.
    """
    assert_body_tenant(body.tenant_id, tenant)
    if not body.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    tenant_id = tenant.tenant_id
    message = body.message.strip()
    notified = await notify_student(
        tenant_id=tenant_id,
        phone=body.phone,
        message=message,
        intent="staff_reply",
    )

    turn: Optional[ChatTurnRecord] = None
    if notified:
        session_id = session_id_for_phone(tenant_id, body.phone)
        assert_session_for_tenant(session_id, tenant)
        persistence = MessagePersistence()
        try:
            latest = persistence.get_latest_turn(
                tenant_id=tenant_id,
                session_id=session_id,
            )
            if latest:
                turn = turn_to_record(latest)
        except RuntimeError:
            turn = None

    return DashboardChatSendResponse(
        ok=notified,
        tenant_id=tenant_id,
        phone=normalize_phone(body.phone),
        delivered=notified,
        turn=turn,
    )
