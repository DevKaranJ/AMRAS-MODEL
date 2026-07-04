from typing import Any

import pytest

from app.jobs.base import BaseJob, JobContext, JobStatus


class DummyJob(BaseJob):
    async def execute(self, **kwargs: Any) -> Any:
        if kwargs.get("fail"):
            self.context.status = JobStatus.FAILED
            self.context.error = "Simulated failure"
            raise ValueError("Simulated failure")

        self.context.status = JobStatus.COMPLETED
        self.context.result = {"success": True}
        return self.context.result


@pytest.mark.asyncio
async def test_job_execution() -> None:
    context = JobContext(job_id="test_job_1")
    assert context.status == JobStatus.QUEUED

    job = DummyJob(context)

    # Simulate execution running
    context.status = JobStatus.RUNNING
    assert await job.get_status() == JobStatus.RUNNING

    # Execute successfully
    result = await job.execute()
    assert result == {"success": True}
    assert await job.get_status() == JobStatus.COMPLETED
    assert context.result == {"success": True}


@pytest.mark.asyncio
async def test_job_failure() -> None:
    context = JobContext(job_id="test_job_2")
    job = DummyJob(context)

    with pytest.raises(ValueError):
        await job.execute(fail=True)

    assert await job.get_status() == JobStatus.FAILED
    assert context.error == "Simulated failure"


@pytest.mark.asyncio
async def test_job_pause_resume_cancel() -> None:
    context = JobContext(job_id="test_job_3")
    job = DummyJob(context)

    await job.pause()
    assert await job.get_status() == JobStatus.PAUSED

    await job.resume()
    assert await job.get_status() == JobStatus.RESUMED

    await job.cancel()
    assert await job.get_status() == JobStatus.CANCELLED
