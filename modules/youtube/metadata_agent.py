import logging
from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vision import Narration
from app.models.youtube import VideoMetadata

logger = logging.getLogger(__name__)


class MetadataAgent:
    """
    Generates Chapters, Video metadata, Playlist metadata, Language metadata.
    """

    def __init__(self, ai_provider_manager: Any = None) -> None:
        self.ai = ai_provider_manager

    def format_timestamp(self, seconds: float) -> str:
        """Format seconds into HH:MM:SS or MM:SS."""
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"

    async def generate_chapters(self, narrations: List[Narration]) -> List[Dict[str, Any]]:
        """Generate YouTube chapters from narration timestamps."""
        logger.info(f"Generating chapters from {len(narrations)} narrations.")

        chapters = []
        # Fallback if empty
        if not narrations:
            chapters.append({"timestamp": "00:00", "title": "Introduction", "seconds": 0})
            return chapters

        # Sort by timestamp
        sorted_narrations = sorted(narrations, key=lambda x: getattr(x, "start_time_ms", 0))

        chapters.append({"timestamp": "00:00", "title": "Introduction", "seconds": 0})

        # Generate a chapter every 5 narrations
        for i, n in enumerate(sorted_narrations):
            if i > 0 and i % 5 == 0:
                seconds = getattr(n, "start_time_ms", 0) / 1000.0
                chapters.append(
                    {
                        "timestamp": self.format_timestamp(seconds),
                        "title": f"Chapter Part {i // 5}",
                        "seconds": seconds,
                    }
                )

        return chapters

    async def generate_video_metadata(
        self, db: AsyncSession, job_id: int, chapters: List[Dict[str, Any]]
    ) -> VideoMetadata:
        """Construct the overall video metadata block and persist to DB."""
        logger.info(f"Generating final video metadata block for job {job_id}.")

        # Check for existing metadata first to avoid duplicate inserts
        result = await db.execute(select(VideoMetadata).where(VideoMetadata.job_id == job_id))
        existing_metadata = result.scalars().first()

        if existing_metadata:
            logger.info(f"Found existing video metadata for job {job_id}")
            return existing_metadata

        metadata = VideoMetadata(
            job_id=job_id,
            chapters=chapters,
            license="standard",
            category_id=1,  # Film & Animation
            made_for_kids=False,
        )
        db.add(metadata)
        await db.flush()
        return metadata
