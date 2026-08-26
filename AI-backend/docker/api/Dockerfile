# =============================================================================
# Axiom AI — API container (multi-stage: builder venv + slim runtime)
#
#   1. builder — installs requirements.txt into /opt/venv
#   2. runtime — copies venv + src/ + config/, runs uvicorn with MCP stdio
#      subprocesses (same Python as the API process).
#
# No Playwright / torch — lean runtime image.
#
# Ingest adds ~190 MB: pymupdf (110 MB, includes the ONNX layout/table weights
# used by pymupdf4llm) + onnxruntime (80 MB). Weights ship inside the wheels, so
# there is no download at startup and no network dependency at inference. Scanned
# pages go to the Gemini vision API rather than a local OCR engine, which is what
# keeps torch and the multi-GB Docling model set out of this image.
# =============================================================================

# syntax=docker/dockerfile:1

# ── Stage 1 — build deps ─────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /build
COPY requirements.txt ./
RUN pip install --upgrade pip wheel \
 && pip install -r requirements.txt

# ── Stage 2 — runtime ───────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    PATH="/opt/venv/bin:$PATH" \
    LANGFUSE_PROMPTS=false

RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
COPY src    ./src
COPY config ./config

# Lifespan warms MCP tools + router; allow buffer on cold start.
HEALTHCHECK --interval=30s --timeout=5s --start-period=120s --retries=3 \
    CMD sh -c 'curl -fsS "http://127.0.0.1:${PORT:-8000}/health" || exit 1'

EXPOSE 8000

# Render (and other PaaS) inject PORT; docker-compose keeps default 8000.
CMD ["sh", "-c", "exec uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers"]
