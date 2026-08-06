"""Twilio request signature validation."""

from __future__ import annotations


def validate_twilio_signature(
    *,
    auth_token: str,
    url: str,
    params: dict[str, str],
    signature: str,
) -> bool:
    if not auth_token:
        return False
    if not signature:
        return False

    from twilio.request_validator import RequestValidator

    return RequestValidator(auth_token).validate(url, params, signature)
