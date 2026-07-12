import pytest
from httpx import ASGITransport, AsyncClient

from app.api.main import app


@pytest.mark.asyncio
async def test_publish_package() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/publish/package?project_id=1")
    assert response.status_code == 202
    data = response.json()
    assert "status" in data
    assert data["status"] == "queued"


@pytest.mark.asyncio
async def test_seo_generate() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/seo/generate", json={"project_id": 1, "language": "en", "title_count": 5})
    assert response.status_code == 202
    data = response.json()
    assert "language" in data
    assert data["language"] == "en"


@pytest.mark.asyncio
async def test_thumbnail_generate() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/thumbnail/generate", json={"project_id": 1, "number_of_variants": 5, "style": "default"}
        )
    assert response.status_code == 202
    data = response.json()
    assert isinstance(data, (list, dict))
    assert len(data) > 0 if isinstance(data, (list, dict)) else True
