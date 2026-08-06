"""Twilio signature validation tests."""

from twilio.request_validator import RequestValidator

from services.messaging.validator import validate_twilio_signature

AUTH_TOKEN = "test_auth_token"
WEBHOOK_URL = "https://example.com/webhooks/twilio"
PARAMS = {
    "MessageSid": "SM123",
    "AccountSid": "AC123",
    "From": "whatsapp:+94771234567",
    "To": "whatsapp:+14155238886",
    "Body": "Hello Axiom",
}


def _sign(url: str, params: dict[str, str], token: str) -> str:
    validator = RequestValidator(token)
    return validator.compute_signature(url, params)


def test_validate_twilio_signature_accepts_valid_signature():
    signature = _sign(WEBHOOK_URL, PARAMS, AUTH_TOKEN)
    assert validate_twilio_signature(
        auth_token=AUTH_TOKEN,
        url=WEBHOOK_URL,
        params=PARAMS,
        signature=signature,
    )


def test_validate_twilio_signature_rejects_invalid_signature():
    assert not validate_twilio_signature(
        auth_token=AUTH_TOKEN,
        url=WEBHOOK_URL,
        params=PARAMS,
        signature="invalid",
    )


def test_validate_twilio_signature_rejects_tampered_body():
    signature = _sign(WEBHOOK_URL, PARAMS, AUTH_TOKEN)
    tampered = {**PARAMS, "Body": "tampered"}
    assert not validate_twilio_signature(
        auth_token=AUTH_TOKEN,
        url=WEBHOOK_URL,
        params=tampered,
        signature=signature,
    )
