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

ResourceSubPath = Literal["drive", "rag", "schedule"]

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
_SCHEDULE_PATTERNS = (
    r"\bschedule\b",
    r"\btimetable\b",
    r"\bclass time\b",
    r"\bclass times\b",
    r"\bwhen is\b",
    r"\bwhat time\b",
    r"\bwhat day\b",
    r"\bnext class\b",
    r"\btoday.*class",
    r"\bclass.*today",
    r"\btomorrow.*class",
    r"\bclass.*tomorrow",
    r"\bweekly\b",
    r"\bweek schedule\b",
    r"\bmy class\b",
    r"\bkal class",
    r"\breta class",
    r"\bissarahata\b",
    r"\b timetable\b",
    r"\b වේලාව\b",
    r"\b நேரம்\b",
    r"\b வகுப்பு\b",
    r"\b அட்டவணை\b",
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
    """Keyword sub-router: schedule > drive > rag."""
    text = message.lower().strip()
    schedule_score = sum(1 for p in _SCHEDULE_PATTERNS if re.search(p, text))
    drive_score = sum(1 for p in _DRIVE_PATTERNS if re.search(p, text))
    rag_score = sum(1 for p in _RAG_PATTERNS if re.search(p, text))

    # Schedule takes priority — time-related queries are unambiguous
    if schedule_score > 0:
        return "schedule"
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


class ScheduleClient(Protocol):
    """Protocol for schedule lookups — Direct or MCP."""

    async def get_next_class(
        self, *, tenant_id: str, student_id: str | None = None
    ) -> dict[str, Any]: ...

    async def get_schedule_for_date(
        self, *, tenant_id: str, student_id: str | None = None, date_str: str
    ) -> dict[str, Any]: ...

    async def get_week_schedule(
        self, *, tenant_id: str, student_id: str | None = None
    ) -> dict[str, Any]: ...


class DirectScheduleClient:
    """In-process schedule client using ScheduleService directly."""

    def __init__(self) -> None:
        from services.schedule.schedule_service import ScheduleService
        self._svc = ScheduleService()

    async def get_next_class(
        self, *, tenant_id: str, student_id: str | None = None
    ) -> dict[str, Any]:
        row = self._svc.get_next_class(tenant_id, student_id=student_id)
        if not row:
            return {"ok": True, "found": False, "message": "No upcoming classes found."}
        return {"ok": True, "found": True, "schedule": row}

    async def get_schedule_for_date(
        self, *, tenant_id: str, student_id: str | None = None, date_str: str
    ) -> dict[str, Any]:
        from datetime import date as dt_date
        try:
            d = dt_date.fromisoformat(date_str)
        except ValueError:
            return {"ok": False, "error": f"Invalid date format: {date_str}. Use YYYY-MM-DD."}
        rows = self._svc.get_schedules_for_date(tenant_id, d, student_id=student_id)
        return {"ok": True, "date": date_str, "schedules": rows, "count": len(rows)}

    async def get_week_schedule(
        self, *, tenant_id: str, student_id: str | None = None
    ) -> dict[str, Any]:
        rows = self._svc.get_week_schedule(tenant_id, student_id=student_id)
        return {"ok": True, "schedules": rows, "count": len(rows)}


class McpScheduleClient:
    """MCP subprocess schedule client."""

    def __init__(self, tools_by_name: dict[str, Any]) -> None:
        self._tools = tools_by_name

    async def _invoke(self, tool_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        tool = self._tools.get(tool_name)
        if tool is None:
            return {"ok": False, "error": f"MCP tool unavailable: {tool_name}"}
        raw = await tool.ainvoke(payload)
        text = _mcp_text(raw)
        return json.loads(text)

    async def get_next_class(
        self, *, tenant_id: str, student_id: str | None = None
    ) -> dict[str, Any]:
        return await self._invoke("get_next_class", {"tenant_id": tenant_id, "student_id": student_id or ""})

    async def get_schedule_for_date(
        self, *, tenant_id: str, student_id: str | None = None, date_str: str
    ) -> dict[str, Any]:
        return await self._invoke("get_schedule_for_date", {"tenant_id": tenant_id, "date": date_str, "student_id": student_id or ""})

    async def get_week_schedule(
        self, *, tenant_id: str, student_id: str | None = None
    ) -> dict[str, Any]:
        return await self._invoke("get_week_schedule", {"tenant_id": tenant_id, "student_id": student_id or ""})


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
        schedule: ScheduleClient | None = None,
        crm: CrmClient | None = None,
        pick_store: DrivePickStore | None = None,
    ) -> None:
        self.drive = drive
        self.rag = rag
        self.schedule = schedule or DirectScheduleClient()
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

        if sub_path == "schedule":
            return await self._handle_schedule(
                tenant_id=tenant_id,
                user_message=user_message,
                state=state,
                tool_log=tool_log,
                language=language,
                tenant_name=tenant_name,
            )

        if sub_path == "drive":
            return await self._handle_drive(
                tenant_id=tenant_id,
                user_message=user_message,
                state=state,
                tool_log=tool_log,
                language=language,
                tenant_name=tenant_name,
            )

        # Default: RAG
        return await self._handle_rag(
            tenant_id=tenant_id,
            user_message=user_message,
            enrolled_class_ids=enrolled_class_ids,
            tool_log=tool_log,
            language=language,
        )

    async def _handle_schedule(
        self,
        *,
        tenant_id: str,
        user_message: str,
        state: AgentState,
        tool_log: list[str],
        language: str,
        tenant_name: str,
    ) -> ResourceAgentResult:
        """Handle schedule queries via ScheduleClient."""
        from datetime import timedelta
        from services.schedule.schedule_service import get_tenant_now, get_tenant_today

        student_id = state.get("student_id") or state.get("user_id") or ""
        text = user_message.lower().strip()

        if any(w in text for w in ["tomorrow", "හෙට", "நாளை"]):
            now_local = get_tenant_now(tenant_id)
            tomorrow = now_local.date() + timedelta(days=1)
            result = await self.schedule.get_schedule_for_date(
                tenant_id=tenant_id, student_id=student_id, date_str=tomorrow.isoformat()
            )
            tool_log.append(f"schedule(tomorrow={tomorrow}): count={result.get('count', 0)}")
            answer = _format_schedule_reply(result, "tomorrow", language, tenant_name)
        elif any(w in text for w in ["today", "අද", "இன்று"]):
            today = get_tenant_today(tenant_id)
            result = await self.schedule.get_schedule_for_date(
                tenant_id=tenant_id, student_id=student_id, date_str=today.isoformat()
            )
            tool_log.append(f"schedule(today={today}): count={result.get('count', 0)}")
            answer = _format_schedule_reply(result, "today", language, tenant_name)
        elif any(w in text for w in ["week", "weekly", "සතිය", "வார"]):
            result = await self.schedule.get_week_schedule(
                tenant_id=tenant_id, student_id=student_id
            )
            tool_log.append(f"schedule(week): count={result.get('count', 0)}")
            answer = _format_schedule_reply(result, "week", language, tenant_name)
        elif any(w in text for w in ["next", "ඊළඟ", "அடுத்த"]):
            result = await self.schedule.get_next_class(
                tenant_id=tenant_id, student_id=student_id
            )
            tool_log.append(f"schedule(next): found={result.get('found', False)}")
            answer = _format_schedule_reply(result, "next", language, tenant_name)
        else:
            result = await self.schedule.get_next_class(
                tenant_id=tenant_id, student_id=student_id
            )
            tool_log.append(f"schedule(next_default): found={result.get('found', False)}")
            answer = _format_schedule_reply(result, "next", language, tenant_name)

        return ResourceAgentResult(
            answer=answer,
            tool_output="\n".join(tool_log),
            sub_path="schedule",
        )

    async def _handle_drive(
        self,
        *,
        tenant_id: str,
        user_message: str,
        state: AgentState,
        tool_log: list[str],
        language: str,
        tenant_name: str,
    ) -> ResourceAgentResult:
        """Handle Drive file requests."""
        folder = _infer_drive_folder(user_message)
        result = await self.drive.drive_list(tenant_id=tenant_id, folder=folder)
        tool_log.append(f"drive_list({folder}): ok={result.get('ok')}")
        files = result.get("files") or []
        picks = files_from_drive_payload(files)
        session_id = str(state.get("session_id") or "")
        user_id = str(state.get("user_id") or state.get("student_id") or state.get("phone") or "")
        if result.get("ok") and picks and tenant_id and session_id:
            self.pick_store.put(
                tenant_id=tenant_id, session_id=session_id, user_id=user_id,
                files=picks, folder=folder, tenant_name=tenant_name, language=language,
            )
        answer = build_resource_drive_list_reply(
            files=files, folder=folder, tenant_name=tenant_name,
            error=result.get("error"), language=language,
        )
        return ResourceAgentResult(answer=answer, tool_output="\n".join(tool_log), sub_path="drive")

    async def _handle_rag(
        self,
        *,
        tenant_id: str,
        user_message: str,
        enrolled_class_ids: list[str],
        tool_log: list[str],
        language: str,
    ) -> ResourceAgentResult:
        """Handle RAG knowledge base queries."""
        result = await self.rag.kb_search(
            tenant_id=tenant_id, query=user_message, class_ids=enrolled_class_ids, language=language,
        )
        tool_log.append(f"kb_search: ok={result.get('ok')}")
        citations = result.get("citations") or []
        num_docs = int(result.get("num_docs") or 0)
        scores = [float(c.get("score")) for c in citations if c.get("score") is not None]
        best_score = max(scores) if scores else 0.0
        low_confidence = (
            not result.get("ok") or num_docs == 0 or best_score < RETRIEVAL_ESCALATION_THRESHOLD
        )
        if low_confidence:
            tool_log.append(
                f"rag_confidence: docs={num_docs}, best={best_score:.3f}, "
                f"threshold={RETRIEVAL_ESCALATION_THRESHOLD}, low=True"
            )
            return ResourceAgentResult(
                answer="I couldn't find enough reliable information to answer that confidently. Would you like me to send this to your tutor?",
                tool_output="\n".join(tool_log),
                sub_path="rag",
            )
        answer = build_resource_rag_reply(
            answer=result.get("answer", ""), citations=citations, error=result.get("error"), language=language,
        )
        return ResourceAgentResult(answer=answer, tool_output="\n".join(tool_log), sub_path="rag")


def _last_user_text(state: AgentState) -> str:
    messages = state.get("messages") or []
    for msg in reversed(messages):
        if hasattr(msg, "content"):
            content = msg.content
            return content if isinstance(content, str) else str(content)
        if isinstance(msg, dict) and msg.get("role") == "user":
            return str(msg.get("content") or "")
    return ""


def _format_schedule_reply(
    result: dict[str, Any],
    query_type: str,
    language: str,
    tenant_name: str,
) -> str:
    """Format schedule query result into a friendly reply."""
    if not result.get("ok"):
        return "Sorry, I couldn't check the schedule right now. Please try again later."

    if query_type == "next":
        if not result.get("found"):
            return _t("schedule_no_upcoming", language, tenant_name=tenant_name)
        schedule = result.get("schedule", {})
        return _format_single_class(schedule, "next", language)

    schedules = result.get("schedules", [])
    count = result.get("count", len(schedules))

    if count == 0:
        if query_type == "today":
            return _t("schedule_no_classes_today", language, tenant_name=tenant_name)
        if query_type == "tomorrow":
            return _t("schedule_no_classes_tomorrow", language, tenant_name=tenant_name)
        return _t("schedule_no_classes", language, tenant_name=tenant_name)

    if query_type == "week":
        return _format_week_schedule(schedules, language)

    return _format_day_schedule(schedules, query_type, language)


def _format_single_class(schedule: dict[str, Any], query_type: str, language: str) -> str:
    class_info = schedule.get("subject_classes") or {}
    teacher_info = schedule.get("staff_users") or {}
    class_name = class_info.get("name") or class_info.get("subject") or "your class"
    day = schedule.get("day_of_week", "")
    start = schedule.get("start_time", "")
    end = schedule.get("end_time", "")
    room = schedule.get("room")
    date_str = schedule.get("date", "")
    teacher = teacher_info.get("name", "")

    time_str = f"{start} - {end}" if end else start
    parts = [f"{class_name} is on {day}" if day else class_name]
    if date_str:
        parts = [f"{class_name} is on {date_str}"]
    parts.append(f"from {time_str}")
    if room:
        parts.append(f"in {room}")
    if teacher:
        parts.append(f"with {teacher}")

    return " ".join(parts) + "."


def _format_day_schedule(schedules: list[dict], query_type: str, language: str) -> str:
    lines = []
    for s in schedules:
        class_info = s.get("subject_classes") or {}
        class_name = class_info.get("name") or class_info.get("subject") or "Class"
        start = s.get("start_time", "")
        end = s.get("end_time", "")
        room = s.get("room")
        time_str = f"{start}-{end}" if end else start
        line = f"- {class_name}: {time_str}"
        if room:
            line += f" ({room})"
        lines.append(line)
    return "\n".join(lines)


def _format_week_schedule(schedules: list[dict], language: str) -> str:
    by_day: dict[str, list] = {}
    for s in schedules:
        day = s.get("day_of_week", "unknown")
        by_day.setdefault(day, []).append(s)

    lines = []
    for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
        day_schedules = by_day.get(day, [])
        if not day_schedules:
            continue
        lines.append(f"**{day.title()}:**")
        for s in day_schedules:
            class_info = s.get("subject_classes") or {}
            class_name = class_info.get("name") or class_info.get("subject") or "Class"
            start = s.get("start_time", "")
            end = s.get("end_time", "")
            room = s.get("room")
            time_str = f"{start}-{end}" if end else start
            line = f"  - {class_name}: {time_str}"
            if room:
                line += f" ({room})"
            lines.append(line)
    return "\n".join(lines) if lines else "No classes scheduled this week."


def _t(key: str, language: str, **kwargs: Any) -> str:
    translations = {
        "en": {
            "schedule_no_upcoming": "You don't have any upcoming classes scheduled.",
            "schedule_no_classes_today": "You don't have any classes scheduled for today.",
            "schedule_no_classes_tomorrow": "You don't have any classes scheduled for tomorrow.",
            "schedule_no_classes": "No classes found for that time.",
        },
        "si": {
            "schedule_no_upcoming": "ඔබට තවත් පන්ති නියම කර නැත.",
            "schedule_no_classes_today": "අද ඔබට පන්ති නියම කර නැත.",
            "schedule_no_classes_tomorrow": "හෙට ඔබට පන්ති නියම කර නැත.",
            "schedule_no_classes": "එම කාලය සඳහා පන්ති හමු නොවීය.",
        },
        "ta": {
            "schedule_no_upcoming": "உங்களுக்கு வரும் வகுப்புகள் எதுவும் திட்டமிடப்படவில்லை.",
            "schedule_no_classes_today": "இன்று உங்களுக்கு வகுப்புகள் எதுவும் திட்டமிடப்படவில்லை.",
            "schedule_no_classes_tomorrow": "நாளை உங்களுக்கு வகுப்புகள் எதுவும் திட்டமிடப்படவில்லை.",
            "schedule_no_classes": "அந்த நேரத்தில் வகுப்புகள் எதுவும் கிடைக்கவில்லை.",
        },
    }
    lang_map = translations.get(language, translations["en"])
    template = lang_map.get(key, translations["en"].get(key, key))
    try:
        return template.format(**kwargs)
    except (KeyError, IndexError):
        return template


async def run_resource_agent(
    state: AgentState,
    *,
    drive: DriveClient | None = None,
    rag: RagClient | None = None,
    schedule: ScheduleClient | None = None,
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
    if schedule is None:
        schedule = DirectScheduleClient()

    agent = ResourceAgent(drive=drive, rag=rag, schedule=schedule, crm=crm)
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
