from modules.narration.exceptions import (
    ConsistencyError,
    ContextRetrievalError,
    FactCheckError,
    NarrationException,
    QAError,
    ScriptPlanningError,
    StoryNarrationError,
    StyleGenerationError,
)


def test_narration_exception() -> None:
    exc = NarrationException("base narration error")
    assert exc.error_code == "NARRATION_ERROR"
    assert exc.message == "base narration error"


def test_script_planning_error() -> None:
    exc = ScriptPlanningError("planning failed")
    assert exc.error_code == "SCRIPT_PLANNING_ERROR"
    assert exc.message == "planning failed"


def test_story_narration_error() -> None:
    exc = StoryNarrationError("narration failed")
    assert exc.error_code == "STORY_NARRATION_ERROR"
    assert exc.message == "narration failed"


def test_fact_check_error() -> None:
    exc = FactCheckError("fact failed")
    assert exc.error_code == "FACT_CHECK_ERROR"
    assert exc.message == "fact failed"


def test_context_retrieval_error() -> None:
    exc = ContextRetrievalError("context failed")
    assert exc.error_code == "CONTEXT_RETRIEVAL_ERROR"
    assert exc.message == "context failed"


def test_style_generation_error() -> None:
    exc = StyleGenerationError("style failed")
    assert exc.error_code == "STYLE_GENERATION_ERROR"
    assert exc.message == "style failed"


def test_consistency_error() -> None:
    exc = ConsistencyError("consistency failed")
    assert exc.error_code == "CONSISTENCY_ERROR"
    assert exc.message == "consistency failed"


def test_qa_error() -> None:
    exc = QAError("qa failed")
    assert exc.error_code == "QA_ERROR"
    assert exc.message == "qa failed"
