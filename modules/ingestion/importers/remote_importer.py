from abc import ABC, abstractmethod
from typing import Any, Dict, List


class RemoteProvider(ABC):
    """Abstract base class for Remote Manga Providers."""

    @abstractmethod
    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Search for manga."""
        pass

    @abstractmethod
    async def list_chapters(self, manga_id: str) -> List[Dict[str, Any]]:
        """List chapters for a specific manga."""
        pass

    @abstractmethod
    async def download_chapter(self, manga_id: str, chapter_id: str, dest_dir: str) -> bool:
        """Downloads a specific chapter to the destination directory."""
        pass
