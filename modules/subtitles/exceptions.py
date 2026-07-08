from typing import Any, Dict

from app.core.exceptions import AmrasException


class SubtitleEngineError(AmrasException):
    """Base exception for Subtitle Engine errors."""

    def __init__(self, message: str, details: Dict[str, Any] | None = None):
        super().__init__(
            message=message,
            error_code="SUBTITLE_ENGINE_ERROR",
            debug_details=details,
            retryable=False,
        )


class SubtitleGenerationError(SubtitleEngineError):
    """Raised when subtitle generation fails."""

    def __init__(self, message: str, details: Dict[str, Any] | None = None):
        super().__init__(message, details)
        self.error_code = "SUBTITLE_GENERATION_ERROR"
        self.retryable = True


class TranslationError(SubtitleEngineError):
    """Raised when translation fails."""

    def __init__(self, message: str, details: Dict[str, Any] | None = None):
        super().__init__(message, details)
        self.error_code = "TRANSLATION_ERROR"
        self.retryable = True


class SynchronizationError(SubtitleEngineError):
    """Raised when subtitle synchronization fails."""

    def __init__(self, message: str, details: Dict[str, Any] | None = None):
        super().__init__(message, details)
        self.error_code = "SYNCHRONIZATION_ERROR"
        self.retryable = False


class FormattingError(SubtitleEngineError):
    """Raised when formatting rules are violated and cannot be auto-corrected."""

    def __init__(self, message: str, details: Dict[str, Any] | None = None):
        super().__init__(message, details)
        self.error_code = "FORMATTING_ERROR"
        self.retryable = False
