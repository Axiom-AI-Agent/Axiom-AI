"""Shared CRM client protocol for agent nodes (direct + MCP paths)."""

from __future__ import annotations

import json
from typing import Any, Protocol


class CrmClient(Protocol):
    async def get_student(self, *, tenant_id: str, phone: str) -> dict[str, Any]: ...

    async def list_classes(
        self,
        *,
        tenant_id: str,
        subject: str | None = None,
        grade: str | None = None,
    ) -> list[dict[str, Any]]: ...

    async def register_student(
        self,
        *,
        tenant_id: str,
        phone: str,
        student_id: str,
        name: str | None = None,
        school: str | None = None,
        district: str | None = None,
        consent: bool = False,
    ) -> dict[str, Any]: ...

    async def create_enrollment(
        self,
        *,
        tenant_id: str,
        student_id: str,
        class_id: str,
    ) -> dict[str, Any]: ...

    async def create_escalation(
        self,
        *,
        tenant_id: str,
        student_id: str,
        reason_code: str,
        media_url: str | None = None,
        student_message: str | None = None,
        enrollment_id: str | None = None,
    ) -> dict[str, Any]: ...

    async def resolve_escalation(
        self,
        *,
        tenant_id: str,
        escalation_id: str,
    ) -> dict[str, Any]: ...


class DirectCrmClient:
    """In-process CRM path (dev/tests without MCP subprocesses)."""

    def __init__(self) -> None:
        from agents.tools.crm_tool import CrmTool

        self._tool = CrmTool()

    async def get_student(self, *, tenant_id: str, phone: str) -> dict[str, Any]:
        return json.loads(self._tool.get_student(tenant_id=tenant_id, phone=phone))

    async def list_classes(
        self,
        *,
        tenant_id: str,
        subject: str | None = None,
        grade: str | None = None,
    ) -> list[dict[str, Any]]:
        payload = json.loads(
            self._tool.list_classes(tenant_id=tenant_id, subject=subject, grade=grade)
        )
        return payload.get("classes") or []

    async def register_student(self, **kwargs: Any) -> dict[str, Any]:
        return json.loads(self._tool.register_student(**kwargs))

    async def create_enrollment(self, **kwargs: Any) -> dict[str, Any]:
        return json.loads(self._tool.create_enrollment(**kwargs))

    async def create_escalation(self, **kwargs: Any) -> dict[str, Any]:
        return json.loads(self._tool.create_escalation(**kwargs))

    async def resolve_escalation(self, **kwargs: Any) -> dict[str, Any]:
        return json.loads(self._tool.resolve_escalation(**kwargs))


class McpCrmClient:
    """MCP CRM tools → async dispatch."""

    def __init__(self, tools_by_name: dict[str, Any]) -> None:
        self._tools = tools_by_name

    async def _invoke(self, tool_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        tool = self._tools.get(tool_name)
        if tool is None:
            return {"ok": False, "error": f"MCP tool unavailable: {tool_name}"}
        raw = await tool.ainvoke(payload)
        if isinstance(raw, list):
            text = next(
                (item.get("text", "") for item in raw if isinstance(item, dict)),
                str(raw),
            )
        else:
            text = str(raw)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"ok": False, "error": text}

    async def get_student(self, *, tenant_id: str, phone: str) -> dict[str, Any]:
        return await self._invoke("get_student", {"tenant_id": tenant_id, "phone": phone})

    async def list_classes(
        self,
        *,
        tenant_id: str,
        subject: str | None = None,
        grade: str | None = None,
    ) -> list[dict[str, Any]]:
        payload = await self._invoke(
            "list_classes",
            {"tenant_id": tenant_id, "subject": subject, "grade": grade},
        )
        return payload.get("classes") or []

    async def register_student(self, **kwargs: Any) -> dict[str, Any]:
        return await self._invoke("register_student", kwargs)

    async def create_enrollment(self, **kwargs: Any) -> dict[str, Any]:
        return await self._invoke("create_enrollment", kwargs)

    async def create_escalation(self, **kwargs: Any) -> dict[str, Any]:
        return await self._invoke("create_escalation", kwargs)

    async def resolve_escalation(self, **kwargs: Any) -> dict[str, Any]:
        return await self._invoke("resolve_escalation", kwargs)
