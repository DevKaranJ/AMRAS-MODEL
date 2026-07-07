from typing import Any, Dict, Optional

from app.schemas.timeline import CameraPathCreate


class CameraDirectorAgent:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    def plan_camera_movement(self, panel_metadata: Dict[str, Any], duration_ms: int) -> CameraPathCreate:
        is_battle = panel_metadata.get("is_battle", False)
        emotion = panel_metadata.get("emotion")

        if is_battle:
            return CameraPathCreate(
                type="aggressive_zoom",
                start_zoom=1.0,
                end_zoom=1.5,
                duration_ms=duration_ms
            )
        elif emotion in ["sad", "dramatic"]:
            return CameraPathCreate(
                type="slow_zoom",
                start_zoom=1.0,
                end_zoom=1.2,
                duration_ms=duration_ms
            )
        else:
            return CameraPathCreate(
                type="static",
                start_zoom=1.0,
                end_zoom=1.0,
                duration_ms=duration_ms
            )
