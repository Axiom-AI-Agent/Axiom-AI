"""Resource agent node — Drive vs RAG sub-router via MCP tools."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Literal, Protocol

from langchain_core.messages import AIMessage
from loguru import logger

from agents.drive_file_pick import (
    DrivePickStore,
    files_from_drive_payload,
    get_drive_pick_store,
)
from agents.nodes.crm_client import (
    CrmClient,
    DirectCrmClient,
)
from agents.prompts.agent_prompts import (
    build_resource_drive_list_reply,
    build_resource_rag_reply,
    get_resource_not_enrolled_reply,
)
from agents.state import AgentState
from infrastructure.config import (
    RETRIEVAL_ESCALATION_THRESHOLD,
)
from services.language import resolve_canned_language, t

ResourceSubPath = Literal["drive", "rag"]

_DRIVE_PATTERNS = (
    r"\bpapers?\b",
    r"\btutes?\b",
    r"\btextbook\b",
    r"\bsyllabus\b",
    r"\bpdfs?\b",
    r"past paper",
    r"model paper",
    r"send me",
    r"download",
    r"get me",
    r"can i get",
    r"\bewanna\b",
    r"\bevanna\b",
    r"send karanna",
    r"file eka",
    r"tute eka",
    r"paper eka",
    r"පේපර්",
    r"ටියුට්",
    r"පෙළපොත්",
    r"பாடத்தாள",
    r"அனுப்பு",
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
    r"tell me about",
    r"kiyala\s+denn",
    r"\bkiyanna\b",
    r"\bkiyapan\b",
    r"explain karanna",
    r"විස්තර",
    r"කියලා",
    r"කියන්න",
    r"මොකක්ද",
    r"விளக்கு",
    r"சொல்லி",
    r"என்ன",
    r"விவரம்",
)


class DriveClient(Protocol):
    async def drive_search(
        self,
        *,
        tenant_id: str,
        query: str,
        folder: str | None = "papers",
    ) -> dict[str, Any]: ...

    async def drive_list(
        self,
        *,
        tenant_id: str,
        folder: str = "papers",
    ) -> dict[str, Any]: ...


class RagClient(Protocol):
    async def kb_search(
        self,
        *,
        tenant_id: str,
        query: str,
        class_ids: list[str] | None = None,
        language: str = "en",
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
    return "rag"


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

    async def drive_list(
        self,
        *,
        tenant_id: str,
        folder: str = "papers",
    ) -> dict[str, Any]:
        raw = self._tool.drive_list(tenant_id=tenant_id, folder=folder)
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
        language: str = "en",
    ) -> dict[str, Any]:
        raw = self._tool.kb_search(
            tenant_id=tenant_id,
            query=query,
            class_ids=class_ids,
            language=language,
        )
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

    async def drive_list(
        self,
        *,
        tenant_id: str,
        folder: str = "papers",
    ) -> dict[str, Any]:
        tool = self._tools.get("drive_list")
        if tool is None:
            return {"ok": False, "error": "MCP tool unavailable: drive_list"}
        raw = await tool.ainvoke({"tenant_id": tenant_id, "folder": folder})
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
        language: str = "en",
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
        pick_store: DrivePickStore | None = None,
    ) -> None:
        self.drive = drive
        self.rag = rag
        self.crm = crm or DirectCrmClient()
        self.pick_store = pick_store or get_drive_pick_store()

    async def run(self, state: AgentState) -> ResourceAgentResult:
        tenant_id = state.get("tenant_id") or ""
        user_message = _last_user_text(state)
        tenant_name = state.get("tenant_name") or "your tuition centre"
        sub_path = classify_resource_subpath(user_message)
        enrolled_class_ids = list(state.get("enrolled_class_ids") or [])
        language = resolve_canned_language(
            message=user_message,
            language_pref=state.get("language_pref"),
        )

        if not state.get("is_enrolled"):
            return ResourceAgentResult(
                answer=get_resource_not_enrolled_reply(
                    tenant_name=tenant_name,
                    language=language,
                ),
                sub_path=sub_path,
            )

        if not enrolled_class_ids:
            return ResourceAgentResult(
                answer=t("resource_no_enrollment", language, tenant_name=tenant_name),
                sub_path=sub_path,
            )

        tool_log: list[str] = []

        if sub_path == "drive":
            folder = _infer_drive_folder(user_message)
            result = await self.drive.drive_list(
                tenant_id=tenant_id,
                folder=folder,
            )
            tool_log.append(f"drive_list({folder}): ok={result.get('ok')}")
            files = result.get("files") or []
            picks = files_from_drive_payload(files)
            session_id = str(state.get("session_id") or "")
            user_id = str(
                state.get("user_id") or state.get("student_id") or state.get("phone") or ""
            )
            if result.get("ok") and picks and tenant_id and session_id:
                self.pick_store.put(
                    tenant_id=tenant_id,
                    session_id=session_id,
                    user_id=user_id,
                    files=picks,
                    folder=folder,
                    tenant_name=tenant_name,
                    language=language,
                )
            answer = build_resource_drive_list_reply(
                files=files,
                folder=folder,
                tenant_name=tenant_name,
                error=result.get("error"),
                language=language,
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
            language=language,
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
            tool_log.append(
                "rag_confidence: "
                f"docs={num_docs}, "
                f"best_score={best_score:.3f}, "
                f"threshold="
                f"{RETRIEVAL_ESCALATION_THRESHOLD}, "
                "low=True"
            )

            return ResourceAgentResult(
                answer=(
                    "I couldn't find enough reliable "
                    "information in your tutor's notes "
                    "to answer that confidently. "
                    "Would you like me to send this "
                    "question to your tutor?"
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
            language=language,
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
