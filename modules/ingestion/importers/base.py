from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict


class BaseImporter(ABC):
    """Base class for all Manga Importers."""

    @abstractmethod
    async def import_manga(self, source: Path, manga_id: int) -> Dict[str, Any]:
        """Imports a manga from the given source."""
        pass

    @abstractmethod
    async def validate_source(self, source: Path) -> bool:
        """Validates if this importer can handle the given source."""
        pass
