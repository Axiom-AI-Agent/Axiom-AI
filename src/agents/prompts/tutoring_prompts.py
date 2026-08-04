"""Local prompt seeds — used only when Langfuse is unavailable (offline dev)."""

from __future__ import annotations

from agents.prompts import agent_prompts as ap

# Mirror Langfuse names → local fallback text (PromptService offline path).
LOCAL_PROMPTS: dict[str, str | list[dict[str, str]]] = {
    ap.LANGFUSE_PROMPT_NAMES["guardrail_system"]: ap._GUARDRAIL_SYSTEM_FALLBACK.strip(),
    ap.LANGFUSE_PROMPT_NAMES["router_system"]: ap._ROUTER_SYSTEM_FALLBACK.strip(),
    ap.LANGFUSE_PROMPT_NAMES["router_hard_rules"]: ap._ROUTER_HARD_RULES_FALLBACK.strip(),
    ap.LANGFUSE_PROMPT_NAMES["router_user"]: ap._ROUTER_USER_FALLBACK.strip(),
    ap.LANGFUSE_PROMPT_NAMES["direct_system"]: ap._DIRECT_SYSTEM_FALLBACK.strip(),
    ap.LANGFUSE_PROMPT_NAMES["merge_system"]: ap._MERGE_SYSTEM_FALLBACK.strip(),
    ap.LANGFUSE_PROMPT_NAMES["out_of_scope_reply"]: ap._OUT_OF_SCOPE_REPLY_FALLBACK.strip(),
    ap.LANGFUSE_PROMPT_NAMES["admissions_stub"]: ap._ADMISSIONS_STUB_FALLBACK.strip(),
    ap.LANGFUSE_PROMPT_NAMES["resource_stub"]: ap._RESOURCE_STUB_FALLBACK.strip(),
    ap.LANGFUSE_PROMPT_NAMES["payment_stub"]: ap._PAYMENT_STUB_FALLBACK.strip(),
    ap.LANGFUSE_PROMPT_NAMES["escalation_stub"]: ap._ESCALATION_STUB_FALLBACK.strip(),
}

# Legacy aliases kept for older tests
OUT_OF_SCOPE_REPLY = LOCAL_PROMPTS[ap.LANGFUSE_PROMPT_NAMES["out_of_scope_reply"]]
GUARDRAIL_SYSTEM = LOCAL_PROMPTS[ap.LANGFUSE_PROMPT_NAMES["guardrail_system"]]
ROUTER_SYSTEM = LOCAL_PROMPTS[ap.LANGFUSE_PROMPT_NAMES["router_system"]]
MERGE_SYSTEM = LOCAL_PROMPTS[ap.LANGFUSE_PROMPT_NAMES["merge_system"]]
DIRECT_SYSTEM = LOCAL_PROMPTS[ap.LANGFUSE_PROMPT_NAMES["direct_system"]]
