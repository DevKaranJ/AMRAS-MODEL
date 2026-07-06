from modules.story.exceptions import (
    CharacterDetectionError,
    EventDetectionError,
    RelationshipAnalysisError,
    StoryEngineError,
    TimelineConsistencyError,
    WorldAnalysisError,
)


def test_character_detection_error() -> None:
    err = CharacterDetectionError("test")
    assert err.error_code == "CHARACTER_DETECTION_ERROR"


def test_event_detection_error() -> None:
    err = EventDetectionError("test")
    assert err.error_code == "EVENT_DETECTION_ERROR"


def test_timeline_consistency_error() -> None:
    err = TimelineConsistencyError("test")
    assert err.error_code == "TIMELINE_CONSISTENCY_ERROR"


def test_relationship_analysis_error() -> None:
    err = RelationshipAnalysisError("test")
    assert err.error_code == "RELATIONSHIP_ANALYSIS_ERROR"


def test_world_analysis_error() -> None:
    err = WorldAnalysisError("test")
    assert err.error_code == "WORLD_ANALYSIS_ERROR"


def test_story_engine_error() -> None:
    err = StoryEngineError("test")
    assert err.error_code == "STORY_ENGINE_ERROR"
    assert err.retryable is False
