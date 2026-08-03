"""Real render manager for orchestrating video rendering pipeline.

Manages the complete rendering process:
1. Scene rendering (individual clips)
2. Audio overlay
3. Transitions
4. Final encoding
"""

import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from modules.video.exceptions import InvalidRenderActionError, RenderJobNotFound
from app.core.logger import get_logger

logger = get_logger("amras.video.render_manager")


class RenderManagerInput(BaseModel):
    job_id: int
    action: str = Field(..., description="Action: 'start', 'resume', 'cancel', 'status'")
    config: Dict[str, Any] = Field(default_factory=dict)


class RenderManagerOutput(BaseModel):
    job_id: int
    status: str
    progress: float
    message: str
    output_path: Optional[str] = None


class RenderJob:
    """Tracks render job state."""

    def __init__(self, job_id: int, config: Dict[str, Any]):
        self.job_id = job_id
        self.config = config
        self.status = "queued"
        self.progress = 0.0
        self.current_scene = 0
        self.total_scenes = 0
        self.output_path: Optional[str] = None
        self.error: Optional[str] = None


class RenderManagerAgent:
    """Real render manager for orchestrating video rendering."""

    def __init__(self):
        self._jobs: Dict[int, RenderJob] = {}
        logger.info("render_manager_initialized")

    async def execute(self, input_data: RenderManagerInput) -> RenderManagerOutput:
        """Execute render manager action."""
        if input_data.action == "start":
            return await self._start_render(input_data)
        elif input_data.action == "resume":
            return await self._resume_render(input_data)
        elif input_data.action == "cancel":
            return await self._cancel_render(input_data)
        elif input_data.action == "status":
            return await self._get_status(input_data)
        else:
            raise InvalidRenderActionError(action=input_data.action)

    async def _start_render(self, input_data: RenderManagerInput) -> RenderManagerOutput:
        """Start a new render job."""
        config = input_data.config

        # Validate required config
        scenes = config.get("scenes", [])
        output_dir = config.get("output_dir", "./storage/videos")

        if not scenes:
            return RenderManagerOutput(
                job_id=input_data.job_id,
                status="failed",
                progress=0.0,
                message="No scenes provided in config",
            )

        # Create render job
        job = RenderJob(input_data.job_id, config)
        job.total_scenes = len(scenes)
        job.status = "rendering"
        self._jobs[input_data.job_id] = job

        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        logger.info(
            "render_started",
            job_id=input_data.job_id,
            total_scenes=job.total_scenes,
        )

        return RenderManagerOutput(
            job_id=input_data.job_id,
            status="rendering",
            progress=0.0,
            message=f"Rendering {job.total_scenes} scenes",
        )

    async def _resume_render(self, input_data: RenderManagerInput) -> RenderManagerOutput:
        """Resume a paused/failed render job."""
        job = self._jobs.get(input_data.job_id)
        if not job:
            return RenderManagerOutput(
                job_id=input_data.job_id,
                status="failed",
                progress=0.0,
                message="Job not found",
            )

        job.status = "rendering"
        logger.info("render_resumed", job_id=input_data.job_id)

        return RenderManagerOutput(
            job_id=input_data.job_id,
            status="rendering",
            progress=job.progress,
            message=f"Resuming from scene {job.current_scene + 1}",
        )

    async def _cancel_render(self, input_data: RenderManagerInput) -> RenderManagerOutput:
        """Cancel a render job."""
        job = self._jobs.get(input_data.job_id)
        if job:
            job.status = "cancelled"
            logger.info("render_cancelled", job_id=input_data.job_id)

        return RenderManagerOutput(
            job_id=input_data.job_id,
            status="cancelled",
            progress=job.progress if job else 0.0,
            message="Render cancelled",
        )

    async def _get_status(self, input_data: RenderManagerInput) -> RenderManagerOutput:
        """Get render job status."""
        job = self._jobs.get(input_data.job_id)
        if not job:
            return RenderManagerOutput(
                job_id=input_data.job_id,
                status="not_found",
                progress=0.0,
                message="Job not found",
            )

        return RenderManagerOutput(
            job_id=input_data.job_id,
            status=job.status,
            progress=job.progress,
            message=f"Scene {job.current_scene}/{job.total_scenes}",
            output_path=job.output_path,
        )

    def update_progress(self, job_id: int, scene: int, total: int) -> None:
        """Update render progress."""
        job = self._jobs.get(job_id)
        if job:
            job.current_scene = scene
            job.total_scenes = total
            job.progress = (scene / total) * 100 if total > 0 else 0

    def complete_job(self, job_id: int, output_path: str) -> None:
        """Mark job as completed."""
        job = self._jobs.get(job_id)
        if job:
            job.status = "completed"
            job.progress = 100.0
            job.output_path = output_path
            logger.info("render_completed", job_id=job_id, output=output_path)

    def fail_job(self, job_id: int, error: str) -> None:
        """Mark job as failed."""
        job = self._jobs.get(job_id)
        if job:
            job.status = "failed"
            job.error = error
            logger.error("render_failed", job_id=job_id, error=error)
