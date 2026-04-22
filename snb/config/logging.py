"""Structured logging built on loguru.

Two output modes:
- human-readable (default, dev)
- JSON lines (when LOG_JSON=true, suited for prod/aggregators)
"""

from __future__ import annotations

import sys
from typing import Any

from loguru import logger


_CONFIGURED = False


def configure_logging(level: str = "INFO", json_mode: bool = False) -> None:
    global _CONFIGURED
    logger.remove()
    if json_mode:
        logger.add(
            sys.stdout,
            level=level.upper(),
            serialize=True,
            backtrace=False,
            diagnose=False,
        )
    else:
        logger.add(
            sys.stdout,
            level=level.upper(),
            colorize=True,
            backtrace=True,
            diagnose=False,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> "
                "<level>{level: <8}</level> "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> "
                "| <level>{message}</level>"
            ),
        )
    _CONFIGURED = True


def get_logger(name: str | None = None, **context: Any):  # noqa: ANN401
    if not _CONFIGURED:
        configure_logging()
    bound = logger.bind(**context) if context else logger
    if name:
        bound = bound.bind(component=name)
    return bound
