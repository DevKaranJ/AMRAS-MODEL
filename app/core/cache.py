import json
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional

from app.config.settings import settings


class CacheBackend(ABC):
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        pass

    @abstractmethod
    async def clear(self) -> None:
        pass


class MemoryCache(CacheBackend):
    def __init__(self) -> None:
        self._cache: dict[str, dict[str, Any]] = {}

    async def get(self, key: str) -> Optional[Any]:
        item = self._cache.get(key)
        if not item:
            return None

        if item["expires_at"] and item["expires_at"] < time.time():
            await self.delete(key)
            return None

        return item["value"]

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        expires_at = time.time() + ttl if ttl else None
        self._cache[key] = {"value": value, "expires_at": expires_at}

    async def delete(self, key: str) -> None:
        self._cache.pop(key, None)

    async def clear(self) -> None:
        self._cache.clear()


class DiskCache(CacheBackend):
    def __init__(self, cache_dir: Path) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, key: str) -> Path:
        # Simple sanitization for file names
        safe_key = "".join(c for c in key if c.isalnum() or c in ("-", "_")).rstrip()
        return self.cache_dir / f"{safe_key}.json"

    async def get(self, key: str) -> Optional[Any]:
        path = self._get_path(key)
        if not path.exists():
            return None

        try:
            with open(path, "r") as f:
                data = json.load(f)

            if data.get("expires_at") and data["expires_at"] < time.time():
                await self.delete(key)
                return None

            return data.get("value")
        except (json.JSONDecodeError, OSError):
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        path = self._get_path(key)
        expires_at = time.time() + ttl if ttl else None

        data = {"value": value, "expires_at": expires_at}
        with open(path, "w") as f:
            json.dump(data, f)

    async def delete(self, key: str) -> None:
        path = self._get_path(key)
        if path.exists():
            path.unlink()

    async def clear(self) -> None:
        for item in self.cache_dir.iterdir():
            if item.is_file():
                item.unlink()


# Default cache instances
memory_cache = MemoryCache()
disk_cache = DiskCache(settings.storage.cache_dir)
