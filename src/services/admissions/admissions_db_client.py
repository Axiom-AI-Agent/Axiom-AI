"""Supabase access for admissions CRM operations."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from loguru import logger

from infrastructure.db.supabase_client import get_supabase_client

ENROLLMENT_PAYMENT_REASON = "enrollment_payment_review"


class AdmissionsDbClient:
    """Tenant-scoped student, class, and enrollment persistence."""

    def get_student(self, *, tenant_id: str, phone: str) -> dict[str, Any] | None:
        client = get_supabase_client()
        response = (
            client.table("students")
            .select(
                "id, tenant_id, name, phone, school, district, consent_at, language_pref, created_at"
            )
            .eq("tenant_id", tenant_id)
            .eq("phone", phone)
            .limit(1)
            .execute()
        )
        rows = response.data or []
        return rows[0] if rows else None

    def get_student_by_id(self, *, tenant_id: str, student_id: str) -> dict[str, Any] | None:
        client = get_supabase_client()
        response = (
            client.table("students")
            .select(
                "id, tenant_id, name, phone, school, district, consent_at, language_pref, created_at"
            )
            .eq("tenant_id", tenant_id)
            .eq("id", student_id)
            .limit(1)
            .execute()
        )
        rows = response.data or []
        return rows[0] if rows else None

    def update_student(
        self,
        *,
        tenant_id: str,
        student_id: str,
        name: str | None = None,
        school: str | None = None,
        district: str | None = None,
        consent: bool = False,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"updated_at": datetime.now(timezone.utc).isoformat()}
        if name is not None:
            payload["name"] = name
        if school is not None:
            payload["school"] = school
        if district is not None:
            payload["district"] = district
        if consent:
            payload["consent_at"] = datetime.now(timezone.utc).isoformat()

        client = get_supabase_client()
        response = (
            client.table("students")
            .update(payload)
            .eq("tenant_id", tenant_id)
            .eq("id", student_id)
            .execute()
        )
        rows = response.data or []
        if not rows:
            raise RuntimeError(f"Student not found: {student_id}")
        return rows[0]

    def list_classes(
        self,
        *,
        tenant_id: str,
        subject: str | None = None,
        grade: str | None = None,
    ) -> list[dict[str, Any]]:
        client = get_supabase_client()
        query = (
            client.table("subject_classes")
            .select("id, tenant_id, name, subject, grade, fee_amount, fee_cycle")
            .eq("tenant_id", tenant_id)
        )
        if subject:
            query = query.ilike("subject", f"%{subject}%")
        if grade:
            query = query.ilike("grade", f"%{grade}%")
        response = query.order("subject").execute()
        return response.data or []

    def get_class(self, *, tenant_id: str, class_id: str) -> dict[str, Any] | None:
        client = get_supabase_client()
        response = (
            client.table("subject_classes")
            .select("id, tenant_id, name, subject, grade, fee_amount, fee_cycle")
            .eq("tenant_id", tenant_id)
            .eq("id", class_id)
            .limit(1)
            .execute()
        )
        rows = response.data or []
        return rows[0] if rows else None

    def list_enrollments(self, *, tenant_id: str, student_id: str) -> list[dict[str, Any]]:
        client = get_supabase_client()
        response = (
            client.table("enrollments")
            .select("id, tenant_id, student_id, class_id, status, created_at")
            .eq("tenant_id", tenant_id)
            .eq("student_id", student_id)
            .execute()
        )
        return response.data or []

    def get_enrollment(self, *, tenant_id: str, enrollment_id: str) -> dict[str, Any] | None:
        client = get_supabase_client()
        response = (
            client.table("enrollments")
            .select("id, tenant_id, student_id, class_id, status, created_at")
            .eq("tenant_id", tenant_id)
            .eq("id", enrollment_id)
            .limit(1)
            .execute()
        )
        rows = response.data or []
        return rows[0] if rows else None

    def get_pending_enrollment(
        self, *, tenant_id: str, student_id: str
    ) -> dict[str, Any] | None:
        for row in self.list_enrollments(tenant_id=tenant_id, student_id=student_id):
            if row.get("status") == "pending":
                return row
        return None

    def create_enrollment(
        self,
        *,
        tenant_id: str,
        student_id: str,
        class_id: str,
        status: str = "pending",
    ) -> dict[str, Any]:
        existing = self.list_enrollments(tenant_id=tenant_id, student_id=student_id)
        for row in existing:
            if row.get("class_id") == class_id and row.get("status") in ("active", "pending"):
                return row

        client = get_supabase_client()
        payload = {
            "tenant_id": tenant_id,
            "student_id": student_id,
            "class_id": class_id,
            "status": status,
        }
        try:
            response = client.table("enrollments").insert(payload).execute()
            rows = response.data or []
            if rows:
                return rows[0]
        except Exception as exc:
            logger.warning("Enrollment insert failed ({}); checking existing row", exc)
            for row in existing:
                if row.get("class_id") == class_id:
                    return row
            raise
        return payload

    def activate_enrollment(self, *, tenant_id: str, enrollment_id: str) -> dict[str, Any]:
        client = get_supabase_client()
        response = (
            client.table("enrollments")
            .update({"status": "active"})
            .eq("tenant_id", tenant_id)
            .eq("id", enrollment_id)
            .execute()
        )
        rows = response.data or []
        if not rows:
            raise RuntimeError(f"Enrollment not found: {enrollment_id}")
        return rows[0]

    def create_invoice_for_class(
        self,
        *,
        tenant_id: str,
        student_id: str,
        class_row: dict[str, Any],
    ) -> dict[str, Any]:
        period = datetime.now(timezone.utc).strftime("%Y-%m")
        amount = class_row.get("fee_amount") or 0
        client = get_supabase_client()
        existing = (
            client.table("invoices")
            .select("id, tenant_id, student_id, period, status")
            .eq("tenant_id", tenant_id)
            .eq("student_id", student_id)
            .eq("period", period)
            .limit(1)
            .execute()
        )
        rows = existing.data or []
        if rows:
            return rows[0]

        payload = {
            "tenant_id": tenant_id,
            "student_id": student_id,
            "period": period,
            "amount_due": amount,
            "status": "pending",
        }
        response = client.table("invoices").insert(payload).execute()
        return (response.data or [payload])[0]

    def create_bank_slip_upload(
        self,
        *,
        tenant_id: str,
        invoice_id: str,
        image_ref: str,
    ) -> dict[str, Any]:
        client = get_supabase_client()
        payload = {
            "tenant_id": tenant_id,
            "invoice_id": invoice_id,
            "image_ref": image_ref,
        }
        response = client.table("bank_slip_uploads").insert(payload).execute()
        return (response.data or [payload])[0]

    def create_escalation(
        self,
        *,
        tenant_id: str,
        student_id: str,
        enrollment_id: str,
        reason_code: str = ENROLLMENT_PAYMENT_REASON,
    ) -> dict[str, Any]:
        client = get_supabase_client()
        existing = (
            client.table("escalations")
            .select("id, tenant_id, student_id, enrollment_id, status, reason_code")
            .eq("tenant_id", tenant_id)
            .eq("enrollment_id", enrollment_id)
            .in_("status", ["open", "assigned"])
            .limit(1)
            .execute()
        )
        rows = existing.data or []
        if rows:
            return rows[0]

        payload = {
            "tenant_id": tenant_id,
            "student_id": student_id,
            "enrollment_id": enrollment_id,
            "reason_code": reason_code,
            "status": "open",
        }
        response = client.table("escalations").insert(payload).execute()
        return (response.data or [payload])[0]

    def get_open_enrollment_escalation(
        self, *, tenant_id: str, enrollment_id: str
    ) -> dict[str, Any] | None:
        client = get_supabase_client()
        response = (
            client.table("escalations")
            .select("id, tenant_id, student_id, enrollment_id, status, reason_code")
            .eq("tenant_id", tenant_id)
            .eq("enrollment_id", enrollment_id)
            .in_("status", ["open", "assigned"])
            .limit(1)
            .execute()
        )
        rows = response.data or []
        return rows[0] if rows else None

    def resolve_escalation(
        self, *, tenant_id: str, escalation_id: str
    ) -> dict[str, Any]:
        client = get_supabase_client()
        response = (
            client.table("escalations")
            .update(
                {
                    "status": "resolved",
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
            )
            .eq("tenant_id", tenant_id)
            .eq("id", escalation_id)
            .execute()
        )
        rows = response.data or []
        if not rows:
            raise RuntimeError(f"Escalation not found: {escalation_id}")
        return rows[0]

    def mark_invoice_paid(self, *, tenant_id: str, invoice_id: str) -> dict[str, Any]:
        client = get_supabase_client()
        response = (
            client.table("invoices")
            .update(
                {
                    "status": "paid",
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
            )
            .eq("tenant_id", tenant_id)
            .eq("id", invoice_id)
            .execute()
        )
        rows = response.data or []
        if not rows:
            raise RuntimeError(f"Invoice not found: {invoice_id}")
        return rows[0]

    def get_latest_invoice_for_student(
        self, *, tenant_id: str, student_id: str
    ) -> dict[str, Any] | None:
        client = get_supabase_client()
        response = (
            client.table("invoices")
            .select("id, tenant_id, student_id, period, amount_due, status")
            .eq("tenant_id", tenant_id)
            .eq("student_id", student_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        rows = response.data or []
        return rows[0] if rows else None
