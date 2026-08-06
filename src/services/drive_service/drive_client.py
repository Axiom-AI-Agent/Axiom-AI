"""Google Drive client — service account, tenant-scoped folder search."""

from __future__ import annotations

import os
import socket
from typing import Any, Protocol

from loguru import logger

from infrastructure.config import DRIVE_MOCK, GOOGLE_SERVICE_ACCOUNT_JSON

_DRIVE_API_BASE = "https://www.googleapis.com/drive/v3"
_DRIVE_READONLY_SCOPE = "https://www.googleapis.com/auth/drive.readonly"
_IPV4_PREFERRED = False


def _prefer_ipv4_for_urllib3() -> None:
    """Make urllib3/requests resolve A records only (AF_INET).

    On dual-stack macOS, ``getaddrinfo`` often returns IPv6 first. httplib2
    (default googleapiclient transport) connects to that address and can hang
    ~60s when the IPv6 route is broken. urllib3/requests honor
    ``allowed_gai_family()``; forcing AF_INET avoids machine-specific
    ``networksetup -setv6off`` workarounds.
    """
    global _IPV4_PREFERRED
    if _IPV4_PREFERRED:
        return
    import urllib3.util.connection as urllib3_cn

    urllib3_cn.allowed_gai_family = lambda: socket.AF_INET  # type: ignore[assignment]
    _IPV4_PREFERRED = True
    logger.info("Drive HTTP transport: urllib3 prefer IPv4 (AF_INET)")


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
    """Google Drive API v3 via service account + requests (not httplib2)."""

    def __init__(self, credentials_path: str) -> None:
        from google.auth.transport.requests import AuthorizedSession
        from google.oauth2 import service_account

        _prefer_ipv4_for_urllib3()
        creds = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=[_DRIVE_READONLY_SCOPE],
        )
        # AuthorizedSession uses requests/urllib3 (Happy Eyeballs-friendly + our IPv4 preference)
        # instead of googleapiclient's default httplib2 transport.
        self._session = AuthorizedSession(creds)
        self._timeout_s = float(os.getenv("DRIVE_HTTP_TIMEOUT_S", "30"))

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

        response = self._session.get(
            f"{_DRIVE_API_BASE}/files",
            params={
                "q": q,
                "pageSize": page_size,
                "fields": "files(id, name, mimeType, webViewLink, webContentLink)",
                "supportsAllDrives": "true",
                "includeItemsFromAllDrives": "true",
            },
            timeout=self._timeout_s,
        )
        if response.status_code >= 400:
            logger.error(
                "Drive files.list failed status={} body={}",
                response.status_code,
                response.text[:500],
            )
            response.raise_for_status()

        payload = response.json()
        results: list[dict[str, Any]] = []
        for item in payload.get("files", []):
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
