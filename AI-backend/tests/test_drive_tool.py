"""Drive tool unit tests — class-scoped nested Drive layout."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from agents.tools.drive_tool import DriveTool, clear_class_folder_cache
from services.drive_service.drive_client import MockDriveBackend, find_child_folder, normalize_folder_key

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


def _nested_backend() -> MockDriveBackend:
    return MockDriveBackend(
        {
            "drive-root": [
                {
                    "id": "folder-physics",
                    "name": "A/L Physics 2026",
                    "mimeType": "application/vnd.google-apps.folder",
                },
                {
                    "id": "folder-chem",
                    "name": "A/L Chemistry 2026",
                    "mimeType": "application/vnd.google-apps.folder",
                },
                {
                    "id": "root-papers",
                    "name": "papers",
                    "mimeType": "application/vnd.google-apps.folder",
                },
            ],
            "folder-physics": [
                {"id": "phys-papers", "name": "papers"},
                {"id": "phys-tutes", "name": "tutes"},
                {"id": "phys-textbooks", "name": "textbooks"},
                {"id": "phys-syllabus", "name": "syllabus"},
            ],
            "folder-chem": [
                {"id": "chem-papers", "name": "papers"},
            ],
            "phys-papers": [
                {
                    "id": "file-p1",
                    "name": "2024-model-paper-physics.pdf",
                    "link": "https://drive.google.com/file/d/abc/view",
                }
            ],
            "phys-tutes": [
                {
                    "id": "file-t1",
                    "name": "tute-03-mechanics.pdf",
                    "link": "https://drive.google.com/file/d/tute/view",
                }
            ],
            "chem-papers": [
                {
                    "id": "file-c1",
                    "name": "2024-chemistry-paper.pdf",
                    "link": "https://drive.google.com/file/d/chem/view",
                }
            ],
            "root-papers": [
                {
                    "id": "file-leak",
                    "name": "SHOULD-NOT-SEE-all-classes.pdf",
                    "link": "https://drive.google.com/file/d/leak/view",
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
def mock_backend():
    return _nested_backend()


def _load_physics(_tenant_id: str, class_ids: list[str]) -> list[dict]:
    by_id = {PHYSICS_CLASS["id"]: PHYSICS_CLASS, CHEMISTRY_CLASS["id"]: CHEMISTRY_CLASS}
    return [by_id[cid] for cid in class_ids if cid in by_id]


def test_find_child_folder_normalizes_al_slash():
    backend = _nested_backend()
    folder_id = find_child_folder(
        backend,
        parent_id="drive-root",
        names=["AL Physics 2026", "A/L Physics 2026"],
    )
    assert folder_id == "folder-physics"
    assert normalize_folder_key("A/L Physics 2026") == normalize_folder_key("AL Physics 2026")


def test_drive_search_returns_matching_file(mock_backend):
    tool = DriveTool(backend=mock_backend)
    with patch.object(tool, "_get_drive_root", return_value="drive-root"):
        with patch.object(tool, "_load_classes", side_effect=_load_physics):
            raw = tool.drive_search(
                tenant_id="tenant-demo-physics",
                query="physics paper",
                folder="papers",
                class_ids=["class-physics-al-2026"],
            )
    payload = json.loads(raw)
    assert payload["ok"] is True
    assert len(payload["files"]) == 1
    assert "physics" in payload["files"][0]["name"].lower()
    assert payload["files"][0]["class_id"] == "class-physics-al-2026"


def test_drive_rejects_disallowed_folder(mock_backend):
    tool = DriveTool(backend=mock_backend)
    with patch.object(tool, "_get_drive_root", return_value="drive-root"):
        raw = tool.drive_search(
            tenant_id="tenant-demo-physics",
            query="notes",
            folder="notes",
            class_ids=["class-physics-al-2026"],
        )
    payload = json.loads(raw)
    assert payload["ok"] is False
    assert "not allowed" in payload["error"].lower()


def test_drive_search_requires_class_ids(mock_backend):
    tool = DriveTool(backend=mock_backend)
    with patch.object(tool, "_get_drive_root", return_value="drive-root"):
        raw = tool.drive_search(
            tenant_id="tenant-demo-physics",
            query="paper",
            folder="papers",
        )
    payload = json.loads(raw)
    assert payload["ok"] is False
    assert "class_ids" in payload["error"]


def test_drive_search_unknown_tenant(mock_backend):
    tool = DriveTool(backend=mock_backend)
    with patch.object(tool, "_get_drive_root", return_value=None):
        raw = tool.drive_search(
            tenant_id="tenant-unknown",
            query="paper",
            class_ids=["class-physics-al-2026"],
        )
    payload = json.loads(raw)
    assert payload["ok"] is False


def test_drive_list_scoped_to_folder(mock_backend):
    tool = DriveTool(backend=mock_backend)
    with patch.object(tool, "_get_drive_root", return_value="drive-root"):
        with patch.object(tool, "_load_classes", side_effect=_load_physics):
            raw = tool.drive_list(
                tenant_id="tenant-demo-physics",
                folder="papers",
                class_ids=["class-physics-al-2026"],
            )
    payload = json.loads(raw)
    assert payload["ok"] is True
    assert payload["files"][0]["folder"] == "papers"
    assert payload["files"][0]["name"] == "2024-model-paper-physics.pdf"


def test_drive_list_tutes_folder(mock_backend):
    tool = DriveTool(backend=mock_backend)
    with patch.object(tool, "_get_drive_root", return_value="drive-root"):
        with patch.object(tool, "_load_classes", side_effect=_load_physics):
            raw = tool.drive_list(
                tenant_id="tenant-demo-physics",
                folder="tute",
                class_ids=["class-physics-al-2026"],
            )
    payload = json.loads(raw)
    assert payload["ok"] is True
    assert payload["files"][0]["folder"] == "tutes"
    assert payload["files"][0]["name"] == "tute-03-mechanics.pdf"


def test_physics_enrollment_does_not_see_chemistry_or_root_papers(mock_backend):
    tool = DriveTool(backend=mock_backend)
    with patch.object(tool, "_get_drive_root", return_value="drive-root"):
        with patch.object(tool, "_load_classes", side_effect=_load_physics):
            raw = tool.drive_list(
                tenant_id="tenant-demo",
                folder="papers",
                class_ids=["class-physics-al-2026"],
            )
    names = [item["name"] for item in json.loads(raw)["files"]]
    assert names == ["2024-model-paper-physics.pdf"]
    assert "chemistry" not in "".join(names).lower()
    assert "SHOULD-NOT-SEE" not in "".join(names)


def test_missing_class_folder_does_not_fall_back_to_root(mock_backend):
    tool = DriveTool(backend=mock_backend)
    missing = {
        "id": "class-biology-al-2026",
        "name": "A/L Biology 2026",
        "subject": "Biology",
        "grade": "A/L",
    }
    with patch.object(tool, "_get_drive_root", return_value="drive-root"):
        with patch.object(tool, "_load_classes", return_value=[missing]):
            raw = tool.drive_list(
                tenant_id="tenant-demo",
                folder="papers",
                class_ids=["class-biology-al-2026"],
            )
    payload = json.loads(raw)
    assert payload["ok"] is True
    assert payload["files"] == []
    assert "A/L Biology 2026" in payload.get("message", "")
    assert "SHOULD-NOT-SEE" not in payload.get("message", "")


def test_message_hint_selects_one_of_two_enrollments(mock_backend):
    tool = DriveTool(backend=mock_backend)
    ids = ["class-physics-al-2026", "class-chemistry-al-2026"]
    with patch.object(tool, "_get_drive_root", return_value="drive-root"):
        with patch.object(tool, "_load_classes", side_effect=_load_physics):
            raw = tool.drive_list(
                tenant_id="tenant-demo",
                folder="papers",
                class_ids=ids,
                hint="chemistry past papers",
            )
    files = json.loads(raw)["files"]
    assert len(files) == 1
    assert "chemistry" in files[0]["name"].lower()


def test_generic_past_papers_unions_enrolled_classes(mock_backend):
    tool = DriveTool(backend=mock_backend)
    ids = ["class-physics-al-2026", "class-chemistry-al-2026"]
    with patch.object(tool, "_get_drive_root", return_value="drive-root"):
        with patch.object(tool, "_load_classes", side_effect=_load_physics):
            raw = tool.drive_list(
                tenant_id="tenant-demo",
                folder="papers",
                class_ids=ids,
                hint="past papers",
            )
    names = {item["name"] for item in json.loads(raw)["files"]}
    assert names == {"2024-model-paper-physics.pdf", "2024-chemistry-paper.pdf"}


def test_chemistry_hint_does_not_open_unenrolled_chemistry_folder(mock_backend):
    tool = DriveTool(backend=mock_backend)
    with patch.object(tool, "_get_drive_root", return_value="drive-root"):
        with patch.object(tool, "_load_classes", side_effect=_load_physics):
            raw = tool.drive_list(
                tenant_id="tenant-demo",
                folder="papers",
                class_ids=["class-physics-al-2026"],
                hint="chemistry past papers",
            )
    names = [item["name"] for item in json.loads(raw)["files"]]
    assert names == ["2024-model-paper-physics.pdf"]
    assert "chemistry" not in "".join(names).lower()


def test_student_id_drops_spoofed_class_ids(mock_backend):
    tool = DriveTool(backend=mock_backend)
    with patch.object(tool, "_get_drive_root", return_value="drive-root"):
        with patch.object(tool, "_enrolled_class_ids", return_value={"class-physics-al-2026"}):
            with patch.object(tool, "_load_classes", side_effect=_load_physics):
                raw = tool.drive_list(
                    tenant_id="tenant-demo",
                    folder="papers",
                    class_ids=["class-physics-al-2026", "class-chemistry-al-2026"],
                    student_id="stu-physics-only",
                )
    names = [item["name"] for item in json.loads(raw)["files"]]
    assert names == ["2024-model-paper-physics.pdf"]


def test_student_id_rejects_when_not_enrolled_in_requested_classes(mock_backend):
    tool = DriveTool(backend=mock_backend)
    with patch.object(tool, "_enrolled_class_ids", return_value={"class-physics-al-2026"}):
        raw = tool.drive_list(
            tenant_id="tenant-demo",
            folder="papers",
            class_ids=["class-chemistry-al-2026"],
            student_id="stu-physics-only",
        )
    payload = json.loads(raw)
    assert payload["ok"] is False
    assert "not enrolled" in payload["error"].lower()
