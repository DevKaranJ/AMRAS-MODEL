from pathlib import Path
from typing import Any

from app.jobs.base import BaseJob, JobStatus
from modules.ingestion.agents.collection_agent import CollectionAgent


class ProcessImportJob(BaseJob):
    """Job to process local import of manga."""

    def __init__(self, context: Any, collection_agent: CollectionAgent) -> None:
        super().__init__(context)
        self.collection_agent = collection_agent

    async def execute(self, **kwargs: Any) -> Any:
        source_path = Path(kwargs.get("source_path", ""))
        import_job_id = kwargs.get("import_job_id")

        if not source_path or not import_job_id:
            raise ValueError("source_path and import_job_id are required")

        self.context.status = JobStatus.RUNNING

        try:
            result = await self.collection_agent.process_import(source_path, import_job_id)
            self.context.status = JobStatus.COMPLETED
            self.context.result = result
            return result
        except Exception as e:
            self.context.status = JobStatus.FAILED
            self.context.error = str(e)
            raise e
