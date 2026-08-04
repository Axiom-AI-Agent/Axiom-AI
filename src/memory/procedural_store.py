"""Procedural memory — tenant onboarding workflows from mem_procedures."""

from __future__ import annotations

from loguru import logger

from infrastructure.db.supabase_client import get_supabase_client
from memory.schemas import Procedure


class ProceduralStore:
    """Lookup procedural workflows scoped by tenant."""

    def get_procedure(
        self,
        *,
        tenant_id: str,
        name: str,
    ) -> Procedure | None:
        try:
            client = get_supabase_client()
            response = (
                client.table("mem_procedures")
                .select("id, tenant_id, name, description, steps, active")
                .eq("tenant_id", tenant_id)
                .eq("name", name)
                .eq("active", True)
                .limit(1)
                .execute()
            )
        except Exception as exc:
            logger.warning("Procedural lookup failed for {}/{}: {}", tenant_id, name, exc)
            return None

        rows = response.data or []
        if not rows:
            return None
        row = rows[0]
        steps = row.get("steps") or []
        if not isinstance(steps, list):
            steps = []
        return Procedure(
            id=str(row["id"]),
            tenant_id=str(row["tenant_id"]),
            name=str(row["name"]),
            description=row.get("description"),
            steps=steps,
            active=bool(row.get("active", True)),
        )

    def list_procedures(self, *, tenant_id: str) -> list[Procedure]:
        try:
            client = get_supabase_client()
            response = (
                client.table("mem_procedures")
                .select("id, tenant_id, name, description, steps, active")
                .eq("tenant_id", tenant_id)
                .eq("active", True)
                .execute()
            )
        except Exception as exc:
            logger.warning("Procedural list failed for {}: {}", tenant_id, exc)
            return []

        procedures: list[Procedure] = []
        for row in response.data or []:
            steps = row.get("steps") or []
            if not isinstance(steps, list):
                steps = []
            procedures.append(
                Procedure(
                    id=str(row["id"]),
                    tenant_id=str(row["tenant_id"]),
                    name=str(row["name"]),
                    description=row.get("description"),
                    steps=steps,
                    active=bool(row.get("active", True)),
                )
            )
        return procedures
