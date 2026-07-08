from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.timeline import CameraPath, Timeline, TimelinePanel, TimelineScene
from app.schemas.timeline import TimelineGenerateRequest, TimelineRebuildRequest
from modules.timeline.agents import (
    AudioSynchronizationAgent,
    CameraDirectorAgent,
    MotionPlanningAgent,
    PanelSelectionAgent,
    QualityAssuranceAgent,
    ReadingFlowAgent,
    SceneCompositionAgent,
    TimelinePlanningAgent,
)


class TimelineService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.planning_agent = TimelinePlanningAgent()
        self.panel_selection = PanelSelectionAgent()
        self.camera_director = CameraDirectorAgent()
        self.scene_composition = SceneCompositionAgent()
        self.audio_sync = AudioSynchronizationAgent()
        self.reading_flow = ReadingFlowAgent()
        self.motion_planning = MotionPlanningAgent()
        self.qa_agent = QualityAssuranceAgent()

    async def generate_timeline(self, request: TimelineGenerateRequest) -> Dict[str, Any]:
        """
        Orchestrates the timeline generation process.
        """
        # Placeholder mock data - TODO: replace with actual data retrieval
        pages: List[Dict[str, Any]] = [{"id": 1, "panels": [{"id": 10}, {"id": 11}]}]
        narrations: List[Dict[str, Any]] = [{"id": 100, "duration_ms": 3000}]

        # 1. Create Initial Draft
        timeline_schema = self.planning_agent.create_initial_timeline(
            project_id=request.project_id,
            settings=request.settings or {}
        )

        # Persist timeline to database
        timeline = Timeline(
            project_id=timeline_schema.project_id,
            status=timeline_schema.status,
            duration_ms=timeline_schema.duration_ms,
            settings=timeline_schema.settings
        )
        self.db.add(timeline)
        await self.db.flush()

        # 2. Plan Scenes
        scenes = self.planning_agent.plan_scenes(timeline.id, pages, narrations)

        # 3. Synchronize Audio
        _ = self.audio_sync.synchronize([s.model_dump() for s in scenes], narrations)

        # Store all scenes and their panel data
        all_panels_data = []
        all_camera_paths = []

        # 4. Panel Selection and Camera Directing
        for scene_schema in scenes:
            # Create scene in database
            scene = TimelineScene(
                timeline_id=scene_schema.timeline_id,
                sequence_number=scene_schema.sequence_number,
                start_time_ms=scene_schema.start_time_ms,
                end_time_ms=scene_schema.end_time_ms,
                duration_ms=scene_schema.duration_ms,
                page_id=scene_schema.page_id
            )
            self.db.add(scene)
            await self.db.flush()

            panels = self.panel_selection.select_panels(
                scene_id=scene.id,
                page_data=pages[0],
                scene_duration_ms=scene_schema.duration_ms
            )
            ordered_panels = self.reading_flow.order_panels([p.model_dump() for p in panels])

            # Store panel data for timeline assembly
            for panel_dict in ordered_panels:
                # Derive panel metadata from content instead of hardcoding neutral
                panel_metadata = {
                    "emotion": panel_dict.get("emotion", "neutral"),
                    "is_action": panel_dict.get("is_action", False),
                    "dialogue_density": panel_dict.get("dialogue_density", 0.0)
                }

                camera_path = self.camera_director.plan_camera_movement(
                    panel_metadata=panel_metadata,
                    duration_ms=panel_dict.get("duration_ms", 0)
                )

                # Create panel in database
                panel = TimelinePanel(
                    scene_id=scene.id,
                    panel_id=panel_dict.get("panel_id"),
                    sequence_number=panel_dict.get("sequence_number", 0),
                    start_time_ms=panel_dict.get("start_time_ms", 0),
                    end_time_ms=panel_dict.get("end_time_ms", 0),
                    duration_ms=panel_dict.get("duration_ms", 0),
                    importance_score=panel_dict.get("importance_score", 0.0)
                )
                self.db.add(panel)

                all_panels_data.append(panel_dict)
                if camera_path:
                    all_camera_paths.append(camera_path)

        # Update timeline status and duration
        timeline.status = "generated"
        timeline.duration_ms = sum(s.duration_ms for s in scenes)

        await self.db.commit()
        await self.db.refresh(timeline)

        # 5. Quality Assurance
        timeline_data = {
            "id": timeline.id,
            "project_id": timeline.project_id,
            "status": timeline.status,
            "duration_ms": timeline.duration_ms,
            "scenes": [s.model_dump() for s in scenes],
            "panels": all_panels_data,
            "camera_paths": all_camera_paths
        }
        issues = self.qa_agent.audit_timeline(timeline_data)
        if issues:
            pass

        return timeline_data

    async def get_timeline(self, project_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve timeline from database by project_id."""
        stmt = select(Timeline).where(Timeline.project_id == project_id)
        result = await self.db.execute(stmt)
        timeline = result.scalar_one_or_none()

        if not timeline:
            return None

        return {
            "id": timeline.id,
            "project_id": timeline.project_id,
            "status": timeline.status,
            "duration_ms": timeline.duration_ms,
            "settings": timeline.settings
        }

    async def rebuild_timeline(self, request: TimelineRebuildRequest) -> Dict[str, Any]:
        """Rebuild a timeline with optional scene filtering."""
        stmt = select(Timeline).where(Timeline.id == request.timeline_id)
        result = await self.db.execute(stmt)
        timeline = result.scalar_one_or_none()

        if not timeline:
            return {"status": "error", "message": "Timeline not found"}

        # TODO: Implement actual rebuild logic
        timeline.status = "rebuilding"
        await self.db.commit()

        return {
            "status": "rebuilding",
            "timeline_id": request.timeline_id,
            "rebuild_scenes": request.rebuild_scenes
        }

    async def get_timeline_scenes(self, timeline_id: int) -> List[Dict[str, Any]]:
        """Get all scenes for a timeline."""
        stmt = select(TimelineScene).where(TimelineScene.timeline_id == timeline_id)
        result = await self.db.execute(stmt)
        scenes = result.scalars().all()

        return [
            {
                "id": scene.id,
                "timeline_id": scene.timeline_id,
                "sequence_number": scene.sequence_number,
                "start_time_ms": scene.start_time_ms,
                "end_time_ms": scene.end_time_ms,
                "duration_ms": scene.duration_ms
            }
            for scene in scenes
        ]

    async def get_timeline_cameras(self, scene_id: int) -> List[Dict[str, Any]]:
        """Get camera paths for a scene."""
        stmt = select(TimelinePanel).where(TimelinePanel.scene_id == scene_id)
        result = await self.db.execute(stmt)
        panels = result.scalars().all()

        camera_ids = [p.camera_path_id for p in panels if p.camera_path_id]

        if not camera_ids:
            return []

        camera_stmt = select(CameraPath).where(CameraPath.id.in_(camera_ids))
        camera_result = await self.db.execute(camera_stmt)
        cameras = camera_result.scalars().all()

        return [
            {
                "id": camera.id,
                "type": camera.type,
                "duration_ms": camera.duration_ms
            }
            for camera in cameras
        ]

    async def get_timeline_transitions(self, timeline_id: int) -> List[Dict[str, Any]]:
        """Get transitions for a timeline."""
        # TODO: Implement actual transition retrieval
        return []

    async def get_timeline_status(self, project_id: int) -> Dict[str, Any]:
        """Get timeline status for a project."""
        stmt = select(Timeline).where(Timeline.project_id == project_id)
        result = await self.db.execute(stmt)
        timeline = result.scalar_one_or_none()

        if not timeline:
            return {"project_id": project_id, "status": "not_found"}

        return {
            "project_id": project_id,
            "timeline_id": timeline.id,
            "status": timeline.status,
            "duration_ms": timeline.duration_ms
        }
