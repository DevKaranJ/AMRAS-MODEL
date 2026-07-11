from typing import Any, Dict

from pydantic import BaseModel, Field

from modules.video.exceptions import EncodingError


class EncodingInput(BaseModel):
    input_path: str
    output_path: str
    codec: str = Field(..., description="e.g., H.264, H.265, AV1")
    format: str = Field(..., description="e.g., mp4, mkv")
    resolution: str
    fps: int
    config: Dict[str, Any] = Field(default_factory=dict)


class EncodingOutput(BaseModel):
    status: str
    output_path: str
    size_bytes: int
    duration_ms: int


class EncodingAgent:
    """
    Agent responsible for encoding the final video or scene into the specified format/codec.
    """

    async def execute(self, input_data: EncodingInput) -> EncodingOutput:
        # Mock implementation
        if not input_data.input_path:
            raise EncodingError(reason="Missing input path")

        return EncodingOutput(
            status="completed", output_path=input_data.output_path, size_bytes=1048576, duration_ms=60000
        )
