from unittest.mock import AsyncMock, MagicMock

import pytest

from app.schemas.timeline import TimelineGenerateRequest
from modules.timeline.service import TimelineService


@pytest.fixture
def mock_db_session() -> AsyncMock:
    return AsyncMock()

class TestTimelineService:
    @pytest.mark.asyncio
    async def test_generate_timeline_success(self, mock_db_session: AsyncMock) -> None:
        service = TimelineService(db=mock_db_session)
        request = TimelineGenerateRequest(project_id=1, settings={"test": True})

        result = await service.generate_timeline(request)

        assert isinstance(result, dict)
        assert result["project_id"] == 1
        assert result["status"] == "generated"
        assert "scenes" in result

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
        result = await service.generate_timeline(request)

        assert result["project_id"] == 2
        assert result["status"] == "generated"
