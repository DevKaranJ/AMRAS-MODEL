from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.logger import get_logger
from app.models.memory import MemoryStore, MemoryVersion

logger = get_logger("amras.memory.core")


class MemoryManagerAgent:
    """
    Core agent responsible for managing generic memory stores.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def store_memory(
        self,
        entity_id: str,
        entity_type: str,
        memory_type: str,
        data: Dict[str, Any],
        confidence: float = 1.0,
        change_reason: Optional[str] = None,
    ) -> MemoryStore:
        """Stores a new memory or updates an existing one with versioning."""
        stmt = select(MemoryStore).where(MemoryStore.entity_id == entity_id)
        result = await self.session.execute(stmt)
        memory = result.scalar_one_or_none()

        if memory:
            # Create a new version from current state
            version_record = MemoryVersion(
                memory_id=memory.id,
                version=memory.version,
                data=memory.data,
                change_reason=change_reason or "Automated update",
            )
            self.session.add(version_record)

            # Update current state
            memory.data = data
            memory.version += 1
            memory.confidence = confidence
            logger.info("memory_updated", entity_id=entity_id, new_version=memory.version)
        else:
            # Create new memory
            memory = MemoryStore(
                entity_id=entity_id,
                entity_type=entity_type,
                memory_type=memory_type,
                data=data,
                version=1,
                confidence=confidence,
            )
            self.session.add(memory)
            logger.info("memory_created", entity_id=entity_id)

        await self.session.commit()
        await self.session.refresh(memory)
        return memory

    async def get_memory(self, entity_id: str) -> Optional[MemoryStore]:
        """Retrieve a memory by entity_id."""
        stmt = select(MemoryStore).where(MemoryStore.entity_id == entity_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_memory_history(self, entity_id: str) -> List[MemoryVersion]:
        """Retrieve the version history of a memory."""
        stmt = select(MemoryStore).options(selectinload(MemoryStore.versions)).where(MemoryStore.entity_id == entity_id)
        result = await self.session.execute(stmt)
        memory = result.scalar_one_or_none()
        if not memory:
            return []
        return sorted(memory.versions, key=lambda v: v.version, reverse=True)
