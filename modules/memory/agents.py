from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.logger import get_logger
from app.models.memory import CharacterMemory, EventMemory, RelationshipMemory
from modules.memory.core import MemoryManagerAgent

logger = get_logger("amras.memory.agents")


class BaseMemoryAgent:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.manager = MemoryManagerAgent(session)


class CharacterMemoryAgent(BaseMemoryAgent):
    async def update_character(self, entity_id: str, data: Dict[str, Any], confidence: float = 1.0) -> CharacterMemory:
        # 1. Update Core MemoryStore
        await self.manager.store_memory(
            entity_id=entity_id,
            entity_type="character",
            memory_type="character",
            data=data,
            confidence=confidence,
            change_reason="Character update",
        )

        # 2. Update CharacterMemory specific table
        stmt = select(CharacterMemory).where(CharacterMemory.name == data.get("name"))
        result = await self.session.execute(stmt)
        char_mem = result.scalar_one_or_none()

        if not char_mem:
            char_mem = CharacterMemory(
                memory_id=1,  # This is a simplification. Should get proper ID from memory store
                name=data.get("name", entity_id),
                aliases=data.get("aliases", []),
                current_status=data.get("current_status"),
                first_appearance_chapter=data.get("first_appearance_chapter"),
                last_appearance_chapter=data.get("last_appearance_chapter"),
            )
            self.session.add(char_mem)
        else:
            char_mem.current_status = data.get("current_status", char_mem.current_status)
            char_mem.last_appearance_chapter = data.get("last_appearance_chapter", char_mem.last_appearance_chapter)
            if data.get("aliases"):
                existing = char_mem.aliases or []
                char_mem.aliases = list(set(existing + data["aliases"]))

        await self.session.commit()
        await self.session.refresh(char_mem)
        return char_mem


class EventMemoryAgent(BaseMemoryAgent):
    async def update_event(self, entity_id: str, data: Dict[str, Any], confidence: float = 1.0) -> EventMemory:
        await self.manager.store_memory(
            entity_id=entity_id,
            entity_type="event",
            memory_type="event",
            data=data,
            confidence=confidence,
            change_reason="Event update",
        )

        stmt = select(EventMemory).where(EventMemory.name == data.get("name"))
        result = await self.session.execute(stmt)
        event_mem = result.scalar_one_or_none()

        if not event_mem:
            event_mem = EventMemory(
                memory_id=1,
                name=data.get("name", entity_id),
                event_type=data.get("event_type", "unknown"),
                importance=data.get("importance", 1),
                chapter_id=data.get("chapter_id"),
                outcome=data.get("outcome"),
            )
            self.session.add(event_mem)
        else:
            event_mem.outcome = data.get("outcome", event_mem.outcome)

        await self.session.commit()
        await self.session.refresh(event_mem)
        return event_mem


class RelationshipMemoryAgent(BaseMemoryAgent):
    async def update_relationship(
        self, entity_id: str, data: Dict[str, Any], confidence: float = 1.0
    ) -> RelationshipMemory:
        await self.manager.store_memory(
            entity_id=entity_id,
            entity_type="relationship",
            memory_type="relationship",
            data=data,
            confidence=confidence,
            change_reason="Relationship update",
        )

        stmt = select(RelationshipMemory).where(
            RelationshipMemory.source_entity_id == data.get("source_entity_id"),
            RelationshipMemory.target_entity_id == data.get("target_entity_id"),
        )
        result = await self.session.execute(stmt)
        rel_mem = result.scalar_one_or_none()

        if not rel_mem:
            rel_mem = RelationshipMemory(
                memory_id=1,
                source_entity_id=data.get("source_entity_id", "unknown"),
                target_entity_id=data.get("target_entity_id", "unknown"),
                relationship_type=data.get("relationship_type", "unknown"),
                trust_score=data.get("trust_score"),
                conflict_score=data.get("conflict_score"),
            )
            self.session.add(rel_mem)
        else:
            if "trust_score" in data:
                rel_mem.trust_score = data["trust_score"]
            if "conflict_score" in data:
                rel_mem.conflict_score = data["conflict_score"]

        await self.session.commit()
        await self.session.refresh(rel_mem)
        return rel_mem


class WorldMemoryAgent(BaseMemoryAgent):
    pass


class RetrievalAgent(BaseMemoryAgent):
    pass
