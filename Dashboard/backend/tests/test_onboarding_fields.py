from pydantic import ValidationError
import pytest

from app.schemas.auth import OnboardingFieldInput
from app.services.onboarding_fields import (
    FieldConfigLockedError,
    save_tenant_onboarding_fields,
)


def test_reserved_onboarding_key_rejected():
    with pytest.raises(ValidationError):
        OnboardingFieldInput(field_key="name", label="Full name")


def test_select_field_requires_two_options():
    with pytest.raises(ValidationError):
        OnboardingFieldInput(
            field_key="stream",
            label="Stream",
            field_type="select",
            options=["Physical"],
        )


def test_select_field_accepts_options():
    item = OnboardingFieldInput(
        field_key="stream",
        label="Stream",
        field_type="select",
        options=["Physical", "Biological"],
    )
    assert item.options == ["Physical", "Biological"]


def test_text_field_drops_options():
    item = OnboardingFieldInput(
        field_key="school",
        label="School",
        field_type="text",
        options=["ignored"],
    )
    assert item.options is None


class _LockedTenant:
    field_config_locked = True
    id = "tenant-x"


class _FakeQuery:
    def filter(self, *_args, **_kwargs):
        return self

    def delete(self, *_args, **_kwargs):
        raise AssertionError("must not delete fields when locked")


class _FakeDb:
    def query(self, *_args, **_kwargs):
        return _FakeQuery()

    def add(self, *_args, **_kwargs):
        raise AssertionError("must not insert fields when locked")


def test_save_fields_rejects_when_locked():
    with pytest.raises(FieldConfigLockedError):
        save_tenant_onboarding_fields(
            _FakeDb(),
            _LockedTenant(),
            [],
            lock=True,
        )
