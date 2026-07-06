import pytest

from modules.vision.agents.vision_agent import CharacterDetectionAgent, LayoutAgent, SceneAnalysisAgent, VisionAgent


@pytest.mark.asyncio
async def test_vision_agent() -> None:
    agent = VisionAgent()
    assert agent.name == "VisionAgent"
    assert await agent.health_check()
    res = await agent.execute({"page_id": 1})
    assert isinstance(res, dict)
    assert res["page"] == 1
    assert "panels" in res
    assert await agent.validate({"page_id": 1})
    assert await agent.rollback("1")
    assert agent.description != ""
    assert agent.version != ""


@pytest.mark.asyncio
async def test_layout_agent() -> None:
    agent = LayoutAgent()
    assert agent.name == "LayoutAgent"
    assert await agent.health_check()
    res = await agent.execute({"page_id": 1})
    assert isinstance(res, dict)
    assert len(res["panels"]) > 0
    assert await agent.validate({"page_id": 1})
    assert await agent.rollback("1")
    assert agent.description != ""
    assert agent.version != ""


@pytest.mark.asyncio
async def test_character_detection_agent() -> None:
    agent = CharacterDetectionAgent()
    assert agent.name == "CharacterDetectionAgent"
    assert await agent.health_check()
    res = await agent.execute({"page_id": 1})
    assert isinstance(res, dict)
    assert len(res["characters"]) > 0
    assert await agent.validate({"page_id": 1})
    assert await agent.rollback("1")
    assert agent.description != ""
    assert agent.version != ""


@pytest.mark.asyncio
async def test_scene_analysis_agent() -> None:
    agent = SceneAnalysisAgent()
    assert agent.name == "SceneAnalysisAgent"
    assert await agent.health_check()
    res = await agent.execute({"page_id": 1})
    assert isinstance(res, dict)
    assert "scene_type" in res
    assert await agent.validate({"page_id": 1})
    assert await agent.rollback("1")
    assert agent.description != ""
    assert agent.version != ""
