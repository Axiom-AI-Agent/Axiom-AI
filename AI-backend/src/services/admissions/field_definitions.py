"""Tenant onboarding field definitions — custom slots beyond core name/class/consent."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

COLUMN_BACKED_KEYS = frozenset({"school", "district"})
RESERVED_FIELD_KEYS = frozenset({"name", "phone", "class", "course", "consent"})


@dataclass(frozen=True)
class TenantFieldDef:
    field_key: str
    label: str
    field_type: str = "text"
    options: tuple[str, ...] | None = None
    required: bool = False
    sort_order: int = 0


DEFAULT_FIELD_DEFINITIONS: tuple[TenantFieldDef, ...] = (
    TenantFieldDef(
        field_key="school",
        label="School",
        field_type="text",
        required=True,
        sort_order=0,
    ),
    TenantFieldDef(
        field_key="district",
        label="District",
        field_type="text",
        required=True,
        sort_order=1,
    ),
)


def parse_field_definitions(rows: list[dict[str, Any]] | None) -> list[TenantFieldDef]:
    """Turn DB/CRM rows into field defs, skipping reserved core keys."""
    parsed: list[TenantFieldDef] = []
    for row in rows or []:
        if row.get("active") is False:
            continue
        key = str(row.get("field_key") or "").strip()
        if not key or key.lower() in RESERVED_FIELD_KEYS:
            continue
        raw_options = row.get("options")
        options: tuple[str, ...] | None = None
        if isinstance(raw_options, list):
            options = tuple(str(item) for item in raw_options if str(item).strip())
        parsed.append(
            TenantFieldDef(
                field_key=key,
                label=str(row.get("label") or key).strip() or key,
                field_type=str(row.get("field_type") or "text").strip() or "text",
                options=options or None,
                required=bool(row.get("required")),
                sort_order=int(row.get("sort_order") or 0),
            )
        )
    parsed.sort(key=lambda item: (item.sort_order, item.field_key))
    return parsed


def coerce_extra_fields(value: dict[str, Any] | str | None) -> dict[str, Any] | None:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        parsed = json.loads(stripped)
        if not isinstance(parsed, dict):
            raise ValueError("extra_fields must be a JSON object")
        return parsed
    return dict(value)


def merge_column_backed_fields(
    *,
    school: str | None,
    district: str | None,
    extra_fields: dict[str, Any] | None,
) -> tuple[str | None, str | None, dict[str, Any]]:
    """Dual-write school/district into extra_fields; copy extra keys into columns."""
    extra: dict[str, Any] = dict(extra_fields or {})
    school_val = school if school not in (None, "") else extra.get("school")
    district_val = district if district not in (None, "") else extra.get("district")
    if school_val:
        extra["school"] = school_val
    if district_val:
        extra["district"] = district_val
    return (
        str(school_val) if school_val else None,
        str(district_val) if district_val else None,
        extra,
    )
