#!/usr/bin/env python3
"""Phase 5/6 dashboard API smoke — TestClient (no running server required)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env", override=True)

TENANT_ID = "tenant-demo-physics"


def _chain_mock(data=None, count=0):
    mock = MagicMock()
    mock.execute.return_value = MagicMock(data=data or [], count=count)
    mock.select.return_value = mock
    mock.eq.return_value = mock
    mock.in_.return_value = mock
    mock.order.return_value = mock
    mock.limit.return_value = mock
    return mock


def main() -> int:
    from api.main import app
    from api.tenant_scope import TenantScope, require_active_tenant
    from fastapi.testclient import TestClient

    app.dependency_overrides[require_active_tenant] = lambda: TenantScope(
        tenant_id=TENANT_ID,
        slug="demo-physics",
        name="Demo Physics Academy",
    )

    print("=== Dashboard API smoke ===")

    with patch("api.routers.dashboard.overview.get_supabase_client") as mock_overview_supa:
        mock_overview_supa.return_value = MagicMock(
            table=MagicMock(return_value=_chain_mock(count=1))
        )
        with TestClient(app) as client:
            overview = client.get("/dashboard/overview", params={"tenant_id": TENANT_ID})
            assert overview.status_code == 200, overview.text
            print("OK GET /dashboard/overview")

            with patch("api.routers.dashboard.escalations.get_supabase_client") as mock_esc:
                supa = MagicMock()
                mock_esc.return_value = supa
                supa.table.return_value = _chain_mock(data=[])

                esc = client.get(
                    "/dashboard/escalations",
                    params={"tenant_id": TENANT_ID},
                )
                assert esc.status_code == 200, esc.text
                print("OK GET /dashboard/escalations")

            with patch("api.routers.dashboard.chat.MessagePersistence") as mock_persist:
                mock_persist.return_value = MagicMock(
                    list_recent_sessions=MagicMock(return_value=[]),
                )
                conv = client.get(
                    "/dashboard/chat/conversations",
                    params={"tenant_id": TENANT_ID},
                )
                assert conv.status_code == 200, conv.text
                print("OK GET /dashboard/chat/conversations")

            with patch(
                "api.routers.dashboard.chat.notify_student",
                return_value=True,
            ), patch("api.routers.dashboard.chat.MessagePersistence") as mock_persist:
                mock_persist.return_value = MagicMock(
                    get_latest_turn=MagicMock(
                        return_value={
                            "id": "turn-1",
                            "role": "system",
                            "content": "Staff hello",
                            "created_at": "2026-08-05T00:00:00Z",
                        }
                    ),
                )
                send = client.post(
                    "/dashboard/chat/send",
                    params={"tenant_id": TENANT_ID},
                    json={
                        "tenant_id": TENANT_ID,
                        "phone": "94771234567",
                        "message": "Staff hello",
                    },
                )
                assert send.status_code == 200, send.text
                body = send.json()
                assert body.get("delivered") is True
                print("OK POST /dashboard/chat/send")

    app.dependency_overrides.clear()
    print("=== Dashboard smoke passed ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
