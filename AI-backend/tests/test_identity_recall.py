"""Identity recall and resource enrollment gate tests."""

from __future__ import annotations

import pytest
from langchain_core.messages import HumanMessage

from agents.nodes.resource_agent import ResourceAgent
from services.identity.context import IdentityContext
from services.identity.recall_context import build_recall_context, format_student_profile


class FakeMemoryTool:
    def recall_turns(self, **kwargs) -> str:
        return "User: hi\nAssistant: Hello!"


class FakeDrive:
    async def drive_search(self, *, tenant_id: str, query: str, folder: str | None = "papers"):
        return {"ok": True, "files": [{"name": "paper.pdf", "link": "https://example.com"}]}


class FakeRag:
    async def kb_search(self, *, tenant_id: str, query: str):
        return {"ok": True, "answer": "Velocity is speed with direction.", "citations": []}


def test_format_student_profile_enrolled():
    ctx = IdentityContext(
        tenant_id="tenant-demo-physics",
        tenant_slug="demo-physics",
        tenant_name="Demo Physics Academy",
        phone="94771234567",
        session_id="tenant-demo-physics:94771234567",
        student_id="stu-physics-001",
        student_exists=True,
        student_name="Amaya Perera",
        is_enrolled=True,
        enrollment_status="active",
        active_class_names=("A/L Physics 2026",),
    )
    profile = format_student_profile(ctx)
    assert "Amaya Perera" in profile
    assert "A/L Physics 2026" in profile
    assert "Enrolled" in profile


def test_format_student_profile_unknown_visitor():
    ctx = IdentityContext(
        tenant_id="tenant-demo-physics",
        tenant_slug="demo-physics",
        tenant_name="Demo Physics Academy",
        phone="94770999999",
        session_id="tenant-demo-physics:94770999999",
    )
    profile = format_student_profile(ctx)
    assert "Unknown visitor" in profile
    assert "94770999999" in profile


def test_build_recall_context_includes_profile_before_st():
    ctx = IdentityContext(
        tenant_id="tenant-demo-physics",
        tenant_slug="demo-physics",
        tenant_name="Demo Physics Academy",
        phone="94771234567",
        session_id="tenant-demo-physics:94771234567",
        student_id="stu-physics-001",
        student_exists=True,
        student_name="Amaya Perera",
        is_enrolled=True,
        enrollment_status="active",
        active_class_names=("A/L Physics 2026",),
    )
    full_context, profile = build_recall_context(ctx, FakeMemoryTool())
    assert full_context.index("[STUDENT PROFILE]") < full_context.index("[RECENT CONVERSATION]")
    assert "Amaya Perera" in full_context
    assert profile.startswith("[STUDENT PROFILE]")


@pytest.mark.asyncio
async def test_resource_agent_blocks_non_enrolled_drive():
    agent = ResourceAgent(drive=FakeDrive(), rag=FakeRag())
    state = {
        "tenant_id": "tenant-demo-physics",
        "tenant_name": "Demo Physics",
        "is_enrolled": False,
        "messages": [HumanMessage(content="Send me the 2023 physics past paper")],
    }
    result = await agent.run(state)
    assert "enrolled students only" in result.answer.lower()
    assert "2023" not in result.answer


@pytest.mark.asyncio
async def test_resource_agent_blocks_non_enrolled_rag():
    agent = ResourceAgent(drive=FakeDrive(), rag=FakeRag())
    state = {
        "tenant_id": "tenant-demo-physics",
        "is_enrolled": False,
        "messages": [HumanMessage(content="Explain velocity from tutor notes")],
    }
    result = await agent.run(state)
    assert result.sub_path == "rag"
    assert "enrolled" in result.answer.lower()


@pytest.mark.asyncio
async def test_resource_agent_allows_pending_enrollment():
    agent = ResourceAgent(drive=FakeDrive(), rag=FakeRag())
    state = {
        "tenant_id": "tenant-demo-physics",
        "is_enrolled": True,
        "messages": [HumanMessage(content="Explain velocity from tutor notes")],
    }
    result = await agent.run(state)
    assert "velocity" in result.answer.lower()
