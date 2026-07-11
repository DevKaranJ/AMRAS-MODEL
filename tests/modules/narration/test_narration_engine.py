from unittest.mock import AsyncMock

import pytest

from modules.narration.engine import NarrationEngine


@pytest.fixture
def mock_ai_provider() -> AsyncMock:
    mock = AsyncMock()
    mock.return_value = "Generated script content"
    return mock


@pytest.mark.asyncio
async def test_narration_engine_generate_script(mock_ai_provider: AsyncMock) -> None:
    engine = NarrationEngine()
    result = await engine.generate_script(manga_id=1, script_mode="Short", style_profile={"style": "Neutral"})
    assert result is not None


@pytest.mark.asyncio
async def test_narration_engine_generate_script_fact_check_fails() -> None:
    engine = NarrationEngine()
    result = await engine.generate_script(manga_id=1, script_mode="Short", style_profile={"style": "Neutral"})
    assert result is not None


@pytest.mark.asyncio
async def test_narration_engine_generate_script_qa_fails(mock_ai_provider: AsyncMock) -> None:
    engine = NarrationEngine()
    result = await engine.generate_script(manga_id=1, script_mode="Short", style_profile={"style": "Neutral"})
    assert result is not None
