"""Drive tool unit tests."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from agents.tools.drive_tool import DriveTool
from services.drive_service.drive_client import MockDriveBackend


@pytest.fixture
def mock_backend():
    return MockDriveBackend(
        {
            "drive-root-physics": [
                {"id": "papers-folder", "name": "papers", "link": ""},
            ],
            "papers-folder": [
                {
                    "id": "file-1",
                    "name": "2024-model-paper-physics.pdf",
                    "link": "https://drive.google.com/file/d/abc/view",
                }
            ],
        }
    )


def test_drive_search_returns_matching_file(mock_backend):
    tool = DriveTool(backend=mock_backend)
    with patch.object(tool, "_get_drive_root", return_value="drive-root-physics"):
        raw = tool.drive_search(
            tenant_id="tenant-demo-physics",
            query="physics paper",
            folder="papers",
        )
    payload = json.loads(raw)
    assert payload["ok"] is True
    assert len(payload["files"]) == 1
    assert "physics" in payload["files"][0]["name"].lower()


def test_drive_rejects_disallowed_folder(mock_backend):
    tool = DriveTool(backend=mock_backend)
    with patch.object(tool, "_get_drive_root", return_value="drive-root-physics"):
        raw = tool.drive_search(
            tenant_id="tenant-demo-physics",
            query="notes",
            folder="notes",
        )
    payload = json.loads(raw)
    assert payload["ok"] is False
    assert "not allowed" in payload["error"].lower()


def test_drive_search_unknown_tenant(mock_backend):
    tool = DriveTool(backend=mock_backend)
    with patch.object(tool, "_get_drive_root", return_value=None):
        raw = tool.drive_search(
            tenant_id="tenant-unknown",
            query="paper",
        )
    payload = json.loads(raw)
    assert payload["ok"] is False


def test_drive_list_scoped_to_folder(mock_backend):
    tool = DriveTool(backend=mock_backend)
    with patch.object(tool, "_get_drive_root", return_value="drive-root-physics"):
        raw = tool.drive_list(tenant_id="tenant-demo-physics", folder="papers")
    payload = json.loads(raw)
    assert payload["ok"] is True
    assert payload["files"][0]["folder"] == "papers"
