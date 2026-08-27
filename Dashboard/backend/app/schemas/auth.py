from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)


StaffRoleValue = Literal[
    "admin",
    "tutor",
    "marker",
    "viewer",
]

OnboardingFieldType = Literal[
    "text",
    "number",
    "select",
    "boolean",
    "date",
]

RESERVED_ONBOARDING_FIELD_KEYS = frozenset(
    {"name", "phone", "class", "course", "consent"}
)


class OnboardingFieldInput(BaseModel):
    field_key: str = Field(min_length=1, max_length=64)
    label: str = Field(min_length=1, max_length=100)
    field_type: OnboardingFieldType = "text"
    options: list[str] | None = None
    required: bool = False
    sort_order: int = Field(default=0, ge=0, le=100)

    @field_validator("field_key")
    @classmethod
    def clean_field_key(cls, value: str) -> str:
        key = value.strip().lower().replace(" ", "_")
        if not key or not key[0].isalpha():
            raise ValueError("Field key must start with a letter.")
        if any(ch not in "abcdefghijklmnopqrstuvwxyz0123456789_" for ch in key):
            raise ValueError(
                "Field key may only contain lowercase letters, numbers, and underscores."
            )
        if key in RESERVED_ONBOARDING_FIELD_KEYS:
            raise ValueError(
                f"'{key}' is a core field and cannot be used as a custom onboarding field."
            )
        return key

    @field_validator("label")
    @classmethod
    def clean_label(cls, value: str) -> str:
        return value.strip()

    @field_validator("options")
    @classmethod
    def clean_options(
        cls,
        value: list[str] | None,
    ) -> list[str] | None:
        if value is None:
            return None
        cleaned = [item.strip() for item in value if str(item).strip()]
        return cleaned or None

    @model_validator(mode="after")
    def select_requires_options(self) -> "OnboardingFieldInput":
        if self.field_type == "select":
            if not self.options or len(self.options) < 2:
                raise ValueError("Select fields need at least two options.")
        else:
            self.options = None
        return self


class OnboardingFieldResponse(BaseModel):
    field_key: str
    label: str
    field_type: str
    options: list[str] | None = None
    required: bool
    sort_order: int
    active: bool = True


class OnboardingFieldsPutRequest(BaseModel):
    fields: list[OnboardingFieldInput] = Field(
        default_factory=list,
        max_length=15,
    )

    @field_validator("fields")
    @classmethod
    def unique_field_keys(
        cls,
        value: list[OnboardingFieldInput],
    ) -> list[OnboardingFieldInput]:
        keys = [item.field_key for item in value]
        if len(keys) != len(set(keys)):
            raise ValueError("Onboarding field keys must be unique.")
        return value


class OnboardingFieldsResponse(BaseModel):
    locked: bool
    fields: list[OnboardingFieldResponse]


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

    admin: AdminRegistration

    staff_members: list[
        StaffRegistration
    ] = Field(
        default_factory=list,
        max_length=5,
    )

    onboarding_fields: list[
        OnboardingFieldInput
    ] = Field(
        default_factory=list,
        max_length=15,
    )

    @field_validator("institution_name")
    @classmethod
    def clean_institution_name(
        cls,
        value: str,
    ) -> str:
        return value.strip()

    @field_validator("onboarding_fields")
    @classmethod
    def unique_field_keys(
        cls,
        value: list[OnboardingFieldInput],
    ) -> list[OnboardingFieldInput]:
        keys = [item.field_key for item in value]
        if len(keys) != len(set(keys)):
            raise ValueError(
                "Onboarding field keys must be unique."
            )
        return value


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
    telegram_linked: bool = False


class TelegramLinkCodeResponse(BaseModel):
    code: str
    expires_at: datetime
    ttl_minutes: int
    telegram_bot_username: str | None = None


class TelegramLinkStatusResponse(BaseModel):
    linked: bool
    channel: str | None = None
    channel_address: str | None = None
    linked_at: datetime | None = None
    telegram_bot_username: str | None = None