import pytest
from httpx import ASGITransport, AsyncClient

from app.api.main import app


@pytest.mark.asyncio
async def test_update_memory_endpoint() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/memory/update",
            json={
                "entity_id": "hero_1",
                "entity_type": "character",
                "memory_type": "semantic",
                "data": {"name": "Hero"},
            },
        )
    assert response.status_code == 201
    assert response.json()["entity_id"] == "hero_1"


@pytest.mark.asyncio
async def test_rebuild_memory_endpoint() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/memory/rebuild")
    assert response.status_code == 202


@pytest.mark.asyncio
async def test_get_memories_endpoint() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/memory")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_conflicts_endpoint() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/memory/conflicts")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_not_found_endpoints() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/memory/character/unknown")
        assert response.status_code == 404

        response = await ac.get("/memory/event/unknown")
        assert response.status_code == 404

        response = await ac.get("/memory/location/unknown")
        assert response.status_code == 404
