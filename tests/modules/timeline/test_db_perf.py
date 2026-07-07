import sys

sys.path.append('.')
import time

import pytest

from app.models.timeline import Timeline, TimelineScene


@pytest.mark.asyncio
class TestTimelineDatabase:
    # We will simulate a quick performance/DB check.
    # Since we are using an async mock session in our regular tests,
    # we'll write logic to verify large object creation in Python as a performance boundary test.

    async def test_performance_large_timeline(self) -> None:
        start_time = time.time()

        # Simulate creating a large number of scenes and panels for an 8-hour timeline
        # Say, 10,000 scenes
        scenes = []
        for i in range(10000):
            scene = TimelineScene(
                id=i,
                timeline_id=1,
                sequence_number=i,
                start_time_ms=i * 2000,
                end_time_ms=(i + 1) * 2000,
                duration_ms=2000
            )
            scenes.append(scene)

        end_time = time.time()

        # Ensure it takes less than 1 second to allocate 10,000 scenes in memory
        assert (end_time - start_time) < 1.0
        assert len(scenes) == 10000

    async def test_timeline_model_initialization(self) -> None:
        timeline = Timeline(project_id=1, status="draft", duration_ms=5000)
        assert timeline.project_id == 1
        assert timeline.status == "draft"
        assert timeline.duration_ms == 5000
