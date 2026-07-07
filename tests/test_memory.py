from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import MemoryStore
from modules.memory.agents import CharacterMemoryAgent, EventMemoryAgent, RelationshipMemoryAgent
from modules.memory.core import MemoryManagerAgent
from modules.memory.validation import MemoryValidationAgent, QAAgent


class MockResult:
    def __init__(self, value: "Any") -> None:
        self.value = value

    def scalar_one_or_none(self) -> "Any":
        if isinstance(self.value, list) and len(self.value) > 0:
            val = self.value.pop(0)
            return val
        return self.value


@pytest.fixture
def mock_session() -> "Any":
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.mark.asyncio
async def test_memory_manager_store_memory_new(mock_session: Any) -> None:
    mock_session.execute.return_value = MockResult(None)
    agent = MemoryManagerAgent(mock_session)

    memory = await agent.store_memory("hero_1", "character", "semantic", {"name": "Hero"})

    assert memory.entity_id == "hero_1"
    assert memory.version == 1
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_memory_manager_store_memory_update(mock_session: Any) -> None:
    existing_memory = MemoryStore(id=1, entity_id="hero_1", version=1, data={"name": "Hero"})
    mock_session.execute.return_value = MockResult(existing_memory)

    agent = MemoryManagerAgent(mock_session)
    memory = await agent.store_memory("hero_1", "character", "semantic", {"name": "Hero", "level": 2})

    assert memory.version == 2
    assert memory.data["level"] == 2
    mock_session.add.assert_called_once()  # Should add MemoryVersion
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_character_memory_agent_update(mock_session: Any) -> None:
    mock_session.execute.return_value = MockResult([None, None])
    agent = CharacterMemoryAgent(mock_session)

    char = await agent.update_character("char_1", {"name": "Villain", "current_status": "alive"})
    assert char.name == "Villain"
    assert char.current_status == "alive"


@pytest.mark.asyncio
async def test_event_memory_agent_update(mock_session: Any) -> None:
    mock_session.execute.return_value = MockResult([None, None])
    agent = EventMemoryAgent(mock_session)
    event = await agent.update_event("event_1", {"name": "Battle", "event_type": "combat"})
    assert event.name == "Battle"
    assert event.event_type == "combat"


@pytest.mark.asyncio
async def test_relationship_memory_agent_update(mock_session: Any) -> None:
    mock_session.execute.return_value = MockResult([None, None])
    agent = RelationshipMemoryAgent(mock_session)
    rel = await agent.update_relationship(
        "rel_1", {"source_entity_id": "char1", "target_entity_id": "char2", "relationship_type": "friends"}
    )
    assert rel.relationship_type == "friends"
    assert rel.source_entity_id == "char1"


@pytest.mark.asyncio
async def test_memory_validation_detect_conflicts(mock_session: Any) -> None:
    existing_memory = MemoryStore(id=1, entity_id="char_1", version=1, data={"current_status": "dead"})
    mock_session.execute.return_value = MockResult(existing_memory)

    agent = MemoryValidationAgent(mock_session)
    conflicts = await agent.detect_conflicts("char_1", {"current_status": "alive"})

    assert len(conflicts) == 1
    assert conflicts[0].conflict_type == "status_contradiction"


@pytest.mark.asyncio
async def test_qa_agent(mock_session: Any) -> None:
    agent = QAAgent(mock_session)
    result = await agent.verify_integrity()
    assert result["status"] == "ok"
