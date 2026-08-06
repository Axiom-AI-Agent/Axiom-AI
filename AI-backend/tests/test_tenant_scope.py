"""Tenant scope validation for dashboard endpoints."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from api.tenant_scope import assert_body_tenant, resolve_tenant_id
from api.tenant_scope import TenantScope, require_active_tenant
from domain.enums import TenantStatus
from fastapi import HTTPException


def test_resolve_tenant_id_prefers_matching_header_and_query():
    assert (
        resolve_tenant_id(
            tenant_id="tenant-demo-physics",
            x_tenant_id="tenant-demo-physics",
        )
        == "tenant-demo-physics"
    )


def test_resolve_tenant_id_rejects_mismatch():
    with pytest.raises(HTTPException) as exc:
        resolve_tenant_id(
            tenant_id="tenant-a",
            x_tenant_id="tenant-b",
        )
    assert exc.value.status_code == 400


def test_resolve_tenant_id_requires_value():
    with pytest.raises(HTTPException) as exc:
        resolve_tenant_id(tenant_id=None, x_tenant_id=None)
    assert exc.value.status_code == 400


def test_assert_body_tenant_rejects_cross_tenant():
    scope = TenantScope(tenant_id="tenant-a")
    with pytest.raises(HTTPException) as exc:
        assert_body_tenant("tenant-b", scope)
    assert exc.value.status_code == 403


@patch("api.tenant_scope.get_supabase_client")
def test_require_active_tenant_not_found(mock_supa):
    mock_supa.return_value.table.return_value = MagicMock(
        select=MagicMock(
            return_value=MagicMock(
                eq=MagicMock(
                    return_value=MagicMock(
                        limit=MagicMock(
                            return_value=MagicMock(execute=MagicMock(return_value=MagicMock(data=[])))
                        )
                    )
                )
            )
        )
    )
    with pytest.raises(HTTPException) as exc:
        require_active_tenant("missing-tenant")
    assert exc.value.status_code == 404


@patch("api.tenant_scope.get_supabase_client")
def test_require_active_tenant_suspended(mock_supa):
    mock_supa.return_value.table.return_value = MagicMock(
        select=MagicMock(
            return_value=MagicMock(
                eq=MagicMock(
                    return_value=MagicMock(
                        limit=MagicMock(
                            return_value=MagicMock(
                                execute=MagicMock(
                                    return_value=MagicMock(
                                        data=[
                                            {
                                                "id": "tenant-x",
                                                "slug": "x",
                                                "name": "X",
                                                "status": TenantStatus.SUSPENDED.value,
                                            }
                                        ]
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )
    )
    with pytest.raises(HTTPException) as exc:
        require_active_tenant("tenant-x")
    assert exc.value.status_code == 403


def test_dashboard_rejects_missing_tenant(client_no_tenant_override):
    response = client_no_tenant_override.get("/dashboard/overview")
    assert response.status_code == 400


def test_dashboard_staff_send_rejects_body_tenant_mismatch(client):
    response = client.post(
        "/dashboard/chat/send",
        params={"tenant_id": "tenant-demo-physics"},
        json={
            "tenant_id": "other-tenant",
            "phone": "94771234567",
            "message": "Hello",
        },
    )
    assert response.status_code == 403
