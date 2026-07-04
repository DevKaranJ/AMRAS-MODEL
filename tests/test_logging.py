import pytest

from app.config.settings import settings
from app.core.logger import get_logger, setup_logging


def test_logger_creation() -> None:
    # Testing that setup_logging configures structlog without crashing
    setup_logging()
    logger = get_logger("test_module")
    assert logger is not None


def test_log_error_formatting(monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture) -> None:
    # Force json output
    monkeypatch.setattr(settings.log, "format", "json")
    setup_logging()

    logger = get_logger("test_error")
    try:
        raise ValueError("Simulated error")
    except ValueError as e:
        logger.error("Error occurred", exc_info=e)

    # structlog output in tests can be captured via caplog if it propagates to standard logging
    assert "Error occurred" in caplog.text
    assert "Simulated error" in caplog.text
