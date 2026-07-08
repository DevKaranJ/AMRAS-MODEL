# type: ignore
import pytest

from modules.subtitles.agents import (
    FormattingAgent,
    LocalizationAgent,
    QAAgent,
    SubtitleGenerationAgent,
    SynchronizationAgent,
    TranslationAgent,
)
from modules.subtitles.exceptions import (
    SubtitleGenerationError,
    SynchronizationError,
)


@pytest.mark.asyncio
async def test_subtitle_generation_agent_valid() -> None:
    agent = SubtitleGenerationAgent()
    payload = {
        "narration_script": "This is a test script.",
        "settings": {"max_lines": 2, "max_characters_per_line": 42},
    }
    assert await agent.validate(payload)
    result = await agent.execute(payload)
    assert "segments" in result


@pytest.mark.asyncio
async def test_subtitle_generation_agent_invalid() -> None:
    agent = SubtitleGenerationAgent()
    payload = {}
    assert not await agent.validate(payload)
    with pytest.raises(SubtitleGenerationError):
        await agent.execute(payload)


@pytest.mark.asyncio
async def test_synchronization_agent_valid() -> None:
    agent = SynchronizationAgent()
    payload = {"segments": [{"text": "Hello"}], "audio_timestamps": [{"text": "Hello", "start": 0, "end": 1000}]}
    assert await agent.validate(payload)
    result = await agent.execute(payload)
    assert "synchronized_segments" in result


@pytest.mark.asyncio
async def test_synchronization_agent_invalid() -> None:
    agent = SynchronizationAgent()
    with pytest.raises(SynchronizationError):
        await agent.execute({})


@pytest.mark.asyncio
async def test_translation_agent_valid() -> None:
    agent = TranslationAgent()
    payload = {"segments": [{"text": "Hello"}], "source_language": "English", "target_language": "Spanish"}
    assert await agent.validate(payload)
    result = await agent.execute(payload)
    assert "translated_segments" in result


@pytest.mark.asyncio
async def test_localization_agent_valid() -> None:
    agent = LocalizationAgent()
    payload = {"segments": [{"text": "Hello, John-san"}], "profile": {"honorifics_strategy": "remove"}}
    assert await agent.validate(payload)
    result = await agent.execute(payload)
    assert "localized_segments" in result


@pytest.mark.asyncio
async def test_formatting_agent_valid() -> None:
    agent = FormattingAgent()
    payload = {
        "segments": [{"text": "This is a very long line that should be broken."}],
        "settings": {"max_lines": 2, "max_characters_per_line": 20},
    }
    assert await agent.validate(payload)
    result = await agent.execute(payload)
    assert "formatted_segments" in result


@pytest.mark.asyncio
async def test_qa_agent_overlap() -> None:
    agent = QAAgent()
    payload = {
        "segments": [
            {"text": "A", "start_time_ms": 0, "end_time_ms": 1000},
            {"text": "B", "start_time_ms": 500, "end_time_ms": 1500},
        ]
    }
    assert await agent.validate(payload)
    result = await agent.execute(payload)
    assert not result["passed"]
    assert len(result["issues"]) == 1
