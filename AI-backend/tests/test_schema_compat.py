"""Schema compatibility helpers for optional DB columns."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from infrastructure.db.schema_compat import (
    is_undefined_column_error,
    reset_missing_columns,
)
from services.identity.resolver import IdentityResolver


def setup_function() -> None:
    reset_missing_columns()


def test_detects_postgres_undefined_column():
    exc = Exception(
        "{'message': 'column subject_classes.payments_enabled does not exist', "
        "'code': '42703'}"
    )
    assert is_undefined_column_error(exc, "payments_enabled")
    assert not is_undefined_column_error(exc, "timezone")


def test_lookup_class_meta_retries_without_payments_column():
    resolver = IdentityResolver()
    missing = Exception(
        "{'message': 'column subject_classes.payments_enabled does not exist', "
        "'code': '42703'}"
    )
    ok = MagicMock()
    ok.data = [{"id": "class-1", "name": "A/L Physics"}]
    query = MagicMock()
    query.eq.return_value = query
    query.in_.return_value = query
    query.execute.side_effect = [missing, ok]
    table = MagicMock()
    table.select.return_value = query
    client = MagicMock()
    client.table.return_value = table

    with patch(
        "services.identity.resolver.get_supabase_client",
        return_value=client,
    ):
        meta = resolver._lookup_class_meta("tenant-demo-physics", ["class-1"])

    assert meta["class-1"]["name"] == "A/L Physics"
    assert meta["class-1"]["payments_enabled"] is True
    assert table.select.call_args_list[0].args[0] == "id, name, payments_enabled"
    assert table.select.call_args_list[1].args[0] == "id, name"
