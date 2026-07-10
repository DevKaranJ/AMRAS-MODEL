from typing import Any, Dict, List, Optional

from app.schemas.timeline import TimelineCreate, TimelineSceneCreate


class TimelinePlanningAgent:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    def create_initial_timeline(self, project_id: int, settings: Dict[str, Any]) -> TimelineCreate:
        return TimelineCreate(project_id=project_id, status="draft", duration_ms=0, settings=settings)

    def plan_scenes(
        self, timeline_id: int, pages: List[Dict[str, Any]], narrations: List[Dict[str, Any]]
    ) -> List[TimelineSceneCreate]:
        scenes = []
        current_time_ms = 0
        sequence_number = 1

        for _i, page in enumerate(pages):
            duration_ms = self._estimate_duration(page, narrations)

            scene = TimelineSceneCreate(
                timeline_id=timeline_id,
                sequence_number=sequence_number,
                start_time_ms=current_time_ms,
                end_time_ms=current_time_ms + duration_ms,
                duration_ms=duration_ms,
                page_id=page.get("id"),
            )
            scenes.append(scene)

            current_time_ms += duration_ms
            sequence_number += 1

        return scenes

    def _estimate_duration(self, page: Dict[str, Any], narrations: List[Dict[str, Any]]) -> int:
        return 2000
