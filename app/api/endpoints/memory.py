from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.database.session import get_db_session
from app.models.memory import CharacterMemory, ConflictReport, EventMemory, MemoryStore, WorldMemory
from app.schemas.memory import (
    CharacterMemoryRead,
    ConflictReportRead,
    EventMemoryRead,
    MemorySearchRequest,
    MemoryStoreCreate,
    MemoryStoreRead,
    WorldMemoryRead,
)
from modules.memory.core import MemoryManagerAgent

logger = get_logger("amras.api.memory")
router = APIRouter()


@router.post("/update", response_model=MemoryStoreRead, status_code=status.HTTP_201_CREATED)
async def update_memory(
    memory_in: MemoryStoreCreate,
    db: AsyncSession = Depends(get_db_session),
) -> Any:
    """Store or update a memory in the system."""
    logger.info("memory_update_requested", entity_id=memory_in.entity_id)
    manager = MemoryManagerAgent(db)
    memory = await manager.store_memory(
        entity_id=memory_in.entity_id,
        entity_type=memory_in.entity_type,
        memory_type=memory_in.memory_type,
        data=memory_in.data,
        confidence=memory_in.confidence,
        change_reason="API update",
    )
    return memory


@router.post("/rebuild", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def rebuild_memory() -> Any:
    """Trigger a background job to rebuild the memory index and knowledge graph."""
    logger.info("memory_rebuild_requested")
    return {"status": "unsupported", "message": "Memory rebuild is not yet implemented"}


@router.get("", response_model=List[MemoryStoreRead])
async def get_memories(
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db_session),
) -> Any:
    """Retrieve a paginated list of memories."""
    stmt = select(MemoryStore)
    if entity_type:
        stmt = stmt.where(MemoryStore.entity_type == entity_type)
    stmt = stmt.order_by(MemoryStore.id).offset(offset).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/character/{name}", response_model=CharacterMemoryRead)
async def get_character_memory(name: str, db: AsyncSession = Depends(get_db_session)) -> Any:
    """Retrieve character memory by name."""
    stmt = select(CharacterMemory).where(CharacterMemory.name == name)
    result = await db.execute(stmt)
    character = result.scalar_one_or_none()
    if not character:
        raise HTTPException(status_code=404, detail="Character memory not found")
    return character


@router.get("/event/{name}", response_model=EventMemoryRead)
async def get_event_memory(name: str, db: AsyncSession = Depends(get_db_session)) -> Any:
    """Retrieve event memory by name."""
    stmt = select(EventMemory).where(EventMemory.name == name)
    result = await db.execute(stmt)
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event memory not found")
    return event


@router.get("/location/{name}", response_model=WorldMemoryRead)
async def get_location_memory(name: str, db: AsyncSession = Depends(get_db_session)) -> Any:
    """Retrieve world/location memory by name."""
    stmt = select(WorldMemory).where(WorldMemory.name == name)
    result = await db.execute(stmt)
    location = result.scalar_one_or_none()
    if not location:
        raise HTTPException(status_code=404, detail="Location memory not found")
    return location


@router.post("/search", response_model=List[MemoryStoreRead])
async def search_memory(
    search_request: MemorySearchRequest,
    db: AsyncSession = Depends(get_db_session),
) -> Any:
    """
    Search memory by entity/memory type and optional keyword.

    The ``query`` field performs a case-insensitive substring match against the
    ``entity_id`` column.  Full-text / vector search can be wired in here once a
    search index is available.
    """
    stmt = select(MemoryStore)
    if search_request.entity_type:
        stmt = stmt.where(MemoryStore.entity_type == search_request.entity_type)
    if search_request.memory_type:
        stmt = stmt.where(MemoryStore.memory_type == search_request.memory_type)
    if search_request.query:
        stmt = stmt.where(MemoryStore.entity_id.ilike(f"%{search_request.query}%"))
    stmt = stmt.limit(search_request.limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/history/{entity_id}", response_model=List[Dict[str, Any]])
async def get_memory_history(entity_id: str, db: AsyncSession = Depends(get_db_session)) -> Any:
    """Retrieve the version history of a specific memory."""
    manager = MemoryManagerAgent(db)
    versions = await manager.get_memory_history(entity_id)
    return [
        {
            "version": v.version,
            "data": v.data,
            "change_reason": v.change_reason,
            "created_at": v.created_at.isoformat() if v.created_at else None,
        }
        for v in versions
    ]


@router.get("/conflicts", response_model=List[ConflictReportRead])
async def get_memory_conflicts(
    resolved: Optional[bool] = Query(None, description="Filter by resolution status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db_session),
) -> Any:
    """Retrieve detected memory conflicts."""
    stmt = select(ConflictReport)
    if resolved is not None:
        stmt = stmt.where(ConflictReport.resolved.is_(resolved))
    stmt = stmt.order_by(ConflictReport.id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()
