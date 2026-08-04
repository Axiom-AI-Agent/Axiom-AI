"""Langfuse observability — tracing per tenant/session/user and prompt hooks.

Prompt fetch pattern ported from BookMe AI ``infrastructure/observability.py``.
"""

from __future__ import annotations

import functools
import inspect
import os
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Callable, Generator, Iterable, TypeVar

from loguru import logger

from infrastructure.config import LANGFUSE_HOST, LANGFUSE_PROMPT_LABEL, OBSERVABILITY_ENABLED

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

        if inspect.iscoroutinefunction(fn):
            return async_wrapper  # type: ignore[return-value]
        return sync_wrapper  # type: ignore[return-value]

    return decorator


def flush() -> None:
    client = get_langfuse_client()
    if client is not None:
        client.flush()


def fetch_prompt(
    name: str,
    *,
    fallback: str,
    **compile_vars: str,
) -> str:
    """Resolve a prompt by Langfuse name with local fallback (BookMe pattern)."""
    client = get_langfuse_client()
    if client is not None:
        try:
            prompt_obj = client.get_prompt(name, label=LANGFUSE_PROMPT_LABEL)
            if compile_vars:
                return prompt_obj.compile(**compile_vars)
            return prompt_obj.compile()
        except Exception as exc:
            logger.debug("Langfuse prompt {} unavailable: {}", name, exc)

    if compile_vars:
        return fallback.format(**compile_vars)
    return fallback


def prefetch_prompts(names: Iterable[str]) -> int:
    """Warm Langfuse prompt cache at startup."""
    client = get_langfuse_client()
    if client is None:
        return 0
    warmed = 0
    for name in names:
        try:
            client.get_prompt(name, label=LANGFUSE_PROMPT_LABEL)
            warmed += 1
        except Exception as exc:
            logger.debug("prefetch: {} not in Langfuse ({})", name, exc)
    return warmed


@asynccontextmanager
async def langfuse_turn_attributes(
    *,
    user_id: str | None = None,
    session_id: str | None = None,
    metadata: dict[str, Any] | None = None,
    tags: list[str] | None = None,
) -> AsyncIterator[None]:
    """Propagate user/session/tags to nested spans for one chat turn."""
    if not is_langfuse_enabled() or not _import_langfuse_symbols():
        yield
        return

    prop_kwargs: dict[str, Any] = {}
    if user_id:
        prop_kwargs["user_id"] = user_id
    if session_id:
        prop_kwargs["session_id"] = session_id
    if metadata:
        prop_kwargs["metadata"] = metadata
    if tags:
        prop_kwargs["tags"] = tags

    if not prop_kwargs:
        yield
        return

    assert _propagate_attributes is not None
    with _propagate_attributes(**prop_kwargs):
        yield


def update_current_trace(
    *,
    metadata: dict[str, Any] | None = None,
    tags: list[str] | None = None,
) -> None:
    if not is_langfuse_enabled():
        return
    try:
        from langfuse import get_client

        client = get_client()
        span_meta: dict[str, Any] = {}
        if metadata:
            span_meta.update(metadata)
        if tags:
            span_meta["tags"] = tags
        if span_meta:
            client.update_current_span(metadata=span_meta)
    except Exception as exc:
        logger.debug("update_current_trace failed: {}", exc)


def update_current_observation(
    *,
    input: str | None = None,
    output: str | None = None,
    metadata: dict[str, Any] | None = None,
    usage: dict[str, Any] | None = None,
    model: str | None = None,
) -> None:
    """Attach I/O + usage to the current span/generation."""
    if not is_langfuse_enabled():
        return
    try:
        from langfuse import get_client

        client = get_client()
        if usage is not None or model is not None:
            gen: dict[str, Any] = {}
            if input is not None:
                gen["input"] = input
            if output is not None:
                gen["output"] = output
            if metadata is not None:
                gen["metadata"] = metadata
            if model is not None:
                gen["model"] = model
            if usage is not None:
                gen["usage_details"] = usage
            try:
                client.update_current_generation(**gen)
                return
            except Exception:
                pass
        span: dict[str, Any] = {}
        if input is not None:
            span["input"] = input
        if output is not None:
            span["output"] = output
        if metadata is not None:
            span["metadata"] = metadata
        if span:
            client.update_current_span(**span)
    except Exception as exc:
        logger.debug("update_current_observation failed: {}", exc)
