"""Drive MCP server — tool surface and tenant/class scoping."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from agents.tools.drive_tool import DriveTool, clear_class_folder_cache
from services.drive_service.drive_client import MockDriveBackend

PHYSICS_CLASS = {
    "id": "class-physics-al-2026",
    "name": "A/L Physics 2026",
    "subject": "Physics",
    "grade": "A/L",
}
CHEMISTRY_CLASS = {
    "id": "class-chemistry-al-2026",
    "name": "A/L Chemistry 2026",
    "subject": "Chemistry",
    "grade": "A/L",
}


def _nested(root_id: str, class_folder: str, papers_id: str, filename: str, file_id: str) -> MockDriveBackend:
    return MockDriveBackend(
        {
            root_id: [
                {
                    "id": class_folder,
                    "name": "A/L Physics 2026" if "physics" in filename else "A/L Chemistry 2026",
                    "mimeType": "application/vnd.google-apps.folder",
                }
            ],
            class_folder: [{"id": papers_id, "name": "papers"}],
            papers_id: [
                {
                    "id": file_id,
                    "name": filename,
                    "link": f"https://drive.google.com/file/d/{file_id}/view",
                }
            ],
        }
    )


@pytest.fixture(autouse=True)
def _clear_drive_cache():
    clear_class_folder_cache()
    yield
    clear_class_folder_cache()


@pytest.fixture
def physics_drive_backend():
    return _nested(
        "drive-root-physics",
        "folder-physics",
        "papers-folder",
        "2024-model-paper-physics.pdf",
        "file-1",
    )


@pytest.fixture
def chemistry_drive_backend():
    return _nested(
        "drive-root-chemistry",
        "folder-chem",
        "chem-papers",
        "2024-chemistry-paper.pdf",
        "file-c1",
    )


def _load_for(row: dict):
    def _load(_tenant_id: str, class_ids: list[str]) -> list[dict]:
        return [row] if row["id"] in class_ids else []

    return _load


def test_drive_mcp_search_returns_link(physics_drive_backend):
    import mcp_servers.drive_server as drive_server

    drive_server._tool = DriveTool(backend=physics_drive_backend)
    with patch.object(DriveTool, "_get_drive_root", return_value="drive-root-physics"):
        with patch.object(DriveTool, "_load_classes", side_effect=_load_for(PHYSICS_CLASS)):
            raw = drive_server.drive_search(
                tenant_id="tenant-demo-physics",
                query="physics paper",
                folder="papers",
                class_ids=["class-physics-al-2026"],
            )
    payload = json.loads(raw)
    assert payload["ok"] is True
    assert len(payload["files"]) == 1
    assert "drive.google.com" in payload["files"][0]["link"]


def test_drive_mcp_list_folder(physics_drive_backend):
    import mcp_servers.drive_server as drive_server

    drive_server._tool = DriveTool(backend=physics_drive_backend)
    with patch.object(DriveTool, "_get_drive_root", return_value="drive-root-physics"):
        with patch.object(DriveTool, "_load_classes", side_effect=_load_for(PHYSICS_CLASS)):
            raw = drive_server.drive_list(
                tenant_id="tenant-demo-physics",
                folder="papers",
                class_ids=["class-physics-al-2026"],
            )
    payload = json.loads(raw)
    assert payload["ok"] is True
    assert payload["files"][0]["folder"] == "papers"


def test_drive_mcp_rejects_disallowed_folder(physics_drive_backend):
    import mcp_servers.drive_server as drive_server

    drive_server._tool = DriveTool(backend=physics_drive_backend)
    with patch.object(DriveTool, "_get_drive_root", return_value="drive-root-physics"):
        raw = drive_server.drive_search(
            tenant_id="tenant-demo-physics",
            query="notes",
            folder="notes",
            class_ids=["class-physics-al-2026"],
        )
    payload = json.loads(raw)
    assert payload["ok"] is False
    assert "not allowed" in payload["error"].lower()


def test_drive_mcp_tenant_isolation(physics_drive_backend, chemistry_drive_backend):
    import mcp_servers.drive_server as drive_server

    physics_tool = DriveTool(backend=physics_drive_backend)
    chemistry_tool = DriveTool(backend=chemistry_drive_backend)

    with patch.object(DriveTool, "_get_drive_root", return_value="drive-root-physics"):
        with patch.object(DriveTool, "_load_classes", side_effect=_load_for(PHYSICS_CLASS)):
            drive_server._tool = physics_tool
            raw_a = drive_server.drive_search(
                tenant_id="tenant-demo-physics",
                query="paper",
                folder="papers",
                class_ids=["class-physics-al-2026"],
            )
    with patch.object(DriveTool, "_get_drive_root", return_value="drive-root-chemistry"):
        with patch.object(DriveTool, "_load_classes", side_effect=_load_for(CHEMISTRY_CLASS)):
            drive_server._tool = chemistry_tool
            raw_b = drive_server.drive_search(
                tenant_id="tenant-demo-chemistry",
                query="paper",
                folder="papers",
                class_ids=["class-chemistry-al-2026"],
            )

    file_a = json.loads(raw_a)["files"][0]["name"]
    file_b = json.loads(raw_b)["files"][0]["name"]
    assert "physics" in file_a.lower()
    assert "chemistry" in file_b.lower()
    assert file_a != file_b
