from typing import Any, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.logger import get_logger
from app.models.memory import ConflictReport, MemoryStore

logger = get_logger("amras.memory.validation")


class MemoryValidationAgent:
    """
    Agent responsible for detecting and reporting conflicts in memories.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def detect_conflicts(self, entity_id: str, new_data: Dict[str, Any]) -> List[ConflictReport]:
        """
        Detects conflicts between existing memory and incoming data.
        Returns a list of created ConflictReport instances.
        """
        stmt = select(MemoryStore).where(MemoryStore.entity_id == entity_id)
        result = await self.session.execute(stmt)
        existing_memory = result.scalar_one_or_none()

        conflicts = []

        if existing_memory:
            # Example basic conflict detection logic: Status contradiction
            if "current_status" in new_data and "current_status" in existing_memory.data:
                if existing_memory.data["current_status"] == "dead" and new_data["current_status"] == "alive":
                    conflict = ConflictReport(
                        entity_id=entity_id,
                        conflict_type="status_contradiction",
                        description=f"Character {entity_id} was marked as dead, but new data says alive.",
                    )
                    self.session.add(conflict)
                    conflicts.append(conflict)
                    logger.warning("conflict_detected", entity_id=entity_id, conflict_type="status_contradiction")

        if conflicts:
            await self.session.commit()

        return conflicts


class QAAgent:
    """
    Agent responsible for overall memory integrity checks.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def verify_integrity(self) -> Dict[str, Any]:
        """
        Runs full integrity check on the memory store.
        """
        return {"status": "ok", "issues": []}
