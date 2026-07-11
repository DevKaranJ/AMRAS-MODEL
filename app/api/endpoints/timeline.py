from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.schemas.timeline import (
    TimelineGenerateRequest,
    TimelineRebuildRequest,
)
from modules.timeline.service import TimelineService

router = APIRouter()


@router.post("/generate", response_model=Dict[str, Any], status_code=status.HTTP_202_ACCEPTED)
async def generate_timeline(
    request: TimelineGenerateRequest, db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    service = TimelineService(db)
    result = await service.generate_timeline(request)
    return result


@router.post("/rebuild", response_model=Dict[str, Any], status_code=status.HTTP_202_ACCEPTED)
async def rebuild_timeline(
    request: TimelineRebuildRequest, db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    service = TimelineService(db)
    result = await service.rebuild_timeline(request)
    return result


@router.get("", response_model=Dict[str, Any])
async def get_timeline(project_id: int, db: AsyncSession = Depends(get_db_session)) -> Dict[str, Any]:
    service = TimelineService(db)
    timeline = await service.get_timeline(project_id)
    if not timeline:
        raise HTTPException(status_code=404, detail="Timeline not found")
    return timeline


@router.get("/scene", response_model=List[Dict[str, Any]])
async def get_timeline_scenes(timeline_id: int, db: AsyncSession = Depends(get_db_session)) -> List[Dict[str, Any]]:
    service = TimelineService(db)
    return await service.get_timeline_scenes(timeline_id)


@router.get("/camera", response_model=List[Dict[str, Any]])
async def get_timeline_cameras(scene_id: int, db: AsyncSession = Depends(get_db_session)) -> List[Dict[str, Any]]:
    service = TimelineService(db)
    return await service.get_timeline_cameras(scene_id)


@router.get("/transitions", response_model=List[Dict[str, Any]])
async def get_timeline_transitions(
    timeline_id: int, db: AsyncSession = Depends(get_db_session)
) -> List[Dict[str, Any]]:
    service = TimelineService(db)
    return await service.get_timeline_transitions(timeline_id)


@router.get("/status", response_model=Dict[str, Any])
async def get_timeline_status(project_id: int, db: AsyncSession = Depends(get_db_session)) -> Dict[str, Any]:
    service = TimelineService(db)
    return await service.get_timeline_status(project_id)
