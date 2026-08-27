"""Tolerate schema lag when optional columns are not yet migrated."""

from __future__ import annotations

from loguru import logger

_MISSING_COLUMNS: set[str] = set()


def is_undefined_column_error(exc: BaseException, column: str) -> bool:
    text = str(exc)
    return column in text and ("42703" in text or "does not exist" in text)


def column_available(table: str, column: str) -> bool:
    return f"{table}.{column}" not in _MISSING_COLUMNS


def mark_column_missing(table: str, column: str) -> None:
    key = f"{table}.{column}"
    if key in _MISSING_COLUMNS:
        return
    _MISSING_COLUMNS.add(key)
    logger.warning(
        "{} is missing in the database; apply the matching SQL migration",
        key,
    )


def reset_missing_columns() -> None:
    _MISSING_COLUMNS.clear()
