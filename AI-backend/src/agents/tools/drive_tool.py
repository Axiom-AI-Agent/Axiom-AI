"""Drive tool — class-scoped paper/textbook/syllabus search under a tenant root."""

from __future__ import annotations

import json
import time
from typing import Any

from loguru import logger

from infrastructure.config import DRIVE_ALLOWED_FOLDERS
from infrastructure.db.supabase_client import get_supabase_client
from infrastructure.observability import observe
from services.drive_service.drive_client import (
    build_drive_backend,
    find_child_folder,
    normalize_folder_compact,
    normalize_folder_key,
    resolve_subfolder_id,
)

_CACHE_TTL_SECONDS = 300.0
_class_folder_cache: dict[tuple[str, str], tuple[float, str]] = {}


def _normalize_drive_folder_id(raw: str | None) -> str | None:
    """Strip URL query junk users paste from Drive share links (e.g. ``?usp=drive_link``)."""
    if raw is None:
        return None
    value = str(raw).strip()
    if not value:
        return None
    return value.split("?", 1)[0].strip() or None


def clear_class_folder_cache() -> None:
    _class_folder_cache.clear()


_ENROLLED_STATUSES = frozenset({"active", "pending"})


def _class_name_candidates(row: dict[str, Any]) -> list[str]:
    """Labels used to detect a class in the student message (subject is OK here)."""
    name = str(row.get("name") or "").strip()
    subject = str(row.get("subject") or "").strip()
    grade = str(row.get("grade") or "").strip()
    candidates: list[str] = []
    for value in (
        name,
        subject,
        f"{grade} {subject}".strip(),
        f"{subject} {grade}".strip(),
        f"{grade} {name}".strip(),
    ):
        if value and value not in candidates:
            candidates.append(value)
    return candidates


def _drive_folder_candidates(row: dict[str, Any]) -> list[str]:
    """Drive child-folder names — dashboard class name, not a bare subject.

    Bare ``Physics`` would also match a sibling ``Physics Revision`` folder the
    student is not enrolled in. Folder names must match the Classes page.
    """
    name = str(row.get("name") or "").strip()
    subject = str(row.get("subject") or "").strip()
    grade = str(row.get("grade") or "").strip()
    candidates: list[str] = []
    for value in (
        name,
        f"{grade} {subject}".strip() if grade and subject else "",
        f"{subject} {grade}".strip() if grade and subject else "",
    ):
        if value and value not in candidates:
            candidates.append(value)
    return candidates


_HINT_SKIP_TOKENS = {
    "paper",
    "papers",
    "past",
    "tute",
    "tutes",
    "textbook",
    "textbooks",
    "syllabus",
    "file",
    "files",
    "folder",
    "send",
    "have",
    "last",
    "week",
}


