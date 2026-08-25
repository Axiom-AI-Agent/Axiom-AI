"""
Dashboard API HTTP tests
(mocked Supabase + CRM).
"""

from __future__ import annotations

import json
from unittest.mock import (
    MagicMock,
    patch,
)

from api.schemas import (
    ChatTurnsResponse,
)


def _chain_mock(
    data=None,
    count=0,
):
    mock = MagicMock()

    mock.execute.return_value = (
        MagicMock(
            data=data or [],
            count=count,
        )
    )

    mock.select.return_value = (
        mock
    )

    mock.eq.return_value = (
        mock
    )

    mock.in_.return_value = (
        mock
    )

    mock.order.return_value = (
        mock
    )

    mock.limit.return_value = (
        mock
    )

    return mock


@patch(
    "api.routers.dashboard.escalations."
    "get_supabase_client"
)
@patch(
    "api.routers.dashboard.escalations."
    "CrmTool"
)
def test_resolve_payment_escalation(
    mock_crm_cls,
    mock_supa,
    client,
):
    supa = MagicMock()

    mock_supa.return_value = (
        supa
    )

    supa.table.return_value = (
        _chain_mock(
            data=[
                {
                    "id":
                        "esc-1",
                    "reason_code":
                        "payment_receipt",
                }
            ]
        )
    )

    mock_crm = MagicMock()

    mock_crm_cls.return_value = (
        mock_crm
    )

    mock_crm.resolve_escalation.return_value = (
        json.dumps(
            {
                "ok":
                    True,
                "student":
                    {
                        "phone":
                            "94771234567",
                        "name":
                            "Amaya",
                    },
                "class":
                    {
                        "name":
                            "A/L Physics",
                    },
                "enrollment":
                    {
                        "status":
                            "active",
                    },
            }
        )
    )

    with patch(
        (
            "api.routers.dashboard."
            "escalations.notify_student"
        ),
        return_value=True,
    ) as notify:
        response = client.patch(
            (
                "/dashboard/"
                "escalations/esc-1/"
                "resolve"
            ),
            params={
                "tenant_id":
                    "tenant-demo-physics",
                "notify":
                    "true",
            },
        )

    assert (
        response.status_code
        == 200
    )

    body = (
        response.json()
    )

    assert (
        body["ok"]
        is True
    )

    assert (
        body["resolution"]
        == "approved"
    )

    assert (
        body["student_notified"]
        is True
    )

    notify.assert_called_once()


@patch(
    "api.routers.dashboard.escalations."
    "get_supabase_client"
)
@patch(
    "api.routers.dashboard.escalations."
    "CrmTool"
)
def test_reject_payment_escalation(
    mock_crm_cls,
    mock_supa,
    client,
):
    mock_supa.return_value = (
        MagicMock(
            table=MagicMock(
                return_value=(
                    _chain_mock(
                        data=[
                            {
                                "id":
                                    "tenant-demo-physics",
                                "name":
                                    "Demo",
                            }
                        ]
                    )
                )
            )
        )
    )

    mock_crm = MagicMock()

    mock_crm_cls.return_value = (
        mock_crm
    )

    (
        mock_crm
        .reject_payment_escalation
        .return_value
    ) = json.dumps(
        {
            "ok":
                True,
            "reason_code":
                "payment_receipt",
            "student":
                {
                    "phone":
                        "94771234567",
                    "name":
                        "Amaya",
                },
        }
    )

    with patch(
        (
            "api.routers.dashboard."
            "escalations.notify_student"
        ),
        return_value=True,
    ):
        response = client.patch(
            (
                "/dashboard/"
                "escalations/esc-1/"
                "reject"
            ),
            params={
                "tenant_id":
                    "tenant-demo-physics",
            },
        )

    assert (
        response.status_code
        == 200
    )

    assert (
        response.json()[
            "resolution"
        ]
        == "rejected"
    )


@patch(
    "api.routers.dashboard.overview."
    "get_supabase_client"
)
def test_dashboard_overview(
    mock_supa,
    client,
):
    supa = MagicMock()

    mock_supa.return_value = (
        supa
    )

    supa.table.return_value = (
        _chain_mock(
            count=2
        )
    )

    response = client.get(
        "/dashboard/overview",
        params={
            "tenant_id":
                "tenant-demo-physics",
        },
    )

    assert (
        response.status_code
        == 200
    )

    body = (
        response.json()
    )

    assert (
        body["tenant_id"]
        == "tenant-demo-physics"
    )

    assert (
        "open_escalations"
        in body
    )


@patch(
    "api.routers.dashboard.chat_logs."
    "get_chat_turns"
)
def test_dashboard_chat_logs_alias(
    mock_get_turns,
    client,
):
    mock_get_turns.return_value = (
        ChatTurnsResponse(
            tenant_id=(
                "tenant-demo-physics"
            ),
            session_id=(
                "tenant-demo-physics:"
                "94771234567"
            ),
            turns=[],
        )
    )

    response = client.get(
        "/dashboard/chat-logs",
        params={
            "tenant_id":
                "tenant-demo-physics",
            "phone":
                "94771234567",
        },
    )

    assert (
        response.status_code
        == 200
    )

    (
        mock_get_turns
        .assert_called_once()
    )


