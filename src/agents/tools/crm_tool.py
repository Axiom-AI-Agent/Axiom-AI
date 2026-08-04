"""CRM business logic — called by MCP server only (Week 13 pattern)."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger

from services.admissions.admissions_db_client import AdmissionsDbClient, ENROLLMENT_PAYMENT_REASON


class CrmTool:
    def __init__(self, *, db: AdmissionsDbClient | None = None) -> None:
        self.db = db or AdmissionsDbClient()

    def _assert_tenant(self, expected: str, actual: str, *, resource: str) -> None:
        if expected != actual:
            raise ValueError(
                f"Cross-tenant mismatch on {resource}: expected {expected}, got {actual}"
            )

    def register_student(
        self,
        *,
        tenant_id: str,
        phone: str,
        student_id: str | None = None,
        name: str | None = None,
        school: str | None = None,
        district: str | None = None,
        consent: bool = False,
    ) -> str:
        """Update student profile fields for onboarding."""
        row = self.db.get_student(tenant_id=tenant_id, phone=phone)
        if row is None:
            return json.dumps({"ok": False, "error": f"No student for phone {phone}"})

        if student_id:
            self._assert_tenant(tenant_id, row["tenant_id"], resource="student")
            if row["id"] != student_id:
                return json.dumps({"ok": False, "error": "student_id does not match phone"})

        updated = self.db.update_student(
            tenant_id=tenant_id,
            student_id=row["id"],
            name=name,
            school=school,
            district=district,
            consent=consent,
        )
        return json.dumps({"ok": True, "student": updated})

    def get_student(self, *, tenant_id: str, phone: str) -> str:
        row = self.db.get_student(tenant_id=tenant_id, phone=phone)
        if row is None:
            return json.dumps({"ok": True, "student": None, "enrollments": []})

        enrollments = self.db.list_enrollments(tenant_id=tenant_id, student_id=row["id"])
        pending = self.db.get_pending_enrollment(tenant_id=tenant_id, student_id=row["id"])
        open_escalation = None
        if pending:
            open_escalation = self.db.get_open_enrollment_escalation(
                tenant_id=tenant_id,
                enrollment_id=pending["id"],
            )
        return json.dumps(
            {
                "ok": True,
                "student": row,
                "enrollments": enrollments,
                "pending_enrollment": pending,
                "open_escalation": open_escalation,
            }
        )

    def list_classes(
        self,
        *,
        tenant_id: str,
        subject: str | None = None,
        grade: str | None = None,
    ) -> str:
        classes = self.db.list_classes(tenant_id=tenant_id, subject=subject, grade=grade)
        return json.dumps({"ok": True, "classes": classes})

    def create_enrollment(
        self,
        *,
        tenant_id: str,
        student_id: str,
        class_id: str,
    ) -> str:
        student = self.db.get_student_by_id(tenant_id=tenant_id, student_id=student_id)
        if student is None:
            return json.dumps({"ok": False, "error": f"Student not found: {student_id}"})

        class_row = self.db.get_class(tenant_id=tenant_id, class_id=class_id)
        if class_row is None:
            return json.dumps({"ok": False, "error": f"Class not found: {class_id}"})

        try:
            self._assert_tenant(tenant_id, student["tenant_id"], resource="student")
            self._assert_tenant(tenant_id, class_row["tenant_id"], resource="class")
        except ValueError as exc:
            return json.dumps({"ok": False, "error": str(exc)})

        if not student.get("consent_at"):
            return json.dumps({"ok": False, "error": "PDPA consent required before enrollment"})

        try:
            enrollment = self.db.create_enrollment(
                tenant_id=tenant_id,
                student_id=student_id,
                class_id=class_id,
                status="pending",
            )
            invoice = self.db.create_invoice_for_class(
                tenant_id=tenant_id,
                student_id=student_id,
                class_row=class_row,
            )
        except Exception as exc:
            logger.warning("create_enrollment failed: {}", exc)
            return json.dumps({"ok": False, "error": str(exc)})

        return json.dumps(
            {
                "ok": True,
                "enrollment": enrollment,
                "class": class_row,
                "invoice": invoice,
                "status": "pending",
            }
        )

    def submit_payment_receipt(
        self,
        *,
        tenant_id: str,
        student_id: str,
        image_ref: str,
    ) -> str:
        """Attach payment receipt to pending enrollment and open staff escalation."""
        student = self.db.get_student_by_id(tenant_id=tenant_id, student_id=student_id)
        if student is None:
            return json.dumps({"ok": False, "error": f"Student not found: {student_id}"})

        pending = self.db.get_pending_enrollment(tenant_id=tenant_id, student_id=student_id)
        if pending is None:
            return json.dumps({"ok": False, "error": "No pending enrollment awaiting payment"})

        class_row = self.db.get_class(tenant_id=tenant_id, class_id=pending["class_id"])
        invoice = self.db.get_latest_invoice_for_student(
            tenant_id=tenant_id,
            student_id=student_id,
        )
        if invoice is None and class_row:
            invoice = self.db.create_invoice_for_class(
                tenant_id=tenant_id,
                student_id=student_id,
                class_row=class_row,
            )
        if invoice is None:
            return json.dumps({"ok": False, "error": "No invoice found for payment receipt"})

        try:
            slip = self.db.create_bank_slip_upload(
                tenant_id=tenant_id,
                invoice_id=invoice["id"],
                image_ref=image_ref,
            )
            escalation = self.db.create_escalation(
                tenant_id=tenant_id,
                student_id=student_id,
                enrollment_id=pending["id"],
                reason_code=ENROLLMENT_PAYMENT_REASON,
            )
        except Exception as exc:
            logger.warning("submit_payment_receipt failed: {}", exc)
            return json.dumps({"ok": False, "error": str(exc)})

        return json.dumps(
            {
                "ok": True,
                "enrollment": pending,
                "invoice": invoice,
                "bank_slip": slip,
                "escalation": escalation,
                "class": class_row,
            }
        )

    def resolve_enrollment_escalation(
        self,
        *,
        tenant_id: str,
        escalation_id: str,
    ) -> str:
        """Staff resolves payment review — activates enrollment."""
        from infrastructure.db.supabase_client import get_supabase_client

        supa = get_supabase_client()
        resp = (
            supa.table("escalations")
            .select("id, tenant_id, student_id, enrollment_id, status, reason_code")
            .eq("tenant_id", tenant_id)
            .eq("id", escalation_id)
            .limit(1)
            .execute()
        )
        rows = resp.data or []
        if not rows:
            return json.dumps({"ok": False, "error": f"Escalation not found: {escalation_id}"})
        escalation = rows[0]

        if escalation.get("status") == "resolved":
            return json.dumps({"ok": False, "error": "Escalation already resolved"})

        enrollment_id = escalation.get("enrollment_id")
        if not enrollment_id:
            return json.dumps({"ok": False, "error": "Escalation has no linked enrollment"})

        enrollment = self.db.get_enrollment(tenant_id=tenant_id, enrollment_id=enrollment_id)
        if enrollment is None:
            return json.dumps({"ok": False, "error": f"Enrollment not found: {enrollment_id}"})

        student = self.db.get_student_by_id(
            tenant_id=tenant_id,
            student_id=enrollment["student_id"],
        )
        class_row = self.db.get_class(tenant_id=tenant_id, class_id=enrollment["class_id"])
        invoice = self.db.get_latest_invoice_for_student(
            tenant_id=tenant_id,
            student_id=enrollment["student_id"],
        )

        try:
            self.db.resolve_escalation(tenant_id=tenant_id, escalation_id=escalation_id)
            activated = self.db.activate_enrollment(
                tenant_id=tenant_id,
                enrollment_id=enrollment_id,
            )
            if invoice and invoice.get("status") != "paid":
                self.db.mark_invoice_paid(tenant_id=tenant_id, invoice_id=invoice["id"])
        except Exception as exc:
            logger.warning("resolve_enrollment_escalation failed: {}", exc)
            return json.dumps({"ok": False, "error": str(exc)})

        return json.dumps(
            {
                "ok": True,
                "escalation_id": escalation_id,
                "enrollment": activated,
                "student": student,
                "class": class_row,
                "phone": (student or {}).get("phone"),
            }
        )
