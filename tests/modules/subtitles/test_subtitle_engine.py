# type: ignore
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subtitles import SubtitleJob
from modules.subtitles.engine import SubtitleEngine


@pytest.fixture
def mock_db_session() -> AsyncMock:
    session = AsyncMock(spec=AsyncSession)
    return session


@pytest.mark.asyncio
async def test_get_subtitle_job(mock_db_session) -> None:
    engine = SubtitleEngine(db_session=mock_db_session)
    mock_result = MagicMock()
    mock_job = SubtitleJob(id=1, project_id=1, timeline_id=1, language_id=1)
    mock_result.scalar_one_or_none.return_value = mock_job
    mock_db_session.execute.return_value = mock_result

    job = await engine.get_subtitle_job(1)
    assert job is not None
    assert job.id == 1
    mock_db_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_create_subtitle_job(mock_db_session) -> None:
    engine = SubtitleEngine(db_session=mock_db_session)

    job = await engine.create_subtitle_job(project_id=1, timeline_id=2, language_id=3, settings={"max_lines": 2})
    assert job.project_id == 1
    assert job.timeline_id == 2
    assert job.language_id == 3
    assert job.settings == {"max_lines": 2}
    mock_db_session.add.assert_called_once_with(job)
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(job)


@pytest.mark.asyncio
async def test_generate_subtitles_not_found(mock_db_session) -> None:
    engine = SubtitleEngine(db_session=mock_db_session)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result

    await engine.generate_subtitles(1, "test", [])
    mock_db_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_translate_subtitles_not_found(mock_db_session) -> None:
    engine = SubtitleEngine(db_session=mock_db_session)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result

    await engine.translate_subtitles(1)
    mock_db_session.commit.assert_not_called()
