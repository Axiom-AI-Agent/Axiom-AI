"""Langfuse observability — tracing per tenant/session/user and prompt hooks."""

from __future__ import annotations

import functools
import os
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Generator, TypeVar

from loguru import logger

from infrastructure.config import LANGFUSE_HOST, OBSERVABILITY_ENABLED

F = TypeVar("F", bound=Callable[..., Any])

_langfuse_client = None
_init_attempted = False
_propagate_attributes = None
_observe_decorator = None


@dataclass
class TraceContext:
    """Langfuse trace scope for a WhatsApp conversation turn."""

    tenant_id: str
    session_id: str | None = None
    user_id: str | None = None
    tenant_slug: str | None = None
    channel: str = "twilio_whatsapp"
    extra_metadata: dict[str, Any] = field(default_factory=dict)

    def tags(self) -> list[str]:
        tags = [f"channel:{self.channel}"]
        if self.tenant_slug:
            tags.append(f"tenant:{self.tenant_slug}")
        return tags

    def metadata(self) -> dict[str, Any]:
        data = {"tenant_id": self.tenant_id, "channel": self.channel}
        data.update(self.extra_metadata)
        return data


def _import_langfuse_symbols() -> bool:
    global _propagate_attributes, _observe_decorator
    if _propagate_attributes is not None:
        return _observe_decorator is not None
    try:
        from langfuse import observe, propagate_attributes

        _propagate_attributes = propagate_attributes
        _observe_decorator = observe
        return True
    except ImportError:
        _propagate_attributes = None
        _observe_decorator = None
        return False


def get_langfuse_client():
    """Return Langfuse client or None when disabled / unconfigured."""
    global _langfuse_client, _init_attempted
    if _init_attempted:
        return _langfuse_client
    _init_attempted = True

    if not OBSERVABILITY_ENABLED:
        return None

    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    if not public_key or not secret_key:
        logger.debug("Langfuse keys not set — tracing disabled")
        return None

    try:
        from langfuse import Langfuse, get_client

        Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=LANGFUSE_HOST,
        )
        _langfuse_client = get_client()
    except Exception as exc:
        logger.warning("Langfuse init failed: {}", exc)
        _langfuse_client = None
    return _langfuse_client


def is_langfuse_enabled() -> bool:
    return get_langfuse_client() is not None


@contextmanager
def trace_context(ctx: TraceContext) -> Generator[None, None, None]:
    """Propagate tenant/session/user identifiers to all nested Langfuse observations."""
    if not is_langfuse_enabled() or not _import_langfuse_symbols():
        yield
        return

    assert _propagate_attributes is not None
    with _propagate_attributes(
        session_id=ctx.session_id,
        user_id=ctx.user_id,
        tags=ctx.tags(),
        metadata=ctx.metadata(),
    ):
        yield


def observe(name: str | None = None) -> Callable[[F], F]:
    """Decorator: Langfuse span when configured, else passthrough."""

    def decorator(fn: F) -> F:
        if is_langfuse_enabled() and _import_langfuse_symbols() and _observe_decorator is not None:
            return _observe_decorator(name=name)(fn)  # type: ignore[return-value]

        @functools.wraps(fn)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            return await fn(*args, **kwargs)

        @functools.wraps(fn)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            return fn(*args, **kwargs)

        if functools.iscoroutinefunction(fn):
            return async_wrapper  # type: ignore[return-value]
        return sync_wrapper  # type: ignore[return-value]

    return decorator


def flush() -> None:
    client = get_langfuse_client()
    if client is not None:
        client.flush()
