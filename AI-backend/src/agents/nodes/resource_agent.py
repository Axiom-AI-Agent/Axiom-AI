"""Resource agent node — Drive vs RAG sub-router via MCP tools."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Literal, Protocol
from infrastructure.config import (
    RETRIEVAL_ESCALATION_THRESHOLD,
)
from langchain_core.messages import AIMessage
from loguru import logger

from agents.prompts.agent_prompts import (
    build_resource_drive_reply,
    build_resource_rag_reply,
    get_resource_not_enrolled_reply,
)

from agents.nodes.crm_client import (
    CrmClient,
    DirectCrmClient,
)
from agents.state import AgentState
from domain.escalation_reasons import (
    LOW_RAG_CONFIDENCE,
)
from domain.escalation_reasons import (
    LOW_RAG_CONFIDENCE,
)

ResourceSubPath = Literal["drive", "rag"]

_DRIVE_PATTERNS = (
    r"\bpaper\b",
    r"\btute\b",
    r"\btextbook\b",
    r"\bsyllabus\b",
    r"\bpdf\b",
    r"past paper",
    r"model paper",
    r"send me",
    r"download",
    r"get me",
    r"can i get",
)
_RAG_PATTERNS = (
    r"\bexplain\b",
    r"\bunderstand\b",
    r"\blesson\b",
    r"\bnotes?\b",
    r"\buploaded\b",
    r"what did",
    r"how does",
    r"help me with",
    r"what is",
    r"what are",
)


class DriveClient(Protocol):
    async def drive_search(
        self,
        *,
        tenant_id: str,
        query: str,
        folder: str | None = "papers",
    ) -> dict[str, Any]: ...


class RagClient(Protocol):
    async def kb_search(
        self,
        *,
        tenant_id: str,
        query: str,
        class_ids: list[str] | None = None,
    ) -> dict[str, Any]: ...


@dataclass
class ResourceAgentResult:
    answer: str
    tool_output: str = ""
    sub_path: ResourceSubPath = "rag"


def classify_resource_subpath(message: str) -> ResourceSubPath:
    """Keyword sub-router: drive for file requests, rag for explanations."""
    text = message.lower().strip()
    drive_score = sum(1 for p in _DRIVE_PATTERNS if re.search(p, text))
    rag_score = sum(1 for p in _RAG_PATTERNS if re.search(p, text))
    if drive_score > rag_score:
        return "drive"
    if rag_score > 0:
        return "rag"
    if "?" in text:
        return "rag"
    return "drive"


def _infer_drive_folder(message: str) -> str:
    text = message.lower()
    if "textbook" in text or "chapter" in text:
        return "textbooks"
    if "syllabus" in text:
        return "syllabus"
    return "papers"


class DirectDriveClient:
    def __init__(self) -> None:
        from agents.tools.drive_tool import DriveTool

        self._tool = DriveTool()

    async def drive_search(
        self,
        *,
        tenant_id: str,
        query: str,
        folder: str | None = "papers",
    ) -> dict[str, Any]:
        raw = self._tool.drive_search(tenant_id=tenant_id, query=query, folder=folder)
        return json.loads(raw)


class DirectRagClient:
    def __init__(self) -> None:
        from agents.tools.rag_tool import RagTool

        self._tool = RagTool()

    async def kb_search(
        self,
        *,
        tenant_id: str,
        query: str,
        class_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        raw = self._tool.kb_search(tenant_id=tenant_id, query=query, class_ids=class_ids)
        return json.loads(raw)


class McpDriveClient:
    def __init__(self, tools_by_name: dict[str, Any]) -> None:
        self._tools = tools_by_name

    async def drive_search(
        self,
        *,
        tenant_id: str,
        query: str,
        folder: str | None = "papers",
    ) -> dict[str, Any]:
        tool = self._tools.get("drive_search")
        if tool is None:
            return {"ok": False, "error": "MCP tool unavailable: drive_search"}
        raw = await tool.ainvoke({"tenant_id": tenant_id, "query": query, "folder": folder})
        text = _mcp_text(raw)
        return json.loads(text)


class McpRagClient:
    def __init__(self, tools_by_name: dict[str, Any]) -> None:
        self._tools = tools_by_name

    async def kb_search(
        self,
        *,
        tenant_id: str,
        query: str,
        class_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        tool = self._tools.get("kb_search")
        if tool is None:
            return {"ok": False, "error": "MCP tool unavailable: kb_search"}
        payload: dict[str, Any] = {"tenant_id": tenant_id, "query": query}
        if class_ids:
            payload["class_ids"] = class_ids
        raw = await tool.ainvoke(payload)
        text = _mcp_text(raw)
        return json.loads(text)


def _mcp_text(raw: Any) -> str:
    if isinstance(raw, list):
        return next((item.get("text", "") for item in raw if isinstance(item, dict)), str(raw))
    return str(raw)


class ResourceAgent:
    def __init__(
        self,
        *,
        drive: DriveClient,
        rag: RagClient,
        crm: CrmClient | None = None,
    ) -> None:
        self.drive = drive
        self.rag = rag
        self.crm = crm or DirectCrmClient()

    async def run(self, state: AgentState) -> ResourceAgentResult:
        tenant_id = state.get("tenant_id") or ""
        user_message = _last_user_text(state)
        tenant_name = state.get("tenant_name") or "your tuition centre"
        sub_path = classify_resource_subpath(user_message)
        enrolled_class_ids = list(state.get("enrolled_class_ids") or [])

        if not state.get("is_enrolled"):
            return ResourceAgentResult(
                answer=get_resource_not_enrolled_reply(tenant_name=tenant_name),
                sub_path=sub_path,
            )

        if not enrolled_class_ids:
            return ResourceAgentResult(
                answer=(
                    "I couldn't find an active class enrollment for your account. "
                    f"Please contact {tenant_name} to confirm your enrollment."
                ),
                sub_path=sub_path,
            )

        tool_log: list[str] = []

        if sub_path == "drive":
            folder = _infer_drive_folder(user_message)
            result = await self.drive.drive_search(
                tenant_id=tenant_id,
                query=user_message,
                folder=folder,
            )
            tool_log.append(f"drive_search({folder}): ok={result.get('ok')}")
            answer = build_resource_drive_reply(
                files=result.get("files") or [],
                query=user_message,
                tenant_name=tenant_name,
                error=result.get("error"),
                empty_message=result.get("message"),
            )
            return ResourceAgentResult(
                answer=answer,
                tool_output="\n".join(tool_log),
                sub_path="drive",
                    )
        result = await self.rag.kb_search(
            tenant_id=tenant_id,
            query=user_message,
            class_ids=enrolled_class_ids,
        )

        tool_log.append(
            f"kb_search: ok={result.get('ok')}"
        )

        citations = (
            result.get("citations")
            or []
        )

        num_docs = int(
            result.get("num_docs")
            or 0
        )

        scores = [
            float(citation.get("score"))
            for citation in citations
            if citation.get("score")
            is not None
        ]

        best_score = (
            max(scores)
            if scores
            else 0.0
        )

        low_confidence = (
            not result.get("ok")
            or num_docs == 0
            or best_score
            < RETRIEVAL_ESCALATION_THRESHOLD
        )

        if low_confidence:
            student_id = (
                state.get("user_id")
                or state.get("student_id")
                or ""
            )

            tool_log.append(
                "rag_confidence: "
                f"docs={num_docs}, "
                f"best_score={best_score:.3f}, "
                f"threshold="
                f"{RETRIEVAL_ESCALATION_THRESHOLD}"
            )

            if tenant_id and student_id:
                escalation = (
                    await self.crm.create_escalation(
                        tenant_id=tenant_id,
                        student_id=student_id,
                        reason_code=(
                            LOW_RAG_CONFIDENCE
                        ),
                        student_message=(
                            user_message
                            or None
                        ),
                    )
                )

                tool_log.append(
                    "create_escalation: "
                    f"ok={escalation.get('ok')}"
                )

            return ResourceAgentResult(
                answer=(
                    "I couldn't find enough reliable "
                    "information in your tutor's notes "
                    "to answer that confidently. "
                    "I've sent this to your tutor "
                    "for review."
                ),
                tool_output="\n".join(
                    tool_log
                ),
                sub_path="rag",
            )

        answer = build_resource_rag_reply(
            answer=result.get(
                "answer",
                "",
            ),
            citations=citations,
            error=result.get("error"),
        )

        return ResourceAgentResult(
            answer=answer,
            tool_output="\n".join(
                tool_log
            ),
            sub_path="rag",
        )


def _last_user_text(state: AgentState) -> str:
    messages = state.get("messages") or []
    for msg in reversed(messages):
        if hasattr(msg, "content"):
            content = msg.content
            return content if isinstance(content, str) else str(content)
        if isinstance(msg, dict) and msg.get("role") == "user":
            return str(msg.get("content") or "")
    return ""


async def run_resource_agent(
    state: AgentState,
    *,
    drive: DriveClient | None = None,
    rag: RagClient | None = None,
    crm: CrmClient | None = None,
) -> dict[str, Any]:
    from infrastructure.config import ALLOW_INPROCESS_TOOLS

    if drive is None:
        if not ALLOW_INPROCESS_TOOLS:
            raise RuntimeError(
                "MCP drive client required; set ALLOW_INPROCESS_TOOLS=true for in-process DriveTool."
            )
        drive = DirectDriveClient()
    if rag is None:
        if not ALLOW_INPROCESS_TOOLS:
            raise RuntimeError(
                "MCP rag client required; set ALLOW_INPROCESS_TOOLS=true for in-process RagTool."
            )
        rag = DirectRagClient()

    agent = ResourceAgent(drive=drive, rag=rag,crm=crm)
    result = await agent.run(state)
    logger.debug("Resource agent sub_path={} tool_output={}", result.sub_path, result.tool_output[:300])
    return {
        "messages": [AIMessage(content=result.answer)],
        "agent_outputs": [
            {
                "route": "resource",
                "sub_path": result.sub_path,
                "tool_output": result.tool_output,
                "answer": result.answer,
                "status": "ok",
            }
        ],
    }
