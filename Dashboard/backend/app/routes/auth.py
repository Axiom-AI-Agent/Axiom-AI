import os

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.deps.auth import get_current_staff
from app.models import StaffUser

from app.schemas.auth import (
    AuthResponse,
    AuthUserResponse,
    CreatedStaffResponse,
    LoginRequest,
    MeResponse,
    OrganizationRegisterRequest,
)

from app.services.auth_service import (
    authenticate_staff,
    create_access_token,
    hash_password,
    register_organization,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: OrganizationRegisterRequest,
    db: Session = Depends(get_db),
):
    try:
        (
            tenant,
            admin,
            additional_staff,
        ) = register_organization(
            db,
            payload,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        ) from error

    token = create_access_token(
        admin,
    )

    return AuthResponse(
        access_token=token,
        user=AuthUserResponse(
            id=admin.id,
            tenant_id=tenant.id,
            institution_name=tenant.name,
            name=admin.name,
            email=admin.email,
            role=admin.role.value,
        ),
        created_staff=[
            CreatedStaffResponse(
                id=user.id,
                name=user.name,
                email=user.email,
                role=user.role.value,
            )
            for user in [
                admin,
                *additional_staff,
            ]
        ],
    )


@router.post(
    "/login",
    response_model=AuthResponse,
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    staff = authenticate_staff(
        db,
        payload.email,
        payload.password,
    )

    if staff is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    token = create_access_token(
        staff,
    )

    return AuthResponse(
        access_token=token,
        user=AuthUserResponse(
            id=staff.id,
            tenant_id=staff.tenant_id,
            institution_name=staff.tenant.name,
            name=staff.name,
            email=staff.email,
            role=staff.role.value,
        ),
    )


@router.get(
    "/me",
    response_model=MeResponse,
)
def me(
    current_staff: StaffUser = Depends(
        get_current_staff,
    ),
):
    return MeResponse(
        id=current_staff.id,
        tenant_id=current_staff.tenant_id,
        institution_name=current_staff.tenant.name,
        name=current_staff.name,
        email=current_staff.email,
        role=current_staff.role.value,
        created_at=current_staff.created_at,
    )


@router.post("/bootstrap-demo-physics")
def bootstrap_demo_physics(
    bootstrap_key: str,
    db: Session = Depends(get_db),
):
    expected_key = os.getenv(
        "DEMO_BOOTSTRAP_KEY",
    )

    if (
        not expected_key
        or bootstrap_key != expected_key
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid bootstrap key",
        )

    try:
        # Ensure the existing demo staff table
        # contains the auth columns.
        db.execute(
            text(
                """
                ALTER TABLE staff_users
                ADD COLUMN IF NOT EXISTS email TEXT
                """
            )
        )

        db.execute(
            text(
                """
                ALTER TABLE staff_users
                ADD COLUMN IF NOT EXISTS password_hash TEXT
                """
            )
        )

        db.execute(
            text(
                """
                ALTER TABLE staff_users
                ADD COLUMN IF NOT EXISTS is_active BOOLEAN
                NOT NULL DEFAULT TRUE
                """
            )
        )

        db.execute(
            text(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS
                idx_staff_users_email
                ON staff_users(email)
                """
            )
        )

        password_hash = hash_password(
            "DemoPhysics123!"
        )

        result = db.execute(
            text(
                """
                UPDATE staff_users
                SET
                    email = :email,
                    password_hash = :password_hash,
                    is_active = TRUE
                WHERE id = :staff_id
                  AND tenant_id = :tenant_id
                RETURNING
                    id,
                    tenant_id,
                    name,
                    email,
                    role,
                    is_active
                """
            ),
            {
                "email": "demo.physics@axiom.ai",
                "password_hash": password_hash,
                "staff_id": "staff-physics-001",
                "tenant_id": "tenant-demo-physics",
            },
        )

        staff = result.mappings().first()

        if staff is None:
            db.rollback()

            raise HTTPException(
                status_code=404,
                detail=(
                    "Demo Physics admin was not found. "
                    "The demo seed may not exist in this database."
                ),
            )

        db.commit()

        return {
            "ok": True,
            "tenant_id": staff["tenant_id"],
            "staff_id": staff["id"],
            "name": staff["name"],
            "email": staff["email"],
            "role": str(staff["role"]),
            "is_active": staff["is_active"],
        }

    except HTTPException:
        raise

    except Exception as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Bootstrap failed: {str(error)}",
        ) from error