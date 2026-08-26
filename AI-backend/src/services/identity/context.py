"""Resolved tenant + student scope for one WhatsApp conversation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IdentityContext:
    """Resolved tenant scope; student_id is set only when a DB record exists."""

    tenant_id: str
    tenant_slug: str | None
    tenant_name: str | None
    phone: str
    session_id: str
    student_id: str | None = None
    human_mode: bool = False
    student_exists: bool = False
    student_name: str | None = None
    is_enrolled: bool = False
    enrollment_status: str = "none"
    active_class_names: tuple[str, ...] = ()
    enrolled_class_ids: tuple[str, ...] = ()
    language_pref: str = "en"

    @property
    def memory_user_id(self) -> str:
        """Stable recall key — student id when enrolled, otherwise phone."""
        return self.student_id or self.phone

    @property
    def can_access_resources(self) -> bool:
        """Past papers and RAG require pending or active enrollment."""
        return self.is_enrolled
