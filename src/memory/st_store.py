"""Short-term memory — ring buffer over Supabase st_turns."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from loguru import logger

from domain.enums import MessageRole
from infrastructure.config import ST_MAX_TURNS, ST_TTL_SECONDS
from infrastructure.db.supabase_client import get_supabase_client
from memory.schemas import ConversationTurn


class STStore:
    """Session-scoped turn buffer backed by st_turns."""

    def recall_turns(
        self,
        *,
        tenant_id: str,
        session_id: str,
        limit: int | None = None,
    ) -> list[ConversationTurn]:
        max_rows = limit or ST_MAX_TURNS
        try:
            client = get_supabase_client()
            response = (
                client.table("st_turns")
                .select("role, content, created_at")
                .eq("tenant_id", tenant_id)
                .eq("session_id", session_id)
                .order("created_at", desc=True)
                .limit(max_rows)
                .execute()
            )
        except Exception as exc:
            logger.warning("ST recall failed for {}: {}", session_id, exc)
            return []

        cutoff = datetime.now(tz=UTC) - timedelta(seconds=ST_TTL_SECONDS)
        turns: list[ConversationTurn] = []
        for row in reversed(response.data or []):
            created_raw = row.get("created_at")
            created_at: datetime | None = None
            if created_raw:
                created_at = datetime.fromisoformat(str(created_raw).replace("Z", "+00:00"))
                if created_at < cutoff:
                    continue
            turns.append(
                ConversationTurn(
                    role=str(row["role"]),
                    content=str(row["content"]),
                    created_at=created_at,
                )
            )
        return turns

    def add_turn(
        self,
        *,
        tenant_id: str,
        session_id: str,
        user_id: str,
        role: MessageRole | str,
        content: str,
    ) -> None:
        role_value = role.value if isinstance(role, MessageRole) else role
        try:
            client = get_supabase_client()
            client.table("st_turns").insert(
                {
                    "tenant_id": tenant_id,
                    "user_id": user_id,
                    "session_id": session_id,
                    "role": role_value,
                    "content": content,
                }
            ).execute()
            self._trim_session(tenant_id=tenant_id, session_id=session_id)
        except Exception as exc:
            logger.warning("ST add_turn failed for {}: {}", session_id, exc)

    def _trim_session(self, *, tenant_id: str, session_id: str) -> None:
        try:
            client = get_supabase_client()
            response = (
                client.table("st_turns")
                .select("id")
                .eq("tenant_id", tenant_id)
                .eq("session_id", session_id)
                .order("created_at", desc=True)
                .execute()
            )
            rows = response.data or []
            if len(rows) <= ST_MAX_TURNS:
                return
            stale_ids = [row["id"] for row in rows[ST_MAX_TURNS:]]
            client.table("st_turns").delete().in_("id", stale_ids).execute()
        except Exception as exc:
            logger.debug("ST trim skipped for {}: {}", session_id, exc)

    @staticmethod
    def format_history(turns: list[ConversationTurn]) -> str:
        if not turns:
            return ""
        lines = [f"{turn.role}: {turn.content}" for turn in turns]
        return "\n".join(lines)
