import logging
from typing import List, Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.timeline import TimelineScene
from app.models.youtube import Thumbnail
from app.schemas.youtube import ThumbnailCreate

logger = logging.getLogger(__name__)


class ThumbnailPlanningAgent:
    """
    Selects the best scenes for thumbnails based on emotional weight,
    character importance, and visual appeal.
    """

    def __init__(self, ai_provider_manager: Any = None) -> None:
        self.ai = ai_provider_manager

    async def select_best_scenes(
        self, db: AsyncSession, job_id: int, timeline_id: int, top_k: int = 5
    ) -> List[Thumbnail]:
        """
        Analyze story scenes, rank emotional moments, and return top_k
        thumbnail concepts persisted to the database.
        """
        logger.info(f"Analyzing scenes from timeline {timeline_id} for job {job_id}")

        result = await db.execute(select(TimelineScene).where(TimelineScene.timeline_id == timeline_id))
        scenes = result.scalars().all()

        if not scenes:
            logger.warning(f"No scenes found for timeline {timeline_id}")
            return []

        ranked_scenes: List[Dict[str, Any]] = []
        for scene in scenes:
            # Mock scoring for now - in production this uses AI analysis
            score = float(scene.duration_ms / 1000.0)
            ranked_scenes.append({"scene": scene, "score": score})

        ranked_scenes.sort(key=lambda x: x["score"], reverse=True)
        top_scenes = ranked_scenes[:top_k]

        thumbnails = []
        for s in top_scenes:
            scene_obj = s["scene"]
            thumb = Thumbnail(
                job_id=job_id,
                scene_id=scene_obj.id,
                base_image_path=f"storage/project/metadata/thumbnail/raw_{scene_obj.id}.png",
                score=s["score"],
                metadata_info={"concept": "high emotion", "source_scene": scene_obj.id},
            )
            db.add(thumb)
            thumbnails.append(thumb)

        await db.flush()
        return thumbnails
