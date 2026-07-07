import json
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from modules.narration.agents import (
    ConsistencyAgent,
    ContextAgent,
    EngagementAgent,
    FactVerificationAgent,
    HumanizationAgent,
    QAAgent,
    ScriptPlannerAgent,
    StoryNarratorAgent,
    StyleEnforcementAgent,
)
from modules.narration.exceptions import (
    ConsistencyError,
    ContextRetrievalError,
    FactCheckError,
    QAError,
    ScriptPlanningError,
    StoryNarrationError,
    StyleGenerationError,
)


@pytest.fixture
def mock_ai_provider() -> Any:
    with patch("app.shared.providers.base.ai_provider_manager.generate_text", new_callable=AsyncMock) as mock_gen:
        yield mock_gen


@pytest.mark.asyncio
async def test_script_planner_agent(mock_ai_provider: AsyncMock) -> None:
    mock_ai_provider.return_value = json.dumps(
        {"status": "planned", "scenes": [{"id": 1, "description": "Intro", "pacing": "Normal"}]}
    )
    agent = ScriptPlannerAgent()

    with pytest.raises(ScriptPlanningError):
        await agent.execute({})

    result = await agent.execute({"manga_id": 1, "script_mode": "Short"})
    assert result["status"] == "planned"
    assert result["scenes"][0]["description"] == "Intro"


@pytest.mark.asyncio
async def test_story_narrator_agent(mock_ai_provider: AsyncMock) -> None:
    mock_ai_provider.return_value = "This is a narrated story."
    agent = StoryNarratorAgent()

    with pytest.raises(StoryNarrationError):
        await agent.execute({})

    result = await agent.execute({"scene": {}, "context": {}})
    assert result["status"] == "narrated"
    assert result["text"] == "This is a narrated story."


@pytest.mark.asyncio
async def test_humanization_agent(mock_ai_provider: AsyncMock) -> None:
    mock_ai_provider.return_value = "Human text."
    agent = HumanizationAgent()

    with pytest.raises(StyleGenerationError):
        await agent.execute({})

    result = await agent.execute({"text": "test text"})
    assert result["status"] == "humanized"
    assert result["text"] == "Human text."


@pytest.mark.asyncio
async def test_context_agent() -> None:
    agent = ContextAgent()

    with pytest.raises(ContextRetrievalError):
        await agent.execute({})

    result = await agent.execute({"manga_id": 1})
    assert result["status"] == "retrieved"
    assert "manga_id" in result["context"]


@pytest.mark.asyncio
async def test_consistency_agent(mock_ai_provider: AsyncMock) -> None:
    agent = ConsistencyAgent()

    with pytest.raises(ConsistencyError):
        await agent.execute({})

    result = await agent.execute({"text": "test", "context": {}})
    assert result["status"] == "verified"


@pytest.mark.asyncio
async def test_engagement_agent(mock_ai_provider: AsyncMock) -> None:
    mock_ai_provider.return_value = "Engaged text."
    agent = EngagementAgent()

    with pytest.raises(StyleGenerationError):
        await agent.execute({})

    result = await agent.execute({"text": "test"})
    assert result["status"] == "enhanced"
    assert result["text"] == "Engaged text."


@pytest.mark.asyncio
async def test_fact_verification_agent(mock_ai_provider: AsyncMock) -> None:
    agent = FactVerificationAgent()

    with pytest.raises(FactCheckError):
        await agent.execute({})

    result = await agent.execute({"text": "test"})
    assert result["status"] == "checked"
    assert result["is_valid"] is True


@pytest.mark.asyncio
async def test_style_enforcement_agent(mock_ai_provider: AsyncMock) -> None:
    mock_ai_provider.return_value = "Styled text."
    agent = StyleEnforcementAgent()

    with pytest.raises(StyleGenerationError):
        await agent.execute({})

    result = await agent.execute({"text": "test", "style_profile": {}})
    assert result["status"] == "enforced"
    assert result["text"] == "Styled text."


@pytest.mark.asyncio
async def test_qa_agent(mock_ai_provider: AsyncMock) -> None:
    agent = QAAgent()

    with pytest.raises(QAError):
        await agent.execute({})

    result = await agent.execute({"script_id": 1})
    assert result["status"] == "approved"
