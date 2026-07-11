import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_get_voices(client: AsyncClient) -> None:
    response = await client.get("/audio/voices")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list) or isinstance(data, dict)


async def test_regenerate_audio(client: AsyncClient) -> None:
    response = await client.post("/audio/regenerate", json={"segment_ids": [1, 2]})
    assert response.status_code == 200
    data = response.json()
    assert "status" in data or isinstance(data, dict)


async def test_normalize_audio(client: AsyncClient) -> None:
    response = await client.post("/audio/normalize", json={"job_id": 1, "target_lufs": -14.0})
    assert response.status_code == 200
    data = response.json()
    assert "status" in data or isinstance(data, dict)
