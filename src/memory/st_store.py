"""Short-term memory store — Supabase ``st_turns`` ring buffer.

Adapted from Week 13 ``memory/st_store.py`` for tenant-scoped Supabase REST client.
"""

from __future__ import annotations

from loguru import logger

from domain.enums import MessageRole
from infrastructure.config import ST_MAX_TURNS
from infrastructure.db.supabase_client import get_supabase_client
from memory.schemas import ConversationTurn


class ShortTermMemoryStore:
    """Recent conversation turns per tenant/session."""

    def recall_turns(
        self,
        *,
        tenant_id: str,
        session_id: str,
        user_id: str | None = None,
        limit: int = 10,
    ) -> list[ConversationTurn]:
        try:
            client = get_supabase_client()
            query = (
                client.table("st_turns")
                .select("role, content, created_at")
                .eq("tenant_id", tenant_id)
                .eq("session_id", session_id)
                .order("created_at", desc=False)
                .limit(limit)
            )
            if user_id:
                query = query.eq("user_id", user_id)
            response = query.execute()
            rows = response.data or []
        except Exception as exc:
            logger.warning("ST recall failed: {}", exc)
            return []

        turns: list[ConversationTurn] = []
        for row in rows:
            role = row.get("role", "user")
            if role not in ("user", "assistant"):
                role = "user" if role == MessageRole.USER.value else "assistant"
            turns.append(
                ConversationTurn(
                    tenant_id=tenant_id,
                    user_id=user_id or "",
                    session_id=session_id,
                    role=role,
                    content=str(row.get("content") or ""),
                )
            )
        return turns

    def add_turn(self, turn: ConversationTurn) -> None:
        try:
            client = get_supabase_client()
            client.table("st_turns").insert(
                {
                    "tenant_id": turn.tenant_id,
                    "user_id": turn.user_id,
                    "session_id": turn.session_id,
                    "role": turn.role,
                    "content": turn.content,
                }
            ).execute()
            self._trim(turn.tenant_id, turn.session_id)
        except Exception as exc:
            logger.warning("ST add_turn failed: {}", exc)

    def _trim(self, tenant_id: str, session_id: str) -> None:
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
            for row in rows[ST_MAX_TURNS:]:
                client.table("st_turns").delete().eq("id", row["id"]).execute()
        except Exception as exc:
            logger.debug("ST trim skipped: {}", exc)

    @staticmethod
    def format_turns(turns: list[ConversationTurn]) -> str:
        if not turns:
            return ""
        lines: list[str] = []
        for turn in turns:
            label = "User" if turn.role == "user" else "Assistant"
            lines.append(f"{label}: {turn.content}")
        return "\n".join(lines)

    def recent_pairs(
        self,
        *,
        tenant_id: str,
        user_id: str,
        session_id: str,
        k: int = 10,
    ) -> list[tuple[str, str]]:
        """Return up to k (user, assistant) pairs — BookMe SessionStore interface."""
        turns = self.recall_turns(
            tenant_id=tenant_id,
            session_id=session_id,
            user_id=user_id,
            limit=k * 2,
        )
        pairs: list[tuple[str, str]] = []
        i = 0
        while i < len(turns) - 1:
            if turns[i].role == "user" and turns[i + 1].role == "assistant":
                pairs.append((turns[i].content, turns[i + 1].content))
                i += 2
            else:
                i += 1
        return pairs[-k:]
