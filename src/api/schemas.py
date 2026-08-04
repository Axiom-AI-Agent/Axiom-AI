"""Pydantic API schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from domain.enums import PaymentStatus, TenantStatus


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
