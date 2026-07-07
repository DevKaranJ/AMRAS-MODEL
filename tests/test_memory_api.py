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
    assert data["entity_id"] == "hero_test_1"
    assert data["id"] is not None
    assert data["version"] == 1
    assert data["data"]["name"] == "Hero"


@pytest.mark.asyncio
async def test_rebuild_memory_endpoint() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/memory/rebuild")
    assert response.status_code == 202


@pytest.mark.asyncio
async def test_get_memories_endpoint() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # First create a memory
        await ac.post(
            "/memory/update",
            json={
                "entity_id": "test_get_memories_1",
                "entity_type": "character",
                "memory_type": "semantic",
                "data": {"name": "TestChar"},
            },
        )
        # Then retrieve memories
        response = await ac.get("/memory")
    assert response.status_code == 200
    memories = response.json()
    assert isinstance(memories, list)


@pytest.mark.asyncio
async def test_get_memories_with_filter() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create character memory
        await ac.post(
            "/memory/update",
            json={
                "entity_id": "test_filter_char_1",
                "entity_type": "character",
                "memory_type": "semantic",
                "data": {"name": "FilterChar"},
            },
        )
        # Create event memory
        await ac.post(
            "/memory/update",
            json={
                "entity_id": "test_filter_event_1",
                "entity_type": "event",
                "memory_type": "event",
                "data": {"name": "FilterEvent"},
            },
        )
        # Filter by character type
        response = await ac.get("/memory?entity_type=character")
        assert response.status_code == 200
        memories = response.json()
        assert all(m["entity_type"] == "character" for m in memories)


@pytest.mark.asyncio
async def test_search_memory_endpoint() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create a memory
        await ac.post(
            "/memory/update",
            json={
                "entity_id": "test_search_1",
                "entity_type": "character",
                "memory_type": "semantic",
                "data": {"name": "SearchChar"},
            },
        )
        # Search
        response = await ac.post(
            "/memory/search",
            json={
                "query": "test",
                "entity_type": "character",
                "limit": 10,
            },
        )
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)


@pytest.mark.asyncio
async def test_get_memory_history() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        entity_id = "test_history_1"
        # Create initial memory
        await ac.post(
            "/memory/update",
            json={
                "entity_id": entity_id,
                "entity_type": "character",
                "memory_type": "semantic",
                "data": {"name": "V1"},
            },
        )
        # Update memory
        await ac.post(
            "/memory/update",
            json={
                "entity_id": entity_id,
                "entity_type": "character",
                "memory_type": "semantic",
                "data": {"name": "V2", "status": "updated"},
            },
        )
        # Get history
        response = await ac.get(f"/memory/history/{entity_id}")
        assert response.status_code == 200
        history = response.json()
        assert isinstance(history, list)
        assert len(history) >= 1


@pytest.mark.asyncio
async def test_get_conflicts_endpoint() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/memory/conflicts")
    assert response.status_code == 200
    conflicts = response.json()
    assert isinstance(conflicts, list)


@pytest.mark.asyncio
async def test_get_conflicts_with_filter() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/memory/conflicts?resolved=false")
        assert response.status_code == 200
        conflicts = response.json()
        assert isinstance(conflicts, list)


@pytest.mark.asyncio
async def test_not_found_endpoints() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/memory/character/nonexistent_char_xyz")
        assert response.status_code == 404

        response = await ac.get("/memory/event/nonexistent_event_xyz")
        assert response.status_code == 404

        response = await ac.get("/memory/location/nonexistent_loc_xyz")
        assert response.status_code == 404
