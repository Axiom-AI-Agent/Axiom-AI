"""CRM business logic — called by MCP server only (Week 13 pattern)."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger

from domain.escalation_reasons import (
    ENROLLMENT_PAYMENT_REASON,
    PAYMENT_RECEIPT,
    is_payment_reason,
)
from services.admissions.admissions_db_client import AdmissionsDbClient


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
        selected_class_id: str | None = None,
        clear_selected_class: bool = False,
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
            selected_class_id=selected_class_id,
            clear_selected_class=clear_selected_class,
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

    def commit_onboarding(
        self,
        *,
        tenant_id: str,
        phone: str,
        name: str,
        school: str,
        district: str,
        class_id: str,
    ) -> str:
        """Atomic post-confirmation write: student profile + pending enrollment."""
        if self.db.get_student(tenant_id=tenant_id, phone=phone):
            return json.dumps({"ok": False, "error": "A student profile already exists for this number"})

        class_row = self.db.get_class(tenant_id=tenant_id, class_id=class_id)
        if class_row is None:
            return json.dumps({"ok": False, "error": f"Class not found: {class_id}"})

        student: dict | None = None
        try:
            student = self.db.create_student(
                tenant_id=tenant_id,
                phone=phone,
                name=name,
                school=school,
                district=district,
                consent=True,
            )
            enrollment = self.db.create_enrollment(
                tenant_id=tenant_id,
                student_id=student["id"],
                class_id=class_id,
                status="pending",
            )
            invoice = self.db.create_invoice_for_class(
                tenant_id=tenant_id,
                student_id=student["id"],
                class_row=class_row,
            )
        except Exception as exc:
            logger.warning("commit_onboarding failed: {}", exc)
            if student:
                try:
                    self.db.delete_student(tenant_id=tenant_id, student_id=student["id"])
                except Exception as rollback_exc:
                    logger.warning("commit_onboarding rollback failed: {}", rollback_exc)
            return json.dumps({"ok": False, "error": str(exc)})

        return json.dumps(
            {
                "ok": True,
                "student": student,
                "enrollment": enrollment,
                "class": class_row,
                "invoice": invoice,
                "status": "pending",
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

    def get_tenant_info(self, *, tenant_id: str) -> str:
        tenant = self.db.get_tenant(tenant_id=tenant_id)
        if tenant is None:
            return json.dumps({"ok": False, "error": f"Tenant not found: {tenant_id}"})
        classes = self.db.list_classes(tenant_id=tenant_id)
        staff = self.db.list_staff(tenant_id=tenant_id)
        return json.dumps(
            {
                "ok": True,
                "tenant": tenant,
                "classes": classes,
                "staff": staff,
            }
        )

    def get_class_details(
        self,
        *,
        tenant_id: str,
        class_id: str | None = None,
        class_name: str | None = None,
        subject: str | None = None,
        grade: str | None = None,
    ) -> str:
        if class_id:
            row = self.db.get_class(tenant_id=tenant_id, class_id=class_id)
            if row is None:
                return json.dumps({"ok": False, "error": f"Class not found: {class_id}"})
            return json.dumps({"ok": True, "classes": [row]})

        classes = self.db.list_classes(
            tenant_id=tenant_id,
            subject=subject,
            grade=grade,
        )
        if class_name:
            lowered = class_name.lower()
            classes = [
                c
                for c in classes
                if lowered in str(c.get("name") or "").lower()
                or str(c.get("name") or "").lower() in lowered
            ]
        return json.dumps({"ok": True, "classes": classes})

    def list_staff(self, *, tenant_id: str, role: str | None = None) -> str:
        staff = self.db.list_staff(tenant_id=tenant_id, role=role)
        return json.dumps({"ok": True, "staff": staff})

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

    def create_escalation(
        self,
        *,
        tenant_id: str,
        student_id: str,
        reason_code: str,
        media_url: str | None = None,
        student_message: str | None = None,
        enrollment_id: str | None = None,
    ) -> str:
        """Open (or return existing) escalation for dashboard inbox."""
        student = self.db.get_student_by_id(tenant_id=tenant_id, student_id=student_id)
        if student is None:
            return json.dumps({"ok": False, "error": f"Student not found: {student_id}"})

        try:
            self._assert_tenant(tenant_id, student["tenant_id"], resource="student")
        except ValueError as exc:
            return json.dumps({"ok": False, "error": str(exc)})

        pending = self.db.get_pending_enrollment(tenant_id=tenant_id, student_id=student_id)
        linked_enrollment = enrollment_id or (pending["id"] if pending else None)

        if is_payment_reason(reason_code) and pending is None and linked_enrollment is None:
            return json.dumps(
                {
                    "ok": False,
                    "error": "No pending enrollment — complete admissions before submitting payment",
                }
            )

        try:
            escalation = self.db.create_escalation(
                tenant_id=tenant_id,
                student_id=student_id,
                reason_code=reason_code,
                enrollment_id=linked_enrollment if is_payment_reason(reason_code) else enrollment_id,
                media_url=media_url,
                student_message=student_message,
            )
        except Exception as exc:
            logger.warning("create_escalation failed: {}", exc)
            return json.dumps({"ok": False, "error": str(exc)})

        return json.dumps(
            {
                "ok": True,
                "escalation": escalation,
                "enrollment": pending,
            }
        )

    def submit_payment_receipt(
        self,
        *,
        tenant_id: str,
        student_id: str,
        image_ref: str,
    ) -> str:
        """Legacy alias — creates payment_receipt escalation without bank_slip storage."""
        return self.create_escalation(
            tenant_id=tenant_id,
            student_id=student_id,
            reason_code=PAYMENT_RECEIPT,
            media_url=image_ref,
        )

    def resolve_escalation(
        self,
        *,
        tenant_id: str,
        escalation_id: str,
        reviewed_by: str | None = None,
    ) -> str:
        """Reason-aware resolve: payment → activate enrollment; tutor → close only."""
        escalation = self.db.get_escalation(tenant_id=tenant_id, escalation_id=escalation_id)
        if escalation is None:
            return json.dumps({"ok": False, "error": f"Escalation not found: {escalation_id}"})

        if escalation.get("status") == "resolved":
            return json.dumps({"ok": False, "error": "Escalation already resolved"})

        reason = escalation.get("reason_code")
        if is_payment_reason(reason):
            return self.resolve_payment_escalation(
                tenant_id=tenant_id,
                escalation_id=escalation_id,
                reviewed_by=reviewed_by,
            )

        student = self.db.get_student_by_id(
            tenant_id=tenant_id,
            student_id=escalation["student_id"],
        )
        try:
            self.db.resolve_escalation(
                tenant_id=tenant_id,
                escalation_id=escalation_id,
                resolution="closed",
                reviewed_by=reviewed_by,
            )
        except Exception as exc:
            logger.warning("resolve_escalation failed: {}", exc)
            return json.dumps({"ok": False, "error": str(exc)})

        return json.dumps(
            {
                "ok": True,
                "escalation_id": escalation_id,
                "reason_code": reason,
                "student": student,
                "phone": (student or {}).get("phone"),
                "enrollment": None,
            }
        )

    def resolve_payment_escalation(
        self,
        *,
        tenant_id: str,
        escalation_id: str,
        reviewed_by: str | None = None,
    ) -> str:
        """Staff approves payment — activates pending enrollment."""
        escalation = self.db.get_escalation(tenant_id=tenant_id, escalation_id=escalation_id)
        if escalation is None:
            return json.dumps({"ok": False, "error": f"Escalation not found: {escalation_id}"})

        if escalation.get("status") == "resolved":
            return json.dumps({"ok": False, "error": "Escalation already resolved"})

        enrollment_id = escalation.get("enrollment_id")
        if not enrollment_id:
            return json.dumps({"ok": False, "error": "Payment escalation has no linked enrollment"})

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
            self.db.resolve_escalation(
                tenant_id=tenant_id,
                escalation_id=escalation_id,
                resolution="approved",
                reviewed_by=reviewed_by,
            )
            activated = self.db.activate_enrollment(
                tenant_id=tenant_id,
                enrollment_id=enrollment_id,
            )
            if invoice and invoice.get("status") != "paid":
                self.db.mark_invoice_paid(tenant_id=tenant_id, invoice_id=invoice["id"])
        except Exception as exc:
            logger.warning("resolve_payment_escalation failed: {}", exc)
            return json.dumps({"ok": False, "error": str(exc)})

        return json.dumps(
            {
                "ok": True,
                "escalation_id": escalation_id,
                "reason_code": escalation.get("reason_code"),
                "enrollment": activated,
                "student": student,
                "class": class_row,
                "phone": (student or {}).get("phone"),
            }
        )

    def reject_payment_escalation(
        self,
        *,
        tenant_id: str,
        escalation_id: str,
        reviewed_by: str | None = None,
    ) -> str:
        """Staff rejects payment — closes escalation without activating enrollment."""
        escalation = self.db.get_escalation(tenant_id=tenant_id, escalation_id=escalation_id)
        if escalation is None:
            return json.dumps({"ok": False, "error": f"Escalation not found: {escalation_id}"})

        if escalation.get("status") == "resolved":
            return json.dumps({"ok": False, "error": "Escalation already resolved"})

        if not is_payment_reason(escalation.get("reason_code")):
            return json.dumps({"ok": False, "error": "Only payment escalations can be rejected"})

        student = self.db.get_student_by_id(
            tenant_id=tenant_id,
            student_id=escalation["student_id"],
        )
        try:
            self.db.close_escalation(
                tenant_id=tenant_id,
                escalation_id=escalation_id,
                resolution="rejected",
                reviewed_by=reviewed_by,
            )
        except Exception as exc:
            logger.warning("reject_payment_escalation failed: {}", exc)
            return json.dumps({"ok": False, "error": str(exc)})

        return json.dumps(
            {
                "ok": True,
                "escalation_id": escalation_id,
                "reason_code": escalation.get("reason_code"),
                "resolution": "rejected",
                "student": student,
                "phone": (student or {}).get("phone"),
                "enrollment": None,
            }
        )

    def resolve_enrollment_escalation(
        self,
        *,
        tenant_id: str,
        escalation_id: str,
    ) -> str:
        """Backward-compatible alias for payment resolve."""
        return self.resolve_payment_escalation(
            tenant_id=tenant_id,
            escalation_id=escalation_id,
        )
