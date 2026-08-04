"""Messaging payload schemas — Twilio + channel-agnostic chat."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from domain.enums import ChatChannel


class TwilioInboundMessage(BaseModel):
    message_sid: str = Field(alias="MessageSid")
    account_sid: str = Field(alias="AccountSid")
    from_number: str = Field(alias="From")
    to_number: str = Field(alias="To")
    body: str = Field(default="", alias="Body")
    num_media: int = Field(default=0, alias="NumMedia")
    media_url: Optional[str] = Field(default=None, alias="MediaUrl0")
    profile_name: Optional[str] = Field(default=None, alias="ProfileName")

    model_config = {"populate_by_name": True}


class TwilioSendResult(BaseModel):
    sid: Optional[str] = None
    status: str
    dry_run: bool = False
    detail: str = ""


class InboundMessage(BaseModel):
    """Normalized inbound message from any channel."""

    channel: ChatChannel
    phone: str
    body: str = ""
    tenant_id: Optional[str] = None
    to_number: Optional[str] = None
    media_url: Optional[str] = None
    external_id: Optional[str] = None
    num_media: int = 0


class ChatTurnResult(BaseModel):
    """Result of one chat turn — used by HTTP and Twilio paths."""

    reply: str
    tenant_id: str
    tenant_slug: Optional[str] = None
    tenant_name: Optional[str] = None
    student_id: str
    phone: str
    session_id: str
    student_registered: bool = True
    channel: ChatChannel = ChatChannel.TWILIO_WHATSAPP