@patch(
    "api.routers.dashboard.chat."
    "get_supabase_client"
)
@patch(
    "api.routers.dashboard.chat."
    "MessagePersistence"
)
def test_dashboard_chat_conversations(
    mock_persistence_cls,
    mock_supa,
    client,
):
    mock_persistence = (
        MagicMock()
    )

    (
        mock_persistence_cls
        .return_value
    ) = mock_persistence

    (
        mock_persistence
        .list_recent_sessions
        .return_value
    ) = [
        {
            "id":
                "turn-1",
            "session_id":
                (
                    "tenant-demo-physics:"
                    "94771234567"
                ),
            "user_id":
                "stu-1",
            "role":
                "user",
            "content":
                "Hello",
            "created_at":
                (
                    "2026-08-04"
                    "T12:00:00Z"
                ),
        }
    ]

    supa = MagicMock()

    mock_supa.return_value = (
        supa
    )

    def table_side_effect(
        name,
    ):
        chain = (
            _chain_mock()
        )

        if name == "students":
            (
                chain.execute
                .return_value
            ) = MagicMock(
                data=[
                    {
                        "id":
                            "stu-1",
                        "name":
                            "Amaya",
                        "phone":
                            "94771234567",
                    }
                ]
            )

        elif (
            name
            == "escalations"
        ):
            (
                chain.execute
                .return_value
            ) = MagicMock(
                data=[]
            )

        return chain

    supa.table.side_effect = (
        table_side_effect
    )

    response = client.get(
        (
            "/dashboard/chat/"
            "conversations"
        ),
        params={
            "tenant_id":
                "tenant-demo-physics",
        },
    )

    assert (
        response.status_code
        == 200
    )

    body = (
        response.json()
    )

    assert (
        len(
            body[
                "conversations"
            ]
        )
        == 1
    )

    assert (
        body[
            "conversations"
        ][0]["phone"]
        == "94771234567"
    )

    assert (
        body[
            "conversations"
        ][0]["last_sender"]
        == "student"
    )


@patch(
    "api.routers.dashboard.chat."
    "get_supabase_client"
)
@patch(
    "api.routers.dashboard.chat."
    "MessagePersistence"
)
def test_dashboard_chat_thread(
    mock_persistence_cls,
    mock_supa,
    client,
):
    mock_persistence = (
        MagicMock()
    )

    (
        mock_persistence_cls
        .return_value
    ) = mock_persistence

    (
        mock_persistence
        .get_turns
        .return_value
    ) = [
        {
            "id":
                "turn-1",
            "role":
                "assistant",
            "content":
                "Hi!",
            "created_at":
                (
                    "2026-08-04"
                    "T12:00:00Z"
                ),
        }
    ]

    supa = MagicMock()

    mock_supa.return_value = (
        supa
    )

    def table_side_effect(
        name,
    ):
        chain = (
            _chain_mock()
        )

        if name == "students":
            (
                chain.execute
                .return_value
            ) = MagicMock(
                data=[
                    {
                        "id":
                            "stu-1",
                        "name":
                            "Amaya",
                        "phone":
                            "94771234567",
                    }
                ]
            )

        elif (
            name
            == "escalations"
        ):
            (
                chain.execute
                .return_value
            ) = MagicMock(
                data=[
                    {
                        "id":
                            "esc-1",
                        "reason_code":
                            "talk_to_tutor",
                        "status":
                            "open",
                    }
                ]
            )

        return chain

    supa.table.side_effect = (
        table_side_effect
    )

    response = client.get(
        (
            "/dashboard/chat/"
            "conversations/"
            "94771234567"
        ),
        params={
            "tenant_id":
                "tenant-demo-physics",
        },
    )

    assert (
        response.status_code
        == 200
    )

    body = (
        response.json()
    )

    assert (
        body[
            "student_name"
        ]
        == "Amaya"
    )

    assert (
        body[
            "turns"
        ][0]["sender"]
        == "bot"
    )

    assert (
        len(
            body[
                "open_escalations"
            ]
        )
        == 1
    )


@patch(
    (
        "api.routers.dashboard.chat."
        "notify_student"
    ),
    return_value=True,
)
@patch(
    (
        "api.routers.dashboard.chat."
        "MessagePersistence"
    )
)
def test_dashboard_staff_send_returns_turn(
    mock_persistence_cls,
    mock_notify,
    client,
):
    mock_persistence = (
        MagicMock()
    )

    (
        mock_persistence_cls
        .return_value
    ) = mock_persistence

    (
        mock_persistence
        .get_latest_turn
        .return_value
    ) = {
        "id":
            "turn-staff-1",
        "role":
            "system",
        "content":
            "Staff reply here",
        "created_at":
            (
                "2026-08-04"
                "T12:01:00Z"
            ),
    }

    response = client.post(
        "/dashboard/chat/send",
        json={
            "tenant_id":
                "tenant-demo-physics",
            "phone":
                "94771234567",
            "message":
                "Staff reply here",
        },
    )

    assert (
        response.status_code
        == 200
    )

    body = (
        response.json()
    )

    assert (
        body["delivered"]
        is True
    )

    assert (
        body[
            "turn"
        ]["sender"]
        == "staff"
    )

    (
        mock_notify
        .assert_called_once()
    )


@patch(
    (
        "api.routers.dashboard.chat."
        "notify_student"
    ),
    return_value=False,
)
def test_dashboard_staff_send_returns_502_when_delivery_fails(
    mock_notify,
    client,
):
    response = client.post(
        "/dashboard/chat/send",
        json={
            "tenant_id":
                "tenant-demo-physics",
            "phone":
                "94771234567",
            "message":
                "Staff reply here",
        },
    )

    assert (
        response.status_code
        == 502
    )

    body = (
        response.json()
    )

    assert (
        "delivery failed"
        in body[
            "detail"
        ].lower()
    )

    (
        mock_notify
        .assert_called_once()
    )