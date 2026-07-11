from typing import Any, Dict

from pydantic import BaseModel, Field


class CompositionInput(BaseModel):
    panel_paths: list[str]
    background_path: str | None
    safe_margins: Dict[str, int]
    config: Dict[str, Any] = Field(default_factory=dict)


class CompositionOutput(BaseModel):
    status: str
    composed_frame_data: Dict[str, Any]


class CompositionAgent:
    """
    Agent responsible for composing panels, backgrounds, overlays, and safe margins.
    """

    async def execute(self, input_data: CompositionInput) -> CompositionOutput:
        # Mock implementation
        return CompositionOutput(status="success", composed_frame_data={"layers": len(input_data.panel_paths)})
