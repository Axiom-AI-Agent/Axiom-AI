"""
Single async entry for one chat turn: decision graph → orchestrator (or OOS short-circuit).

Ported from BookMe AI ``agents/chat_pipeline.py``; wired to Axiom IdentityContext.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Literal

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from agents.decision_bridge import map_decision_to_agent_state
from agents.decision_graph import EmitFn, build_decision_input
from agents.drive_file_pick import try_consume_drive_pick
from agents.escalation_confirmation import (
    classify_confirmation,
    get_pending_low_confidence_question,
)
from agents.orchestrator import AgentOrchestrator
from agents.tools.memory_tool import MemoryTool
from domain.escalation_reasons import (
    LOW_RAG_CONFIDENCE,
)
from infrastructure.observability import (
    get_current_trace_id,
    langfuse_turn_attributes,
    observe,
    update_current_observation,
    update_current_trace,
)
from services.admissions.onboarding_route import apply_onboarding_patch_overrides
from services.identity.context import IdentityContext
from services.identity.recall_context import build_recall_context
from services.language import resolve_reply_language, t

Verdict = Literal["proceed", "out_of_scope"]


async def _noop_emit(_: dict[str, Any]) -> None:
    return None


@dataclass
class ChatResult:
    answer: str
    verdict: Verdict
    route: str
    routes: list[str]
    session_id: str
    latency_ms: int
    timings: dict[str, int] = field(default_factory=dict)
    trace_id: str | None = None


def _routes_from_patch(patch: dict, *, verdict: Verdict) -> tuple[str, list[str]]:
    decisions = patch.get("route_decisions") or []
    names = [d.get("route", "direct") for d in decisions if d.get("route")]
    if verdict == "out_of_scope" and not names:
        return "out_of_scope", ["out_of_scope"]
    if not names:
        return "direct", ["direct"]
    return names[0], names


@observe(name="chat_turn")
async def run_chat_turn(
    *,
    ctx: IdentityContext,
    message: str,
    decision_graph: Any,
    orchestrator: AgentOrchestrator,
    memory_tool: MemoryTool | None = None,
    emit: EmitFn | None = None,
    channel: str = "http_dev",
    media_url: str | None = None,
    extra_metadata: dict[str, Any] | None = None,
) -> ChatResult:
    emit_fn: EmitFn = emit or _noop_emit
    t_total = time.perf_counter()
    timings: dict[str, int] = {}
    memory = memory_tool or MemoryTool()
    memory_context, student_profile_context = build_recall_context(ctx, memory)
    reply_language = resolve_reply_language(
        message=message,
        language_pref=ctx.language_pref,
    )
    pending_escalation_message = (
        get_pending_low_confidence_question(
            memory_tool=memory,
            tenant_id=ctx.tenant_id,
            user_id=(
                ctx.student_id
                or ctx.phone
            ),
            session_id=ctx.session_id,
        )
    )

    drive_pick_reply = try_consume_drive_pick(
        message=message,
        tenant_id=ctx.tenant_id,
        session_id=ctx.session_id,
        user_id=ctx.memory_user_id,
    )
    if drive_pick_reply is not None:
        timings["total_ms"] = int((time.perf_counter() - t_total) * 1000)
        return ChatResult(
            answer=drive_pick_reply,
            verdict="proceed",
            route="resource",
            routes=["resource"],
            session_id=ctx.session_id,
            latency_ms=timings["total_ms"],
            timings=timings,
            trace_id=get_current_trace_id(),
        )

    confirmation = (
        classify_confirmation(message)
        if pending_escalation_message
        else "none"
    )
    if (
        pending_escalation_message
        and confirmation == "no"
    ):
        timings["total_ms"] = int(
            (
                time.perf_counter()
                - t_total
            )
            * 1000
        )

        return ChatResult(
            answer=t("escalation_declined", reply_language),
            verdict="proceed",
            route="direct",
            routes=["direct"],
            session_id=ctx.session_id,
            latency_ms=timings[
                "total_ms"
            ],
            timings=timings,
            trace_id=(
                get_current_trace_id()
            ),
        )
    tenant_name = ctx.tenant_name or ctx.tenant_slug or "your tuition centre"

    turn_metadata: dict[str, Any] = {
        "tenant_id": ctx.tenant_id,
        "tenant_slug": ctx.tenant_slug,
        "channel": channel,
    }
    if extra_metadata:
        turn_metadata.update(extra_metadata)

    async with langfuse_turn_attributes(
        user_id=ctx.student_id or ctx.phone,
        session_id=ctx.session_id,
        metadata=turn_metadata,
        tags=[f"tenant:{ctx.tenant_slug}", f"channel:{channel}"] if ctx.tenant_slug else [f"channel:{channel}"],
    ):
        update_current_observation(input=(message or "")[:500])
        await emit_fn({"type": "stage_start", "stage": "decision"})
        t_dec = time.perf_counter()
        config: RunnableConfig = {"configurable": {"emit": emit_fn}}
        decision_out = await decision_graph.ainvoke(
            build_decision_input(message=message, router_context=memory_context),
            config=config,
        )
        timings["decision_ms"] = int((time.perf_counter() - t_dec) * 1000)

        patch = map_decision_to_agent_state(
            decision_out,
            messages=[HumanMessage(content=message)],
            memory_context=memory_context,
            tenant_id=ctx.tenant_id,
            user_id=ctx.student_id or ctx.phone,
            student_id=ctx.student_id or "",
            student_name=ctx.student_name or "",
            phone=ctx.phone,
            session_id=ctx.session_id,
            tenant_name=tenant_name,
            is_enrolled=ctx.is_enrolled,
            enrolled_class_ids=list(ctx.enrolled_class_ids),
            student_profile_context=student_profile_context,
            media_url=media_url,
            language_pref=reply_language,
        )
        verdict: Verdict = (
            "out_of_scope" if patch.get("verdict") == "out_of_scope" else "proceed"
        )

        if apply_onboarding_patch_overrides(
            patch,
            tenant_id=ctx.tenant_id,
            phone=ctx.phone,
            student_exists=ctx.student_exists,
            message=message,
        ):
            verdict = "proceed"
        elif media_url and verdict == "proceed":
            patch["route_decisions"] = [
                {
                    "route": "payment_check",
                    "action": "check",
                    "params": {},
                    "confidence": 1.0,
                    "reasoning": "payment receipt image attached",
                }
            ]

        if (
            pending_escalation_message
            and confirmation == "yes"
        ):
            verdict = "proceed"

            patch["verdict"] = "proceed"

            patch[
                "pending_escalation_reason"
            ] = LOW_RAG_CONFIDENCE

            patch[
                "pending_escalation_message"
            ] = pending_escalation_message

            patch["route_decisions"] = [
                {
                    "route": "escalation",
                    "action":
                        "confirmed_handoff",
                    "params": {
                        "reason_code":
                            LOW_RAG_CONFIDENCE,
                    },
                    "confidence": 1.0,
                    "reasoning": (
                        "Student confirmed "
                        "low-confidence tutor "
                        "handoff."
                    ),
                }
            ]

        if verdict == "out_of_scope":
            answer = patch.get("final_answer") or ""
            route, routes = _routes_from_patch(patch, verdict=verdict)
            timings["total_ms"] = int((time.perf_counter() - t_total) * 1000)
            update_current_trace(metadata={"verdict": verdict, "routes": routes}, tags=[verdict])
            return ChatResult(
                answer=answer,
                verdict=verdict,
                route=route,
                routes=routes,
                session_id=ctx.session_id,
                latency_ms=timings["total_ms"],
                timings=timings,
                trace_id=get_current_trace_id(),
            )

        t_orch = time.perf_counter()
        final_state = await orchestrator.arun_state(patch, config=config)
        timings["orchestrator_ms"] = int((time.perf_counter() - t_orch) * 1000)
        timings["total_ms"] = int((time.perf_counter() - t_total) * 1000)

        agent = orchestrator._to_agent_response(final_state, timings["orchestrator_ms"])
        update_current_trace(
            metadata={"verdict": verdict, "routes": agent.routes},
            tags=[verdict],
        )
        update_current_observation(output=(agent.answer or "")[:500])
        return ChatResult(
            answer=agent.answer,
            verdict=verdict,
            route=agent.route,
            routes=agent.routes,
            session_id=ctx.session_id,
            latency_ms=timings["total_ms"],
            timings=timings,
            trace_id=get_current_trace_id(),
        )
