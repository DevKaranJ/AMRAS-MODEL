import pytest
from httpx import ASGITransport, AsyncClient

from app.api.main import app


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
class TestTimelineAPI:
    async def test_generate_timeline(self, client: AsyncClient) -> None:
        response = await client.post(
            "/timeline/generate",
            json={"project_id": 1, "settings": {"quality": "high"}}
        )
        assert response.status_code == 202
        data = response.json()
        assert data["project_id"] == 1
        assert data["status"] == "generated"

    async def test_rebuild_timeline(self, client: AsyncClient) -> None:
        response = await client.post(
            "/timeline/rebuild",
            json={"timeline_id": 100}
        )
        assert response.status_code == 202
        assert response.json()["timeline_id"] == 100

    async def test_get_timeline(self, client: AsyncClient) -> None:
        response = await client.get("/timeline?project_id=1")
        assert response.status_code == 200
        assert response.json()["project_id"] == 1

    async def test_get_timeline_scenes(self, client: AsyncClient) -> None:
        response = await client.get("/timeline/scene?timeline_id=1")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_get_timeline_cameras(self, client: AsyncClient) -> None:
        response = await client.get("/timeline/camera?scene_id=1")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_get_timeline_transitions(self, client: AsyncClient) -> None:
        response = await client.get("/timeline/transitions?timeline_id=1")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_get_timeline_status(self, client: AsyncClient) -> None:
        response = await client.get("/timeline/status?project_id=1")
        assert response.status_code == 200
        assert response.json()["status"] == "completed"

    async def test_generate_timeline_validation_error(self, client: AsyncClient) -> None:
        # Missing required field `project_id`
        response = await client.post(
            "/timeline/generate",
            json={"settings": {"quality": "high"}}
        )
        assert response.status_code == 422
