"""Admissions agent node — multi-turn onboarding via CRM MCP tools."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from langchain_core.messages import AIMessage
from loguru import logger

from agents.nodes.crm_client import CrmClient, DirectCrmClient
from agents.state import AgentState
from services.admissions.onboarding_flow import OnboardingFlow


@dataclass
class AdmissionsAgentResult:
    answer: str
    tool_output: str = ""


class AdmissionsAgent:
    def __init__(
        self,
        *,
        crm: CrmClient | None = None,
        flow: OnboardingFlow | None = None,
    ) -> None:
        self.crm = crm or DirectCrmClient()
        self.flow = flow or OnboardingFlow()

    async def run(self, state: AgentState) -> AdmissionsAgentResult:
        tenant_id = state.get("tenant_id") or ""
        tenant_name = state.get("tenant_name") or "our tuition centre"
        student_id = state.get("user_id") or state.get("student_id") or ""
        phone = state.get("phone") or ""

        user_message = _last_user_text(state)
        tool_log: list[str] = []

        if not tenant_id or not phone:
            return AdmissionsAgentResult(
                answer="I need your contact details to complete registration. Please try again.",
            )

        student_payload = await self.crm.get_student(tenant_id=tenant_id, phone=phone)
        tool_log.append(f"get_student: {json.dumps(student_payload)[:300]}")
        student = student_payload.get("student")
        enrollments = student_payload.get("enrollments") or []
        pending_enrollment = student_payload.get("pending_enrollment")
        open_escalation = student_payload.get("open_escalation")

        ob_state = self.flow.load_from_student(
            student,
            enrollments=enrollments,
            pending_enrollment=pending_enrollment,
            open_escalation=open_escalation,
        )

        if ob_state.already_enrolled and ob_state.complete:
            class_row = await self._class_for_enrollment(tenant_id, ob_state.slots.class_id)
            answer = self.flow.already_registered_message(
                student=student or {},
                class_row=class_row,
                tenant_name=tenant_name,
            )
            return AdmissionsAgentResult(answer=answer, tool_output="\n".join(tool_log))

        if ob_state.awaiting_review:
            answer = self.flow.awaiting_review_message(tenant_name=tenant_name)
            return AdmissionsAgentResult(answer=answer, tool_output="\n".join(tool_log))

        sid = (student or {}).get("id") or student_id

        if ob_state.pending_payment:
            answer = self.flow.payment_pending_message(
                slots=ob_state.slots,
                class_row=await self._class_for_enrollment(
                    tenant_id, ob_state.slots.class_id
                ),
                tenant_name=tenant_name,
            )
            return AdmissionsAgentResult(answer=answer, tool_output="\n".join(tool_log))

        classes = await self.crm.list_classes(tenant_id=tenant_id)
        tool_log.append(f"list_classes: {len(classes)} classes")

        ob_state = self.flow.apply_message(ob_state, user_message, classes=classes)

        if ob_state.ambiguous_classes:
            answer = self.flow.disambiguation_prompt(ob_state.ambiguous_classes)
            return AdmissionsAgentResult(answer=answer, tool_output="\n".join(tool_log))

        slots = ob_state.slots

        await self._persist_slots(
            crm=self.crm,
            tenant_id=tenant_id,
            phone=phone,
            student=student,
            sid=sid,
            slots=slots,
            tool_log=tool_log,
        )

        if ob_state.complete and slots.class_id and sid:
            enroll = await self.crm.create_enrollment(
                tenant_id=tenant_id,
                student_id=sid,
                class_id=slots.class_id,
            )
            tool_log.append(f"create_enrollment: {enroll.get('ok')}")
            if enroll.get("ok"):
                answer = self.flow.payment_pending_message(
                    slots=slots,
                    class_row=enroll.get("class"),
                    tenant_name=tenant_name,
                )
                return AdmissionsAgentResult(answer=answer, tool_output="\n".join(tool_log))
            error = enroll.get("error", "Could not start enrollment.")
            return AdmissionsAgentResult(
                answer=f"Sorry — {error} Please reply YES to confirm consent first.",
                tool_output="\n".join(tool_log),
            )

        answer = self.flow.prompt_for_step(ob_state.next_step, tenant_name=tenant_name)
        return AdmissionsAgentResult(answer=answer, tool_output="\n".join(tool_log))

    async def _class_for_enrollment(
        self, tenant_id: str, class_id: str | None
    ) -> dict[str, Any] | None:
        if not class_id:
            return None
        classes = await self.crm.list_classes(tenant_id=tenant_id)
        return next((c for c in classes if c.get("id") == class_id), None)

    async def _persist_slots(
        self,
        *,
        crm: CrmClient,
        tenant_id: str,
        phone: str,
        student: dict[str, Any] | None,
        sid: str,
        slots: Any,
        tool_log: list[str],
    ) -> None:
        if slots.name and slots.name != (student or {}).get("name"):
            reg = await crm.register_student(
                tenant_id=tenant_id,
                phone=phone,
                student_id=sid,
                name=slots.name,
            )
            tool_log.append(f"register_student(name): {reg.get('ok')}")

        if slots.school and slots.school != (student or {}).get("school"):
            reg = await crm.register_student(
                tenant_id=tenant_id,
                phone=phone,
                student_id=sid,
                school=slots.school,
            )
            tool_log.append(f"register_student(school): {reg.get('ok')}")

        if slots.district and slots.district != (student or {}).get("district"):
            reg = await crm.register_student(
                tenant_id=tenant_id,
                phone=phone,
                student_id=sid,
                district=slots.district,
            )
            tool_log.append(f"register_student(district): {reg.get('ok')}")

        if slots.consent and not (student or {}).get("consent_at"):
            reg = await crm.register_student(
                tenant_id=tenant_id,
                phone=phone,
                student_id=sid,
                consent=True,
            )
            tool_log.append(f"register_student(consent): {reg.get('ok')}")


def _last_user_text(state: AgentState) -> str:
    messages = state.get("messages") or []
    for msg in reversed(messages):
        if hasattr(msg, "content"):
            content = msg.content
            return content if isinstance(content, str) else str(content)
        if isinstance(msg, dict) and msg.get("role") == "user":
            return str(msg.get("content") or "")
    return ""


async def run_admissions_agent(
    state: AgentState,
    *,
    crm: CrmClient | None = None,
) -> dict[str, Any]:
    agent = AdmissionsAgent(crm=crm)
    result = await agent.run(state)
    logger.debug("Admissions agent tool_output: {}", result.tool_output[:500])
    return {
        "messages": [AIMessage(content=result.answer)],
        "agent_outputs": [
            {
                "route": "admissions",
                "tool_output": result.tool_output,
                "answer": result.answer,
                "status": "ok",
            }
        ],
    }


# Re-export MCP clients for orchestrator wiring.
from agents.nodes.crm_client import DirectCrmClient, McpCrmClient

__all__ = ["DirectCrmClient", "McpCrmClient", "AdmissionsAgent", "run_admissions_agent"]
