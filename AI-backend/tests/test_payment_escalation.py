"""CRM escalation create/resolve tests for Phase 5 flows."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from agents.tools.crm_tool import CrmTool
from domain.escalation_reasons import PAYMENT_RECEIPT, TALK_TO_TUTOR


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.get_student_by_id.return_value = {
        "id": "stu-1",
        "tenant_id": "tenant-a",
        "phone": "94770000001",
    }
    db.get_pending_enrollment.return_value = {
        "id": "enr-1",
        "class_id": "class-1",
        "status": "pending",
    }
    db.create_escalation.return_value = {
        "id": "esc-1",
        "reason_code": PAYMENT_RECEIPT,
        "status": "open",
    }
    db.get_escalation.return_value = {
        "id": "esc-1",
        "tenant_id": "tenant-a",
        "student_id": "stu-1",
        "enrollment_id": "enr-1",
        "reason_code": PAYMENT_RECEIPT,
        "status": "open",
    }
    db.get_enrollment.return_value = {
        "id": "enr-1",
        "student_id": "stu-1",
        "class_id": "class-1",
        "status": "pending",
    }
    db.get_tenant.return_value = {"id": "tenant-a", "payments_enabled": True}
    db.get_class.return_value = {"id": "class-1", "subject": "Physics"}
    db.get_latest_invoice_for_student.return_value = {"id": "inv-1", "status": "pending"}
    db.resolve_escalation.return_value = {"id": "esc-1", "status": "resolved"}
    db.activate_enrollment.return_value = {"id": "enr-1", "status": "active"}
    db.mark_invoice_paid.return_value = {"id": "inv-1", "status": "paid"}
    return db


def test_create_payment_escalation(mock_db):
    tool = CrmTool(db=mock_db)
    raw = tool.create_escalation(
        tenant_id="tenant-a",
        student_id="stu-1",
        reason_code=PAYMENT_RECEIPT,
        media_url="https://example.com/slip.jpg",
        student_message="Here is my receipt",
    )
    payload = json.loads(raw)
    assert payload["ok"] is True
    mock_db.create_escalation.assert_called_once()
    call_kwargs = mock_db.create_escalation.call_args.kwargs
    assert call_kwargs["reason_code"] == PAYMENT_RECEIPT
    assert call_kwargs["media_url"] == "https://example.com/slip.jpg"
    assert call_kwargs["enrollment_id"] == "enr-1"


def test_create_payment_escalation_blocked_when_payments_disabled(mock_db):
    mock_db.get_tenant.return_value = {"id": "tenant-a", "payments_enabled": False}
    tool = CrmTool(db=mock_db)
    raw = tool.create_escalation(
        tenant_id="tenant-a",
        student_id="stu-1",
        reason_code=PAYMENT_RECEIPT,
        media_url="https://example.com/slip.jpg",
    )
    payload = json.loads(raw)
    assert payload["ok"] is False
    assert "disabled" in payload["error"].lower()
    mock_db.create_escalation.assert_not_called()


def test_create_talk_to_tutor_escalation(mock_db):
    mock_db.get_pending_enrollment.return_value = None
    tool = CrmTool(db=mock_db)
    raw = tool.create_escalation(
        tenant_id="tenant-a",
        student_id="stu-1",
        reason_code=TALK_TO_TUTOR,
        student_message="Need to talk to sir",
    )
    payload = json.loads(raw)
    assert payload["ok"] is True
    call_kwargs = mock_db.create_escalation.call_args.kwargs
    assert call_kwargs["reason_code"] == TALK_TO_TUTOR
    assert call_kwargs.get("enrollment_id") is None


def test_resolve_payment_escalation_activates_enrollment(mock_db):
    tool = CrmTool(db=mock_db)
    raw = tool.resolve_escalation(tenant_id="tenant-a", escalation_id="esc-1")
    payload = json.loads(raw)
    assert payload["ok"] is True
    assert payload["enrollment"]["status"] == "active"
    mock_db.activate_enrollment.assert_called_once()


def test_resolve_talk_to_tutor_does_not_activate_enrollment(mock_db):
    mock_db.get_escalation.return_value = {
        "id": "esc-2",
        "tenant_id": "tenant-a",
        "student_id": "stu-1",
        "reason_code": TALK_TO_TUTOR,
        "status": "open",
    }
    tool = CrmTool(db=mock_db)
    raw = tool.resolve_escalation(tenant_id="tenant-a", escalation_id="esc-2")
    payload = json.loads(raw)
    assert payload["ok"] is True
    assert payload["enrollment"] is None
    mock_db.activate_enrollment.assert_not_called()


def test_reject_payment_escalation(mock_db):
    mock_db.get_escalation.return_value = {
        "id": "esc-1",
        "tenant_id": "tenant-a",
        "student_id": "stu-1",
        "reason_code": PAYMENT_RECEIPT,
        "status": "open",
    }
    mock_db.close_escalation.return_value = {"id": "esc-1", "status": "resolved"}
    tool = CrmTool(db=mock_db)
    raw = tool.reject_payment_escalation(tenant_id="tenant-a", escalation_id="esc-1")
    payload = json.loads(raw)
    assert payload["ok"] is True
    assert payload["resolution"] == "rejected"
    mock_db.activate_enrollment.assert_not_called()
