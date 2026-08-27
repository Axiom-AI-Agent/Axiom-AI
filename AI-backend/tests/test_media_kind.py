"""Regression tests for inbound media handling (B6).

The reported bug: a student photographed their bank slip and was told "Sorry, I
can only process voice notes (not audio files). Please record a voice message
instead." The inbound path only asked "is this a voice note?" and treated every
other attachment as a broken one, so the image never reached the payment agent.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from domain.enums import ChatChannel
from services.identity.context import IdentityContext
from services.media.media_kind import MediaKind, classify_media
from services.messaging.pipeline import ChatPipeline
from services.messaging.schemas import InboundMessage


@pytest.mark.parametrize(
    ("url", "content_type", "expected"),
    [
        ("https://api.twilio.com/media/abc", "image/jpeg", MediaKind.IMAGE),
        ("https://api.twilio.com/media/abc", "audio/ogg", MediaKind.VOICE_NOTE),
        ("https://api.twilio.com/media/abc", "application/pdf", MediaKind.DOCUMENT),
        ("https://api.twilio.com/media/abc", "audio/mpeg", MediaKind.AUDIO_FILE),
        ("https://api.twilio.com/media/abc", "video/mp4", MediaKind.VIDEO),
        ("https://cdn.example.com/slip.jpg", None, MediaKind.IMAGE),
        ("https://cdn.example.com/note.ogg", None, MediaKind.VOICE_NOTE),
        ("https://cdn.example.com/song.mp3", None, MediaKind.AUDIO_FILE),
        ("https://cdn.example.com/slip.pdf?X-Sig=abc", None, MediaKind.DOCUMENT),
        (None, None, MediaKind.NONE),
    ],
)
def test_media_kind_classification(url, content_type, expected):
    assert classify_media(url, content_type=content_type) is expected


def test_only_images_and_documents_are_treated_as_slips():
    assert MediaKind.IMAGE.is_payment_slip_candidate
    assert MediaKind.DOCUMENT.is_payment_slip_candidate
    assert not MediaKind.VOICE_NOTE.is_payment_slip_candidate
    assert not MediaKind.AUDIO_FILE.is_payment_slip_candidate
    assert not MediaKind.VIDEO.is_payment_slip_candidate


@pytest.fixture
def ctx() -> IdentityContext:
    return IdentityContext(
        tenant_id="tenant-demo-physics",
        tenant_slug="demo-physics",
        tenant_name="Demo Physics Academy",
        phone="94771234567",
        session_id="tenant-demo-physics:94771234567",
        student_exists=True,
    )


def _pipeline() -> ChatPipeline:
    return ChatPipeline(
        resolver=MagicMock(),
        messaging=MagicMock(),
        persistence=MagicMock(),
    )


def _image(**overrides) -> InboundMessage:
    payload = {
        "channel": ChatChannel.TWILIO_WHATSAPP,
        "phone": "94771234567",
        "body": "",
        "media_url": "https://api.twilio.com/media/slip",
        "media_content_type": "image/jpeg",
        "num_media": 1,
    }
    payload.update(overrides)
    return InboundMessage(**payload)


@pytest.mark.asyncio
async def test_b6_payment_slip_image_reaches_the_agent(ctx: IdentityContext):
    pipeline = _pipeline()
    pipeline._run_agent_turn = AsyncMock(return_value="Thanks! Checking your payment slip.")

    reply = await pipeline._build_reply(ctx, _image())

    assert "voice" not in reply.lower()
    assert reply == "Thanks! Checking your payment slip."
    pipeline._run_agent_turn.assert_awaited_once()


@pytest.mark.asyncio
async def test_b6_pdf_slip_also_reaches_the_agent(ctx: IdentityContext):
    pipeline = _pipeline()
    pipeline._run_agent_turn = AsyncMock(return_value="Got your slip.")

    reply = await pipeline._build_reply(
        ctx, _image(media_content_type="application/pdf")
    )

    assert reply == "Got your slip."


@pytest.mark.asyncio
async def test_a_real_audio_file_still_gets_the_voice_note_hint(ctx: IdentityContext):
    pipeline = _pipeline()
    pipeline._run_agent_turn = AsyncMock(return_value="should not be reached")

    reply = await pipeline._build_reply(
        ctx, _image(media_content_type="audio/mpeg")
    )

    assert "voice" in reply.lower()
    pipeline._run_agent_turn.assert_not_awaited()


@pytest.mark.asyncio
async def test_video_gets_its_own_message_not_the_voice_note_one(ctx: IdentityContext):
    pipeline = _pipeline()
    pipeline._run_agent_turn = AsyncMock(return_value="should not be reached")

    reply = await pipeline._build_reply(
        ctx, _image(media_content_type="video/mp4")
    )

    assert "voice notes" not in reply.lower()
    assert "photo" in reply.lower()


def test_twilio_form_carries_the_declared_content_type():
    from services.messaging.parser import parse_twilio_form

    parsed = parse_twilio_form(
        {
            "MessageSid": "SM1",
            "AccountSid": "AC1",
            "From": "whatsapp:+94771234567",
            "To": "whatsapp:+14155238886",
            "Body": "",
            "NumMedia": "1",
            "MediaUrl0": "https://api.twilio.com/media/abc",
            "MediaContentType0": "image/jpeg",
        }
    )
    assert parsed.media_content_type == "image/jpeg"
    assert (
        classify_media(parsed.media_url, content_type=parsed.media_content_type)
        is MediaKind.IMAGE
    )
