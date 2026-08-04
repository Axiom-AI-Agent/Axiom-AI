"""Memory dataclasses for short-term turns and procedural workflows."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ConversationTurn:
    role: str
    content: str
    created_at: datetime | None = None

    def to_message(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass(frozen=True)
class Procedure:
    id: str
    tenant_id: str
    name: str
    description: str | None
    steps: list[dict[str, object]]
    active: bool = True
