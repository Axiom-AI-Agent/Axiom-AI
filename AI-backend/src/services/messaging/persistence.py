"""Persist inbound/outbound messaging to Supabase (message_logs + st_turns)."""

from __future__ import annotations

from loguru import logger

from domain.enums import ChatChannel, MessageRole
from infrastructure.db.supabase_client import get_supabase_client
from services.identity.context import IdentityContext


class MessagePersistence:
    """Write message_logs and st_turns rows for a conversation turn."""

    def log_inbound(
        self,
        ctx: IdentityContext,
        *,
        body: str,
        intent: str = "inbound",
        media_url: str | None = None,
        channel: ChatChannel = ChatChannel.HTTP_DEV,
    ) -> None:
        content = body.strip()
        if not content and media_url:
            content = f"[media] {media_url}"

        if ctx.student_exists and ctx.student_id:
            self._insert_message_log(ctx, intent=intent, channel=channel)
            self._insert_turn(ctx, role=MessageRole.USER, content=content or "(empty)")

    def log_outbound(
        self,
        ctx: IdentityContext,
        *,
        body: str,
        intent: str = "outbound",
        channel: ChatChannel = ChatChannel.HTTP_DEV,
    ) -> None:
        if ctx.student_exists and ctx.student_id:
            self._insert_message_log(ctx, intent=intent, channel=channel)
            self._insert_turn(ctx, role=MessageRole.ASSISTANT, content=body)

    def log_staff_reply(
        self,
        ctx: IdentityContext,
        *,
        body: str,
        channel: ChatChannel = ChatChannel.HTTP_DEV,
    ) -> None:
        """Persist a staff-authored message (role=system → sender=staff in dashboard UI)."""
        if ctx.student_exists and ctx.student_id:
            self._insert_message_log(ctx, intent="staff_reply", channel=channel)
            self._insert_turn(ctx, role=MessageRole.SYSTEM, content=body)

    def _insert_message_log(
        self,
        ctx: IdentityContext,
        *,
        intent: str,
        channel: ChatChannel,
    ) -> None:
        try:
            client = get_supabase_client()
            client.table("message_logs").insert(
                {
                    "tenant_id": ctx.tenant_id,
                    "student_id": ctx.student_id,
                    "channel": channel.value,
                    "intent": intent,
                }
            ).execute()
        except Exception as exc:
            logger.warning("Failed to write message_log: {}", exc)

    def _insert_turn(self, ctx: IdentityContext, *, role: MessageRole, content: str) -> None:
        try:
            client = get_supabase_client()
            client.table("st_turns").insert(
                {
                    "tenant_id": ctx.tenant_id,
                    "user_id": ctx.student_id,
                    "session_id": ctx.session_id,
                    "role": role.value,
                    "content": content,
                }
            ).execute()
        except Exception as exc:
            logger.warning("Failed to write st_turn: {}", exc)

    def get_turns(
        self,
        *,
        tenant_id: str,
        session_id: str,
        limit: int = 30,
    ) -> list[dict[str, object]]:
        client = get_supabase_client()
        response = (
            client.table("st_turns")
            .select("id, role, content, created_at")
            .eq("tenant_id", tenant_id)
            .eq("session_id", session_id)
            .order("created_at", desc=False)
            .limit(limit)
            .execute()
        )
        return response.data or []

    def list_recent_sessions(
        self,
        *,
        tenant_id: str,
        limit: int = 50,
    ) -> list[dict[str, object]]:
        """Return the latest turn per session_id, ordered by most recent activity."""
        client = get_supabase_client()
        over_fetch = min(max(limit * 10, limit), 500)
        response = (
            client.table("st_turns")
            .select("id, session_id, user_id, role, content, created_at")
            .eq("tenant_id", tenant_id)
            .order("created_at", desc=True)
            .limit(over_fetch)
            .execute()
        )
        rows = response.data or []
        seen: set[str] = set()
        sessions: list[dict[str, object]] = []
        for row in rows:
            session_id = str(row["session_id"])
            if session_id in seen:
                continue
            seen.add(session_id)
            sessions.append(row)
            if len(sessions) >= limit:
                break
        return sessions

    def get_latest_turn(
        self,
        *,
        tenant_id: str,
        session_id: str,
    ) -> dict[str, object] | None:
        client = get_supabase_client()
        response = (
            client.table("st_turns")
            .select("id, role, content, created_at")
            .eq("tenant_id", tenant_id)
            .eq("session_id", session_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        rows = response.data or []
        return rows[0] if rows else None
