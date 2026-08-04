"""Admissions agent node tests (in-process CRM, no MCP subprocess)."""

from __future__ import annotations

import pytest
from langchain_core.messages import HumanMessage

from agents.nodes.admissions_agent import AdmissionsAgent


class FakeCrmClient:
    def __init__(self) -> None:
        self.student = {
            "id": "stu-new",
            "tenant_id": "tenant-demo-physics",
            "phone": "94771111001",
            "name": None,
            "school": None,
            "district": None,
            "consent_at": None,
        }
        self.enrollments: list = []
        self.pending_enrollment = None
        self.open_escalation = None
        self.classes = [
            {
                "id": "class-physics-al-2026",
                "subject": "Physics",
                "grade": "A/L",
                "name": "A/L Physics 2026",
                "fee_amount": 5000,
            }
        ]

    async def get_student(self, *, tenant_id: str, phone: str) -> dict:
        return {
            "ok": True,
            "student": self.student,
            "enrollments": self.enrollments,
            "pending_enrollment": self.pending_enrollment,
            "open_escalation": self.open_escalation,
        }

    async def list_classes(self, *, tenant_id: str, **kwargs) -> list:
        return self.classes

    async def register_student(self, **kwargs) -> dict:
        for key in ("name", "school", "district"):
            if kwargs.get(key):
                self.student[key] = kwargs[key]
        if kwargs.get("consent"):
            self.student["consent_at"] = "2026-01-01T00:00:00+00:00"
        return {"ok": True, "student": self.student}

    async def create_enrollment(self, **kwargs) -> dict:
        self.pending_enrollment = {
            "id": "enr-1",
            "class_id": kwargs["class_id"],
            "status": "pending",
        }
        return {
            "ok": True,
            "enrollment": self.pending_enrollment,
            "class": self.classes[0],
            "status": "pending",
        }

    async def submit_payment_receipt(self, **kwargs) -> dict:
        self.open_escalation = {"id": "esc-1", "status": "open"}
        return {
            "ok": True,
            "escalation": self.open_escalation,
            "enrollment": self.pending_enrollment,
        }


@pytest.mark.asyncio
async def test_admissions_agent_prompts_for_name_on_first_turn():
    crm = FakeCrmClient()
    agent = AdmissionsAgent(crm=crm)
    state = {
        "tenant_id": "tenant-demo-physics",
        "tenant_name": "Demo Physics Academy",
        "user_id": "stu-new",
        "phone": "94771111001",
        "messages": [HumanMessage(content="I want to join A/L Physics")],
    }
    result = await agent.run(state)
    assert "name" in result.answer.lower()


@pytest.mark.asyncio
async def test_admissions_agent_asks_consent_before_enrollment():
    crm = FakeCrmClient()
    crm.student.update(
        {
            "name": "Kavindu Fernando",
            "school": "Royal College Colombo",
            "district": "Colombo",
        }
    )
    agent = AdmissionsAgent(crm=crm)
    state = {
        "tenant_id": "tenant-demo-physics",
        "tenant_name": "Demo Physics Academy",
        "user_id": "stu-new",
        "phone": "94771111001",
        "messages": [HumanMessage(content="A/L Physics")],
    }
    result = await agent.run(state)
    assert "consent" in result.answer.lower() or "data policy" in result.answer.lower()


@pytest.mark.asyncio
async def test_admissions_agent_requests_payment_after_consent():
    crm = FakeCrmClient()
    crm.student.update(
        {
            "name": "Kavindu Fernando",
            "school": "Royal College Colombo",
            "district": "Colombo",
            "consent_at": "2026-01-01T00:00:00+00:00",
        }
    )
    agent = AdmissionsAgent(crm=crm)
    state = {
        "tenant_id": "tenant-demo-physics",
        "tenant_name": "Demo Physics Academy",
        "user_id": "stu-new",
        "phone": "94771111001",
        "messages": [HumanMessage(content="YES")],
    }
    result = await agent.run(state)
    assert "payment" in result.answer.lower() or "receipt" in result.answer.lower()
    assert "successfully enrolled" not in result.answer.lower()


@pytest.mark.asyncio
async def test_admissions_agent_accepts_payment_receipt():
    crm = FakeCrmClient()
    crm.student.update(
        {
            "name": "Kavindu Fernando",
            "school": "Royal College",
            "district": "Colombo",
            "consent_at": "2026-01-01T00:00:00+00:00",
        }
    )
    crm.pending_enrollment = {
        "id": "enr-1",
        "class_id": "class-physics-al-2026",
        "status": "pending",
    }
    agent = AdmissionsAgent(crm=crm)
    state = {
        "tenant_id": "tenant-demo-physics",
        "tenant_name": "Demo Physics Academy",
        "user_id": "stu-new",
        "phone": "94771111001",
        "media_url": "https://example.com/receipt.jpg",
        "messages": [HumanMessage(content="")],
    }
    result = await agent.run(state)
    assert "received" in result.answer.lower()
    assert "review" in result.answer.lower()
