from typing import Any, Dict, List, Optional

from app.schemas.timeline import SynchronizationCreate


class AudioSynchronizationAgent:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    def synchronize(self, scenes: List[Dict[str, Any]], audio_segments: List[Dict[str, Any]]) -> List[SynchronizationCreate]:
        syncs = []
        for i, scene in enumerate(scenes):
            scene_start = scene.get("start_time_ms", 0)

            if i < len(audio_segments):
                audio = audio_segments[i]
                audio_end = scene_start + audio.get("duration_ms", 0)
                if scene.get("end_time_ms", 0) < audio_end:
                    scene["end_time_ms"] = audio_end
                    scene["duration_ms"] = audio_end - scene_start

                sync = SynchronizationCreate(
                    scene_id=scene.get("id", 0),
                    audio_segment_id=audio.get("id"),
                    narration_id=audio.get("narration_id"),
                    start_time_ms=scene_start,
                    end_time_ms=audio_end,
                    sync_accuracy=1.0
                )
                syncs.append(sync)
        return syncs
