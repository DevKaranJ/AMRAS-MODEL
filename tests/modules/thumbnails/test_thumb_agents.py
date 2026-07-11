from unittest.mock import AsyncMock, Mock  # noqa: E402

import pytest  # noqa: E402


@pytest.fixture
def mock_db_session() -> AsyncMock:
    session = AsyncMock()
    session.add = Mock()  # Make add() synchronous
    return session


from app.models.timeline import TimelineScene  # noqa: E402
from app.models.youtube import Thumbnail  # noqa: E402
from modules.thumbnails.composition_agent import ThumbnailCompositionAgent  # noqa: E402
from modules.thumbnails.planning_agent import ThumbnailPlanningAgent  # noqa: E402


@pytest.mark.asyncio
async def test_thumbnail_planning_agent(mock_db_session: AsyncMock) -> None:
    # Setup test data
    timeline_id = 999
    job_id = 1

    # Mock some scenes
    mock_scenes = []
    for i in range(10):
        mock_scenes.append(
            TimelineScene(
                id=i + 1,
                timeline_id=timeline_id,
                sequence_number=i,
                start_time_ms=i * 1000,
                end_time_ms=(i + 1) * 1000,
                duration_ms=1000 * (i + 1),
            )
        )

    from unittest.mock import MagicMock

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_scenes
    mock_db_session.execute.return_value = mock_result

    # Skip actual creation
    for i in range(10):
        TimelineScene(
            timeline_id=timeline_id,
            sequence_number=i,
            start_time_ms=i * 1000,
            end_time_ms=(i + 1) * 1000,
            duration_ms=1000 * (i + 1),  # Variable duration for scoring
        )

    agent = ThumbnailPlanningAgent()

    concepts = await agent.select_best_scenes(mock_db_session, job_id=job_id, timeline_id=timeline_id, top_k=3)

    assert len(concepts) == 3
    # Concept with highest duration should be first (duration 10000ms -> score 10.0)
    assert concepts[0].score == 10.0
    assert concepts[0].job_id == job_id
    mock_db_session.add.assert_called()  # Flushed to DB


@pytest.mark.asyncio
async def test_thumbnail_composition_agent(mock_db_session: AsyncMock) -> None:
    agent = ThumbnailCompositionAgent()
    thumbnail = Thumbnail(id=1, scene_id=1, base_image_path="test.png", score=90.0)

    variants = await agent.generate_variants(mock_db_session, thumbnail, count=5)

    assert len(variants) == 5
    assert variants[0].variant_name == "Variant A"
    assert "crop" in variants[0].composition_rules
