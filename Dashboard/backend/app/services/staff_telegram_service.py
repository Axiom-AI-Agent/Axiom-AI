import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.enums import ChatChannel
from app.models.staff_channel import StaffChannel
from app.models.staff_link_code import StaffLinkCode
from app.models.staff_user import StaffUser

LINK_TTL_MINUTES = 10
CODE_PREFIX = "AXIOM-"


def create_staff_link_code(db: Session, staff: StaffUser) -> StaffLinkCode:
    now = datetime.now(timezone.utc)
    pending = (
        db.query(StaffLinkCode)
        .filter(
            StaffLinkCode.staff_id == staff.id,
            StaffLinkCode.consumed_at.is_(None),
        )
        .all()
    )
    for row in pending:
        row.consumed_at = now

    code = f"{CODE_PREFIX}{secrets.token_hex(4).upper()}"
    record = StaffLinkCode(
        id=str(uuid.uuid4()),
        tenant_id=staff.tenant_id,
        staff_id=staff.id,
        code=code,
        expires_at=now + timedelta(minutes=LINK_TTL_MINUTES),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_telegram_link_status(db: Session, staff: StaffUser) -> dict:
    channel = (
        db.query(StaffChannel)
        .filter(
            StaffChannel.staff_id == staff.id,
            StaffChannel.channel == ChatChannel.TELEGRAM,
        )
        .first()
    )
    return {
        "linked": channel is not None,
        "channel": ChatChannel.TELEGRAM.value if channel else None,
        "channel_address": channel.channel_address if channel else None,
        "linked_at": channel.created_at if channel else None,
    }


def unlink_telegram(db: Session, staff: StaffUser) -> None:
    (
        db.query(StaffChannel)
        .filter(
            StaffChannel.staff_id == staff.id,
            StaffChannel.channel == ChatChannel.TELEGRAM,
        )
        .delete()
    )
    db.commit()
