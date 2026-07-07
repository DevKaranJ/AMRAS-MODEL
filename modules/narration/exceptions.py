from typing import Any

from app.core.exceptions import AmrasException


class NarrationException(AmrasException):
    """Base exception for all Narration related errors."""

    def __init__(self, message: str, **kwargs: Any):
        if "error_code" not in kwargs:
            kwargs["error_code"] = "NARRATION_ERROR"
        super().__init__(message, **kwargs)


class ScriptPlanningError(NarrationException):
    def __init__(self, message: str, **kwargs: Any):
        super().__init__(message, error_code="SCRIPT_PLANNING_ERROR", **kwargs)


class StoryNarrationError(NarrationException):
    def __init__(self, message: str, **kwargs: Any):
        super().__init__(message, error_code="STORY_NARRATION_ERROR", **kwargs)


class FactCheckError(NarrationException):
    def __init__(self, message: str, **kwargs: Any):
        super().__init__(message, error_code="FACT_CHECK_ERROR", **kwargs)


class ContextRetrievalError(NarrationException):
    def __init__(self, message: str, **kwargs: Any):
        super().__init__(message, error_code="CONTEXT_RETRIEVAL_ERROR", **kwargs)


class StyleGenerationError(NarrationException):
    def __init__(self, message: str, **kwargs: Any):
        super().__init__(message, error_code="STYLE_GENERATION_ERROR", **kwargs)


class ConsistencyError(NarrationException):
    def __init__(self, message: str, **kwargs: Any):
        super().__init__(message, error_code="CONSISTENCY_ERROR", **kwargs)


class QAError(NarrationException):
    def __init__(self, message: str, **kwargs: Any):
        super().__init__(message, error_code="QA_ERROR", **kwargs)
