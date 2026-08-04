"""Drive tool — tenant-scoped paper/textbook/syllabus search."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger

from infrastructure.config import DRIVE_ALLOWED_FOLDERS
from infrastructure.db.supabase_client import get_supabase_client
from infrastructure.observability import observe
from services.drive_service.drive_client import build_drive_backend, resolve_subfolder_id


class DriveTool:
    """Business logic for drive_search / drive_list — used by drive_server and REST."""

    def __init__(self, backend: Any | None = None) -> None:
        self._backend = backend

    def _backend_instance(self) -> Any:
        if self._backend is None:
            self._backend = build_drive_backend()
        return self._backend

    def _get_drive_root(self, tenant_id: str) -> str | None:
        client = get_supabase_client()
        row = client.table("tenants").select("id, drive_folder_id").eq("id", tenant_id).limit(1).execute()
        data = (row.data or [{}])[0]
        if data.get("id") != tenant_id:
            return None
        return data.get("drive_folder_id")

    def _assert_allowed_folder(self, folder: str | None) -> str:
        normalized = (folder or "papers").strip().lower().strip("/")
        if normalized not in DRIVE_ALLOWED_FOLDERS:
            raise ValueError(
                f"Folder '{folder}' not allowed. Use one of: {', '.join(sorted(DRIVE_ALLOWED_FOLDERS))}"
            )
        return normalized

    @observe(name="drive_search")
    def drive_search(
        self,
        *,
        tenant_id: str,
        query: str,
        folder: str | None = "papers",
    ) -> str:
        if not tenant_id:
            return json.dumps({"ok": False, "error": "tenant_id is required"})
        if not query or not query.strip():
            return json.dumps({"ok": False, "error": "query is required"})
        try:
            allowed = self._assert_allowed_folder(folder)
            root_id = self._get_drive_root(tenant_id)
            if not root_id:
                return json.dumps({"ok": False, "error": f"Unknown tenant or missing drive_folder_id: {tenant_id}"})

            backend = self._backend_instance()
            subfolder_id = resolve_subfolder_id(backend, root_folder_id=root_id, subfolder=allowed)
            search_root = subfolder_id or root_id
            files = backend.list_files(folder_id=search_root, query=query.strip(), page_size=5)
            enriched = [{**f, "folder": allowed, "tenant_id": tenant_id} for f in files]
            if not enriched:
                return json.dumps(
                    {
                        "ok": True,
                        "files": [],
                        "message": f"No files matching '{query}' in {allowed}/",
                    }
                )
            return json.dumps({"ok": True, "files": enriched})
        except ValueError as exc:
            return json.dumps({"ok": False, "error": str(exc)})
        except Exception as exc:
            logger.exception("drive_search failed: {}", exc)
            return json.dumps({"ok": False, "error": str(exc)})

    @observe(name="drive_list")
    def drive_list(self, *, tenant_id: str, folder: str = "papers") -> str:
        if not tenant_id:
            return json.dumps({"ok": False, "error": "tenant_id is required"})
        try:
            allowed = self._assert_allowed_folder(folder)
            root_id = self._get_drive_root(tenant_id)
            if not root_id:
                return json.dumps({"ok": False, "error": f"Unknown tenant: {tenant_id}"})

            backend = self._backend_instance()
            subfolder_id = resolve_subfolder_id(backend, root_folder_id=root_id, subfolder=allowed)
            search_root = subfolder_id or root_id
            files = backend.list_files(folder_id=search_root, query=None, page_size=20)
            enriched = [{**f, "folder": allowed, "tenant_id": tenant_id} for f in files]
            return json.dumps({"ok": True, "files": enriched})
        except ValueError as exc:
            return json.dumps({"ok": False, "error": str(exc)})
        except Exception as exc:
            logger.exception("drive_list failed: {}", exc)
            return json.dumps({"ok": False, "error": str(exc)})
