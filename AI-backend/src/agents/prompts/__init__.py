"""Agent prompt templates (Langfuse + local fallbacks)."""

from agents.prompts.agent_prompts import (
    ALL_LANGFUSE_PROMPT_NAMES,
    LANGFUSE_PROMPT_NAMES,
    build_direct_system_prompt,
    build_guardrail_system_prompt,
    build_merge_system_prompt,
    build_router_prompt,
    get_admissions_stub_reply,
    get_escalation_stub_reply,
    get_flagged_abusive_reply,
    get_out_of_scope_reply,
    get_payment_stub_reply,
    get_resource_stub_reply,
)

__all__ = [
    "LANGFUSE_PROMPT_NAMES",
    "ALL_LANGFUSE_PROMPT_NAMES",
    "build_guardrail_system_prompt",
    "build_router_prompt",
    "build_direct_system_prompt",
    "build_merge_system_prompt",
    "get_out_of_scope_reply",
    "get_flagged_abusive_reply",
    "get_admissions_stub_reply",
    "get_resource_stub_reply",
    "get_payment_stub_reply",
    "get_escalation_stub_reply",
]
