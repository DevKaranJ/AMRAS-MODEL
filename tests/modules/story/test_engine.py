from unittest.mock import patch

import pytest

from modules.story.engine import StoryEngine
from modules.story.exceptions import StoryEngineError


@pytest.fixture
def story_engine() -> StoryEngine:
    return StoryEngine()


@pytest.mark.asyncio
async def test_process_chapter_success(story_engine: StoryEngine) -> None:
    vision_data = {"some_vision": "data"}

    result = await story_engine.process_chapter(1, vision_data)

    assert result["chapter"] == 1
    assert "events" in result
    assert "characters" in result
    assert "relationships" in result
    assert "timeline" in result
    assert "locations" in result
    assert "organizations" in result


@pytest.mark.asyncio
async def test_process_chapter_failure(story_engine: StoryEngine) -> None:
    with patch.object(story_engine.story_agent, "process", side_effect=Exception("Test Error")):
        with pytest.raises(StoryEngineError) as exc_info:
            await story_engine.process_chapter(1, {})
        assert "Test Error" in str(exc_info.value)
