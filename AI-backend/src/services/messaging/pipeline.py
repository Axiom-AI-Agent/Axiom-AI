"""Process inbound student messages and produce agent replies."""

from __future__ import annotations

import asyncio

from loguru import logger

from agents.chat_pipeline import run_chat_turn
from agents.runtime import get_decision_graph, get_orchestrator
from domain.enums import ChatChannel
from infrastructure.observability import flush
from services.identity.context import IdentityContext
from services.identity.resolver import IdentityResolver
from services.language import resolve_reply_language, stt_language_hint, t
from services.media.stt_service import _get_twilio_auth, _is_audio_url, transcribe_audio
from services.messaging.persistence import MessagePersistence
from services.messaging.schemas import ChatTurnResult, InboundMessage, TwilioInboundMessage
from services.messaging.twilio_client import TwilioMessagingClient


class ChatPipeline:
    """Channel-agnostic chat pipeline — HTTP dev chat + Twilio webhook."""

    def __init__(
        self,
        *,
        resolver: IdentityResolver | None = None,
        messaging: TwilioMessagingClient | None = None,
        persistence: MessagePersistence | None = None,
    ) -> None:
        self.resolver = resolver or IdentityResolver()
        self.messaging = messaging or TwilioMessagingClient()
        self.persistence = persistence or MessagePersistence()

    async def aprocess_message(self, inbound: InboundMessage) -> ChatTurnResult:
        ctx = self._resolve_identity(inbound)

        self.persistence.log_inbound(
            ctx,
            body=inbound.body,
            media_url=inbound.media_url,
            intent="chat_inbound",
            channel=inbound.channel,
        )

        if ctx.human_mode:
            logger.info("Human mode active for session {} — skipping auto-reply", ctx.session_id)
            flush()
            return self._result(ctx, inbound, reply="")

        reply = await self._build_reply(ctx, inbound)
        self._deliver_reply(ctx, inbound, reply)

        flush()
        return self._result(ctx, inbound, reply=reply)

    def process_message(self, inbound: InboundMessage) -> ChatTurnResult:
        """Sync entry for scripts and tests without a running event loop."""
        return asyncio.run(self.aprocess_message(inbound))

    async def aprocess_twilio(self, inbound: TwilioInboundMessage) -> ChatTurnResult:
        return await self.aprocess_message(
            InboundMessage(
                channel=ChatChannel.TWILIO_WHATSAPP,
                phone=inbound.from_number,
                body=inbound.body,
                to_number=inbound.to_number,
                media_url=inbound.media_url,
                external_id=inbound.message_sid,
                num_media=inbound.num_media,
            )
        )

    def process_twilio(self, inbound: TwilioInboundMessage) -> ChatTurnResult:
        return asyncio.run(self.aprocess_twilio(inbound))

    def _resolve_identity(self, inbound: InboundMessage) -> IdentityContext:
        if inbound.tenant_id:
            return self.resolver.resolve_direct(
                tenant_id=inbound.tenant_id,
                phone=inbound.phone,
            )
        if not inbound.to_number:
            raise ValueError("tenant_id or to_number is required to resolve identity")
        return self.resolver.resolve(
            to_number=inbound.to_number,
            from_number=inbound.phone,
        )

    def _deliver_reply(
        self,
        ctx: IdentityContext,
        inbound: InboundMessage,
        reply: str,
    ) -> None:
        if inbound.channel == ChatChannel.TWILIO_WHATSAPP and inbound.to_number:
            result = self.messaging.send_whatsapp(
                to_number=inbound.phone,
                body=reply,
                from_number=inbound.to_number,
            )
            if result.status in {"sent", "dry_run"}:
                self.persistence.log_outbound(
                    ctx, body=reply, intent="auto_reply", channel=inbound.channel
                )
            return

        if reply:
            self.persistence.log_outbound(
                ctx, body=reply, intent="chat_reply", channel=inbound.channel
            )

    async def _build_reply(self, ctx: IdentityContext, inbound: InboundMessage) -> str:
        # Media attached — check if it's a voice note or unsupported audio
        if inbound.num_media > 0 and inbound.media_url:
            if _is_audio_url(inbound.media_url):
                # Voice note: transcribe before agent processing
                auth = _get_twilio_auth() if inbound.channel == ChatChannel.TWILIO_WHATSAPP else None
                transcript = await transcribe_audio(
                    inbound.media_url,
                    message_sid=inbound.external_id,
                    sender_id=ctx.student_id or ctx.phone,
                    language_hint=stt_language_hint(ctx.language_pref),
                    auth=auth,
                )
                if transcript:
                    inbound.body = transcript
                else:
                    lang = resolve_reply_language(
                        message=inbound.body or "",
                        language_pref=ctx.language_pref,
                    )
                    return t("voice_fail", lang)
            else:
                # Non-voice audio file (MP3, WAV, etc.) — not supported
                lang = resolve_reply_language(
                    message=inbound.body or "",
                    language_pref=ctx.language_pref,
                )
                return t("unsupported_audio", lang)

        try:
            reply = await self._run_agent_turn(ctx, inbound)
        except Exception as exc:
            logger.error("Agent pipeline failed: {}", exc)
            tenant_label = ctx.tenant_name or ctx.tenant_slug or "your tuition centre"
            lang = resolve_reply_language(
                message=inbound.body or "",
                language_pref=ctx.language_pref,
            )
            reply = t("technical_issue", lang, tenant_name=tenant_label)

        if inbound.num_media > 0 and inbound.media_url:
            pass  # payment receipt handled by payment agent when pending enrollment exists

        return reply

    async def _run_agent_turn(self, ctx: IdentityContext, inbound: InboundMessage) -> str:
        orchestrator = await get_orchestrator()
        result = await run_chat_turn(
            ctx=ctx,
            message=inbound.body,
            decision_graph=get_decision_graph(),
            orchestrator=orchestrator,
            channel=inbound.channel.value,
            media_url=inbound.media_url,
            extra_metadata={
                "external_id": inbound.external_id,
                "student_exists": ctx.student_exists,
                "num_media": inbound.num_media,
            },
        )
        return result.answer.strip()

    def _result(
        self,
        ctx: IdentityContext,
        inbound: InboundMessage,
        *,
        reply: str,
    ) -> ChatTurnResult:
        return ChatTurnResult(
            reply=reply,
            tenant_id=ctx.tenant_id,
            tenant_slug=ctx.tenant_slug,
            tenant_name=ctx.tenant_name,
            student_id=ctx.student_id or "",
            phone=ctx.phone,
            session_id=ctx.session_id,
            student_exists=ctx.student_exists,
            channel=inbound.channel,
        )


WhatsAppPipeline = ChatPipeline
