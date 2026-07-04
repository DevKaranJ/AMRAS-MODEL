from typing import Any, Dict, Optional


class AmrasException(Exception):
    """Base exception for all AMRAS related errors."""

    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        retryable: bool = False,
        recovery_suggestion: Optional[str] = None,
        debug_details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.retryable = retryable
        self.recovery_suggestion = recovery_suggestion
        self.debug_details = debug_details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_code": self.error_code,
            "message": self.message,
            "retryable": self.retryable,
            "recovery_suggestion": self.recovery_suggestion,
        }


class ConfigurationError(AmrasException):
    def __init__(self, message: str, **kwargs: Any):
        super().__init__(message, error_code="CONFIG_ERROR", **kwargs)


class DatabaseError(AmrasException):
    def __init__(self, message: str, **kwargs: Any):
        super().__init__(message, error_code="DATABASE_ERROR", retryable=True, **kwargs)


class StorageError(AmrasException):
    def __init__(self, message: str, **kwargs: Any):
        super().__init__(message, error_code="STORAGE_ERROR", **kwargs)


class JobError(AmrasException):
    def __init__(self, message: str, **kwargs: Any):
        super().__init__(message, error_code="JOB_ERROR", **kwargs)


class AIProviderError(AmrasException):
    def __init__(self, message: str, **kwargs: Any):
        super().__init__(message, error_code="AI_PROVIDER_ERROR", retryable=True, **kwargs)


class PluginError(AmrasException):
    def __init__(self, message: str, **kwargs: Any):
        super().__init__(message, error_code="PLUGIN_ERROR", **kwargs)
