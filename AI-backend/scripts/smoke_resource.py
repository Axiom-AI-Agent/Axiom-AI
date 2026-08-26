#!/usr/bin/env python3
"""Smoke test Phase 4 resource agent paths."""

from __future__ import annotations

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

os.environ.setdefault("DRIVE_MOCK", "true")
os.environ.setdefault("LANGFUSE_ENABLED", "false")

from langchain_core.messages import HumanMessage

from agents.nodes.resource_agent import ResourceAgent
from agents.tools.drive_tool import DriveTool
from services.drive_service.drive_client import MockDriveBackend
from services.ingest_service.chunkers import fixed_chunk
from services.ingest_service.pipeline import load_tenant_docs


def smoke_ingest_load() -> None:
    docs = load_tenant_docs(tenant_id="tenant-demo-physics", tenant_slug="demo-physics")
    chunks = fixed_chunk(docs)
    print(f"[OK] Loaded {len(docs)} docs → {len(chunks)} chunks")


def smoke_drive_mock() -> None:
    backend = MockDriveBackend(
        {
            "drive-folder-physics-demo": [{"id": "pf", "name": "papers", "link": ""}],
            "pf": [
                {
                    "id": "f1",
                    "name": "2024-model-paper-physics.pdf",
                    "link": "https://drive.example/paper.pdf",
                }
            ],
        }
    )
    tool = DriveTool(backend=backend)
    import agents.tools.drive_tool as dt

    original = dt.DriveTool._get_drive_root
    dt.DriveTool._get_drive_root = lambda self, tid: "drive-folder-physics-demo"  # type: ignore[method-assign]
    try:
        raw = tool.drive_search(
            tenant_id="tenant-demo-physics",
            query="physics paper",
            folder="papers",
        )
        payload = json.loads(raw)
        assert payload.get("ok"), payload
        print(f"[OK] Drive search: {payload['files'][0]['name']}")
    finally:
        dt.DriveTool._get_drive_root = original  # type: ignore[method-assign]


async def smoke_resource_agent() -> None:
    class _Drive:
        async def drive_search(self, **kwargs):
            return {
                "ok": True,
                "files": [{"name": "paper.pdf", "link": "https://x", "folder": "papers"}],
            }

        async def drive_list(self, **kwargs):
            return {
                "ok": True,
                "files": [{"name": "paper.pdf", "link": "https://x", "folder": "papers"}],
            }

    class _Rag:
        async def kb_search(self, **kwargs):
            return {
                "ok": True,
                "answer": "Velocity is displacement over time.",
                "citations": [{"lesson": "5", "title": "Velocity"}],
            }

    agent = ResourceAgent(drive=_Drive(), rag=_Rag())

    drive_result = await agent.run(
        {
            "tenant_id": "tenant-demo-physics",
            "is_enrolled": True,
            "enrolled_class_ids": ["class-physics-al-2026"],
            "session_id": "smoke-session",
            "user_id": "stu-smoke",
            "messages": [HumanMessage(content="Can I get the physics paper?")],
        }
    )
    assert drive_result.sub_path == "drive"
    print(f"[OK] Resource drive: {drive_result.answer[:80]}...")

    rag_result = await agent.run(
        {
            "tenant_id": "tenant-demo-physics",
            "is_enrolled": True,
            "enrolled_class_ids": ["class-physics-al-2026"],
            "messages": [HumanMessage(content="Explain velocity in lesson 5")],
        }
    )
    assert rag_result.sub_path == "rag"
    print(f"[OK] Resource RAG: {rag_result.answer[:80]}...")


def main() -> int:
    print("=== Phase 4 Resource Smoke ===")
    smoke_ingest_load()
    smoke_drive_mock()
    asyncio.run(smoke_resource_agent())
    print("=== All smoke checks passed ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
