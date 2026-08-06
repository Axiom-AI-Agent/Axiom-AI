"""Langfuse observability — tracing per tenant/session/user and prompt hooks.

Prompt fetch pattern ported from BookMe AI ``infrastructure/observability.py``.
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Callable, Generator, Iterable, TypeVar

import httpx
from loguru import logger

from infrastructure.config import (
    LANGFUSE_ENABLED,
    LANGFUSE_HOST,
    LANGFUSE_PROMPT_LABEL,
    OBSERVABILITY_ENABLED,
)

F = TypeVar("F", bound=Callable[..., Any])

_langfuse_client = None
_init_attempted = False
_langfuse_disabled_reason: str | None = None

try:
    from langfuse import observe as _lf_observe
    from langfuse import get_client as _get_lf_client
except Exception:
    _lf_observe = None
    _get_lf_client = None

try:
    from langfuse import propagate_attributes as _propagate_attributes
except Exception:
    _propagate_attributes = None


def _tracing_enabled() -> bool:
    return bool(OBSERVABILITY_ENABLED and LANGFUSE_ENABLED)


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
    return _lf_observe is not None and _get_lf_client is not None


def _is_langfuse_auth_error(exc: BaseException) -> bool:
    text = str(exc).lower()
    if "401" in text or "403" in text or "unauthorized" in text or "invalid credentials" in text:
        return True
    status_code = getattr(exc, "status_code", None)
    return status_code in (401, 403)


def _suppress_langfuse_sdk_noise() -> None:
    logging.getLogger("langfuse").setLevel(logging.CRITICAL)


def _disable_langfuse(reason: str) -> None:
    global _langfuse_client, _langfuse_disabled_reason
    _langfuse_client = None
    if _langfuse_disabled_reason is not None:
        return
    _langfuse_disabled_reason = reason
    _suppress_langfuse_sdk_noise()
    logger.info("Langfuse disabled — {}. Using local prompt fallbacks.", reason)


def reset_langfuse_state() -> None:
    """Test helper — clear cached Langfuse client state."""
    global _langfuse_client, _init_attempted, _langfuse_disabled_reason
    _langfuse_client = None
    _init_attempted = False
    _langfuse_disabled_reason = None


def langfuse_disabled_reason() -> str | None:
    return _langfuse_disabled_reason


def _verify_langfuse_credentials(public_key: str, secret_key: str) -> bool:
    """Validate API keys once at startup; avoids repeated 401 noise from prompt fetch."""
    url = f"{LANGFUSE_HOST.rstrip('/')}/api/public/projects"
    try:
        response = httpx.get(url, auth=(public_key, secret_key), timeout=8.0)
    except httpx.HTTPError as exc:
        _disable_langfuse(f"unreachable ({exc})")
        return False

    if response.status_code in (401, 403):
        _disable_langfuse("invalid LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY or wrong LANGFUSE_HOST")
        return False
    if response.status_code >= 400:
        _disable_langfuse(f"health check failed (HTTP {response.status_code})")
        return False
    return True


def get_langfuse_client():
    """Return Langfuse client or None when disabled / unconfigured."""
    global _langfuse_client, _init_attempted
    if _init_attempted:
        return _langfuse_client
    _init_attempted = True

    if not OBSERVABILITY_ENABLED or not LANGFUSE_ENABLED:
        logger.debug("Langfuse disabled via config — tracing off")
        return None

    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    if not public_key or not secret_key:
        logger.debug("Langfuse keys not set — tracing disabled")
        return None

    if not _verify_langfuse_credentials(public_key, secret_key):
        return None

    try:
        from langfuse import Langfuse, get_client

        Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=LANGFUSE_HOST,
        )
        _langfuse_client = get_client()
        logger.info("Langfuse connected ({})", LANGFUSE_HOST)
    except Exception as exc:
        reason = "invalid credentials" if _is_langfuse_auth_error(exc) else str(exc)
        _disable_langfuse(reason)
    return _langfuse_client


def is_langfuse_enabled() -> bool:
    return get_langfuse_client() is not None


@contextmanager
def trace_context(ctx: TraceContext) -> Generator[None, None, None]:
    """Propagate tenant/session/user identifiers to all nested Langfuse observations."""
    if not _tracing_enabled() or _get_lf_client is None:
        yield
        return

    if _propagate_attributes is not None:
        with _propagate_attributes(
            session_id=ctx.session_id,
            user_id=ctx.user_id,
            tags=ctx.tags(),
            metadata=ctx.metadata(),
        ):
            yield
        return

    try:
        _get_lf_client().update_current_trace(
            session_id=ctx.session_id,
            user_id=ctx.user_id,
            tags=ctx.tags(),
            metadata=ctx.metadata(),
        )
    except Exception as exc:
        logger.debug("trace_context update failed: {}", exc)
    yield


def observe(*, name: str | None = None, as_type: str | None = None) -> Callable[[F], F]:
    """Decorator wrapping ``langfuse.observe`` — no-op when tracing is off (BookMe pattern)."""

    def _noop(fn: F) -> F:
        return fn

    if not _tracing_enabled() or _lf_observe is None:
        return _noop

    kwargs: dict[str, Any] = {}
    if name is not None:
        kwargs["name"] = name
    if as_type is not None:
        kwargs["as_type"] = as_type
    return _lf_observe(**kwargs)  # type: ignore[return-value]


def get_current_trace_id() -> str | None:
    """OpenTelemetry / Langfuse trace id for the active context, if any."""
    if _get_lf_client is None or not _tracing_enabled():
        return None
    try:
        client = _get_lf_client()
        fn = getattr(client, "get_current_trace_id", None)
        if callable(fn):
            tid = fn()
            return str(tid) if tid else None
    except Exception as exc:
        logger.debug("get_current_trace_id failed: {}", exc)
    return None


def flush() -> None:
    if _get_lf_client is None or not _tracing_enabled():
        return
    try:
        _get_lf_client().flush()
    except Exception as exc:
        logger.debug("Langfuse flush failed: {}", exc)


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
            if _is_langfuse_auth_error(exc):
                _disable_langfuse("prompt fetch unauthorized")
            else:
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
            if _is_langfuse_auth_error(exc):
                _disable_langfuse("prompt prefetch unauthorized")
                return warmed
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
    if not _tracing_enabled() or _get_lf_client is None:
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

    if _propagate_attributes is not None:
        with _propagate_attributes(**prop_kwargs):
            yield
        return

    try:
        _get_lf_client().update_current_trace(**prop_kwargs)
    except Exception as exc:
        logger.debug("langfuse_turn_attributes update failed: {}", exc)
    yield


def update_current_trace(
    *,
    user_id: str | None = None,
    session_id: str | None = None,
    metadata: dict[str, Any] | None = None,
    tags: list[str] | None = None,
) -> None:
    if _get_lf_client is None or not _tracing_enabled():
        return
    try:
        client = _get_lf_client()
        client.update_current_trace(
            user_id=user_id,
            session_id=session_id,
            metadata=metadata,
            tags=tags,
        )
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
    if _get_lf_client is None or not _tracing_enabled():
        return
    try:
        client = _get_lf_client()
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
