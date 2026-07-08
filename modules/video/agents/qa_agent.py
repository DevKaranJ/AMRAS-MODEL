from typing import List

from pydantic import BaseModel

from modules.video.exceptions import QAValidationError


class QAInput(BaseModel):
    video_path: str
    expected_duration_ms: int
    expected_fps: float


class QAReport(BaseModel):
    passed: bool
    dropped_frames: int
    black_frames: int
    sync_drift_ms: int
    artifacts_detected: List[str]


class QAAgent:
    """
    Agent responsible for verifying the rendered video quality, including frame drops,
    black frames, audio sync, and visual artifacts.
    """

    async def execute(self, input_data: QAInput) -> QAReport:
        # Mock implementation
        if not input_data.video_path:
            raise QAValidationError(reason="No video path provided for QA")

        return QAReport(
            passed=True,
            dropped_frames=0,
            black_frames=0,
            sync_drift_ms=10,
            artifacts_detected=[]
        )
