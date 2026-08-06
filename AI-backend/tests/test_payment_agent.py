"""Payment Check agent tests."""

from __future__ import annotations

import pytest
from langchain_core.messages import HumanMessage

from agents.nodes.payment_agent import PaymentAgent


class FakeCrm:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def create_escalation(self, **kwargs) -> dict:
        self.calls.append(kwargs)
        return {"ok": True, "escalation": {"id": "esc-pay-1", "reason_code": kwargs["reason_code"]}}


@pytest.mark.asyncio
async def test_payment_agent_requires_media():
    crm = FakeCrm()
    agent = PaymentAgent(crm=crm)
    state = {
        "tenant_id": "tenant-a",
        "tenant_name": "Demo Physics",
        "student_id": "stu-1",
        "messages": [HumanMessage(content="I paid my fees")],
    }
    result = await agent.run(state)
    assert "photo" in result.answer.lower() or "receipt" in result.answer.lower()
    assert crm.calls == []


@pytest.mark.asyncio
async def test_payment_agent_creates_escalation_with_media():
    crm = FakeCrm()
    agent = PaymentAgent(crm=crm)
    state = {
        "tenant_id": "tenant-a",
        "tenant_name": "Demo Physics",
        "student_id": "stu-1",
        "media_url": "https://example.com/slip.jpg",
        "messages": [HumanMessage(content="Here is my payment")],
    }
    result = await agent.run(state)
    assert crm.calls
    assert crm.calls[0]["reason_code"] == "payment_receipt"
    assert crm.calls[0]["media_url"] == "https://example.com/slip.jpg"
    assert "verify" in result.answer.lower() or "received" in result.answer.lower()
