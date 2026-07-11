import pytest
from httpx import ASGITransport, AsyncClient

from app.api.main import app


@pytest.mark.asyncio
async def test_update_memory_endpoint() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/memory/update",
            json={
                "entity_id": "hero_test_1",
                "entity_type": "character",
                "memory_type": "semantic",
                "data": {"name": "Hero"},
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert isinstance(data, dict)


@pytest.mark.asyncio
async def test_rebuild_memory_endpoint() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/memory/rebuild")
        assert response.status_code == 202
        data = response.json()
        assert isinstance(data, dict)


@pytest.mark.asyncio
async def test_get_memories_endpoint() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/memory")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))


@pytest.mark.asyncio
async def test_get_memories_with_filter() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/memory?entity_type=character")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))


@pytest.mark.asyncio
async def test_search_memory_endpoint() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/memory/search",
            json={
                "query": "test",
                "entity_type": "character",
                "limit": 10,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))


@pytest.mark.asyncio
async def test_get_memory_history() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/memory/history/test_history_1")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))


@pytest.mark.asyncio
async def test_get_conflicts_endpoint() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/memory/conflicts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))


@pytest.mark.asyncio
async def test_get_conflicts_with_filter() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/memory/conflicts?resolved=false")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))


@pytest.mark.asyncio
async def test_not_found_endpoints() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/memory/character/nonexistent_char_xyz")
        # This should return 404 for non-existent character
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
