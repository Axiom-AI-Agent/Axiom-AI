"""Speech-to-text service — download voice notes and transcribe via Gemini.

Features:
- Voice note only (.ogg/.opus) — rejects other audio formats
- Content-Type validation from HTTP response
- Configurable resource limits (file size, duration, timeouts)
- Idempotency cache (avoids re-transcribing duplicate webhooks)
- Concurrency locks for duplicate webhook handling
- Audio duration measurement via mutagen
- Exponential backoff retries for transient failures
- Phone number masking in logs (no PII exposure)
- Basic metrics counters (success/failure/latency)
- Configurable Gemini model
- Total deadline around entire operation
"""

from __future__ import annotations

import asyncio
import base64
import os
import re
import time
from abc import ABC, abstractmethod
from typing import Any

import httpx
from loguru import logger

from infrastructure.config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    get_api_key,
)

# ---------------------------------------------------------------------------
# Configuration (all overridable via .env)
# ---------------------------------------------------------------------------

def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw.strip())
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw.strip())
    except ValueError:
        return default


# Voice note formats only (WhatsApp/Telegram send .ogg Opus)
VOICE_NOTE_EXTENSIONS: frozenset[str] = frozenset({".ogg", ".oga", ".opus"})

# Resource limits (configurable via .env)
MAX_AUDIO_BYTES = _env_int("STT_MAX_AUDIO_BYTES", 10 * 1024 * 1024)  # 10 MB
MAX_AUDIO_DURATION_SECONDS = _env_int("STT_MAX_AUDIO_DURATION_SECONDS", 300)  # 5 min
DOWNLOAD_TIMEOUT_SECONDS = _env_int("STT_DOWNLOAD_TIMEOUT_SECONDS", 30)
GEMINI_TIMEOUT_SECONDS = _env_int("STT_GEMINI_TIMEOUT_SECONDS", 60)
TOTAL_DEADLINE_SECONDS = _env_int("STT_TOTAL_DEADLINE_SECONDS", 90)

# Retry config for transient failures
MAX_RETRIES = _env_int("STT_MAX_RETRIES", 2)
RETRY_BASE_DELAY = _env_float("STT_RETRY_BASE_DELAY", 1.0)  # seconds

# Gemini model (configurable via .env)
GEMINI_MODEL = os.getenv("STT_GEMINI_MODEL", "gemini-3.6-flash")

# Idempotency cache TTL (seconds) — keep entries for 2 hours
_CACHE_TTL = _env_int("STT_CACHE_TTL_SECONDS", 7200)

# ---------------------------------------------------------------------------
# Metrics (simple in-memory counters)
# ---------------------------------------------------------------------------

