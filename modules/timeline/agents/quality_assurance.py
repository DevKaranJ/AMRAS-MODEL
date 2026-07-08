from typing import Any, Dict, List, Optional


class QualityAssuranceAgent:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    def audit_timeline(self, timeline_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        issues = []
        scenes = timeline_data.get("scenes", [])

        for scene in scenes:
            duration = scene.get("duration_ms", 0)
            if duration < 500:
                issues.append({"scene_id": scene.get("id"), "issue_type": "fast_cut", "message": "Scene duration < 500ms."})
            elif duration > 30000:
                issues.append({"scene_id": scene.get("id"), "issue_type": "slow_scene", "message": "Scene duration > 30s."})

        return issues
