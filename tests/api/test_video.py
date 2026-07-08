from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.main import app


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_start_render(client: AsyncClient) -> None:
    response = await client.post(
        "/render/start",
        json={"project_id": 1, "timeline_id": 1, "profile_id": 1, "config": {}}
    )
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "queued"
    assert data["project_id"] == 1

@pytest.mark.asyncio
async def test_resume_render(client: AsyncClient) -> None:
    response = await client.post("/render/resume", json={"job_id": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"
    assert data["id"] == 1

@pytest.mark.asyncio
async def test_cancel_render(client: AsyncClient) -> None:
    response = await client.post("/render/cancel", json={"job_id": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "cancelled"

@pytest.mark.asyncio
async def test_get_render_status(client: AsyncClient) -> None:
    response = await client.get("/render/status/1")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "progress" in data

@pytest.mark.asyncio
async def test_get_render_report(client: AsyncClient) -> None:
    response = await client.get("/render/report/1")
    assert response.status_code == 200
    data = response.json()
    assert "total_time_ms" in data

@pytest.mark.asyncio
async def test_get_render_output(client: AsyncClient) -> None:
    response = await client.get("/render/output/1")
    assert response.status_code == 200
    data = response.json()
    assert "master_video" in data

@pytest.mark.asyncio
async def test_list_render_jobs(client: AsyncClient) -> None:
    response = await client.get("/render/jobs?project_id=1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
