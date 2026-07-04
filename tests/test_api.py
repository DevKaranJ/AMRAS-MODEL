from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.api.main import app
from app.config.settings import settings


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_endpoint(async_client: AsyncClient) -> None:
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_version_endpoint(async_client: AsyncClient) -> None:
    response = await async_client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"version": settings.version}


@pytest.mark.asyncio
async def test_settings_endpoint(async_client: AsyncClient) -> None:
    response = await async_client.get("/settings")
    assert response.status_code == 200
    data = response.json()
    assert "project_name" in data
    assert data["project_name"] == settings.project_name


@pytest.mark.asyncio
async def test_jobs_endpoints(async_client: AsyncClient) -> None:
    response = await async_client.post("/jobs")
    assert response.status_code == 200
    assert response.json()["status"] == "queued"

    job_id = response.json()["job_id"]
    response = await async_client.get(f"/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["job_id"] == job_id
