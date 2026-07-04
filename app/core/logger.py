import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Any, cast

import structlog
from structlog.stdlib import BoundLogger

from app.config.settings import settings


def setup_logging() -> None:
    """Initialize structured logging using structlog."""

    log_level = getattr(logging, settings.log.level.upper(), logging.INFO)

    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]

    if settings.log.file:
        file_handler = RotatingFileHandler(
            filename=settings.log.file,
            maxBytes=int(settings.log.rotation.replace(" MB", "")) * 1024 * 1024
            if "MB" in settings.log.rotation
            else 10485760,  # simple parsing
            backupCount=5,
        )
        handlers.append(file_handler)

    logging.basicConfig(
        format="%(message)s",
        level=log_level,
        handlers=handlers,
    )

    processors: list[Any] = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.log.format.lower() == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = "amras") -> BoundLogger:
    logger = structlog.get_logger(name)
    return cast(BoundLogger, logger)
