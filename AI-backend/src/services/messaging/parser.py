"""Parse Twilio application/x-www-form-urlencoded webhook bodies."""

from __future__ import annotations

from services.messaging.schemas import TwilioInboundMessage


def parse_twilio_form(form: dict[str, str]) -> TwilioInboundMessage:
    num_media_raw = form.get("NumMedia", "0")
    try:
        num_media = int(num_media_raw)
    except ValueError:
        num_media = 0

    payload = {
        "MessageSid": form.get("MessageSid", ""),
        "AccountSid": form.get("AccountSid", ""),
        "From": form.get("From", ""),
        "To": form.get("To", ""),
        "Body": form.get("Body", ""),
        "NumMedia": num_media,
        "MediaUrl0": form.get("MediaUrl0"),
        "MediaContentType0": form.get("MediaContentType0"),
        "ProfileName": form.get("ProfileName"),
    }
    return TwilioInboundMessage.model_validate(payload)
