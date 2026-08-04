"""Pydantic API schemas."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

from domain.enums import PaymentStatus, TenantStatus, MessageRole


class HealthResponse(BaseModel):
    status: Literal["ok", "starting"]
    phase: int = 0


class ReadinessCheck(BaseModel):
    name: str
    ok: bool
    detail: str = ""


class ReadinessResponse(BaseModel):
    ready: bool
    checks: list[ReadinessCheck]


class ConfigResponse(BaseModel):
    provider: str
    router_model: str
    router_provider: str
    guardrail_model: str
    guardrail_provider: str
    chat_model: str
    chat_provider: str
    merge_model: str
    merge_provider: str
    messaging_dry_run: bool
    supabase_configured: bool
    qdrant_configured: bool
    langfuse_configured: bool
    langfuse_prompt_label: str = Field(default="production")


class PaymentStatusUpdate(BaseModel):
    """Example dashboard PATCH body using domain enums."""

    status: PaymentStatus


class TenantSummary(BaseModel):
    id: str
    slug: str
    status: TenantStatus


class ChatRequest(BaseModel):
    """Dev chat request — simulates a student WhatsApp message over HTTP."""

    tenant_id: str = Field(
        description="Tuition agency tenant, e.g. tenant-demo-physics",
        examples=["tenant-demo-physics"],
    )
    phone: str = Field(
        description="Student phone (digits only or E.164). Demo: 94771234567",
        examples=["94771234567"],
    )
    message: str = Field(min_length=1, description="Student message text")
    media_url: Optional[str] = Field(default=None, description="Optional image URL (payment slip, etc.)")


class ChatResponse(BaseModel):
    reply: str
    tenant_id: str
    tenant_slug: Optional[str] = None
    tenant_name: Optional[str] = None
    student_id: str
    phone: str
    session_id: str
    student_registered: bool = True


class ChatTurnRecord(BaseModel):
    id: str
    role: MessageRole
    sender: Literal["student", "bot", "staff"] = Field(
        description="UI label: user→student, assistant→bot, system→staff",
    )
    content: str
    created_at: str


class ChatTurnsResponse(BaseModel):
    tenant_id: str
    session_id: str
    turns: list[ChatTurnRecord]


class ChatConversationSummary(BaseModel):
    session_id: str
    student_id: str
    student_name: Optional[str] = None
    phone: str
    last_message: str
    last_message_at: str
    last_sender: Literal["student", "bot", "staff"]
    has_open_escalation: bool = False
    open_escalation_reason: Optional[str] = None


class ChatConversationsResponse(BaseModel):
    tenant_id: str
    conversations: list[ChatConversationSummary]


class ChatThreadResponse(BaseModel):
    tenant_id: str
    session_id: str
    student_id: str
    student_name: Optional[str] = None
    phone: str
    turns: list[ChatTurnRecord]
    open_escalations: list[dict] = Field(default_factory=list)


class DashboardChatSendRequest(BaseModel):
    tenant_id: str
    phone: str = Field(description="Student phone, e.g. 94771234567")
    message: str = Field(min_length=1)
    staff_id: Optional[str] = Field(
        default=None,
        description="Staff user id or email for audit (optional)",
    )


class DashboardChatSendResponse(BaseModel):
    ok: bool
    tenant_id: str
    phone: str
    delivered: bool
    turn: Optional[ChatTurnRecord] = None


class RAGSearchRequest(BaseModel):
    tenant_id: str
    query: str = Field(min_length=1)


class RAGResponse(BaseModel):
    result: str
    latency_ms: int


class RAGStatusResponse(BaseModel):
    result: str


class DriveSearchRequest(BaseModel):
    tenant_id: str
    query: str = Field(min_length=1)
    folder: Optional[str] = "papers"


class DriveListRequest(BaseModel):
    tenant_id: str
    folder: str = "papers"


class DriveResponse(BaseModel):
    result: str
    latency_ms: int


class IngestUploadResponse(BaseModel):
    ok: bool = True
    tenant_id: str
    strategy: str
    documents: int
    chunks_upserted: int
    collection: str
    points_count: Optional[int] = None
    document_title: Optional[str] = None
    source_filename: Optional[str] = None
