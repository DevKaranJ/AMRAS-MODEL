from typing import Any, Dict, List

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.models.core import Job
from app.models.production import PipelineHistory

logger = get_logger("amras.production.workflow")

class PipelineStageConfig(BaseModel):
    stage_name: str
    dependencies: List[str] = []

class WorkflowManagerAgent:
    """
    Workflow Manager Agent
    Responsibilities: Execute pipeline stages, monitor dependencies, retry failed stages, resume interrupted workflows.
    """
    def __init__(self) -> None:
        self.running_workflows: Dict[int, Any] = {}

    async def execute_pipeline(self, job_id: int, stages: List[PipelineStageConfig], db: AsyncSession) -> Dict[str, Any]:
        """Executes the pipeline stages in dependency order and records history."""
        logger.info(f"Executing pipeline for job {job_id} with {len(stages)} stages.")

        for stage in stages:
            history = PipelineHistory(
                job_id=job_id,
                stage=stage.stage_name,
                status="queued"
            )
            db.add(history)

        await db.commit()

        return {"job_id": job_id, "status": "started", "stages_scheduled": len(stages)}

    async def pause_workflow(self, job_id: int, db: AsyncSession) -> Dict[str, Any]:
        """Pauses a running workflow."""
        logger.info(f"Pausing workflow for job {job_id}.")

        # Update Job status in database
        result = await db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        if not job:
            logger.warning(f"Job {job_id} not found, cannot pause.")
            return {"job_id": job_id, "status": "failed", "error": "Job not found"}

        job.status = "paused"
        await db.commit()

        # Update in-memory tracking
        if job_id in self.running_workflows:
            self.running_workflows[job_id]["status"] = "paused"

        # Update pipeline history status
        result = await db.execute(
            select(PipelineHistory)
            .where(PipelineHistory.job_id == job_id)
            .where(PipelineHistory.status == "running")
        )
        for history in result.scalars():
            history.status = "paused"
        await db.commit()

        return {"job_id": job_id, "status": "paused"}

    async def cancel_workflow(self, job_id: int, db: AsyncSession) -> Dict[str, Any]:
        """Cancels a running workflow."""
        logger.info(f"Canceling workflow for job {job_id}.")

        # Update Job status in database
        result = await db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        if not job:
            logger.warning(f"Job {job_id} not found, cannot cancel.")
            return {"job_id": job_id, "status": "failed", "error": "Job not found"}

        job.status = "canceled"
        await db.commit()

        # Update in-memory tracking
        if job_id in self.running_workflows:
            self.running_workflows[job_id]["status"] = "canceled"

        # Update pipeline history status
        result = await db.execute(
            select(PipelineHistory)
            .where(PipelineHistory.job_id == job_id)
            .where(PipelineHistory.status.in_(["running", "queued", "paused"]))
        )
        for history in result.scalars():
            history.status = "canceled"
        await db.commit()

        return {"job_id": job_id, "status": "canceled"}

    async def resume_workflow(self, job_id: int, failed_stage: str, db: AsyncSession) -> Dict[str, Any]:
        """Resumes an interrupted workflow from a specific stage."""
        logger.info(f"Resuming workflow for job {job_id} at stage {failed_stage}.")

        # Update Job status in database
        result = await db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        if not job:
            logger.warning(f"Job {job_id} not found, cannot resume.")
            return {"job_id": job_id, "status": "failed", "error": "Job not found"}

        # Update pipeline history for the specific stage
        result = await db.execute(
            select(PipelineHistory)
            .where(PipelineHistory.job_id == job_id)
            .where(PipelineHistory.stage == failed_stage)
        )
        history = result.scalar_one_or_none()
        if not history:
            logger.warning(f"Pipeline history for job {job_id} stage {failed_stage} not found, cannot resume.")
            return {"job_id": job_id, "status": "failed", "error": "Pipeline stage not found"}

        job.status = "running"
        history.status = "running"
        await db.commit()

        # Update in-memory tracking
        if job_id in self.running_workflows:
            self.running_workflows[job_id]["status"] = "running"
            self.running_workflows[job_id]["current_stage"] = failed_stage
        else:
            self.running_workflows[job_id] = {
                "status": "running",
                "current_stage": failed_stage
            }

        return {"job_id": job_id, "status": "resumed", "current_stage": failed_stage}

    async def retry_stage(self, job_id: int, stage_name: str, db: AsyncSession) -> Dict[str, Any]:
        """Retries a specific failed stage."""
        logger.info(f"Retrying stage {stage_name} for job {job_id}.")

        # Update in-memory tracking
        if job_id in self.running_workflows:
            self.running_workflows[job_id]["current_stage"] = stage_name
        else:
            self.running_workflows[job_id] = {
                "status": "running",
                "current_stage": stage_name
            }

        # Update pipeline history for the specific stage
        result = await db.execute(
            select(PipelineHistory)
            .where(PipelineHistory.job_id == job_id)
            .where(PipelineHistory.stage == stage_name)
        )
        history = result.scalar_one_or_none()
        if history:
            history.status = "retrying"
            await db.commit()
        else:
            # Create new history entry if it doesn't exist
            new_history = PipelineHistory(
                job_id=job_id,
                stage=stage_name,
                status="retrying"
            )
            db.add(new_history)
            await db.commit()

        return {"job_id": job_id, "stage": stage_name, "status": "retrying"}
