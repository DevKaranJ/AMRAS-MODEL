from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.database.session import get_db_session
from app.models.story import (
    KnowledgeBaseEntry,
    StoryCharacter,
    StoryEvent,
    StoryLocation,
    StoryRelationship,
    StoryTimeline,
)
from app.schemas.story import (
    StoryCharacterRead,
    StoryEventRead,
    StoryLocationRead,
    StoryRelationshipRead,
    StoryTimelineRead,
)
from modules.story.engine import StoryEngine
from modules.story.exceptions import StoryEngineError

logger = get_logger("amras.api.story")
router = APIRouter()
engine = StoryEngine()


@router.post("/process", status_code=status.HTTP_200_OK)
async def process_story(
    chapter_id: int,
    vision_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Process OCR and Vision JSON to build the story understanding.
    """
    try:
        result = await engine.process_chapter(chapter_id, vision_data)
        return {"status": "completed", "data": result}
    except StoryEngineError as exc:
        logger.exception("story_processing_failed", chapter_id=chapter_id, error=str(exc))
        raise HTTPException(status_code=500, detail="Story processing failed. Please retry.") from exc


@router.get("/", response_model=Dict[str, Any])
async def get_story_overview() -> Dict[str, Any]:
    """Returns an overview of the story knowledge base (stub)."""
    return {"status": "active", "message": "Story Engine running"}


@router.get("/characters", response_model=List[StoryCharacterRead])
async def get_characters(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db_session),
) -> Any:
    """List all extracted characters with pagination."""
    result = await db.execute(select(StoryCharacter).order_by(StoryCharacter.id).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/events", response_model=List[StoryEventRead])
async def get_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db_session),
) -> Any:
    """List all extracted story events with pagination."""
    result = await db.execute(select(StoryEvent).order_by(StoryEvent.id).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/relationships", response_model=List[StoryRelationshipRead])
async def get_relationships(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db_session),
) -> Any:
    """List all extracted relationships with pagination."""
    result = await db.execute(select(StoryRelationship).order_by(StoryRelationship.id).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/locations", response_model=List[StoryLocationRead])
async def get_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db_session),
) -> Any:
    """List all tracked locations with pagination."""
    result = await db.execute(select(StoryLocation).order_by(StoryLocation.id).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/world", response_model=List[Dict[str, Any]])
async def get_world_knowledge(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db_session),
) -> Any:
    """List world knowledge base entries with pagination."""
    result = await db.execute(
        select(KnowledgeBaseEntry).order_by(KnowledgeBaseEntry.id).offset(skip).limit(limit)
    )
    entries = result.scalars().all()
    return [{"id": e.id, "category": e.category, "key": e.key, "value": e.value} for e in entries]


@router.get("/timeline", response_model=List[StoryTimelineRead])
async def get_timeline(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db_session),
) -> Any:
    """List timeline entries with pagination."""
    result = await db.execute(select(StoryTimeline).order_by(StoryTimeline.id).offset(skip).limit(limit))
    return result.scalars().all()
