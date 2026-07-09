# type: ignore
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.endpoints.subtitles import get_db_session
from app.api.main import app


@pytest.fixture
def test_client() -> None:
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
@patch("app.api.endpoints.subtitles.SubtitleEngine")
async def test_generate_subtitles(mock_engine, test_client) -> None:
    mock_instance = mock_engine.return_value

    # We must populate created_at and updated_at so Pydantic validation passes when serializing Response
    now = datetime.now(timezone.utc)

    # Instead of instantiating the SQLAlchemy model directly (which errors on un-persisted timestamp columns),
    # we return a plain MagicMock tailored to match the required Pydantic schema keys.
    mock_job = MagicMock()
    mock_job.id = 1
    mock_job.project_id = 1
    mock_job.timeline_id = 1
    mock_job.language_id = 1
    mock_job.status = "pending"
    mock_job.progress = 0.0
    mock_job.settings = {}
    mock_job.created_at = now
    mock_job.updated_at = now
    mock_job.error_message = None

    async def mock_create_job(*args, **kwargs):
        return mock_job

    mock_instance.create_subtitle_job = mock_create_job

    # We also need to mock the database session because the endpoint checks for language existence
    mock_db = MagicMock()
    mock_result = MagicMock()

    mock_lang = MagicMock()
    mock_lang.id = 1
    mock_lang.code = "en"
    mock_lang.name = "EN"
    mock_result.scalar_one_or_none.return_value = mock_lang

    async def mock_execute(*args, **kwargs):
        return mock_result

    mock_db.execute = mock_execute

    async def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db_session] = override_get_db

    response = await test_client.post(
        "/subtitles/generate", json={"project_id": 1, "timeline_id": 1, "language_code": "en", "settings": {}}
    )

    assert response.status_code == 202
    assert response.json()["id"] == 1

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_subtitle_job_status(test_client) -> None:
    pass


@pytest.mark.asyncio
async def test_list_subtitles(test_client) -> None:
    pass


@pytest.mark.asyncio
async def test_list_caption_styles(test_client) -> None:
    pass
