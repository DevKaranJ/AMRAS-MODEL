from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    RESUMED = "resumed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    COMPLETED = "completed"


class JobContext:
    def __init__(self, job_id: str, project_id: Optional[str] = None):
        self.job_id = job_id
        self.project_id = project_id
        self.status: JobStatus = JobStatus.QUEUED
        self.result: Dict[str, Any] = {}
        self.error: Optional[str] = None


class BaseJob(ABC):
    def __init__(self, context: JobContext):
        self.context = context

    @abstractmethod
    async def execute(self, **kwargs: Any) -> Any:
        pass

    async def pause(self) -> None:
        self.context.status = JobStatus.PAUSED

    async def resume(self) -> None:
        self.context.status = JobStatus.RUNNING

    async def cancel(self) -> None:
        self.context.status = JobStatus.CANCELLED

    async def get_status(self) -> JobStatus:
        return self.context.status
