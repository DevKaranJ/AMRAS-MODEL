from typing import Any, Dict

from sqlalchemy import insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vision import ActionDetected, CharacterDetected, ObjectDetected, Panel, VisionJob
from modules.vision.agents.vision_agent import CharacterDetectionAgent, LayoutAgent, SceneAnalysisAgent, VisionAgent
from modules.vision.preprocessing import preprocess_pipeline


class VisionPipeline:
    def __init__(self) -> None:
        self.vision_agent = VisionAgent()
        self.layout_agent = LayoutAgent()
        self.character_agent = CharacterDetectionAgent()
        self.scene_agent = SceneAnalysisAgent()

    async def execute(self, page_id: int, job_id: int, session: AsyncSession) -> Dict[str, Any]:
        """Runs the vision pipeline for a page"""
        try:
            # Update job status to processing
            await session.execute(
                update(VisionJob).where(VisionJob.id == job_id).values(status="processing")
            )
            await session.commit()

            payload = {"page_id": page_id}

            # Step 1: Preprocess (mock)
            preprocess_pipeline(f"page_{page_id}.png")

            # Step 2: Extract vision base info
            vision_res = await self.vision_agent.execute(payload)

            # Step 3: Layout analysis
            layout_res = await self.layout_agent.execute(payload)

            # Step 4: Scene analysis
            scene_res = await self.scene_agent.execute(payload)

            # Step 5: DB Persistence (process each panel individually)
            for panel_data in layout_res.get("panels", []):
                stmt = (
                    insert(Panel)
                    .values(
                        page_id=page_id,
                        panel_number=panel_data["panel_id"],
                        reading_order=panel_data["reading_order"],
                        bounding_box=panel_data["bounding_box"],
                        scene_type=scene_res.get("scene_type"),
                        emotion=scene_res.get("emotion"),
                    )
                    .returning(Panel.id)
                )

                result = await session.execute(stmt)
                panel_id = result.scalar_one()

                # Run panel-specific character/object detection
                panel_payload = {
                    "page_id": page_id,
                    "panel_id": panel_data["panel_id"],
                    "panel_bbox": panel_data["bounding_box"],
                }
                panel_char_res = await self.character_agent.execute(panel_payload)

                for char_data in panel_char_res.get("characters", []):
                    char_stmt = insert(CharacterDetected).values(
                        panel_id=panel_id,
                        identity_estimate=char_data["identity_estimate"],
                        gender=char_data["gender"],
                        age_group=char_data["age_group"],
                        clothing=char_data["clothing"],
                        expression=char_data["expression"],
                        pose=char_data["pose"],
                        confidence=char_data["confidence"],
                        bounding_box=char_data["bounding_box"],
                    )
                    await session.execute(char_stmt)

                for obj_data in panel_char_res.get("objects", []):
                    obj_stmt = insert(ObjectDetected).values(
                        panel_id=panel_id,
                        label=obj_data["label"],
                        confidence=obj_data["confidence"],
                        bounding_box=obj_data["bounding_box"],
                    )
                    await session.execute(obj_stmt)

                for act_data in panel_char_res.get("actions", []):
                    act_stmt = insert(ActionDetected).values(
                        panel_id=panel_id, label=act_data["label"], confidence=act_data["confidence"]
                    )
                    await session.execute(act_stmt)

            await session.commit()

            # Update job status to completed
            await session.execute(
                update(VisionJob).where(VisionJob.id == job_id).values(status="completed")
            )
            await session.commit()

            return {
                "status": "success",
                "page_id": page_id,
                "vision": vision_res,
                "layout": layout_res,
                "scene": scene_res,
            }
        except Exception as e:
            # Mark job as failed
            await session.execute(
                update(VisionJob).where(VisionJob.id == job_id).values(status="failed", error=str(e))
            )
            await session.commit()
            raise
