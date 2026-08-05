"""Resolve tenant and student from Twilio WhatsApp identifiers."""

from __future__ import annotations

import re
from typing import Any

from loguru import logger

from infrastructure.config import DEV_TENANT_ID
from infrastructure.db.supabase_client import get_supabase_client
from services.identity.context import IdentityContext

_WHATSAPP_PREFIX = re.compile(r"^whatsapp:", re.IGNORECASE)
_ENROLLED_STATUSES = frozenset({"active", "pending"})


def normalize_phone(value: str) -> str:
    """Strip Twilio whatsapp: prefix and non-digits (E.164 without +)."""
    cleaned = _WHATSAPP_PREFIX.sub("", value.strip())
    return re.sub(r"\D", "", cleaned)


def normalize_whatsapp_address(value: str) -> str:
    """Ensure Twilio-compatible whatsapp: prefix."""
    phone = normalize_phone(value)
    if phone.startswith("+"):
        return f"whatsapp:{phone}"
    return f"whatsapp:+{phone}"


def build_session_id(tenant_id: str, phone: str) -> str:
    return f"{tenant_id}:{normalize_phone(phone)}"


class IdentityResolver:
    """Lookup tenant by sandbox number and student by sender phone."""

    def resolve(
        self,
        *,
        to_number: str,
        from_number: str,
        fallback_tenant_id: str | None = None,
    ) -> IdentityContext:
        tenant = self._resolve_tenant(to_number, fallback_tenant_id)
        phone = normalize_phone(from_number)
        student = self._lookup_student(tenant["id"], phone)
        return self._build_context(tenant, phone, student)

    def _resolve_tenant(
        self, to_number: str, fallback_tenant_id: str | None
    ) -> dict[str, Any]:
        candidates = {
            to_number.strip(),
            normalize_whatsapp_address(to_number),
            normalize_phone(to_number),
        }
        client = get_supabase_client()

        for candidate in candidates:
            if not candidate:
                continue
            response = (
                client.table("tenants")
                .select("id, slug, name, whatsapp_number, status")
                .eq("whatsapp_number", candidate)
                .limit(1)
                .execute()
            )
            rows = response.data or []
            if rows and rows[0].get("status") == "active":
                return rows[0]

        fallback = fallback_tenant_id or DEV_TENANT_ID
        logger.warning(
            "No tenant matched To={}; falling back to {}",
            to_number,
            fallback,
        )
        response = (
            client.table("tenants")
            .select("id, slug, name, whatsapp_number, status")
            .eq("id", fallback)
            .limit(1)
            .execute()
        )
        rows = response.data or []
        if not rows:
            raise RuntimeError(f"Fallback tenant not found: {fallback}")
        return rows[0]

    def resolve_direct(self, *, tenant_id: str, phone: str) -> IdentityContext:
        """Resolve identity for HTTP dev chat when tenant_id is known."""
        client = get_supabase_client()
        response = (
            client.table("tenants")
            .select("id, slug, name, status")
            .eq("id", tenant_id)
            .limit(1)
            .execute()
        )
        rows = response.data or []
        if not rows:
            raise ValueError(f"Unknown tenant: {tenant_id}")
        tenant = rows[0]
        if tenant.get("status") != "active":
            raise ValueError(f"Tenant is not active: {tenant_id}")

        normalized_phone = normalize_phone(phone)
        student = self._lookup_student(tenant_id, normalized_phone)
        return self._build_context(tenant, normalized_phone, student)

    def _build_context(
        self,
        tenant: dict[str, Any],
        phone: str,
        student: dict[str, Any] | None,
    ) -> IdentityContext:
        tenant_id = tenant["id"]
        session_id = build_session_id(tenant_id, phone)

        if not student:
            return IdentityContext(
                tenant_id=tenant_id,
                tenant_slug=tenant.get("slug"),
                tenant_name=tenant.get("name"),
                phone=phone,
                session_id=session_id,
                student_exists=False,
            )

        enrollments = self._lookup_enrollments(tenant_id, student["id"])
        class_names = self._lookup_class_names(
            tenant_id,
            [row["class_id"] for row in enrollments if row.get("class_id")],
        )
        enrolled_rows = [
            row for row in enrollments if row.get("status") in _ENROLLED_STATUSES
        ]
        enrollment_status = self._enrollment_status(enrollments)

        return IdentityContext(
            tenant_id=tenant_id,
            tenant_slug=tenant.get("slug"),
            tenant_name=tenant.get("name"),
            student_id=student["id"],
            phone=phone,
            session_id=session_id,
            student_exists=True,
            student_name=student.get("name"),
            is_enrolled=bool(enrolled_rows),
            enrollment_status=enrollment_status,
            active_class_names=tuple(
                class_names.get(row["class_id"], row["class_id"]) for row in enrolled_rows
            ),
        )

    @staticmethod
    def _enrollment_status(enrollments: list[dict[str, Any]]) -> str:
        if any(row.get("status") == "active" for row in enrollments):
            return "active"
        if any(row.get("status") == "pending" for row in enrollments):
            return "pending"
        return "none"

    def _lookup_student(self, tenant_id: str, phone: str) -> dict[str, Any] | None:
        client = get_supabase_client()
        response = (
            client.table("students")
            .select("id, name, phone")
            .eq("tenant_id", tenant_id)
            .eq("phone", phone)
            .limit(1)
            .execute()
        )
        rows = response.data or []
        return rows[0] if rows else None

    def _lookup_enrollments(self, tenant_id: str, student_id: str) -> list[dict[str, Any]]:
        client = get_supabase_client()
        response = (
            client.table("enrollments")
            .select("id, class_id, status")
            .eq("tenant_id", tenant_id)
            .eq("student_id", student_id)
            .execute()
        )
        return response.data or []

    def _lookup_class_names(
        self, tenant_id: str, class_ids: list[str]
    ) -> dict[str, str]:
        if not class_ids:
            return {}
        client = get_supabase_client()
        response = (
            client.table("subject_classes")
            .select("id, name")
            .eq("tenant_id", tenant_id)
            .in_("id", class_ids)
            .execute()
        )
        return {row["id"]: row["name"] for row in (response.data or []) if row.get("id")}
