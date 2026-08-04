"""Identity context passed through the chat pipeline."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IdentityContext:
    """Resolved tenant + student scope for one WhatsApp conversation."""

    tenant_id: str
    tenant_slug: str | None
    tenant_name: str | None
    student_id: str
    phone: str
    session_id: str
    human_mode: bool = False
    student_registered: bool = True
