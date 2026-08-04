"""Memory business logic — invoked by memory_server MCP wrapper only."""

from __future__ import annotations

import json

from domain.enums import MessageRole
from memory.procedural_store import ProceduralStore
from memory.schemas import ConversationTurn, Procedure
from memory.st_store import STStore


class MemoryTool:
    """Short-term recall and procedural lookup for agent nodes."""

    def __init__(
        self,
        *,
        st_store: STStore | None = None,
        procedural_store: ProceduralStore | None = None,
    ) -> None:
        self.st_store = st_store or STStore()
        self.procedural_store = procedural_store or ProceduralStore()

    def recall_turns(
        self,
        *,
        tenant_id: str,
        session_id: str,
        limit: int = 10,
    ) -> str:
        turns = self.st_store.recall_turns(
            tenant_id=tenant_id,
            session_id=session_id,
            limit=limit,
        )
        payload = [
            {"role": turn.role, "content": turn.content}
            for turn in turns
        ]
        return json.dumps({"turns": payload, "count": len(payload)})

    def add_turn(
        self,
        *,
        tenant_id: str,
        session_id: str,
        user_id: str,
        role: str,
        content: str,
    ) -> str:
        self.st_store.add_turn(
            tenant_id=tenant_id,
            session_id=session_id,
            user_id=user_id,
            role=MessageRole(role),
            content=content,
        )
        return json.dumps({"status": "ok"})

    def get_procedural(
        self,
        *,
        tenant_id: str,
        name: str | None = None,
    ) -> str:
        if name:
            procedure = self.procedural_store.get_procedure(tenant_id=tenant_id, name=name)
            if procedure is None:
                return json.dumps({"procedure": None})
            return json.dumps({"procedure": self._procedure_dict(procedure)})

        procedures = self.procedural_store.list_procedures(tenant_id=tenant_id)
        return json.dumps(
            {"procedures": [self._procedure_dict(item) for item in procedures]}
        )

    def turns_as_messages(
        self,
        *,
        tenant_id: str,
        session_id: str,
        limit: int = 10,
    ) -> list[ConversationTurn]:
        return self.st_store.recall_turns(
            tenant_id=tenant_id,
            session_id=session_id,
            limit=limit,
        )

    @staticmethod
    def _procedure_dict(procedure: Procedure) -> dict[str, object]:
        return {
            "id": procedure.id,
            "name": procedure.name,
            "description": procedure.description,
            "steps": procedure.steps,
            "active": procedure.active,
        }
