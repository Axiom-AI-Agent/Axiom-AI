"""CRM tool and tenant isolation tests."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from agents.tools.crm_tool import CrmTool


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.get_student.return_value = {
        "id": "stu-1",
        "tenant_id": "tenant-a",
        "phone": "94770000001",
        "name": None,
        "school": None,
        "district": None,
        "consent_at": None,
    }
    db.get_student_by_id.return_value = {
        "id": "stu-1",
        "tenant_id": "tenant-a",
        "phone": "94770000001",
        "consent_at": "2026-01-01T00:00:00+00:00",
    }
    db.get_class.return_value = {
        "id": "class-1",
        "tenant_id": "tenant-a",
        "subject": "Physics",
        "grade": "A/L",
    }
    db.update_student.return_value = {
        "id": "stu-1",
        "tenant_id": "tenant-a",
        "name": "Amaya",
    }
    db.create_enrollment.return_value = {
        "id": "enr-1",
        "tenant_id": "tenant-a",
        "student_id": "stu-1",
        "class_id": "class-1",
        "status": "pending",
    }
    db.list_enrollments.return_value = []
    db.list_classes.return_value = [{"id": "class-1", "subject": "Physics"}]
    db.get_pending_enrollment.return_value = None
    db.get_open_enrollment_escalation.return_value = None
    return db


def test_register_student_updates_profile(mock_db):
    tool = CrmTool(db=mock_db)
    raw = tool.register_student(
        tenant_id="tenant-a",
        phone="94770000001",
        name="Amaya Perera",
    )
    payload = json.loads(raw)
    assert payload["ok"] is True
    mock_db.update_student.assert_called_once()


def test_create_enrollment_requires_consent(mock_db):
    mock_db.get_student_by_id.return_value = {
        "id": "stu-1",
        "tenant_id": "tenant-a",
        "consent_at": None,
    }
    tool = CrmTool(db=mock_db)
    raw = tool.create_enrollment(
        tenant_id="tenant-a",
        student_id="stu-1",
        class_id="class-1",
    )
    payload = json.loads(raw)
    assert payload["ok"] is False
    assert "consent" in payload["error"].lower()


def test_create_enrollment_rejects_cross_tenant_class(mock_db):
    mock_db.get_class.return_value = {
        "id": "class-1",
        "tenant_id": "tenant-b",
        "subject": "Physics",
    }
    tool = CrmTool(db=mock_db)
    raw = tool.create_enrollment(
        tenant_id="tenant-a",
        student_id="stu-1",
        class_id="class-1",
    )
    payload = json.loads(raw)
    assert payload["ok"] is False
    assert "mismatch" in payload["error"].lower()


def test_list_classes_scoped_to_tenant(mock_db):
    tool = CrmTool(db=mock_db)
    raw = tool.list_classes(tenant_id="tenant-a")
    payload = json.loads(raw)
    assert payload["ok"] is True
    mock_db.list_classes.assert_called_once_with(
        tenant_id="tenant-a",
        subject=None,
        grade=None,
    )


def test_get_tenant_info_returns_profile(mock_db):
    mock_db.get_tenant.return_value = {
        "id": "tenant-a",
        "name": "Demo Physics Academy",
        "whatsapp_number": "whatsapp:+14155238886",
    }
    mock_db.list_staff.return_value = [{"id": "s1", "name": "Demo Physics Admin", "role": "admin"}]
    tool = CrmTool(db=mock_db)
    raw = tool.get_tenant_info(tenant_id="tenant-a")
    payload = json.loads(raw)
    assert payload["ok"] is True
    assert payload["tenant"]["name"] == "Demo Physics Academy"
    assert len(payload["staff"]) == 1


def test_commit_onboarding_completes_unenrolled_profile(mock_db):
    mock_db.create_invoice_for_class.return_value = {"id": "inv-1", "status": "pending"}
    tool = CrmTool(db=mock_db)
    raw = tool.commit_onboarding(
        tenant_id="tenant-a",
        phone="94770000001",
        name="Amaya Perera",
        school="Royal College",
        district="Colombo",
        class_id="class-1",
    )
    payload = json.loads(raw)
    assert payload["ok"] is True
    mock_db.update_student.assert_called_once()
    mock_db.create_student.assert_not_called()
    mock_db.create_enrollment.assert_called_once()


def test_commit_onboarding_rejects_already_enrolled(mock_db):
    mock_db.list_enrollments.return_value = [
        {"id": "enr-1", "status": "pending", "class_id": "class-1"}
    ]
    tool = CrmTool(db=mock_db)
    raw = tool.commit_onboarding(
        tenant_id="tenant-a",
        phone="94770000001",
        name="Amaya Perera",
        school="Royal College",
        district="Colombo",
        class_id="class-1",
    )
    payload = json.loads(raw)
    assert payload["ok"] is False
    assert "already exists" in payload["error"].lower()
    mock_db.create_enrollment.assert_not_called()


def test_list_staff_scoped_to_tenant(mock_db):
    mock_db.list_staff.return_value = [{"id": "s1", "name": "Demo Physics Admin", "role": "admin"}]
    tool = CrmTool(db=mock_db)
    raw = tool.list_staff(tenant_id="tenant-a")
    payload = json.loads(raw)
    assert payload["ok"] is True
    mock_db.list_staff.assert_called_once_with(tenant_id="tenant-a", role=None)


def test_list_field_definitions_scoped_to_tenant(mock_db):
    mock_db.list_field_definitions.return_value = [
        {
            "field_key": "school",
            "label": "School",
            "field_type": "text",
            "required": True,
            "sort_order": 0,
        }
    ]
    tool = CrmTool(db=mock_db)
    raw = tool.list_field_definitions(tenant_id="tenant-a")
    payload = json.loads(raw)
    assert payload["ok"] is True
    assert payload["fields"][0]["field_key"] == "school"
    mock_db.list_field_definitions.assert_called_once_with(tenant_id="tenant-a")


def test_commit_onboarding_writes_extra_fields(mock_db):
    mock_db.create_invoice_for_class.return_value = {"id": "inv-1", "status": "pending"}
    tool = CrmTool(db=mock_db)
    raw = tool.commit_onboarding(
        tenant_id="tenant-a",
        phone="94770000001",
        name="Amaya Perera",
        school="Royal College",
        district="Colombo",
        extra_fields={"parent_contact": "0771234567"},
        class_id="class-1",
    )
    payload = json.loads(raw)
    assert payload["ok"] is True
    kwargs = mock_db.update_student.call_args.kwargs
    assert kwargs["school"] == "Royal College"
    assert kwargs["district"] == "Colombo"
    assert kwargs["extra_fields"]["school"] == "Royal College"
    assert kwargs["extra_fields"]["district"] == "Colombo"
    assert kwargs["extra_fields"]["parent_contact"] == "0771234567"
