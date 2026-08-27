"""JWT staff identity for dashboard-agent endpoints only.

Does not change existing DashboardTenant (tenant_id header) behaviour.
tenant_id is taken from the staff_users row, never from query/body.
"""

from __future__ import annotations

import os
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from infrastructure.db.supabase_client import get_supabase_client
from services.identity.staff_resolver import StaffContext

bearer_scheme = HTTPBearer(auto_error=False)


def _jwt_secret() -> str:
    secret = (os.getenv("JWT_SECRET_KEY") or "").strip()
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Staff authentication is not configured",
        )
    return secret


def _jwt_algorithm() -> str:
    return (os.getenv("JWT_ALGORITHM") or "HS256").strip() or "HS256"


def decode_staff_token(token: str) -> dict:
    try:
        return jwt.decode(token, _jwt_secret(), algorithms=[_jwt_algorithm()])
    except JWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error


def require_staff_context(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> StaffContext:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_staff_token(credentials.credentials)
    staff_id = str(payload.get("sub") or "").strip()
    if not staff_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    client = get_supabase_client()
    response = (
        client.table("staff_users")
        .select("id, tenant_id, name, role, email, is_active")
        .eq("id", staff_id)
        .limit(1)
        .execute()
    )
    rows = response.data or []
    if not rows or rows[0].get("is_active") is False:
        raise HTTPException(status_code=401, detail="Staff account not found")

    row = rows[0]
    return StaffContext(
        staff_id=str(row["id"]),
        tenant_id=str(row["tenant_id"]),
        name=str(row.get("name") or "Staff"),
        role=str(row.get("role") or "viewer"),
        email=row.get("email"),
    )


StaffPrincipal = Annotated[StaffContext, Depends(require_staff_context)]
