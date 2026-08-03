import shutil
from pathlib import Path
from typing import Any, Dict

from app.core.logger import get_logger
from modules.ingestion.agents.file_system_agent import FileSystemAgent
from modules.ingestion.importers.base import BaseImporter
from modules.ingestion.importers.folder_importer import FolderImporter

logger = get_logger("amras.ingestion.archive_importer")


class ArchiveImporter(BaseImporter):
    def __init__(self, file_system_agent: FileSystemAgent):
        self.file_system_agent = file_system_agent
        self.folder_importer = FolderImporter()

    async def import_manga(self, source: Path, manga_id: int) -> Dict[str, Any]:
        """Imports a manga from a ZIP/CBZ archive, keeping extracted files."""
        logger.info("importing_from_archive", source=str(source), manga_id=manga_id)

        if source.suffix.lower() not in [".zip", ".cbz"]:
            raise ValueError(f"Unsupported archive format: {source.suffix}")

        # Extract to permanent storage location
        from app.config.settings import settings
        extract_dir = settings.storage.manga_dir / str(manga_id) / "extracted"
        extract_dir.mkdir(parents=True, exist_ok=True)

        try:
            if source.suffix.lower() == ".zip":
                await self.file_system_agent.extract_zip(source, extract_dir)
            elif source.suffix.lower() == ".cbz":
                await self.file_system_agent.extract_cbz(source, extract_dir)

            return await self.folder_importer.import_manga(extract_dir, manga_id)
        except Exception as e:
            logger.error("archive_import_failed", error=str(e))
            raise

    async def validate_source(self, source: Path) -> bool:
        """Validates if source is a valid archive."""
        return source.is_file() and source.suffix.lower() in [".zip", ".cbz"]
