"""Centralised loguru setup (stderr-only for future MCP safety)."""

from __future__ import annotations

import logging
import sys
from typing import Optional

from loguru import logger

_FMT = (
    "<green>{time:HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan> — "
    "<level>{message}</level>"
)

_CONFIGURED = False


class _InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging(level: Optional[str] = None, *, log_file: Optional[str] = None) -> None:
    global _CONFIGURED
    if level is None:
        try:
            from infrastructure.config import LOG_LEVEL

            level = LOG_LEVEL
        except Exception:
            level = "INFO"

    logger.remove()
    logger.add(sys.stderr, format=_FMT, level=level.upper(), colorize=True, backtrace=True, diagnose=False)

    if log_file:
        logger.add(log_file, format=_FMT, level=level.upper(), rotation="10 MB", retention="7 days")

    logging.basicConfig(handlers=[_InterceptHandler()], level=0, force=True)
    _CONFIGURED = True