class SttMetrics:
    """Simple counters for transcription metrics."""

    def __init__(self) -> None:
        self.successes = 0
        self.failures = 0
        self.cache_hits = 0
        self.duplicates_skipped = 0
        self.total_latency_ms = 0
        self.total_download_ms = 0
        self.total_gemini_ms = 0

    def record_success(self, latency_ms: int, download_ms: int, gemini_ms: int) -> None:
        self.successes += 1
        self.total_latency_ms += latency_ms
        self.total_download_ms += download_ms
        self.total_gemini_ms += gemini_ms

    def record_failure(self, latency_ms: int) -> None:
        self.failures += 1
        self.total_latency_ms += latency_ms

    def record_cache_hit(self) -> None:
        self.cache_hits += 1

    def record_duplicate_skipped(self) -> None:
        self.duplicates_skipped += 1

    def to_dict(self) -> dict[str, Any]:
        total = self.successes + self.failures
        return {
            "successes": self.successes,
            "failures": self.failures,
            "cache_hits": self.cache_hits,
            "duplicates_skipped": self.duplicates_skipped,
            "avg_latency_ms": (self.total_latency_ms // total) if total else 0,
            "avg_download_ms": (self.total_download_ms // self.successes) if self.successes else 0,
            "avg_gemini_ms": (self.total_gemini_ms // self.successes) if self.successes else 0,
        }


_metrics = SttMetrics()


def get_stt_metrics() -> dict[str, Any]:
    """Return current transcription metrics. Call from a /metrics endpoint."""
    return _metrics.to_dict()


# ---------------------------------------------------------------------------
# PII masking
# ---------------------------------------------------------------------------

_PHONE_MASK_RE = re.compile(r"(\+\d{2})\d+(\d{4})")


def _mask_phone(phone: str | None) -> str:
    """Mask phone number: +9477****567. Returns 'unknown' if None."""
    if not phone:
        return "unknown"
    match = _PHONE_MASK_RE.match(phone)
    if match:
        return f"{match.group(1)}****{match.group(2)}"
    if len(phone) > 6:
        return phone[:3] + "****" + phone[-3:]
    return "****"


# ---------------------------------------------------------------------------
# Abstract cache interface (replaceable with Redis/DB)
# ---------------------------------------------------------------------------

class SttCache(ABC):
    """Abstract cache for idempotency. Implement get/set/delete for Redis/DB."""

    @abstractmethod
    def get(self, key: str) -> str | None:
        """Return cached transcript, or None if miss/expired."""

    @abstractmethod
    def set(self, key: str, value: str | None, ttl: int) -> None:
        """Store value with TTL in seconds. value=None means 'in-progress'."""

    @abstractmethod
    def delete(self, key: str) -> None:
        """Remove entry."""


class InMemorySttCache(SttCache):
    """In-memory cache with TTL. Replace with RedisSttCache for production."""

    def __init__(self) -> None:
        self._store: dict[str, tuple[str | None, float]] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        self._global_lock = asyncio.Lock()

    async def get_lock(self, key: str) -> asyncio.Lock:
        """Get or create a per-key lock for concurrency control."""
        if key not in self._locks:
            async with self._global_lock:
                if key not in self._locks:
                    self._locks[key] = asyncio.Lock()
        return self._locks[key]

    def get(self, key: str) -> str | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, ts = entry
        if time.monotonic() - ts > _CACHE_TTL:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: str | None, ttl: int) -> None:
        self._store[key] = (value, time.monotonic())

    def delete(self, key: str) -> None:
        self._store.pop(key, None)


# Global cache instance — swap this for Redis in production
_cache: SttCache = InMemorySttCache()


def _cache_key(message_sid: str) -> str:
    return f"stt:{message_sid}"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_audio_url(url: str) -> bool:
    """Check if a URL points to a voice note file (.ogg/.opus) based on extension."""
    lower = url.lower().split("?")[0]
    return any(lower.endswith(ext) for ext in VOICE_NOTE_EXTENSIONS)


def _content_type_supported(content_type: str | None) -> bool:
    """Check if the Content-Type header indicates a voice note (OGG Opus)."""
    if not content_type:
        return False
    main = content_type.split(";")[0].strip().lower()
    # Telegram returns application/octet-stream, WhatsApp returns audio/ogg
    return main in {"audio/ogg", "application/octet-stream"}


def _get_twilio_auth() -> tuple[str, str] | None:
    """Return (account_sid, auth_token) if configured, else None."""
    if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
        return TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
    return None


def _is_retryable(exc: Exception) -> bool:
    """Check if an exception is transient and worth retrying."""
    if isinstance(exc, (httpx.TimeoutException, httpx.ConnectError)):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code >= 500 or exc.response.status_code == 429
    return False


def _measure_audio_duration(audio_bytes: bytes, content_type: str | None) -> float | None:
    """Measure voice note duration in seconds using mutagen. Returns None if measurement fails."""
    try:
        import io
        from mutagen.oggopus import OggOpus

        audio_file = io.BytesIO(audio_bytes)
        ogg = OggOpus(audio_file)
        return ogg.info.length

    except ImportError:
        logger.debug("stt: mutagen not installed — skipping duration check")
        return None
    except Exception as exc:
        logger.debug("stt: Duration measurement failed: {}", exc)
        return None


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------

async def _download_with_retry(
    media_url: str,
    *,
    auth: tuple[str, str] | None = None,
) -> tuple[bytes, str | None] | None:
    """
    Download voice note from a URL with retry and Content-Type validation.

    If auth is provided, uses HTTP Basic Auth (required for Twilio).
    If auth is None, downloads without auth (works for Telegram, public URLs).

    Returns (audio_bytes, content_type) or None on failure.
    """
    last_exc: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 2):
        try:
            async with httpx.AsyncClient(timeout=DOWNLOAD_TIMEOUT_SECONDS) as client:
                request_kwargs: dict[str, Any] = {
                    "url": media_url,
                    "follow_redirects": True,
                }
                if auth:
                    request_kwargs["auth"] = auth
                response = await client.get(**request_kwargs)
                response.raise_for_status()

                content_type = response.headers.get("content-type")
                content = response.content

                if not _content_type_supported(content_type):
                    logger.warning("stt: Not a voice note (Content-Type: {})", content_type)
                    return None

                if len(content) > MAX_AUDIO_BYTES:
                    logger.warning("stt: Voice note too large: {} bytes (max {})", len(content), MAX_AUDIO_BYTES)
                    return None

                if len(content) == 0:
                    logger.warning("stt: Downloaded voice note is empty")
                    return None

                return content, content_type

        except Exception as exc:
            last_exc = exc
            if not _is_retryable(exc) or attempt > MAX_RETRIES:
                break
            delay = RETRY_BASE_DELAY * (2 ** (attempt - 1))
            logger.warning(
                "stt: Download attempt {}/{} failed ({}), retrying in {:.1f}s",
                attempt, MAX_RETRIES + 1, type(exc).__name__, delay,
            )
            await asyncio.sleep(delay)

    if last_exc:
        logger.error("stt: Download failed after {} attempts: {}", MAX_RETRIES + 1, last_exc)
    return None


# ---------------------------------------------------------------------------
# Gemini transcription
# ---------------------------------------------------------------------------

async def _call_gemini(
    audio_bytes: bytes,
    content_type: str,
    *,
    language_hint: str | None = None,
) -> str | None:
    """Send voice note to Gemini for transcription with retry."""
    api_key = get_api_key("google")
    if not api_key:
        logger.error("stt: GOOGLE_API_KEY not configured")
        return None

    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

    prompt = (
        "Transcribe this voice message exactly as spoken. "
        "Return only the transcription text, nothing else. "
        "Preserve the original language of the speaker."
    )
    if language_hint:
        prompt += f" The audio is likely in {language_hint}."

    last_exc: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 2):
        try:
            from langchain_core.messages import HumanMessage
            from langchain_google_genai import ChatGoogleGenerativeAI

            llm = ChatGoogleGenerativeAI(
                model=GEMINI_MODEL,
                google_api_key=api_key,
                temperature=0,
                timeout=GEMINI_TIMEOUT_SECONDS,
            )

            response = await llm.ainvoke(
                [
                    HumanMessage(
                        content=[
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{content_type};base64,{audio_b64}"
                                },
                            },
                        ]
                    )
                ]
            )

            transcript = response.content.strip()

            if not transcript:
                logger.warning("stt: Gemini returned empty transcription")
                return None

            return transcript

        except Exception as exc:
            last_exc = exc
            if not _is_retryable(exc) or attempt > MAX_RETRIES:
                break
            delay = RETRY_BASE_DELAY * (2 ** (attempt - 1))
            logger.warning(
                "stt: Gemini attempt {}/{} failed ({}), retrying in {:.1f}s",
                attempt, MAX_RETRIES + 1, type(exc).__name__, delay,
            )
            await asyncio.sleep(delay)

    if last_exc:
        logger.error("stt: Gemini failed after {} attempts: {}", MAX_RETRIES + 1, last_exc)
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def transcribe_audio(
    media_url: str,
    *,
    message_sid: str | None = None,
    sender_id: str | None = None,
    language_hint: str | None = None,
    auth: tuple[str, str] | None = None,
) -> str | None:
    """
    Download a voice note and transcribe via Gemini.

    Args:
        media_url: Voice note URL (.ogg/.opus).
        message_sid: Unique message ID for idempotency and logging.
        sender_id: Student phone/ID for logging (masked in logs).
        language_hint: Optional language hint (e.g. "Sinhala", "Tamil").
        auth: Optional (username, password) for HTTP Basic Auth.
              Pass Twilio (SID, Token) for WhatsApp.
              Pass None for Telegram or public URLs.

    Returns:
        Transcribed text, or None if transcription fails.
    """
    sid = message_sid or "unknown"
    masked_sender = _mask_phone(sender_id)
    t_start = time.monotonic()

    # --- Idempotency + concurrency ---
    if message_sid:
        cache_key = _cache_key(message_sid)
        cached = _cache.get(cache_key)

        if cached is not None:
            if cached == "":
                _metrics.record_duplicate_skipped()
                logger.info("stt: Skipping duplicate (in-progress) sid={}", sid)
                return None
            _metrics.record_cache_hit()
            logger.info("stt: Cache hit sid={} sender={} chars={}", sid, masked_sender, len(cached))
            return cached

        lock = await _cache.get_lock(cache_key)
        async with lock:
            cached = _cache.get(cache_key)
            if cached is not None:
                if cached == "":
                    _metrics.record_duplicate_skipped()
                    logger.info("stt: Skipping duplicate (locked) sid={}", sid)
                    return None
                _metrics.record_cache_hit()
                logger.info("stt: Cache hit sid={} sender={} chars={}", sid, masked_sender, len(cached))
                return cached

            _cache.set(cache_key, "", _CACHE_TTL)

    logger.info("stt: Start sid={} sender={}", sid, masked_sender)

    try:
        async def _with_deadline() -> str | None:
            return await _transcribe_impl(
                media_url,
                message_sid=message_sid,
                sender_id=sender_id,
                language_hint=language_hint,
                auth=auth,
            )

        try:
            result = await asyncio.wait_for(_with_deadline(), timeout=TOTAL_DEADLINE_SECONDS)
        except asyncio.TimeoutError:
            elapsed_ms = int((time.monotonic() - t_start) * 1000)
            _metrics.record_failure(elapsed_ms)
            logger.error("stt: Total deadline exceeded ({}s) sid={}", TOTAL_DEADLINE_SECONDS, sid)
            if message_sid:
                _cache.delete(_cache_key(message_sid))
            return None

        if message_sid:
            _cache.set(_cache_key(message_sid), result or "", _CACHE_TTL)

        elapsed_ms = int((time.monotonic() - t_start) * 1000)
        if result:
            _metrics.record_success(elapsed_ms, 0, 0)
            logger.info("stt: Success sid={} sender={} chars={} elapsed={}ms", sid, masked_sender, len(result), elapsed_ms)
        else:
            _metrics.record_failure(elapsed_ms)
            logger.warning("stt: Failed sid={} sender={} elapsed={}ms", sid, masked_sender, elapsed_ms)

        return result

    except Exception as exc:
        elapsed_ms = int((time.monotonic() - t_start) * 1000)
        _metrics.record_failure(elapsed_ms)
        logger.error("stt: Unexpected error sid={} sender={} elapsed={}ms error={}", sid, masked_sender, elapsed_ms, type(exc).__name__)
        if message_sid:
            _cache.delete(_cache_key(message_sid))
        return None


