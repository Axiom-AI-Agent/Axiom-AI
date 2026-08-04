"""Twilio WhatsApp webhook router."""

from __future__ import annotations

import os
from urllib.parse import parse_qsl

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, Response
from loguru import logger

from infrastructure.config import TWILIO_AUTH_TOKEN, TWILIO_VALIDATE_SIGNATURE
from services.messaging.parser import parse_twilio_form
from services.messaging.pipeline import ChatPipeline
from services.messaging.validator import validate_twilio_signature

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


def _parse_form_params(raw_body: bytes) -> dict[str, str]:
    decoded = raw_body.decode("utf-8") if raw_body else ""
    return {key: value for key, value in parse_qsl(decoded, keep_blank_values=True)}


def _webhook_public_url(request: Request) -> str:
    configured = os.getenv("TWILIO_WEBHOOK_URL")
    if configured:
        return configured.rstrip("/")
    return str(request.url).split("?")[0]


def _should_validate_signature() -> bool:
    if TWILIO_VALIDATE_SIGNATURE is False:
        return False
    return bool(TWILIO_AUTH_TOKEN)


@router.post("/twilio")
async def twilio_webhook(request: Request, background_tasks: BackgroundTasks) -> Response:
    """
    Twilio WhatsApp sandbox webhook.

    Returns 200 immediately and processes the reply in a BackgroundTask so we
    stay within Twilio's webhook timeout without a worker process.
    """
    raw_body = await request.body()
    params = _parse_form_params(raw_body)

    if _should_validate_signature():
        signature = request.headers.get("X-Twilio-Signature", "")
        url = _webhook_public_url(request)
        if not validate_twilio_signature(
            auth_token=TWILIO_AUTH_TOKEN,
            url=url,
            params=params,
            signature=signature,
        ):
            logger.warning("Twilio signature validation failed for url={}", url)
            raise HTTPException(status_code=403, detail="Invalid Twilio signature")

    if not params and raw_body:
        logger.debug("Empty parsed params; raw body length={}", len(raw_body))

    inbound = parse_twilio_form(params)
    if not inbound.from_number or not inbound.to_number:
        raise HTTPException(status_code=400, detail="Missing From or To in Twilio payload")

    pipeline = ChatPipeline()
    background_tasks.add_task(pipeline.process_twilio, inbound)
    return Response(status_code=200, content="")
