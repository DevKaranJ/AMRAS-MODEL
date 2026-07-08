from typing import Any, Dict, List, Optional


class ReadingFlowAgent:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    def order_panels(self, panels: List[Dict[str, Any]], layout: str = "right-to-left") -> List[Dict[str, Any]]:
        if not panels:
            return []

        def r2l_sort(p: Dict[str, Any]) -> tuple[float, float]:
            return (p.get("y", 0.0), -p.get("x", 0.0))

        def l2r_sort(p: Dict[str, Any]) -> tuple[float, float]:
            return (p.get("y", 0.0), p.get("x", 0.0))

        if layout == "right-to-left":
            return sorted(panels, key=r2l_sort)
        elif layout == "left-to-right":
            return sorted(panels, key=l2r_sort)
        else:
            return panels
