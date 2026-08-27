"""Staff dashboard Q&A agent — separate from the student Guardrail/Router/Orchestrator."""

from __future__ import annotations

from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from loguru import logger

from agents.tools.dashboard_tool import (
    DashboardQueryTool,
    extract_phone_from_message,
    format_overview_fallback,
)
from infrastructure.llm import get_chat_llm
from infrastructure.observability import observe
from services.identity.staff_resolver import StaffContext

_SYSTEM_PROMPT = """You are the Axiom AI Dashboard assistant for tuition-centre staff.
You answer questions about THIS institute's dashboard only, using the JSON data provided.

Rules:
- Use only the provided JSON. Do not invent counts.
- Never claim access to another institute or tenant.
- You cannot resolve escalations, approve payments, broadcast, or change settings.
- If asked to take a mutating action, refuse and point the staff member to the web dashboard.
- Keep answers concise. Use short bullets for lists.
- Mirror the staff member's language when they write in Sinhala or Tamil.
"""


def _llm_content_to_str(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("text"):
                parts.append(str(block["text"]))
        return "\n".join(parts)
    return str(content)


def _select_context(message: str, tool: DashboardQueryTool) -> dict[str, Any]:
    text = (message or "").lower()
    payload: dict[str, Any] = {
        "overview": tool.get_overview(),
        "analytics": tool.get_analytics(),
    }
    class_hints = ("class", "grade", "subject", "batch")
    if any(hint in text for hint in class_hints):
        payload["class_analytics"] = tool.get_class_analytics()
    escalation_hints = ("escalat", "inbox", "ticket", "talk to tutor", "receipt")
    if any(hint in text for hint in escalation_hints):
        payload["escalations"] = tool.get_escalation_summary()
    phone = extract_phone_from_message(message)
    if phone:
        payload["student"] = tool.lookup_student_by_phone(phone)
    return payload


@observe(name="dashboard_agent")
async def run_dashboard_agent(
    *,
    staff: StaffContext,
    message: str,
    llm: Any | None = None,
    tool: DashboardQueryTool | None = None,
) -> str:
    """Answer a staff dashboard question. tenant_id is taken only from ``staff``."""
    question = (message or "").strip()
    if not question:
        return "Ask me about escalations, deflection, enrollments, or class activity."

    query_tool = tool or DashboardQueryTool(staff.tenant_id)
    if query_tool.tenant_id != staff.tenant_id:
        raise ValueError("Dashboard tool tenant_id does not match authenticated staff")

    try:
        context = _select_context(question, query_tool)
    except Exception as exc:
        logger.exception("Dashboard query failed tenant={} staff={}", staff.tenant_id, staff.staff_id)
        return f"I could not load dashboard data right now ({exc})."

    overview = context.get("overview") or {}
    analytics = context.get("analytics")
    chat_llm = llm or get_chat_llm()
    user_blob = (
        f"Staff: {staff.name} ({staff.role})\n"
        f"Question: {question}\n\n"
        f"DASHBOARD_JSON:\n{context}"
    )
    try:
        response = await chat_llm.ainvoke(
            [
                SystemMessage(content=_SYSTEM_PROMPT),
                HumanMessage(content=user_blob),
            ]
        )
        answer = _llm_content_to_str(response.content if hasattr(response, "content") else response).strip()
        if answer:
            return answer
    except Exception as exc:
        logger.warning("Dashboard agent LLM failed ({}); using numeric fallback", exc)

    return format_overview_fallback(overview, analytics if isinstance(analytics, dict) else None)
