"""Escalation agent tests."""

from __future__ import annotations

import pytest
from langchain_core.messages import HumanMessage

from agents.nodes.escalation_agent import EscalationAgent


class FakeCrm:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def create_escalation(self, **kwargs) -> dict:
        self.calls.append(kwargs)
        return {"ok": True, "escalation": {"id": "esc-tutor-1"}}


@pytest.mark.asyncio
async def test_escalation_agent_creates_talk_to_tutor_ticket():
    crm = FakeCrm()
    agent = EscalationAgent(crm=crm)
    state = {
        "tenant_id": "tenant-a",
        "tenant_name": "Demo Physics",
        "student_id": "stu-1",
        "messages": [HumanMessage(content="Can I speak to the tutor please?")],
    }
    result = await agent.run(state)
    assert crm.calls
    assert crm.calls[0]["reason_code"] == "talk_to_tutor"
    assert "notified" in result.answer.lower() or "tutor" in result.answer.lower()
