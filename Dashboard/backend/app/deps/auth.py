from fastapi import (
    Depends,
    HTTPException,
    status,
)

from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from sqlalchemy.orm import Session

from app.database.session import (
    get_db,
)

from app.models import StaffUser

from app.services.auth_service import (
    decode_access_token,
)


bearer_scheme = HTTPBearer(
    auto_error=False,
)


def get_current_staff(
    credentials:
        HTTPAuthorizationCredentials
        | None
    = Depends(
        bearer_scheme,
    ),
    db: Session = Depends(
        get_db,
    ),
) -> StaffUser:

    if credentials is None:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Authentication required"
            ),
            headers={
                "WWW-Authenticate":
                    "Bearer",
            },
        )

    try:
        payload = (
            decode_access_token(
                credentials.credentials,
            )
        )

    except ValueError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Invalid or expired token"
            ),
            headers={
                "WWW-Authenticate":
                    "Bearer",
            },
        ) from error

    staff_id = payload.get(
        "sub",
    )

    if not staff_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    staff = (
        db.query(StaffUser)
        .filter(
            StaffUser.id == staff_id,
            StaffUser.is_active.is_(
                True,
            ),
        )
        .first()
    )

    if staff is None:
        raise HTTPException(
            status_code=401,
            detail=(
                "Staff account not found"
            ),
        )

    return staff