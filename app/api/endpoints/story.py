from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
        # Process the chapter inline (in production, dispatch to background task)
        result = await engine.process_chapter(chapter_id, vision_data)
        return {"status": "completed", "data": result}
    except StoryEngineError as e:
        # StoryEngineError wraps all exceptions including internal failures
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/", response_model=Dict[str, Any])
async def get_story_overview() -> Dict[str, Any]:
    """
    Returns an overview of the story knowledge base (stub).
    """
    # A full implementation would query multiple tables to construct the story graph
    return {"status": "active", "message": "Story Engine running"}


@router.get("/characters", response_model=List[StoryCharacterRead])
async def get_characters(db: AsyncSession = Depends(get_db_session)) -> Any:
    """List all extracted characters."""
    result = await db.execute(select(StoryCharacter).order_by(StoryCharacter.id).limit(100))
    return result.scalars().all()


@router.get("/events", response_model=List[StoryEventRead])
async def get_events(db: AsyncSession = Depends(get_db_session)) -> Any:
    """List all extracted story events."""
    result = await db.execute(select(StoryEvent).order_by(StoryEvent.id).limit(100))
    return result.scalars().all()


@router.get("/relationships", response_model=List[StoryRelationshipRead])
async def get_relationships(db: AsyncSession = Depends(get_db_session)) -> Any:
    """List all extracted relationships."""
    result = await db.execute(select(StoryRelationship).order_by(StoryRelationship.id).limit(100))
    return result.scalars().all()


@router.get("/locations", response_model=List[StoryLocationRead])
async def get_locations(db: AsyncSession = Depends(get_db_session)) -> Any:
    """List all tracked locations."""
    result = await db.execute(select(StoryLocation).order_by(StoryLocation.id).limit(100))
    return result.scalars().all()


@router.get("/world", response_model=List[Dict[str, Any]])
async def get_world_knowledge(db: AsyncSession = Depends(get_db_session)) -> Any:
    """List world knowledge base entries."""
    result = await db.execute(select(KnowledgeBaseEntry).order_by(KnowledgeBaseEntry.id).limit(100))
    entries = result.scalars().all()
    # Serialize since KnowledgeBaseEntryRead wasn't explicitly modeled for full dict output here easily
    return [{"id": e.id, "category": e.category, "key": e.key, "value": e.value} for e in entries]


@router.get("/timeline", response_model=List[StoryTimelineRead])
async def get_timeline(db: AsyncSession = Depends(get_db_session)) -> Any:
    """List timeline entries."""
    result = await db.execute(select(StoryTimeline).order_by(StoryTimeline.id).limit(100))
    return result.scalars().all()
