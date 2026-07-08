from typing import Any, Dict, List, Optional

from app.schemas.timeline import TimelinePanelCreate


class PanelSelectionAgent:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    def select_panels(self, scene_id: int, page_data: Dict[str, Any], scene_duration_ms: int) -> List[TimelinePanelCreate]:
        panels = page_data.get("panels", [])
        if not panels:
            return []

        selected_panels = []
        duration_per_panel = scene_duration_ms // len(panels)
        remainder = scene_duration_ms % len(panels)
        current_time = 0

        for i, panel in enumerate(panels):
            importance = self._calculate_importance(panel)

            # Give the remainder to the last panel
            is_last_panel = (i == len(panels) - 1)
            panel_duration = duration_per_panel + (remainder if is_last_panel else 0)

            selected_panels.append(
                TimelinePanelCreate(
                    scene_id=scene_id,
                    panel_id=panel.get("id"),
                    sequence_number=i + 1,
                    start_time_ms=current_time,
                    end_time_ms=current_time + panel_duration,
                    duration_ms=panel_duration,
                    importance_score=importance
                )
            )
            current_time += panel_duration

        return selected_panels

    def _calculate_importance(self, panel: Dict[str, Any]) -> float:
        score = 0.5
        if panel.get("dialogue_density", 0) > 0.5:
            score += 0.2
        if panel.get("is_action", False):
            score += 0.3
        return min(1.0, score)
