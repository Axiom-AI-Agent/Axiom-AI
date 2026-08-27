import os
import re
import uuid

from datetime import (
    datetime,
    timedelta,
    timezone,
)

import bcrypt

from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.models import (
    StaffUser,
    Tenant,
)

from app.models.enums import (
    StaffRole,
    TenantStatus,
)

from app.schemas.auth import (
    OrganizationRegisterRequest,
)
from app.services.onboarding_fields import (
    save_tenant_onboarding_fields,
)


JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
)

JWT_ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "HS256",
)

JWT_EXPIRE_MINUTES = int(
    os.getenv(
        "JWT_EXPIRE_MINUTES",
        "480",
    )
)


if not JWT_SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY is missing from environment"
    )


def hash_password(
    password: str,
) -> str:
    encoded = password.encode(
        "utf-8",
    )

    hashed = bcrypt.hashpw(
        encoded,
        bcrypt.gensalt(),
    )

    return hashed.decode(
        "utf-8",
    )


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except ValueError:
        return False


def slugify(
    value: str,
) -> str:
    slug = value.lower().strip()

    slug = re.sub(
        r"[^a-z0-9]+",
        "-",
        slug,
    )

    return slug.strip("-") or "institution"


def build_unique_slug(
    db: Session,
    name: str,
) -> str:
    base = slugify(name)
    slug = base
    counter = 2

    while (
        db.query(Tenant)
        .filter(
            Tenant.slug == slug,
        )
        .first()
        is not None
    ):
        slug = (
            f"{base}-{counter}"
        )
        counter += 1

    return slug


def create_access_token(
    staff: StaffUser,
) -> str:
    expires = (
        datetime.now(
            timezone.utc,
        )
        + timedelta(
            minutes=JWT_EXPIRE_MINUTES,
        )
    )

    payload = {
        "sub": staff.id,
        "tenant_id": staff.tenant_id,
        "email": staff.email,
        "role": staff.role.value,
        "exp": expires,
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def decode_access_token(
    token: str,
) -> dict:
    try:
        return jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[
                JWT_ALGORITHM,
            ],
        )

    except JWTError as error:
        raise ValueError(
            "Invalid or expired token"
        ) from error


def authenticate_staff(
    db: Session,
    email: str,
    password: str,
) -> StaffUser | None:
    normalized_email = (
        email.strip().lower()
    )

    staff = (
        db.query(StaffUser)
        .filter(
            StaffUser.email
            == normalized_email,
            StaffUser.is_active.is_(
                True,
            ),
        )
        .first()
    )

    if staff is None:
        return None

    if not staff.password_hash:
        return None

    if not verify_password(
        password,
        staff.password_hash,
    ):
        return None

    return staff


def register_organization(
    db: Session,
    payload:
        OrganizationRegisterRequest,
) -> tuple[
    Tenant,
    StaffUser,
    list[StaffUser],
]:
    emails = [
        payload.admin.email,
        *[
            staff.email
            for staff
            in payload.staff_members
        ],
    ]

    if len(emails) != len(
        set(emails)
    ):
        raise ValueError(
            "Duplicate staff email addresses are not allowed."
        )

    existing = (
        db.query(StaffUser)
        .filter(
            StaffUser.email.in_(
                emails,
            ),
        )
        .first()
    )

    if existing is not None:
        raise ValueError(
            "One of the email addresses is already registered."
        )

    slug = build_unique_slug(
        db,
        payload.institution_name,
    )

    tenant = Tenant(
        id=(
            f"tenant-{slug}-"
            f"{uuid.uuid4().hex[:8]}"
        ),
        name=payload.institution_name,
        slug=slug,
        status=TenantStatus.ACTIVE,
        whatsapp_number=(
            payload.whatsapp_number
        ),
        drive_folder_id=None,
    )

    admin = StaffUser(
        id=str(
            uuid.uuid4(),
        ),
        tenant_id=tenant.id,
        role=StaffRole.ADMIN,
        name=payload.admin.name,
        email=payload.admin.email,
        password_hash=hash_password(
            payload.admin.password,
        ),
        is_active=True,
    )

    staff_users: list[
        StaffUser
    ] = []

    for member in (
        payload.staff_members
    ):
        staff_user = StaffUser(
            id=str(
                uuid.uuid4(),
            ),
            tenant_id=tenant.id,
            role=StaffRole(
                member.role,
            ),
            name=member.name,
            email=member.email,
            password_hash=(
                hash_password(
                    member.password,
                )
            ),
            is_active=True,
        )

        staff_users.append(
            staff_user,
        )

    try:
        db.add(
            tenant,
        )

        db.flush()

        save_tenant_onboarding_fields(
            db,
            tenant,
            payload.onboarding_fields,
            lock=True,
        )

        db.add(
            admin,
        )

        db.add_all(
            staff_users,
        )

        db.commit()

        db.refresh(
            tenant,
        )

        db.refresh(
            admin,
        )

        for staff_user in (
            staff_users
        ):
            db.refresh(
                staff_user,
            )

        return (
            tenant,
            admin,
            staff_users,
        )

    except Exception:
        db.rollback()
        raise