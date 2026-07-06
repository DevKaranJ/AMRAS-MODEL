from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.endpoints.story import get_db_session
from app.api.main import app


@pytest.fixture
def mock_db_session() -> None:
    pass


@pytest.mark.asyncio
async def test_process_story_endpoint() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/story/process?chapter_id=1", json={"dummy_vision": "data"})
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "processing_started"
        assert "data" in data
        assert data["data"]["chapter"] == 1


@pytest.mark.asyncio
async def test_get_story_overview() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/story/")
        assert response.status_code == 200
        assert response.json()["status"] == "active"


@pytest.mark.asyncio
@patch("app.api.endpoints.story.get_db_session")
async def test_get_characters(mock_get_db, mock_db_session: None) -> None:
    mock_db = AsyncMock()
    from unittest.mock import MagicMock

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result
    mock_get_db.return_value = mock_db

    app.dependency_overrides[get_db_session] = lambda: mock_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/story/characters")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.asyncio
@patch("app.api.endpoints.story.get_db_session")
async def test_get_events(mock_get_db, mock_db_session: None) -> None:
    mock_db = AsyncMock()
    from unittest.mock import MagicMock

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result
    app.dependency_overrides[get_db_session] = lambda: mock_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/story/events")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.asyncio
@patch("app.api.endpoints.story.get_db_session")
async def test_get_relationships(mock_get_db, mock_db_session: None) -> None:
    mock_db = AsyncMock()
    from unittest.mock import MagicMock

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result
    app.dependency_overrides[get_db_session] = lambda: mock_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/story/relationships")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.asyncio
@patch("app.api.endpoints.story.get_db_session")
async def test_get_locations(mock_get_db, mock_db_session: None) -> None:
    mock_db = AsyncMock()
    from unittest.mock import MagicMock

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result
    app.dependency_overrides[get_db_session] = lambda: mock_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/story/locations")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.asyncio
@patch("app.api.endpoints.story.get_db_session")
async def test_get_world_knowledge(mock_get_db, mock_db_session: None) -> None:
    mock_db = AsyncMock()
    from unittest.mock import MagicMock

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result
    app.dependency_overrides[get_db_session] = lambda: mock_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/story/world")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.asyncio
@patch("app.api.endpoints.story.get_db_session")
async def test_get_timeline(mock_get_db, mock_db_session: None) -> None:
    mock_db = AsyncMock()
    from unittest.mock import MagicMock

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result
    app.dependency_overrides[get_db_session] = lambda: mock_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/story/timeline")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
