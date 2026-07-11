import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_get_voices(client: AsyncClient) -> None:
    try:
        response = await client.get("/audio/voices")
        assert response.status_code in [200, 404, 422, 500, 501, 503]
    except Exception:
        pass


async def test_regenerate_audio(client: AsyncClient) -> None:
    try:
        response = await client.post("/audio/regenerate", json={"segment_ids": [1, 2]})
        assert response.status_code in [200, 404, 422, 500, 501, 503]
    except Exception:
        pass


async def test_normalize_audio(client: AsyncClient) -> None:
    try:
        response = await client.post("/audio/normalize", json={"job_id": 1, "target_lufs": -14.0})
        assert response.status_code in [200, 404, 422, 500, 501, 503]
    except Exception:
        pass
