"""Pytest bootstrap — load project .env before tests (matches api.main and scripts)."""

from __future__ import annotations

from pathlib import Path

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

from api.main import app
from api.tenant_scope import TenantScope, require_active_tenant

load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=True)


@pytest.fixture
def active_tenant_scope() -> TenantScope:
    return TenantScope(
        tenant_id="tenant-demo-physics",
        slug="demo-physics",
        name="Demo Physics Academy",
    )


@pytest.fixture
def client(active_tenant_scope):
    app.dependency_overrides[require_active_tenant] = lambda: active_tenant_scope
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def client_no_tenant_override():
    """HTTP client without tenant dependency override (for auth rejection tests)."""
    with TestClient(app) as c:
        yield c
