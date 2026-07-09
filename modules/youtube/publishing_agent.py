import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.youtube import PublishedVideo, PublishingJob

logger = logging.getLogger(__name__)


class PublishingAgent:
    """
    Handles Uploading of Video, Thumbnail, Subtitles, Metadata.
    Tracks state in database and supports scheduled publishing.
    """

    def __init__(self, youtube_client: Any = None) -> None:
        self.youtube = youtube_client  # Placeholder for actual API client

    async def get_or_create_job(self, db: AsyncSession, project_id: int) -> PublishingJob:
        """Finds active publishing job or creates new one. Handles concurrent creation safely."""
        # Use SELECT ... FOR UPDATE to lock the row during the check
        result = await db.execute(
            select(PublishingJob)
            .where(PublishingJob.project_id == project_id, PublishingJob.status != 'published')
            .with_for_update()
        )
        job = result.scalars().first()

        if not job:
            try:
                job = PublishingJob(project_id=project_id, status="queued")
                db.add(job)
                await db.flush()
            except IntegrityError:
                # Another process created the job concurrently, re-query
                await db.rollback()
                result = await db.execute(
                    select(PublishingJob)
                    .where(PublishingJob.project_id == project_id, PublishingJob.status != 'published')
                )
                job = result.scalars().first()
                if not job:
                    raise

        return job

    async def upload_package(
        self, db: AsyncSession, job_id: int, package: Dict[str, Any], schedule_time: Optional[datetime] = None
    ) -> PublishedVideo:
        """
        Uploads the validated package to YouTube. Handles immediate and scheduled publishes.
        Persists results into PublishedVideo DB entity.
        """
        logger.info(f"Starting upload for job {job_id}. Scheduled: {schedule_time}")

        # Load Job
        result = await db.execute(select(PublishingJob).where(PublishingJob.id == job_id))
        job = result.scalars().first()

        if not job:
            raise ValueError(f"Job {job_id} not found")

        job.status = "uploading"
        job.progress = 10.0
        await db.flush()

        # Mock upload process with failure handling simulations
        try:
            # 1. Upload Video
            logger.info(f"Uploading video: {package.get('video_path')}")
            job.progress = 50.0

            # 2. Upload Thumbnail
            logger.info(f"Uploading thumbnail: {package.get('thumbnail_path')}")
            job.progress = 70.0

            # 3. Set Metadata
            logger.info("Setting video metadata...")
            job.progress = 90.0

            # Generate a unique mock YouTube ID (since real YouTube API is not available)
            # Using UUID to avoid collisions on the unique constraint
            video_id = f"mock_yt_{uuid4().hex[:11]}"

            # Finish job
            job.status = "scheduled" if schedule_time else "published"
            job.progress = 100.0

            published_record = PublishedVideo(
                job_id=job_id,
                youtube_video_id=video_id,
                url=f"https://youtube.com/watch?v={video_id}",
                status="active",
                published_at=schedule_time or datetime.now(timezone.utc)
            )
            db.add(published_record)
            await db.flush()

            return published_record

        except Exception as e:
            logger.error(f"Upload failed: {str(e)}")
            await db.rollback()
            job.status = "failed"
            job.error_message = str(e)
            await db.flush()
            raise e
