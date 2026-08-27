"""Resource agent node tests (direct tool clients, no MCP)."""

from __future__ import annotations

from typing import Any

import pytest
from langchain_core.messages import HumanMessage

from agents.drive_file_pick import DrivePickStore
from agents.nodes.resource_agent import ResourceAgent


class FakeDrive:
    def __init__(self) -> None:
        self.list_calls: list[dict[str, Any]] = []
        self.search_calls: list[dict[str, Any]] = []

    async def drive_search(self, *, tenant_id: str, query: str, folder: str | None = "papers") -> dict[str, Any]:
        self.search_calls.append({"tenant_id": tenant_id, "query": query, "folder": folder})
        return {"ok": True, "files": []}

    async def drive_list(self, *, tenant_id: str, folder: str = "papers") -> dict[str, Any]:
        self.list_calls.append({"tenant_id": tenant_id, "folder": folder})
        return {
            "ok": True,
            "files": [
                {
                    "name": "2024-model-paper-physics.pdf",
                    "link": "https://drive.example/paper.pdf",
                    "folder": folder or "papers",
                },
                {
                    "name": "tute-03-mechanics.pdf",
                    "link": "https://drive.example/tute.pdf",
                    "folder": folder or "papers",
                },
            ],
        }


class FakeRag:
    async def kb_search(
        self,
        *,
        tenant_id: str,
        query: str,
        class_ids: list[str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return {
            "ok": True,
            "answer": "Velocity is the rate of change of displacement.",
            "citations": [{"title": "Lesson 5 — Velocity", "lesson": "5", "score": 0.88}],
            "num_docs": 1,
        }


@pytest.mark.asyncio
async def test_resource_agent_drive_path():
    drive = FakeDrive()
    store = DrivePickStore()
    agent = ResourceAgent(drive=drive, rag=FakeRag(), pick_store=store)
    state = {
        "tenant_id": "tenant-demo-physics",
        "tenant_name": "Demo Physics",
        "session_id": "tenant-demo-physics:stu-1",
        "user_id": "stu-1",
        "is_enrolled": True,
        "enrolled_class_ids": ["class-physics-al-2026"],
        "messages": [HumanMessage(content="Can I get last week's physics paper?")],
    }
    result = await agent.run(state)
    assert result.sub_path == "drive"
    assert drive.list_calls
    assert not drive.search_calls
    assert "1. 2024-model-paper-physics.pdf" in result.answer
    assert "2. tute-03-mechanics.pdf" in result.answer
    assert "https://drive.example/paper.pdf" not in result.answer
    assert "number" in result.answer.lower()
    pending = store.get(
        tenant_id="tenant-demo-physics",
        session_id="tenant-demo-physics:stu-1",
        user_id="stu-1",
    )
    assert pending is not None
    assert len(pending.files) == 2


@pytest.mark.asyncio
async def test_resource_agent_drive_lists_tutes_without_filename_guess():
    drive = FakeDrive()
    agent = ResourceAgent(drive=drive, rag=FakeRag(), pick_store=DrivePickStore())
    result = await agent.run(
        {
            "tenant_id": "tenant-demo-physics",
            "session_id": "sess",
            "user_id": "stu-1",
            "is_enrolled": True,
            "enrolled_class_ids": ["class-physics-al-2026"],
            "messages": [HumanMessage(content="any tutes?")],
        }
    )
    assert result.sub_path == "drive"
    assert drive.list_calls[0]["folder"] == "papers"
    assert not drive.search_calls
    assert "tute-03-mechanics.pdf" in result.answer


@pytest.mark.asyncio
async def test_resource_agent_drive_lists_textbooks_folder():
    drive = FakeDrive()
    agent = ResourceAgent(drive=drive, rag=FakeRag(), pick_store=DrivePickStore())
    result = await agent.run(
        {
            "tenant_id": "tenant-demo-physics",
            "session_id": "sess",
            "user_id": "stu-1",
            "is_enrolled": True,
            "enrolled_class_ids": ["class-physics-al-2026"],
            "messages": [HumanMessage(content="what are the textbooks you have")],
        }
    )
    assert result.sub_path == "drive"
    assert drive.list_calls[0]["folder"] == "textbooks"
    assert not drive.search_calls


@pytest.mark.asyncio
async def test_resource_agent_drive_lists_syllabus_folder():
    drive = FakeDrive()
    agent = ResourceAgent(drive=drive, rag=FakeRag(), pick_store=DrivePickStore())
    result = await agent.run(
        {
            "tenant_id": "tenant-demo-physics",
            "session_id": "sess",
            "user_id": "stu-1",
            "is_enrolled": True,
            "enrolled_class_ids": ["class-physics-al-2026"],
            "messages": [HumanMessage(content="send me the syllabus")],
        }
    )
    assert result.sub_path == "drive"
    assert drive.list_calls[0]["folder"] == "syllabus"


@pytest.mark.asyncio
async def test_resource_agent_rag_path():
    agent = ResourceAgent(drive=FakeDrive(), rag=FakeRag())
    state = {
        "tenant_id": "tenant-demo-physics",
        "is_enrolled": True,
        "enrolled_class_ids": ["class-physics-al-2026"],
        "messages": [HumanMessage(content="Explain velocity from lesson 5")],
    }
    result = await agent.run(state)
    assert result.sub_path == "rag"
    assert "velocity" in result.answer.lower()


@pytest.mark.asyncio
async def test_resource_agent_singlish_explain_uses_rag():
    drive = FakeDrive()
    agent = ResourceAgent(drive=drive, rag=FakeRag())
    result = await agent.run(
        {
            "tenant_id": "tenant-demo-physics",
            "is_enrolled": True,
            "enrolled_class_ids": ["class-physics-al-2026"],
            "language_pref": "en",
            "messages": [
                HumanMessage(content="Mata zener diode aka gena kiyala dennako")
            ],
        }
    )
    assert result.sub_path == "rag"
    assert not drive.list_calls
    assert "velocity" in result.answer.lower()
    assert "Here are the available" not in result.answer


@pytest.mark.asyncio
async def test_resource_agent_singlish_file_request_localizes_list():
    drive = FakeDrive()
    agent = ResourceAgent(drive=drive, rag=FakeRag(), pick_store=DrivePickStore())
    result = await agent.run(
        {
            "tenant_id": "tenant-demo-physics",
            "session_id": "sess",
            "user_id": "stu-1",
            "is_enrolled": True,
            "enrolled_class_ids": ["class-physics-al-2026"],
            "language_pref": "en",
            "messages": [HumanMessage(content="tute eka ewanna")],
        }
    )
    assert result.sub_path == "drive"
    assert "tute-03-mechanics.pdf" in result.answer
    assert "Here are the available" not in result.answer
    assert "reply karanna" in result.answer.lower()


class FakeLowConfidenceRag:
    async def kb_search(
        self,
        *,
        tenant_id: str,
        query: str,
        class_ids: list[str]
        | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return {
            "ok": True,
            "answer": "",
            "citations": [
                {
                    "title":
                        "Weak match",
                    "score": 0.38,
                }
            ],
            "num_docs": 1,
        }


@pytest.mark.asyncio
async def test_resource_agent_asks_before_low_confidence_handoff():
    agent = ResourceAgent(
        drive=FakeDrive(),
        rag=FakeLowConfidenceRag(),
    )

    state = {
        "tenant_id":
            "tenant-demo-physics",
        "student_id":
            "stu-1",
        "user_id":
            "stu-1",
        "tenant_name":
            "Demo Physics",
        "is_enrolled":
            True,
        "enrolled_class_ids": [
            "class-physics-al-2026",
        ],
        "messages": [
            HumanMessage(
                content=(
                    "Explain something "
                    "not in the notes"
                )
            )
        ],
    }

    result = await agent.run(
        state
    )

    assert result.sub_path == "rag"

    assert (
        "couldn't find enough reliable"
        in result.answer.lower()
    )

    assert (
        "would you like me to send"
        in result.answer.lower()
    )

    assert (
        "tutor"
        in result.answer.lower()
    )

    assert (
        "rag_confidence:"
        in result.tool_output
    )

    assert (
        "low=True"
        in result.tool_output
    )
