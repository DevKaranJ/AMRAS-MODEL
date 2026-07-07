import json
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from modules.narration.engine import NarrationEngine


@pytest.fixture
def mock_ai_provider() -> Any:
    with patch("app.shared.providers.base.ai_provider_manager.generate_text", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = json.dumps(
            {"status": "planned", "scenes": [{"id": 1, "description": "Intro", "pacing": "Normal"}]}
        )
        yield mock_gen


@pytest.mark.asyncio
async def test_narration_engine_initialization() -> None:
    engine = NarrationEngine()
    assert engine.planner is not None
    assert engine.narrator is not None
    assert engine.humanizer is not None
    assert engine.context_agent is not None
    assert engine.consistency is not None
    assert engine.engagement is not None
    assert engine.fact_checker is not None
    assert engine.style_enforcer is not None
    assert engine.qa_agent is not None


@pytest.mark.asyncio
async def test_narration_engine_generate_script(mock_ai_provider: AsyncMock) -> None:
    engine = NarrationEngine()
    result = await engine.generate_script(manga_id=1, script_mode="Short", style_profile={"style": "Neutral"})
    assert result["status"] == "success"
    assert "Generated script" in result["script"]


@pytest.mark.asyncio
async def test_narration_engine_generate_script_with_scenes() -> None:
    # We will mock the script planner agent to return scenes
    class MockPlanner:
        async def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
            return {"status": "planned", "scenes": [{"id": 1, "description": "Intro", "pacing": "Normal"}]}

    engine = NarrationEngine()
    engine.planner = MockPlanner()  # type: ignore

    result = await engine.generate_script(manga_id=1, script_mode="Short", style_profile={"style": "Neutral"})
    assert result["status"] == "success"


@pytest.mark.asyncio
async def test_narration_engine_generate_script_fact_check_fails() -> None:
    # We will mock the script planner agent to return scenes
    class MockPlanner:
        async def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
            return {"status": "planned", "scenes": [{"id": 1, "description": "Intro", "pacing": "Normal"}]}

    class MockFactChecker:
        async def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
            return {"status": "checked", "is_valid": False, "issues": ["Invalid fact"]}

    engine = NarrationEngine()
    engine.planner = MockPlanner()  # type: ignore
    engine.fact_checker = MockFactChecker()  # type: ignore

    result = await engine.generate_script(manga_id=1, script_mode="Short", style_profile={"style": "Neutral"})
    assert result["status"] == "success"


@pytest.mark.asyncio
async def test_narration_engine_generate_script_qa_fails(mock_ai_provider: AsyncMock) -> None:
    class MockQA:
        async def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
            return {"status": "rejected", "issues": ["QA Failed"]}

    engine = NarrationEngine()
    engine.qa_agent = MockQA()  # type: ignore

    result = await engine.generate_script(manga_id=1, script_mode="Short", style_profile={"style": "Neutral"})
    assert result["status"] == "success"
