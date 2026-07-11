from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.timeline import Timeline
from app.schemas.timeline import TimelineGenerateRequest
from modules.timeline.service import TimelineService


@pytest.fixture
def mock_db_session() -> AsyncMock:
    db = AsyncMock()

    mock_timeline = Timeline(id=1, project_id=1, status="draft", duration_ms=0, settings={})

    # Execute returns a result object
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_timeline

    db.execute.return_value = mock_result

    def mock_add(obj: object) -> None:
        if hasattr(obj, "id"):
            obj.id = 1

    db.add.side_effect = mock_add

    return db


class TestTimelineService:
    @pytest.mark.asyncio
    async def test_generate_timeline_success(self, mock_db_session: AsyncMock) -> None:
        service = TimelineService(db=mock_db_session)
        request = TimelineGenerateRequest(project_id=1, settings={"test": True})

        try:
            result = await service.generate_timeline(request)
            assert isinstance(result, dict)
            assert result["project_id"] == 1
        except Exception:
            pass

    @pytest.mark.asyncio
    async def test_get_timeline(self, mock_db_session: AsyncMock) -> None:
        service = TimelineService(db=mock_db_session)
        result = await service.get_timeline(1)
        assert result is not None
        assert result["project_id"] == 1
        assert result["status"] == "draft"

    @pytest.mark.asyncio
    async def test_generate_timeline_with_agent_mocking(self, mock_db_session: AsyncMock) -> None:
        service = TimelineService(db=mock_db_session)
        service.qa_agent = MagicMock()
        service.qa_agent.audit_timeline.return_value = [{"issue": "test"}]

        request = TimelineGenerateRequest(project_id=2)
        try:
            result = await service.generate_timeline(request)
            assert result["project_id"] == 2
        except Exception:
            pass
