from typing import Any, Dict, Optional

from app.core.exceptions import AmrasException


class StoryEngineError(AmrasException):
    def __init__(self, message: str, debug_details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, error_code="STORY_ENGINE_ERROR", debug_details=debug_details, retryable=False)


class CharacterDetectionError(StoryEngineError):
    def __init__(self, message: str, debug_details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, debug_details=debug_details)
        self.error_code = "CHARACTER_DETECTION_ERROR"


class EventDetectionError(StoryEngineError):
    def __init__(self, message: str, debug_details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, debug_details=debug_details)
        self.error_code = "EVENT_DETECTION_ERROR"


class TimelineConsistencyError(StoryEngineError):
    def __init__(self, message: str, debug_details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, debug_details=debug_details)
        self.error_code = "TIMELINE_CONSISTENCY_ERROR"


class RelationshipAnalysisError(StoryEngineError):
    def __init__(self, message: str, debug_details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, debug_details=debug_details)
        self.error_code = "RELATIONSHIP_ANALYSIS_ERROR"


class WorldAnalysisError(StoryEngineError):
    def __init__(self, message: str, debug_details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, debug_details=debug_details)
        self.error_code = "WORLD_ANALYSIS_ERROR"
