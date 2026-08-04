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
