"""Process inbound student messages and produce agent replies."""

from __future__ import annotations

from loguru import logger

from domain.enums import ChatChannel
from infrastructure.observability import TraceContext, flush, observe, trace_context
from services.identity.context import IdentityContext
from services.identity.resolver import IdentityResolver
from services.messaging.persistence import MessagePersistence
from services.messaging.schemas import ChatTurnResult, InboundMessage, TwilioInboundMessage
from services.messaging.twilio_client import TwilioMessagingClient

PHASE1_REPLY_TEMPLATE = (
    "Thanks for messaging {tenant_name}! Axiom AI is connected and received your message. "
    "An agent will help you soon."
)


class ChatPipeline:
    """Channel-agnostic chat pipeline — HTTP dev chat now, Twilio later."""

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

    @observe(name="chat_turn")
    def process_message(self, inbound: InboundMessage) -> ChatTurnResult:
        ctx = self._resolve_identity(inbound)

        trace = TraceContext(
            tenant_id=ctx.tenant_id,
            session_id=ctx.session_id,
            user_id=ctx.student_id,
            tenant_slug=ctx.tenant_slug,
            channel=inbound.channel.value,
            extra_metadata={
                "external_id": inbound.external_id,
                "student_registered": ctx.student_registered,
                "num_media": inbound.num_media,
            },
        )

        with trace_context(trace):
            self.persistence.log_inbound(
                ctx,
                body=inbound.body,
                media_url=inbound.media_url,
                intent="chat_inbound",
            )

            if ctx.human_mode:
                logger.info("Human mode active for session {} — skipping auto-reply", ctx.session_id)
                flush()
                return ChatTurnResult(
                    reply="",
                    tenant_id=ctx.tenant_id,
                    tenant_slug=ctx.tenant_slug,
                    tenant_name=ctx.tenant_name,
                    student_id=ctx.student_id,
                    phone=ctx.phone,
                    session_id=ctx.session_id,
                    student_registered=ctx.student_registered,
                    channel=inbound.channel,
                )

            reply = self._build_reply(ctx, inbound)
            self._deliver_reply(ctx, inbound, reply)

            flush()
            return ChatTurnResult(
                reply=reply,
                tenant_id=ctx.tenant_id,
                tenant_slug=ctx.tenant_slug,
                tenant_name=ctx.tenant_name,
                student_id=ctx.student_id,
                phone=ctx.phone,
                session_id=ctx.session_id,
                student_registered=ctx.student_registered,
                channel=inbound.channel,
            )

    def process_twilio(self, inbound: TwilioInboundMessage) -> ChatTurnResult:
        """Adapter for the Twilio webhook (deferred until sandbox is configured)."""
        return self.process_message(
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
        # Twilio REST send only on the real webhook path (has to_number).
        # HTTP dev chat skips external delivery — reply is returned in the response.
        if inbound.channel == ChatChannel.TWILIO_WHATSAPP and inbound.to_number:
            result = self.messaging.send_whatsapp(
                to_number=inbound.phone,
                body=reply,
                from_number=inbound.to_number,
            )
            if result.status in {"sent", "dry_run"}:
                self.persistence.log_outbound(ctx, body=reply, intent="auto_reply")
            return

        self.persistence.log_outbound(ctx, body=reply, intent="chat_reply")

    def _build_reply(self, ctx: IdentityContext, inbound: InboundMessage) -> str:
        tenant_label = ctx.tenant_name or ctx.tenant_slug or "your tuition centre"
        reply = PHASE1_REPLY_TEMPLATE.format(tenant_name=tenant_label)

        if inbound.num_media > 0 and inbound.media_url:
            reply += " (We received your image — payment review comes in Phase 5.)"

        if not ctx.student_registered:
            reply += " Welcome! We created a profile for this number."

        return reply


# Backwards-compatible alias for existing imports/tests
WhatsAppPipeline = ChatPipeline
