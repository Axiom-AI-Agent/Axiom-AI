"""
Resource agent node tests
(direct tool clients, no MCP).
"""

from __future__ import annotations

from typing import Any

import pytest
from langchain_core.messages import (
    HumanMessage,
)

from agents.nodes.resource_agent import (
    ResourceAgent,
)


class FakeDrive:
    async def drive_search(
        self,
        *,
        tenant_id: str,
        query: str,
        folder: str | None = "papers",
    ) -> dict[str, Any]:
        return {
            "ok": True,
            "files": [
                {
                    "name":
                        (
                            "2024-model-paper-"
                            "physics.pdf"
                        ),
                    "link":
                        (
                            "https://drive."
                            "example/paper.pdf"
                        ),
                    "folder":
                        (
                            folder
                            or "papers"
                        ),
                }
            ],
        }


class FakeRag:
    async def kb_search(
        self,
        *,
        tenant_id: str,
        query: str,
        class_ids: list[str]
        | None = None,
    ) -> dict[str, Any]:
        return {
            "ok": True,
            "answer":
                (
                    "Velocity is the rate "
                    "of change of displacement."
                ),
            "citations": [
                {
                    "title":
                        (
                            "Lesson 5 — "
                            "Velocity"
                        ),
                    "lesson":
                        "5",
                    "score":
                        0.88,
                }
            ],
            "num_docs":
                1,
        }


class FakeLowConfidenceRag:
    async def kb_search(
        self,
        *,
        tenant_id: str,
        query: str,
        class_ids: list[str]
        | None = None,
    ) -> dict[str, Any]:
        return {
            "ok": True,
            "answer": "",
            "citations": [
                {
                    "title":
                        "Weak match",
                    "score":
                        0.38,
                }
            ],
            "num_docs":
                1,
        }


@pytest.mark.asyncio
async def test_resource_agent_drive_path():
    agent = ResourceAgent(
        drive=FakeDrive(),
        rag=FakeRag(),
    )

    state = {
        "tenant_id":
            "tenant-demo-physics",
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
                    "Can I get last week's "
                    "physics paper?"
                )
            )
        ],
    }

    result = (
        await agent.run(
            state
        )
    )

    assert (
        result.sub_path
        == "drive"
    )

    assert (
        "2024-model-paper"
        in result.answer
        or
        "drive.example"
        in result.answer
    )


@pytest.mark.asyncio
async def test_resource_agent_rag_path():
    agent = ResourceAgent(
        drive=FakeDrive(),
        rag=FakeRag(),
    )

    state = {
        "tenant_id":
            "tenant-demo-physics",
        "is_enrolled":
            True,
        "enrolled_class_ids": [
            "class-physics-al-2026",
        ],
        "messages": [
            HumanMessage(
                content=(
                    "Explain velocity "
                    "from lesson 5"
                )
            )
        ],
    }

    result = (
        await agent.run(
            state
        )
    )

    assert (
        result.sub_path
        == "rag"
    )

    assert (
        "velocity"
        in result.answer.lower()
    )


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

    result = (
        await agent.run(
            state
        )
    )

    assert (
        result.sub_path
        == "rag"
    )

    assert (
        (
            "couldn't find enough "
            "reliable information"
        )
        in result.answer.lower()
    )

    assert (
        (
            "would you like me "
            "to send this question"
        )
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