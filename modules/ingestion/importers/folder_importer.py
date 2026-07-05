from pathlib import Path
from typing import Any, Dict

from app.core.logger import get_logger
from modules.ingestion.importers.base import BaseImporter

logger = get_logger("amras.ingestion.folder_importer")

class FolderImporter(BaseImporter):

    async def import_manga(self, source: Path, manga_id: int) -> Dict[str, Any]:
        """Imports a manga from a local folder."""
        logger.info("importing_from_folder", source=str(source), manga_id=manga_id)

        # Scan directories
        chapters = []
        for item in source.iterdir():
            if item.is_dir():
                chapters.append(item.name)

        return {"imported_chapters": len(chapters), "manga_id": manga_id}

    async def validate_source(self, source: Path) -> bool:
        """Validates if source is a folder."""
        return source.is_dir()
