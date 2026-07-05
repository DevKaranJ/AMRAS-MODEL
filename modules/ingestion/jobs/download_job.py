from typing import Any

from app.core.logger import get_logger
from app.jobs.base import BaseJob, JobStatus
from modules.ingestion.importers.remote_importer import RemoteProvider

logger = get_logger("amras.ingestion.download_job")

class ProcessDownloadJob(BaseJob):
    """Job to handle remote downloading of manga."""

    def __init__(self, context: Any, remote_provider: RemoteProvider) -> None:
        super().__init__(context)
        self.remote_provider = remote_provider

    async def execute(self, **kwargs: Any) -> Any:
        manga_id = kwargs.get("manga_id")
        chapter_id = kwargs.get("chapter_id")
        dest_dir = kwargs.get("dest_dir")

        if not manga_id or not chapter_id or not dest_dir:
            raise ValueError("manga_id, chapter_id, and dest_dir are required")

        self.context.status = JobStatus.RUNNING
        logger.info("start_download", manga_id=manga_id, chapter_id=chapter_id)

        try:
            result = await self.remote_provider.download_chapter(manga_id, chapter_id, dest_dir)
            self.context.status = JobStatus.COMPLETED
            self.context.result = {"success": result}
            return self.context.result
        except Exception as e:
            self.context.status = JobStatus.FAILED
            self.context.error = str(e)
            logger.error("failed_download", manga_id=manga_id, chapter_id=chapter_id, error=str(e))
            raise e