def _class_mentioned(row: dict[str, Any], hint: str) -> bool:
    compact_hint = normalize_folder_compact(hint)
    hint_tokens = set(normalize_folder_key(hint).split())
    if not compact_hint:
        return False
    for candidate in _class_name_candidates(row):
        compact = normalize_folder_compact(candidate)
        tokens = normalize_folder_key(candidate).split()
        if compact and len(compact) >= 4 and compact in compact_hint:
            return True
        if compact_hint and len(compact_hint) >= 4 and compact_hint in compact:
            return True
        for tok in tokens:
            if len(tok) < 4 or tok.isdigit() or tok in _HINT_SKIP_TOKENS:
                continue
            if tok in hint_tokens:
                return True
    return False


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
        return _normalize_drive_folder_id(data.get("drive_folder_id"))

    def _load_classes(self, tenant_id: str, class_ids: list[str]) -> list[dict[str, Any]]:
        ids = [cid.strip() for cid in class_ids if cid and str(cid).strip()]
        if not ids:
            return []
        client = get_supabase_client()
        response = (
            client.table("subject_classes")
            .select("id, name, subject, grade")
            .eq("tenant_id", tenant_id)
            .in_("id", ids)
            .execute()
        )
        by_id = {row["id"]: row for row in (response.data or []) if row.get("id")}
        return [by_id[cid] for cid in ids if cid in by_id]

    def _enrolled_class_ids(self, tenant_id: str, student_id: str) -> set[str]:
        client = get_supabase_client()
        response = (
            client.table("enrollments")
            .select("class_id, status")
            .eq("tenant_id", tenant_id)
            .eq("student_id", student_id)
            .execute()
        )
        return {
            str(row["class_id"])
            for row in (response.data or [])
            if row.get("class_id") and row.get("status") in _ENROLLED_STATUSES
        }

    def _assert_allowed_folder(self, folder: str | None) -> str:
        normalized = (folder or "papers").strip().lower().strip("/")
        if normalized not in DRIVE_ALLOWED_FOLDERS:
            raise ValueError(
                f"Folder '{folder}' not allowed. Use one of: {', '.join(sorted(DRIVE_ALLOWED_FOLDERS))}"
            )
        return normalized

    def _select_classes(
        self,
        rows: list[dict[str, Any]],
        hint: str | None,
    ) -> list[dict[str, Any]]:
        if len(rows) <= 1 or not (hint or "").strip():
            return rows
        matched = [row for row in rows if _class_mentioned(row, hint or "")]
        return matched or rows

    def _resolve_class_folder(
        self,
        *,
        tenant_id: str,
        root_id: str,
        row: dict[str, Any],
    ) -> str | None:
        class_id = str(row.get("id") or "")
        cache_key = (tenant_id, class_id)
        cached = _class_folder_cache.get(cache_key)
        now = time.monotonic()
        if cached is not None:
            expires_at, folder_id = cached
            if now < expires_at:
                return folder_id
            _class_folder_cache.pop(cache_key, None)

        backend = self._backend_instance()
        folder_id = find_child_folder(
            backend,
            parent_id=root_id,
            names=_drive_folder_candidates(row),
        )
        if folder_id:
            _class_folder_cache[cache_key] = (now + _CACHE_TTL_SECONDS, folder_id)
        return folder_id

    def _collect_files(
        self,
        *,
        tenant_id: str,
        folder: str,
        class_ids: list[str],
        query: str | None,
        hint: str | None,
        page_size: int,
        student_id: str | None = None,
    ) -> dict[str, Any]:
        ids = [cid.strip() for cid in class_ids if cid and str(cid).strip()]
        if not ids:
            return {"ok": False, "error": "class_ids is required"}
        if student_id and str(student_id).strip():
            allowed = self._enrolled_class_ids(tenant_id, str(student_id).strip())
            ids = [cid for cid in ids if cid in allowed]
            if not ids:
                return {"ok": False, "error": "Student is not enrolled in the requested classes"}

        root_id = self._get_drive_root(tenant_id)
        if not root_id:
            return {"ok": False, "error": f"Unknown tenant or missing drive_folder_id: {tenant_id}"}

        rows = self._load_classes(tenant_id, ids)
        if not rows:
            return {"ok": False, "error": "No matching classes for this tenant"}

        selected = self._select_classes(rows, hint)
        backend = self._backend_instance()
        files: list[dict[str, Any]] = []
        missing: list[str] = []

        for row in selected:
            label = str(row.get("name") or row.get("subject") or row.get("id"))
            class_folder_id = self._resolve_class_folder(
                tenant_id=tenant_id,
                root_id=root_id,
                row=row,
            )
            if not class_folder_id:
                missing.append(label)
                continue
            subfolder_id = resolve_subfolder_id(
                backend,
                root_folder_id=class_folder_id,
                subfolder=folder,
            )
            if not subfolder_id:
                missing.append(f"{label}/{folder}")
                continue
            found = backend.list_files(
                folder_id=subfolder_id,
                query=query.strip() if query else None,
                page_size=page_size,
            )
            files.extend(
                {
                    **item,
                    "folder": folder,
                    "tenant_id": tenant_id,
                    "class_id": row.get("id"),
                    "class_name": label,
                }
                for item in found
            )

        payload: dict[str, Any] = {"ok": True, "files": files}
        if missing and not files:
            expected = missing[0] if missing else "class"
            payload["message"] = (
                f"No files in {folder}/ for this class. "
                f"Create a Drive folder named like '{expected}' under the institute root, "
                f"with papers/, textbooks/, and syllabus/ inside."
            )
        elif not files:
            payload["message"] = f"No files matching '{query}' in {folder}/" if query else f"No files in {folder}/"
        elif missing:
            payload["message"] = "Skipped classes with no Drive folder: " + ", ".join(missing)
        return payload

    @observe(name="drive_search")
    def drive_search(
        self,
        *,
        tenant_id: str,
        query: str,
        folder: str | None = "papers",
        class_ids: list[str] | None = None,
        hint: str | None = None,
        student_id: str | None = None,
    ) -> str:
        if not tenant_id:
            return json.dumps({"ok": False, "error": "tenant_id is required"})
        if not query or not query.strip():
            return json.dumps({"ok": False, "error": "query is required"})
        try:
            allowed = self._assert_allowed_folder(folder)
            payload = self._collect_files(
                tenant_id=tenant_id,
                folder=allowed,
                class_ids=list(class_ids or []),
                query=query.strip(),
                hint=hint or query,
                page_size=5,
                student_id=student_id,
            )
            return json.dumps(payload)
        except ValueError as exc:
            return json.dumps({"ok": False, "error": str(exc)})
        except Exception as exc:
            logger.exception("drive_search failed: {}", exc)
            return json.dumps({"ok": False, "error": str(exc)})

    @observe(name="drive_list")
    def drive_list(
        self,
        *,
        tenant_id: str,
        folder: str = "papers",
        class_ids: list[str] | None = None,
        hint: str | None = None,
        student_id: str | None = None,
    ) -> str:
        if not tenant_id:
            return json.dumps({"ok": False, "error": "tenant_id is required"})
        try:
            allowed = self._assert_allowed_folder(folder)
            payload = self._collect_files(
                tenant_id=tenant_id,
                folder=allowed,
                class_ids=list(class_ids or []),
                query=None,
                hint=hint,
                page_size=20,
                student_id=student_id,
            )
            return json.dumps(payload)
        except ValueError as exc:
            return json.dumps({"ok": False, "error": str(exc)})
        except Exception as exc:
            logger.exception("drive_list failed: {}", exc)
            return json.dumps({"ok": False, "error": str(exc)})
