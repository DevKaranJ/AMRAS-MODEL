from typing import Any, Dict, Optional

from app.schemas.timeline import TransitionCreate


class MotionPlanningAgent:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    def plan_transition(self, from_scene: Dict[str, Any], to_scene: Dict[str, Any]) -> TransitionCreate:
        from_emotion = from_scene.get("metadata", {}).get("emotion")
        to_emotion = to_scene.get("metadata", {}).get("emotion")

        if from_emotion != to_emotion:
            return TransitionCreate(type="fade", duration_ms=500)
        return TransitionCreate(type="cut", duration_ms=0)
