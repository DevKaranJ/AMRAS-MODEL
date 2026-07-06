import pytest

from modules.ocr.agents.ocr_agent import OCRAgent, SoundEffectAgent


@pytest.mark.asyncio
async def test_ocr_agent() -> None:
    agent = OCRAgent()
    assert agent.name == "OCRAgent"
    assert await agent.health_check()
    res = await agent.execute({"page_id": 1})
    assert isinstance(res, dict)
    assert len(res["dialogue"]) > 0
    assert await agent.validate({"page_id": 1})
    assert await agent.rollback("1")
    assert agent.description != ""
    assert agent.version != ""


@pytest.mark.asyncio
async def test_sound_effect_agent() -> None:
    agent = SoundEffectAgent()
    assert agent.name == "SoundEffectAgent"
    assert await agent.health_check()
    res = await agent.execute({"page_id": 1})
    assert isinstance(res, dict)
    assert len(res["sound_effects"]) > 0
    assert await agent.validate({"page_id": 1})
    assert await agent.rollback("1")
    assert agent.description != ""
    assert agent.version != ""
