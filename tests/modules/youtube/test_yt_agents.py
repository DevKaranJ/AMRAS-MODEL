from unittest.mock import AsyncMock

import pytest


@pytest.fixture
def mock_db_session() -> AsyncMock:
    session = AsyncMock()
    return session

from modules.youtube.metadata_agent import MetadataAgent
from modules.youtube.publishing_agent import PublishingAgent
from modules.youtube.qa_agent import QAAgent
from modules.youtube.seo_agent import SEOAgent


@pytest.mark.asyncio
async def test_seo_agent_titles(mock_db_session: AsyncMock) -> None:
    agent = SEOAgent()
    titles = await agent.generate_titles(mock_db_session, profile_id=1, story_context="The hero battles the dragon", count=2)
    assert len(titles) == 2
    assert titles[0].style == "SEO"
    assert titles[1].style == "Curiosity"


@pytest.mark.asyncio
async def test_seo_agent_description(mock_db_session: AsyncMock) -> None:
    agent = SEOAgent()
    desc = await agent.generate_description(mock_db_session, profile_id=1, story_summary="summary", timestamps="00:00 start", links=["link"])
    assert "summary" in desc.text
    assert "link" in desc.text
    assert desc.has_chapters is True


@pytest.mark.asyncio
async def test_metadata_agent_chapters() -> None:
    agent = MetadataAgent()
    narrations = [type("", (), {"id": i, "start_time_ms": i * 1000 * 60})() for i in range(10)]
    chapters = await agent.generate_chapters(narrations)

    assert len(chapters) > 1
    assert chapters[0]["timestamp"] == "00:00"


@pytest.mark.asyncio
async def test_qa_agent_valid_package() -> None:
    agent = QAAgent()
    pkg = {
        "video_path": "test_mock_video.mp4",
        "thumbnail_path": "test_mock_thumb.png",
        "title": "A good title",
        "description": "desc",
        "tags": ["tag1"],
        "metadata": {},
    }
    assert await agent.validate_package(pkg) is True


@pytest.mark.asyncio
async def test_qa_agent_invalid_package() -> None:
    agent = QAAgent()
    pkg = {
        "title": "A good title",
    }
    assert await agent.validate_package(pkg) is False


@pytest.mark.asyncio
async def test_publishing_agent(mock_db_session: AsyncMock) -> None:
    agent = PublishingAgent()

    from app.models.youtube import PublishingJob
    mock_job = PublishingJob(id=1, project_id=1, status='queued', progress=0.0)
    from unittest.mock import MagicMock
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_job
    mock_db_session.execute.return_value = mock_result

    result = await agent.upload_package(mock_db_session, job_id=1, package={"video_path": "mock"})
    assert result.youtube_video_id == "mock_yt_id_123"
    mock_db_session.add.assert_called()

@pytest.mark.asyncio
async def test_metadata_agent_video_metadata(mock_db_session: AsyncMock) -> None:
    agent = MetadataAgent()
    metadata = await agent.generate_video_metadata(mock_db_session, job_id=1, chapters=[])
    assert metadata.job_id == 1
    assert metadata.license == "standard"
    mock_db_session.add.assert_called_once()
    mock_db_session.flush.assert_called_once()

@pytest.mark.asyncio
async def test_playlist_agent(mock_db_session: AsyncMock) -> None:
    from modules.youtube.playlist_agent import PlaylistAgent
    agent = PlaylistAgent()

    # Mock DB empty result
    from unittest.mock import MagicMock
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_db_session.execute.return_value = mock_result

    playlist = await agent.get_or_create_playlist(mock_db_session, manga_id=5, series_title="Naruto")
    assert playlist.manga_id == 5
    assert playlist.title == "Naruto - Full Series Recap"
    mock_db_session.add.assert_called_once()

@pytest.mark.asyncio
async def test_analytics_agent(mock_db_session: AsyncMock) -> None:
    from modules.youtube.analytics_agent import AnalyticsAgent
    agent = AnalyticsAgent()

    profile = await agent.prepare_analytics_baseline(mock_db_session, job_id=1, tags=["hero"])
    assert profile.job_id == 1
    assert profile.expected_ctr == 5.5
    assert len(profile.retention_markers) == 2
    mock_db_session.add.assert_called_once()
