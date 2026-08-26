"""Observability helper tests."""

from unittest.mock import MagicMock, patch

from infrastructure.observability import (
    TraceContext,
    get_langfuse_client,
    is_langfuse_enabled,
    langfuse_disabled_reason,
    reset_langfuse_state,
    trace_context,
)


def setup_function() -> None:
    reset_langfuse_state()


def teardown_function() -> None:
    reset_langfuse_state()


def test_trace_context_tags_and_metadata():
    ctx = TraceContext(
        tenant_id="tenant-demo-physics",
        tenant_slug="demo-physics",
        session_id="sess-1",
        user_id="stu-1",
    )
    assert "tenant:demo-physics" in ctx.tags()
    assert ctx.metadata()["tenant_id"] == "tenant-demo-physics"


def test_trace_context_tags_telegram_channel():
    ctx = TraceContext(
        tenant_id="tenant-demo-physics",
        tenant_slug="demo-physics",
        channel="telegram",
    )
    assert "channel:telegram" in ctx.tags()
    assert ctx.metadata()["channel"] == "telegram"
    assert ctx.metadata()["tenant_id"] == "tenant-demo-physics"


def test_trace_context_noop_when_langfuse_disabled():
    ctx = TraceContext(tenant_id="tenant-demo-physics")
    with trace_context(ctx):
        assert True


@patch("infrastructure.observability.LANGFUSE_ENABLED", True)
@patch("infrastructure.observability.OBSERVABILITY_ENABLED", True)
@patch("infrastructure.observability.os.getenv")
@patch("infrastructure.observability.httpx.get")
def test_invalid_langfuse_credentials_disable_client(mock_get, mock_env_get):
    mock_env_get.side_effect = lambda key, default=None: {
        "LANGFUSE_PUBLIC_KEY": "pk-test",
        "LANGFUSE_SECRET_KEY": "sk-test",
    }.get(key, default)
    response = MagicMock()
    response.status_code = 401
    mock_get.return_value = response

    assert get_langfuse_client() is None
    assert is_langfuse_enabled() is False
    assert langfuse_disabled_reason() is not None
    assert "invalid" in langfuse_disabled_reason().lower()


@patch("infrastructure.observability.LANGFUSE_ENABLED", False)
@patch("infrastructure.observability.OBSERVABILITY_ENABLED", True)
def test_langfuse_explicitly_disabled():
    assert get_langfuse_client() is None
    assert is_langfuse_enabled() is False
