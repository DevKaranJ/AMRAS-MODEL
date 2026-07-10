from typing import AsyncGenerator
import pytest
from app.database.session import get_db_session
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.main import app


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_db_session] = lambda: db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_run_qa(client: AsyncClient) -> None:
    response = await client.post("/qa/run", json={"project_id": 1, "incremental": False})
    assert response.status_code == 200
    data = response.json()
    assert data["project_id"] == 1
    assert data["status"] == "passed"
    assert "scores" in data
    assert data["scores"]["story_score"] == 92.5
    assert data["scores"]["narration_score"] == 98.0


@pytest.mark.asyncio
async def test_repair_issues(client: AsyncClient) -> None:
    response = await client.post("/qa/repair", json={"project_id": 1, "issue_ids": [10, 11]})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["issue_id"] == 10
    assert data[0]["success"] is True


@pytest.mark.asyncio
async def test_revalidate_project(client: AsyncClient) -> None:
    response = await client.post("/qa/revalidate?project_id=1")
    assert response.status_code == 200
    data = response.json()
    assert data["project_id"] == 1
    assert data["status"] == "passed"


@pytest.mark.asyncio
async def test_get_report_not_found(client: AsyncClient) -> None:
    response = await client.get("/qa/report?project_id=999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_report(client: AsyncClient) -> None:
    await client.post("/qa/run", json={"project_id": 1, "incremental": False})

    response = await client.get("/qa/report?project_id=1")
    assert response.status_code == 200
    data = response.json()
    assert data["project_id"] == 1
    assert data["status"] == "passed"


@pytest.mark.asyncio
async def test_get_issues(client: AsyncClient) -> None:
    response = await client.get("/qa/issues?project_id=1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_history(client: AsyncClient) -> None:
    await client.post("/qa/run", json={"project_id": 1, "incremental": False})
    await client.post("/qa/run", json={"project_id": 1, "incremental": False})

    response = await client.get("/qa/history?project_id=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


@pytest.mark.asyncio
async def test_get_metrics(client: AsyncClient) -> None:
    response = await client.get("/qa/metrics?project_id=1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_approval(client: AsyncClient) -> None:
    response = await client.get("/qa/approval?project_id=1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
