"""Procedural memory store — tenant-scoped ``mem_procedures`` lookup.

Adapted from Week 13 ``memory/procedural_store.py`` (MVP: name lookup only).
"""

from __future__ import annotations

from loguru import logger

from infrastructure.db.supabase_client import get_supabase_client
from memory.schemas import Procedure


class ProceduralMemoryStore:
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
                .select("id, tenant_id, name, description, steps")
                .eq("tenant_id", tenant_id)
                .eq("name", name)
                .eq("active", True)
                .limit(1)
                .execute()
            )
            rows = response.data or []
        except Exception as exc:
            logger.warning("Procedural lookup failed: {}", exc)
            return None

        if not rows:
            return None
        row = rows[0]
        return Procedure(
            id=str(row["id"]),
            tenant_id=str(row["tenant_id"]),
            name=str(row["name"]),
            description=str(row.get("description") or ""),
            steps=row.get("steps") or [],
        )

    def list_procedures(self, *, tenant_id: str) -> list[Procedure]:
        try:
            client = get_supabase_client()
            response = (
                client.table("mem_procedures")
                .select("id, tenant_id, name, description, steps")
                .eq("tenant_id", tenant_id)
                .eq("active", True)
                .order("name")
                .execute()
            )
            rows = response.data or []
        except Exception as exc:
            logger.warning("Procedural list failed: {}", exc)
            return []

        return [
            Procedure(
                id=str(row["id"]),
                tenant_id=str(row["tenant_id"]),
                name=str(row["name"]),
                description=str(row.get("description") or ""),
                steps=row.get("steps") or [],
            )
            for row in rows
        ]
