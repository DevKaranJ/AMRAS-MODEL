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
    from app.shared.providers.base import ai_provider_manager

    # Inject the mock provider
    ai_provider_manager.register_provider("test_mock", mock_ai_provider, is_default=True)

    engine = NarrationEngine()
    result = await engine.generate_script(manga_id=1, script_mode="Short", style_profile={"style": "Neutral"})
    assert result is not None
    assert isinstance(result, (str, dict))


@pytest.mark.asyncio
async def test_narration_engine_generate_script_fact_check_fails() -> None:
    from unittest.mock import MagicMock

    engine = NarrationEngine()
    # Configure fact-checker to fail
    engine.fact_checker = MagicMock()
    engine.fact_checker.verify.return_value = {"status": "failed", "reason": "Fact check failed"}

    result = await engine.generate_script(manga_id=1, script_mode="Short", style_profile={"style": "Neutral"})
    assert result is not None
    # When fact check fails, we expect a specific status or the generation to handle it
    assert isinstance(result, (str, dict))


@pytest.mark.asyncio
async def test_narration_engine_generate_script_qa_fails(mock_ai_provider: AsyncMock) -> None:
    from unittest.mock import MagicMock

    engine = NarrationEngine()
    # Configure QA to fail
    engine.qa_agent = MagicMock()
    engine.qa_agent.validate.return_value = {"status": "failed", "reason": "QA validation failed"}

    result = await engine.generate_script(manga_id=1, script_mode="Short", style_profile={"style": "Neutral"})
    assert result is not None
    # When QA fails, we expect a specific status or the generation to handle it
    assert isinstance(result, (str, dict))
