#!/usr/bin/env python3
"""Phase 4 end-to-end smoke — Drive paper link + RAG velocity answer.

Uses mocked Drive by default. Pass --live-rag to hit real Qdrant after ingest.
Real Google Drive MCP: test separately (see docs/DRIVE_INTEGRATION.md).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env", override=True)

os.environ.setdefault("LANGFUSE_ENABLED", "false")

from langchain_core.messages import HumanMessage

from agents.nodes.resource_agent import ResourceAgent
from agents.tools.drive_tool import DriveTool
from agents.tools.rag_tool import RagTool
from services.drive_service.drive_client import MockDriveBackend


def _mock_drive_backend() -> MockDriveBackend:
    return MockDriveBackend(
        {
            "drive-folder-physics-demo": [{"id": "pf", "name": "papers", "link": ""}],
            "pf": [
                {
                    "id": "f1",
                    "name": "2024-model-paper-physics.pdf",
                    "link": "https://drive.google.com/file/d/demo-paper/view",
                }
            ],
        }
    )


async def smoke_drive_paper_link() -> None:
    """Paper query → Drive link (mock backend; no Google credentials)."""
    backend = _mock_drive_backend()
    tool = DriveTool(backend=backend)

    import agents.tools.drive_tool as dt

    original = dt.DriveTool._get_drive_root
    dt.DriveTool._get_drive_root = lambda self, tid: "drive-folder-physics-demo"  # type: ignore[method-assign]
    try:

        class _AsyncDrive:
            async def drive_search(self, **kwargs):
                return json.loads(tool.drive_search(**kwargs))

        class _AsyncRag:
            async def kb_search(self, **kwargs):
                return {"ok": True, "answer": "", "citations": []}

        agent = ResourceAgent(drive=_AsyncDrive(), rag=_AsyncRag())
        result = await agent.run(
            {
                "tenant_id": "tenant-demo-physics",
                "tenant_name": "Demo Physics Academy",
                "messages": [HumanMessage(content="Do you have the 2024 physics past paper?")],
            }
        )
    finally:
        dt.DriveTool._get_drive_root = original  # type: ignore[method-assign]

    assert result.sub_path == "drive", f"expected drive path, got {result.sub_path}"
    assert "drive.google.com" in result.answer or "2024-model-paper" in result.answer, result.answer
    print(f"[OK] Drive paper link: {result.answer[:120]}...")


async def smoke_rag_velocity_mock() -> None:
    """Velocity query → cited RAG answer (mocked RAG service)."""
    from unittest.mock import MagicMock, patch

    tool = RagTool(embedder=MagicMock(), llm=MagicMock())
    mock_result = {
        "answer": "Velocity is the rate of change of displacement with respect to time.",
        "citations": [{"title": "Lesson 5 — Velocity", "lesson": "5", "score": 0.88}],
        "num_docs": 1,
    }

    class _AsyncRag:
        async def kb_search(self, **kwargs):
            with patch("agents.tools.rag_tool.count_points", return_value=2):
                with patch("agents.tools.rag_tool.RAGService") as mock_cls:
                    mock_cls.return_value.generate.return_value = mock_result
                    return json.loads(tool.kb_search(**kwargs))

    class _AsyncDrive:
        async def drive_search(self, **kwargs):
            return {"ok": True, "files": []}

    agent = ResourceAgent(drive=_AsyncDrive(), rag=_AsyncRag())
    result = await agent.run(
        {
            "tenant_id": "tenant-demo-physics",
            "messages": [HumanMessage(content="Explain velocity from the tutor notes")],
        }
    )
    assert result.sub_path == "rag", f"expected rag path, got {result.sub_path}"
    assert "velocity" in result.answer.lower()
    assert "lesson" in result.answer.lower() or "5" in result.answer
    print(f"[OK] RAG velocity + citation: {result.answer[:120]}...")


async def smoke_rag_velocity_live() -> None:
    """Velocity query against real Qdrant (requires ingest + OPENAI_API_KEY)."""
    if not os.getenv("OPENAI_API_KEY"):
        print("SKIP live RAG: OPENAI_API_KEY not set")
        return
    if not os.getenv("QDRANT_URL"):
        print("SKIP live RAG: QDRANT_URL not set")
        return

    from agents.nodes.resource_agent import DirectRagClient, DirectDriveClient

    agent = ResourceAgent(drive=DirectDriveClient(), rag=DirectRagClient())
    result = await agent.run(
        {
            "tenant_id": "tenant-demo-physics",
            "messages": [HumanMessage(content="Explain velocity from the tutor notes")],
        }
    )
    assert result.sub_path == "rag"
    assert "velocity" in result.answer.lower(), result.answer
    print(f"[OK] Live RAG velocity: {result.answer[:160]}...")


async def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 4 e2e smoke")
    parser.add_argument(
        "--live-rag",
        action="store_true",
        help="Also run RAG against real Qdrant (after ingest)",
    )
    args = parser.parse_args()

    print("=== Phase 4 e2e smoke ===")
    await smoke_drive_paper_link()
    await smoke_rag_velocity_mock()
    if args.live_rag:
        await smoke_rag_velocity_live()
    print("=== Phase 4 e2e passed ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
