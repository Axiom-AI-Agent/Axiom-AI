"""Shared pytest bootstrap."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


load_dotenv(
    PROJECT_ROOT / ".env",
    override=False,
)


# Unit/integration tests instantiate the
# LangChain OpenAI-compatible clients, but
# they must never need a real credential.
if not os.getenv("OPENAI_API_KEY"):
    os.environ[
        "OPENAI_API_KEY"
    ] = "test-key-not-used"


# Keep test runtime deterministic.
os.environ.setdefault(
    "AGENT_USE_MCP",
    "false",
)

# Keep test runtime deterministic.
os.environ.setdefault(
    "AGENT_USE_MCP",
    "false",
)

os.environ.setdefault(
    "ALLOW_INPROCESS_TOOLS",
    "true",
)

os.environ.setdefault(
    "JWT_SECRET_KEY",
    "test-jwt-secret",
)


# IMPORTANT:
# Import FastAPI only AFTER test environment
# variables have been configured.
from fastapi.testclient import (  # noqa: E402
    TestClient,
)

from api.main import app  # noqa: E402
from api.tenant_scope import (  # noqa: E402
    TenantScope,
    require_active_tenant,
)


@pytest.fixture
def active_tenant_scope() -> TenantScope:
    return TenantScope(
        tenant_id=(
            "tenant-demo-physics"
        ),
        slug="demo-physics",
        name=(
            "Demo Physics Academy"
        ),
    )


@pytest.fixture
def client(
    active_tenant_scope,
):
    app.dependency_overrides[
        require_active_tenant
    ] = (
        lambda:
            active_tenant_scope
    )

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def client_no_tenant_override():
    with TestClient(app) as c:
        yield c