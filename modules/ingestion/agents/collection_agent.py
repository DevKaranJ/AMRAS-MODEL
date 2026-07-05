from pathlib import Path
from typing import Any, Dict

from app.core.logger import get_logger
from modules.ingestion.agents.base import BaseIngestionAgent
from modules.ingestion.agents.database_agent import DatabaseAgent
from modules.ingestion.agents.file_system_agent import FileSystemAgent
from modules.ingestion.agents.metadata_agent import MetadataAgent
from modules.ingestion.agents.validation_agent import ValidationAgent

logger = get_logger("amras.ingestion.collection_agent")

class CollectionAgent(BaseIngestionAgent):
    def __init__(
        self,
        metadata_agent: MetadataAgent,
        validation_agent: ValidationAgent,
        file_system_agent: FileSystemAgent,
        database_agent: DatabaseAgent
    ):
        self.metadata_agent = metadata_agent
        self.validation_agent = validation_agent
        self.file_system_agent = file_system_agent
        self.database_agent = database_agent

    async def process_import(self, source_path: Path, import_job_id: int) -> Dict[str, Any]:
        """Orchestrates the ingestion pipeline for a given path."""
        logger.info("start_process_import", source_path=str(source_path), job_id=import_job_id)

        try:
            # 1. Update Job Status to Running
            await self.database_agent.update_import_job(import_job_id, status="running")

            # 2. Extract Metadata
            metadata = await self.metadata_agent.extract_metadata(source_path)
            manga_title = metadata.title if hasattr(metadata, "title") else source_path.stem
            logger.info("extracted_metadata", title=manga_title)

            # 3. Create/Get Manga in DB
            manga_id = await self.database_agent.create_or_get_manga(metadata)

            # 4. Process files depending on source
            result = await self.file_system_agent.process_source(source_path, manga_title, manga_id)

            # 5. Validation
            await self.validation_agent.validate_manga(manga_id)

            # 6. Mark job complete
            await self.database_agent.update_import_job(import_job_id, status="completed", progress=100.0)

            logger.info("completed_process_import", source_path=str(source_path), job_id=import_job_id)
            return {"status": "success", "manga_id": manga_id, "result": result}

        except Exception as e:
            logger.exception("failed_process_import", source_path=str(source_path), job_id=import_job_id, error=str(e))
            await self.database_agent.update_import_job(import_job_id, status="failed", error=str(e))
            raise e

    def _is_agent(self) -> bool:
        return True
