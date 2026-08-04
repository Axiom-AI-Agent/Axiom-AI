"""Google Drive client — service account, tenant-scoped folder search."""

from __future__ import annotations

import json
import os
from typing import Any, Protocol

from loguru import logger

from infrastructure.config import DRIVE_MOCK, GOOGLE_SERVICE_ACCOUNT_JSON


class DriveBackend(Protocol):
    def list_files(
        self,
        *,
        folder_id: str,
        query: str | None = None,
        page_size: int = 10,
    ) -> list[dict[str, Any]]: ...


class MockDriveBackend:
    """In-memory Drive mock for local dev and unit tests."""

    def __init__(self, files_by_folder: dict[str, list[dict[str, Any]]] | None = None) -> None:
        self.files_by_folder = files_by_folder or {}

    def list_files(
        self,
        *,
        folder_id: str,
        query: str | None = None,
        page_size: int = 10,
    ) -> list[dict[str, Any]]:
        files = self.files_by_folder.get(folder_id, [])
        if not query:
            return files[:page_size]
        tokens = [t for t in query.lower().split() if len(t) > 2]
        if not tokens:
            tokens = [query.lower()]
        return [
            f
            for f in files
            if any(token in (f.get("name") or "").lower() for token in tokens)
        ][:page_size]


class GoogleDriveBackend:
    """Google Drive API v3 via service account."""

    def __init__(self, credentials_path: str) -> None:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        scopes = ["https://www.googleapis.com/auth/drive.readonly"]
        creds = service_account.Credentials.from_service_account_file(credentials_path, scopes=scopes)
        self._service = build("drive", "v3", credentials=creds, cache_discovery=False)

    def list_files(
        self,
        *,
        folder_id: str,
        query: str | None = None,
        page_size: int = 10,
    ) -> list[dict[str, Any]]:
        q_parts = [f"'{folder_id}' in parents", "trashed = false"]
        if query:
            tokens = [t.replace("'", "\\'") for t in query.split() if len(t) > 2]
            search_term = max(tokens, key=len) if tokens else query.replace("'", "\\'")
            q_parts.append(f"name contains '{search_term}'")
        q = " and ".join(q_parts)
        response = (
            self._service.files()
            .list(
                q=q,
                pageSize=page_size,
                fields="files(id, name, mimeType, webViewLink, webContentLink)",
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
            )
            .execute()
        )
        results: list[dict[str, Any]] = []
        for item in response.get("files", []):
            link = item.get("webViewLink") or item.get("webContentLink") or ""
            results.append(
                {
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "mimeType": item.get("mimeType"),
                    "link": link,
                }
            )
        return results


def build_drive_backend(*, mock_files: dict[str, list[dict[str, Any]]] | None = None) -> DriveBackend:
    if mock_files is not None or DRIVE_MOCK:
        return MockDriveBackend(mock_files)
    if GOOGLE_SERVICE_ACCOUNT_JSON and os.path.isfile(GOOGLE_SERVICE_ACCOUNT_JSON):
        return GoogleDriveBackend(GOOGLE_SERVICE_ACCOUNT_JSON)
    logger.warning("Drive not configured — using empty mock backend")
    return MockDriveBackend({})


def resolve_subfolder_id(backend: DriveBackend, *, root_folder_id: str, subfolder: str) -> str | None:
    """Find subfolder ID (papers/textbooks/syllabus) under tenant root."""
    folders = backend.list_files(folder_id=root_folder_id, query=subfolder, page_size=20)
    for item in folders:
        name = (item.get("name") or "").lower()
        if name == subfolder.lower():
            return item.get("id")
    return None
