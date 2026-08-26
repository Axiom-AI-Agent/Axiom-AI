"""Drive numbered-list pick store tests."""

from __future__ import annotations

from agents.drive_file_pick import (
    DrivePickFile,
    DrivePickStore,
    parse_file_pick_index,
    try_consume_drive_pick,
)


def test_parse_file_pick_index_accepts_plain_and_ordinal():
    assert parse_file_pick_index("2") == 2
    assert parse_file_pick_index("2 please") == 2
    assert parse_file_pick_index("number 3") == 3
    assert parse_file_pick_index("the 1st one") == 1
    assert parse_file_pick_index("send me tutes") is None
    assert parse_file_pick_index("2024") is None


def test_try_consume_drive_pick_resolves_number():
    store = DrivePickStore()
    store.put(
        tenant_id="tenant-a",
        session_id="sess-1",
        user_id="stu-1",
        files=[
            DrivePickFile(name="tute-01.pdf", link="https://drive.example/1"),
            DrivePickFile(name="paper-02.pdf", link="https://drive.example/2"),
        ],
        folder="papers",
    )
    reply = try_consume_drive_pick(
        message="2",
        tenant_id="tenant-a",
        session_id="sess-1",
        user_id="stu-1",
        store=store,
    )
    assert reply is not None
    assert "paper-02.pdf" in reply
    assert "https://drive.example/2" in reply
    assert store.get(tenant_id="tenant-a", session_id="sess-1", user_id="stu-1") is None


def test_try_consume_drive_pick_out_of_range_keeps_list():
    store = DrivePickStore()
    store.put(
        tenant_id="tenant-a",
        session_id="sess-1",
        user_id="stu-1",
        files=[DrivePickFile(name="tute-01.pdf", link="https://drive.example/1")],
        folder="papers",
    )
    reply = try_consume_drive_pick(
        message="9",
        tenant_id="tenant-a",
        session_id="sess-1",
        user_id="stu-1",
        store=store,
    )
    assert reply is not None
    assert "1 to 1" in reply
    assert "tute-01.pdf" in reply
    assert store.get(tenant_id="tenant-a", session_id="sess-1", user_id="stu-1") is not None


def test_try_consume_drive_pick_new_question_clears_pending():
    store = DrivePickStore()
    store.put(
        tenant_id="tenant-a",
        session_id="sess-1",
        user_id="stu-1",
        files=[DrivePickFile(name="tute-01.pdf", link="https://drive.example/1")],
        folder="papers",
    )
    reply = try_consume_drive_pick(
        message="explain velocity",
        tenant_id="tenant-a",
        session_id="sess-1",
        user_id="stu-1",
        store=store,
    )
    assert reply is None
    assert store.get(tenant_id="tenant-a", session_id="sess-1", user_id="stu-1") is None
