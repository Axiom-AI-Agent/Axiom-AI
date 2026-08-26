"""Escalation agent — talk-to-tutor requests → dashboard inbox."""

from __future__ import annotations

import json
from dataclasses import dataclass

from langchain_core.messages import AIMessage
from loguru import logger

from agents.nodes.crm_client import CrmClient, DirectCrmClient
from agents.prompts.agent_prompts import build_escalation_ack_reply
from agents.state import AgentState
from domain.escalation_reasons import (
    LOW_RAG_CONFIDENCE,
    TALK_TO_TUTOR,
)
from services.language import t


@dataclass
class EscalationAgentResult:
    answer: str
    tool_output: str = ""


def _last_user_text(state: AgentState) -> str:
    messages = state.get("messages") or []
    for msg in reversed(messages):
        if hasattr(msg, "content"):
            content = msg.content
            return content if isinstance(content, str) else str(content)
        if isinstance(msg, dict) and msg.get("role") == "user":
            return str(msg.get("content") or "")
    return ""


class EscalationAgent:
    def __init__(self, *, crm: CrmClient | None = None) -> None:
        self.crm = crm or DirectCrmClient()

    async def run(self, state: AgentState) -> EscalationAgentResult:
        tenant_id = state.get("tenant_id") or ""
        tenant_name = state.get("tenant_name") or "our tuition centre"
        student_id = state.get("user_id") or state.get("student_id") or ""
        user_message = _last_user_text(state)
        tool_log: list[str] = []
        language = state.get("language_pref") or "en"

        if not tenant_id or not student_id:
            return EscalationAgentResult(
                answer=t("escalation_need_id", language),
            )

        reason_code = (
            state.get(
                "pending_escalation_reason"
            )
            or TALK_TO_TUTOR
        )

        escalation_message = (
            state.get(
                "pending_escalation_message"
            )
            or user_message
        )


        payload = (
            await self.crm.create_escalation(
                tenant_id=tenant_id,
                student_id=student_id,
                reason_code=reason_code,
                student_message=(
                    escalation_message
                    or None
                ),
            )
        )
        tool_log.append(f"create_escalation: {json.dumps(payload)[:400]}")

        if not payload.get("ok"):
            error = payload.get(
                "error",
                "Could not open escalation.",
            )

            return EscalationAgentResult(
                answer=f"Sorry — {error}",
                tool_output="\n".join(tool_log),
            )

        if reason_code == LOW_RAG_CONFIDENCE:
            answer = t("escalation_low_confidence", language, tenant_name=tenant_name)
        else:
            answer = build_escalation_ack_reply(
                tenant_name=tenant_name,
                language=language,
            )

        return EscalationAgentResult(
            answer=answer,
            tool_output="\n".join(tool_log),
        )


async def run_escalation_agent(
    state: AgentState,
    *,
    crm: CrmClient | None = None,
) -> dict[str, object]:
    agent = EscalationAgent(crm=crm)
    result = await agent.run(state)
    logger.debug("Escalation agent tool_output: {}", result.tool_output[:500])
    return {
        "messages": [AIMessage(content=result.answer)],
        "agent_outputs": [
            {
                "route": "escalation",
                "tool_output": result.tool_output,
                "answer": result.answer,
                "status": "ok",
            }
        ],
    }
