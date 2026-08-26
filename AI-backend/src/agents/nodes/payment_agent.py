"""Payment Check agent — payment receipt → escalation inbox."""

from __future__ import annotations

import json
from dataclasses import dataclass

from langchain_core.messages import AIMessage
from loguru import logger

from agents.nodes.crm_client import CrmClient, DirectCrmClient
from agents.prompts.agent_prompts import build_payment_ack_reply, build_payment_missing_media_reply
from agents.state import AgentState
from domain.escalation_reasons import PAYMENT_RECEIPT
from services.language import t


@dataclass
class PaymentAgentResult:
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


class PaymentAgent:
    def __init__(self, *, crm: CrmClient | None = None) -> None:
        self.crm = crm or DirectCrmClient()

    async def run(self, state: AgentState) -> PaymentAgentResult:
        tenant_id = state.get("tenant_id") or ""
        tenant_name = state.get("tenant_name") or "our tuition centre"
        student_id = state.get("user_id") or state.get("student_id") or ""
        media_url = state.get("media_url")
        language = state.get("language_pref") or "en"
        user_message = _last_user_text(state)
        tool_log: list[str] = []

        if not tenant_id or not student_id:
            return PaymentAgentResult(
                answer=t("payment_need_profile", language),
            )

        if not media_url:
            return PaymentAgentResult(
                answer=build_payment_missing_media_reply(
                    tenant_name=tenant_name,
                    language=language,
                ),
            )

        payload = await self.crm.create_escalation(
            tenant_id=tenant_id,
            student_id=student_id,
            reason_code=PAYMENT_RECEIPT,
            media_url=media_url,
            student_message=user_message or None,
        )
        tool_log.append(f"create_escalation: {json.dumps(payload)[:400]}")

        if not payload.get("ok"):
            error = payload.get("error", "Could not submit payment receipt.")
            return PaymentAgentResult(
                answer=f"Sorry — {error}",
                tool_output="\n".join(tool_log),
            )

        return PaymentAgentResult(
            answer=build_payment_ack_reply(tenant_name=tenant_name, language=language),
            tool_output="\n".join(tool_log),
        )


async def run_payment_agent(
    state: AgentState,
    *,
    crm: CrmClient | None = None,
) -> dict[str, object]:
    agent = PaymentAgent(crm=crm)
    result = await agent.run(state)
    logger.debug("Payment agent tool_output: {}", result.tool_output[:500])
    return {
        "messages": [AIMessage(content=result.answer)],
        "agent_outputs": [
            {
                "route": "payment_check",
                "tool_output": result.tool_output,
                "answer": result.answer,
                "status": "ok",
            }
        ],
    }
