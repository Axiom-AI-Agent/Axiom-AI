from __future__ import annotations

import asyncio
import time
from collections import defaultdict, deque

from fastapi import Request
from starlette.middleware.base import (
    BaseHTTPMiddleware,
)
from starlette.responses import (
    JSONResponse,
    Response,
)


class RateLimitMiddleware(
    BaseHTTPMiddleware
):
    def __init__(
        self,
        app,
        *,
        default_limit: int = 120,
        window_seconds: int = 60,
    ):
        super().__init__(app)

        self.default_limit = (
            default_limit
        )

        self.window_seconds = (
            window_seconds
        )

        self._requests: dict[
            str,
            deque[float],
        ] = defaultdict(deque)

        self._lock = asyncio.Lock()

    def _limit_for_path(
        self,
        path: str,
    ) -> int:
        if path.startswith(
            "/webhooks/twilio"
        ) or path.startswith(
            "/webhooks/telegram"
        ):
            return 180

        if path.startswith(
            "/dashboard/chat/send"
        ):
            return 30

        if path.startswith("/chat"):
            return 60

        if path.startswith("/tools/"):
            return 40

        return self.default_limit

    def _client_key(
        self,
        request: Request,
    ) -> str:
        forwarded = (
            request.headers.get(
                "x-forwarded-for"
            )
        )

        if forwarded:
            client_ip = (
                forwarded.split(",")[0]
                .strip()
            )

        elif request.client:
            client_ip = (
                request.client.host
            )

        else:
            client_ip = "unknown"

        return (
            f"{client_ip}:"
            f"{request.url.path}"
        )

    async def dispatch(
        self,
        request: Request,
        call_next,
    ) -> Response:
        if request.method == "OPTIONS":
            return await call_next(
                request
            )

        path = request.url.path

        if path in {
            "/",
            "/health",
            "/ready",
            "/docs",
            "/openapi.json",
        }:
            return await call_next(
                request
            )

        now = time.monotonic()

        limit = self._limit_for_path(
            path
        )

        key = self._client_key(
            request
        )

        async with self._lock:
            bucket = self._requests[
                key
            ]

            cutoff = (
                now
                - self.window_seconds
            )

            while (
                bucket
                and bucket[0]
                <= cutoff
            ):
                bucket.popleft()

            if len(bucket) >= limit:
                retry_after = max(
                    int(
                        self.window_seconds
                        - (
                            now
                            - bucket[0]
                        )
                    ),
                    1,
                )

                return JSONResponse(
                    status_code=429,
                    content={
                        "detail":
                            "Rate limit exceeded.",
                    },
                    headers={
                        "Retry-After":
                            str(
                                retry_after
                            )
                    },
                )

            bucket.append(now)

        response = await call_next(
            request
        )

        response.headers[
            "X-RateLimit-Limit"
        ] = str(limit)

        return response
