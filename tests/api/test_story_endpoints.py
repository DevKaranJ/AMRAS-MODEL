from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.endpoints.story import get_db_session
from app.api.main import app


@pytest.fixture
def mock_db_session():
    """Fixture that provides a mock database session and sets up dependency override."""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    # Override the dependency
    app.dependency_overrides[get_db_session] = lambda: mock_db

    yield mock_db

    # Cleanup: remove the override after test
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_process_story_endpoint() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/story/process?chapter_id=1", json={"dummy_vision": "data"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert "data" in data
        assert data["data"]["chapter"] == 1


@pytest.mark.asyncio
async def test_get_story_overview() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/story/")
        assert response.status_code == 200
        assert response.json()["status"] == "active"


@pytest.mark.asyncio
async def test_get_characters(mock_db_session) -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/story/characters")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_events(mock_db_session) -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/story/events")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_relationships(mock_db_session) -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/story/relationships")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_locations(mock_db_session) -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/story/locations")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_world_knowledge(mock_db_session) -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/story/world")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_timeline(mock_db_session) -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/story/timeline")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
