import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_get_dashboard(client: AsyncClient) -> None:
    response = await client.get("/production/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert data["projects_count"] >= 0
    assert data["running_jobs"] >= 0
    assert data["completed_jobs"] >= 0
    assert data["failed_jobs"] >= 0


async def test_get_system_health(client: AsyncClient) -> None:
    response = await client.get("/production/system/health")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


async def test_get_system_resources(client: AsyncClient) -> None:
    response = await client.get("/production/system/resources")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["cpu_usage"], (int, float))
    assert isinstance(data["ram_usage"], (int, float))


async def test_list_projects(client: AsyncClient) -> None:
    response = await client.get("/production/projects")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_create_project_not_implemented(client: AsyncClient) -> None:
    response = await client.post("/production/projects", json={"name": "test", "status": "created"})
    assert response.status_code == 501


async def test_run_pipeline(client: AsyncClient) -> None:
    response = await client.post("/production/pipeline/run", json={"config": {}})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "started"


async def test_resume_pipeline(client: AsyncClient) -> None:
    response = await client.post("/production/pipeline/resume", params={"job_id": 123})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "resumed"


async def test_create_backup_not_implemented(client: AsyncClient) -> None:
    response = await client.post("/production/system/backup")
    assert response.status_code == 501


async def test_restore_backup(client: AsyncClient) -> None:
    response = await client.post("/production/system/restore", params={"backup_id": 1})
    assert response.status_code == 200


async def test_list_models(client: AsyncClient) -> None:
    response = await client.get("/production/models")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_install_model_not_implemented(client: AsyncClient) -> None:
    response = await client.post(
        "/production/models/install", json={"name": "test", "provider": "test", "status": "installing"}
    )
    assert response.status_code == 501


async def test_get_storage_stats(client: AsyncClient) -> None:
    response = await client.get("/production/storage")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_cleanup_storage(client: AsyncClient) -> None:
    response = await client.post("/production/storage/cleanup")
    assert response.status_code == 200


async def test_get_logs(client: AsyncClient) -> None:
    response = await client.get("/production/logs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
