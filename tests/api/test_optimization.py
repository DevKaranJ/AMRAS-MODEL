import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_run_optimization(client: AsyncClient) -> None:
    response = await client.post("/optimization/run", json={"project_id": 1})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert "job_id" in data


@pytest.mark.asyncio
async def test_run_profile(client: AsyncClient) -> None:
    response = await client.post("/optimization/profile", json={"target": "system"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"


@pytest.mark.asyncio
async def test_run_benchmark(client: AsyncClient) -> None:
    payload = {"component": "OCR", "operation": "inference", "execution_time": 1.5, "memory_usage": 512.0}
    response = await client.post("/optimization/benchmark", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["component"] == "OCR"


@pytest.mark.asyncio
async def test_run_archive(client: AsyncClient) -> None:
    payload = {"project_id": 1, "archive_path": "/archives/proj_1.zip", "size_mb": 150.5}
    response = await client.post("/optimization/archive", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["status"] == "completed"


@pytest.mark.asyncio
async def test_get_performance(client: AsyncClient) -> None:
    response = await client.get("/optimization/performance")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_benchmarks(client: AsyncClient) -> None:
    response = await client.get("/optimization/benchmarks")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_costs(client: AsyncClient) -> None:
    response = await client.get("/optimization/costs")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_dependencies(client: AsyncClient) -> None:
    response = await client.get("/optimization/dependencies?project_id=1")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_deployments(client: AsyncClient) -> None:
    response = await client.get("/optimization/deployments")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_package_deployment(client: AsyncClient) -> None:
    payload = {"target_env": "docker", "version": "1.0.0", "configuration": {"port": 8000}}
    response = await client.post("/deployment/package", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["status"] == "success"
    assert data["target_env"] == "docker"
