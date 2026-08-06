"""Memory business logic — called by MCP server only (Week 13 pattern)."""

from __future__ import annotations

from memory.procedural_store import ProceduralMemoryStore
from memory.schemas import ConversationTurn
from memory.st_store import ShortTermMemoryStore


class MemoryTool:
    def __init__(
        self,
        *,
        st_store: ShortTermMemoryStore | None = None,
        procedural_store: ProceduralMemoryStore | None = None,
    ) -> None:
        self.st_store = st_store or ShortTermMemoryStore()
        self.procedural_store = procedural_store or ProceduralMemoryStore()

    def recall_turns(
        self,
        *,
        tenant_id: str,
        session_id: str,
        user_id: str,
        limit: int = 10,
    ) -> str:
        turns = self.st_store.recall_turns(
            tenant_id=tenant_id,
            session_id=session_id,
            user_id=user_id,
            limit=limit,
        )
        formatted = self.st_store.format_turns(turns)
        return formatted or "(no prior turns)"

    def add_turn(
        self,
        *,
        tenant_id: str,
        session_id: str,
        user_id: str,
        role: str,
        content: str,
    ) -> str:
        if role not in ("user", "assistant"):
            return f"Invalid role: {role}"
        self.st_store.add_turn(
            ConversationTurn(
                tenant_id=tenant_id,
                user_id=user_id,
                session_id=session_id,
                role=role,
                content=content,
            )
        )
        return f"Stored {role} turn"

    def get_procedural(self, *, tenant_id: str, name: str | None = None) -> str:
        if name:
            proc = self.procedural_store.get_procedure(tenant_id=tenant_id, name=name)
            if proc is None:
                return f"(no procedure named {name})"
            return proc.format_steps()
        procedures = self.procedural_store.list_procedures(tenant_id=tenant_id)
        if not procedures:
            return "(no procedures for tenant)"
        return "\n\n".join(p.format_steps() for p in procedures)
