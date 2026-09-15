"""Lightweight structured observability helpers for ATHARVADRISHTI."""

from __future__ import annotations

import logging
import os
import time
from contextlib import contextmanager
from typing import Iterator


LOGGER_NAME = "atharvadrishti"


def get_logger() -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s %(name)s %(message)s"
            )
        )
        logger.addHandler(handler)
    logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
    logger.propagate = False
    return logger


logger = get_logger()


def log_event(event: str, **fields: object) -> None:
    """Emit one structured key=value log line without storing sensitive payloads."""
    safe_fields = []
    for key, value in fields.items():
        if value is None:
            continue
        safe_fields.append(f"{key}={value}")
    suffix = " " + " ".join(safe_fields) if safe_fields else ""
    logger.info("event=%s%s", event, suffix)


@contextmanager
def timed_event(event: str, **fields: object) -> Iterator[None]:
    """Log start/end timing for an operation."""
    started = time.perf_counter()
    log_event(f"{event}.start", **fields)
    try:
        yield
    except Exception as exc:
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        log_event(
            f"{event}.error",
            elapsed_ms=elapsed_ms,
            error_type=type(exc).__name__,
            **fields,
        )
        raise
    else:
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        log_event(f"{event}.complete", elapsed_ms=elapsed_ms, **fields)
