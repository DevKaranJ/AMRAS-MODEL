import pytest

from modules.story.agents import (
    CharacterAnalysisAgent,
    EventExtractionAgent,
    QAAgent,
    RelationshipAgent,
    StoryAnalysisAgent,
    TimelineAgent,
    WorldAnalysisAgent,
)


@pytest.mark.asyncio
async def test_story_analysis_agent() -> None:
    agent = StoryAnalysisAgent()
    result = await agent.process({"dummy": "vision_data"})
    assert "events" in result
    assert "scenes" in result


@pytest.mark.asyncio
async def test_character_analysis_agent() -> None:
    agent = CharacterAnalysisAgent()
    result = await agent.process({"dummy": "vision_data"})
    assert "characters" in result


@pytest.mark.asyncio
async def test_event_extraction_agent() -> None:
    agent = EventExtractionAgent()
    result = await agent.process({"dummy": "vision_data"})
    assert "extracted_events" in result


@pytest.mark.asyncio
async def test_relationship_agent() -> None:
    agent = RelationshipAgent()
    result = await agent.process({"dummy": "vision_data"})
    assert "relationships" in result


@pytest.mark.asyncio
async def test_timeline_agent() -> None:
    agent = TimelineAgent()
    result = await agent.process({"dummy": "vision_data"})
    assert "timeline_entries" in result


@pytest.mark.asyncio
async def test_world_analysis_agent() -> None:
    agent = WorldAnalysisAgent()
    result = await agent.process({"dummy": "vision_data"})
    assert "locations" in result
    assert "organizations" in result


@pytest.mark.asyncio
async def test_qa_agent() -> None:
    agent = QAAgent()
    result = await agent.process({"dummy": "vision_data"})
    assert result.get("qa_passed") is True
