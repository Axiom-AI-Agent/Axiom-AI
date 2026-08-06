"""Memory schemas — ported from Week 13 ``memory/schemas.py`` (MVP subset)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass
class ConversationTurn:
    tenant_id: str
    user_id: str
    session_id: str
    role: Literal["user", "assistant"]
    content: str

    def to_dict(self) -> dict[str, str]:
        return {
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
        }


@dataclass
class Procedure:
    id: str
    tenant_id: str
    name: str
    description: str
    steps: list[dict[str, Any]] = field(default_factory=list)

    def format_steps(self) -> str:
        if not self.steps:
            return "No steps defined."
        lines = [f"**{self.name}**: {self.description}", "", "**Steps**:"]
        for i, step in enumerate(self.steps, 1):
            prompt = step.get("prompt") or step.get("description") or str(step)
            lines.append(f"{i}. {prompt}")
        return "\n".join(lines)