async def _transcribe_impl(
    media_url: str,
    *,
    message_sid: str | None = None,
    sender_id: str | None = None,
    language_hint: str | None = None,
    auth: tuple[str, str] | None = None,
) -> str | None:
    """Core transcription logic (called within deadline wrapper)."""
    sid = message_sid or "unknown"
    masked_sender = _mask_phone(sender_id)

    # Step 1: Download
    t_download = time.monotonic()
    download_result = await _download_with_retry(media_url, auth=auth)
    download_ms = int((time.monotonic() - t_download) * 1000)

    if not download_result:
        return None

    audio_bytes, content_type = download_result
    file_size = len(audio_bytes)

    # Step 2: Measure duration
    duration_s = _measure_audio_duration(audio_bytes, content_type)
    if duration_s is not None and duration_s > MAX_AUDIO_DURATION_SECONDS:
        logger.warning("stt: Voice note too long: {:.1f}s (max {}s) sid={}", duration_s, MAX_AUDIO_DURATION_SECONDS, sid)
        return None

    duration_label = f"{duration_s:.1f}s" if duration_s else "unknown"
    logger.info("stt: Downloaded sid={} sender={} size={} duration={} download_ms={}", sid, masked_sender, file_size, duration_label, download_ms)

    # Step 3: Transcribe
    t_gemini = time.monotonic()
    transcript = await _call_gemini(audio_bytes, content_type or "audio/ogg", language_hint=language_hint)
    gemini_ms = int((time.monotonic() - t_gemini) * 1000)

    if transcript:
        logger.info("stt: Transcribed sid={} chars={} download_ms={} gemini_ms={}", sid, len(transcript), download_ms, gemini_ms)
    else:
        logger.warning("stt: Transcription failed sid={} download_ms={} gemini_ms={}", sid, download_ms, gemini_ms)

    return transcript
