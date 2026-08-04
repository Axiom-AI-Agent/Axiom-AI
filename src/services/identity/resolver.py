"""Resolve tenant and student from Twilio WhatsApp identifiers."""

from __future__ import annotations

import re
import uuid
from typing import Any

from loguru import logger

from infrastructure.config import DEV_TENANT_ID
from infrastructure.db.supabase_client import get_supabase_client
from services.identity.context import IdentityContext

_WHATSAPP_PREFIX = re.compile(r"^whatsapp:", re.IGNORECASE)


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
        student, registered = self._resolve_or_create_student(tenant["id"], phone)
        session_id = build_session_id(tenant["id"], phone)

        return IdentityContext(
            tenant_id=tenant["id"],
            tenant_slug=tenant.get("slug"),
            tenant_name=tenant.get("name"),
            student_id=student["id"],
            phone=phone,
            session_id=session_id,
            student_registered=registered,
        )

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
        student, registered = self._resolve_or_create_student(tenant["id"], normalized_phone)
        session_id = build_session_id(tenant["id"], normalized_phone)

        return IdentityContext(
            tenant_id=tenant["id"],
            tenant_slug=tenant.get("slug"),
            tenant_name=tenant.get("name"),
            student_id=student["id"],
            phone=normalized_phone,
            session_id=session_id,
            student_registered=registered,
        )

    def _resolve_or_create_student(
        self, tenant_id: str, phone: str
    ) -> tuple[dict[str, Any], bool]:
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
        if rows:
            return rows[0], True

        student_id = f"stu-{uuid.uuid4().hex[:12]}"
        payload = {
            "id": student_id,
            "tenant_id": tenant_id,
            "phone": phone,
            "name": None,
        }
        insert = client.table("students").insert(payload).execute()
        created = (insert.data or [payload])[0]
        logger.info("Provisioned stub student {} for tenant {}", student_id, tenant_id)
        return created, False
