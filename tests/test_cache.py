from pathlib import Path

import pytest

from app.core.cache import DiskCache, MemoryCache


@pytest.mark.asyncio
async def test_memory_cache_read_write() -> None:
    cache = MemoryCache()
    await cache.set("key1", "value1")
    val = await cache.get("key1")
    assert val == "value1"


@pytest.mark.asyncio
async def test_memory_cache_expiration(monkeypatch: pytest.MonkeyPatch) -> None:
    cache = MemoryCache()
    import time

    current_time = time.time()

    def mock_time() -> float:
        return current_time

    monkeypatch.setattr("time.time", mock_time)

    await cache.set("key2", "value2", ttl=1)
    val = await cache.get("key2")
    assert val == "value2"

    # Simulate time passing
    current_time += 1.1

    val_expired = await cache.get("key2")
    assert val_expired is None


@pytest.mark.asyncio
async def test_disk_cache_read_write(tmp_path: Path) -> None:
    cache = DiskCache(cache_dir=tmp_path)
    await cache.set("key3", {"complex": "data"})
    val = await cache.get("key3")
    assert val == {"complex": "data"}

    await cache.delete("key3")
    assert await cache.get("key3") is None


@pytest.mark.asyncio
async def test_disk_cache_expiration(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cache = DiskCache(cache_dir=tmp_path)
    import time

    current_time = time.time()

    def mock_time() -> float:
        return current_time

    monkeypatch.setattr("time.time", mock_time)

    await cache.set("key4", "value4", ttl=1)

    # Simulate time passing
    current_time += 1.1

    val_expired = await cache.get("key4")
    assert val_expired is None
