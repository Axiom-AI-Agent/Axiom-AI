"""Build recall context (student profile + ST turns) before the decision graph."""

from __future__ import annotations

from agents.tools.memory_tool import MemoryTool
from services.admissions.onboarding_route import onboarding_router_context_hint
from services.identity.context import IdentityContext
from services.language import LANGUAGE_NAMES, normalize_language_pref


def format_student_profile(ctx: IdentityContext) -> str:
    """Structured student block for router and agent prompts."""
    if not ctx.student_exists:
        return (
            "[STUDENT PROFILE]\n"
            f"Status: Unknown visitor (not registered)\n"
            f"Phone: {ctx.phone}"
        )

    lines = ["[STUDENT PROFILE]", f"Name: {ctx.student_name or 'Unknown'}", f"Phone: {ctx.phone}"]
    if ctx.is_enrolled:
        classes = ", ".join(ctx.active_class_names) if ctx.active_class_names else "enrolled class"
        if ctx.enrollment_status == "active":
            lines.append(f"Status: Enrolled in {classes}")
        else:
            lines.append(f"Status: Pending enrollment in {classes} (payment may be awaiting approval)")
    else:
        lines.append("Status: Registered but not enrolled in a class yet")
    lang = normalize_language_pref(ctx.language_pref)
    lines.append(f"Preferred language: {LANGUAGE_NAMES[lang]} ({lang})")
    return "\n".join(lines)


def build_recall_context(
    ctx: IdentityContext,
    memory_tool: MemoryTool,
    *,
    limit: int = 10,
) -> tuple[str, str]:
    """Return (full_router_context, student_profile_context) for one chat turn."""
    student_profile = format_student_profile(ctx)
    parts = [student_profile]

    try:
        st_turns = memory_tool.recall_turns(
            tenant_id=ctx.tenant_id,
            session_id=ctx.session_id,
            user_id=ctx.memory_user_id,
            limit=limit,
        )
    except Exception:
        st_turns = "(no prior turns)"

    if st_turns and st_turns != "(no prior turns)":
        parts.append(f"[RECENT CONVERSATION]\n{st_turns}")

    onboarding_hint = onboarding_router_context_hint(
        tenant_id=ctx.tenant_id,
        phone=ctx.phone,
        student_exists=ctx.student_exists,
    )
    if onboarding_hint:
        parts.append(onboarding_hint.strip())

    return "\n\n".join(parts), student_profile
