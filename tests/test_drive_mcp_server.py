"""Drive MCP server — tool surface and tenant scoping (same logic as axiom-drive stdio server)."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from agents.tools.drive_tool import DriveTool
from services.drive_service.drive_client import MockDriveBackend


@pytest.fixture
def physics_drive_backend():
    return MockDriveBackend(
        {
            "drive-root-physics": [{"id": "papers-folder", "name": "papers", "link": ""}],
            "papers-folder": [
                {
                    "id": "file-1",
                    "name": "2024-model-paper-physics.pdf",
                    "link": "https://drive.google.com/file/d/abc/view",
                }
            ],
        }
    )


@pytest.fixture
def chemistry_drive_backend():
    return MockDriveBackend(
        {
            "drive-root-chemistry": [{"id": "chem-papers", "name": "papers", "link": ""}],
            "chem-papers": [
                {
                    "id": "file-c1",
                    "name": "2024-chemistry-paper.pdf",
                    "link": "https://drive.google.com/file/d/chem/view",
                }
            ],
        }
    )


def test_drive_mcp_search_returns_link(physics_drive_backend):
    import mcp_servers.drive_server as drive_server

    drive_server._tool = DriveTool(backend=physics_drive_backend)
    with patch.object(DriveTool, "_get_drive_root", return_value="drive-root-physics"):
        raw = drive_server.drive_search(
            tenant_id="tenant-demo-physics",
            query="physics paper",
            folder="papers",
        )
    payload = json.loads(raw)
    assert payload["ok"] is True
    assert len(payload["files"]) == 1
    assert "drive.google.com" in payload["files"][0]["link"]


def test_drive_mcp_list_folder(physics_drive_backend):
    import mcp_servers.drive_server as drive_server

    drive_server._tool = DriveTool(backend=physics_drive_backend)
    with patch.object(DriveTool, "_get_drive_root", return_value="drive-root-physics"):
        raw = drive_server.drive_list(tenant_id="tenant-demo-physics", folder="papers")
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
        )
    payload = json.loads(raw)
    assert payload["ok"] is False
    assert "not allowed" in payload["error"].lower()


def test_drive_mcp_tenant_isolation(physics_drive_backend, chemistry_drive_backend):
    import mcp_servers.drive_server as drive_server

    physics_tool = DriveTool(backend=physics_drive_backend)
    chemistry_tool = DriveTool(backend=chemistry_drive_backend)

    with patch.object(DriveTool, "_get_drive_root", return_value="drive-root-physics"):
        drive_server._tool = physics_tool
        raw_a = drive_server.drive_search(
            tenant_id="tenant-demo-physics",
            query="paper",
            folder="papers",
        )
    with patch.object(DriveTool, "_get_drive_root", return_value="drive-root-chemistry"):
        drive_server._tool = chemistry_tool
        raw_b = drive_server.drive_search(
            tenant_id="tenant-demo-chemistry",
            query="paper",
            folder="papers",
        )

    file_a = json.loads(raw_a)["files"][0]["name"]
    file_b = json.loads(raw_b)["files"][0]["name"]
    assert "physics" in file_a.lower()
    assert "chemistry" in file_b.lower()
    assert file_a != file_b
