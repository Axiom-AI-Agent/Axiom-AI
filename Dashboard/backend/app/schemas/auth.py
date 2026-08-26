from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
)


StaffRoleValue = Literal[
    "admin",
    "tutor",
    "marker",
    "viewer",
]


class AdminRegistration(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=72,
    )

    @field_validator("name")
    @classmethod
    def clean_name(
        cls,
        value: str,
    ) -> str:
        return value.strip()

    @field_validator("email")
    @classmethod
    def normalize_email(
        cls,
        value: EmailStr,
    ) -> str:
        return str(value).strip().lower()


class StaffRegistration(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=72,
    )

    role: StaffRoleValue = "viewer"

    @field_validator("name")
    @classmethod
    def clean_name(
        cls,
        value: str,
    ) -> str:
        return value.strip()

    @field_validator("email")
    @classmethod
    def normalize_email(
        cls,
        value: EmailStr,
    ) -> str:
        return str(value).strip().lower()


class OrganizationRegisterRequest(BaseModel):
    institution_name: str = Field(
        min_length=2,
        max_length=200,
    )

    whatsapp_number: str | None = None

    drive_folder_id: str | None = None

    admin: AdminRegistration

    staff_members: list[
        StaffRegistration
    ] = Field(
        default_factory=list,
        max_length=5,
    )

    @field_validator("institution_name")
    @classmethod
    def clean_institution_name(
        cls,
        value: str,
    ) -> str:
        return value.strip()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(
        cls,
        value: EmailStr,
    ) -> str:
        return str(value).strip().lower()


class AuthUserResponse(BaseModel):
    id: str
    tenant_id: str
    institution_name: str
    name: str
    email: str
    role: StaffRoleValue


class CreatedStaffResponse(BaseModel):
    id: str
    name: str
    email: str
    role: StaffRoleValue


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthUserResponse
    created_staff: list[
        CreatedStaffResponse
    ] = Field(
        default_factory=list,
    )


class MeResponse(BaseModel):
    id: str
    tenant_id: str
    institution_name: str
    name: str
    email: str
    role: StaffRoleValue
    created_at: datetime


class StaffCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    role: StaffRoleValue


class StaffUpdate(BaseModel):
    name: str | None = None
    role: StaffRoleValue | None = None
    is_active: bool | None = None


class StaffResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    email: str
    role: StaffRoleValue
    is_active: bool