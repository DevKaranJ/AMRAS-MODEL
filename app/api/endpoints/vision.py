from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.models.manga import Page
from app.models.vision import CharacterDetected, Panel, SoundEffect, VisionJob
from app.schemas.vision import CharacterDetectedSchema, PageVisionResult, PanelSchema, SoundEffectSchema

router = APIRouter()


class VisionProcessRequest(BaseModel):
    page_id: int


@router.post("/process", status_code=202)
async def process_vision(req: VisionProcessRequest, session: AsyncSession = Depends(get_db_session)) -> Dict[str, Any]:
    """Starts a vision job for a specific page."""
    # Validate that the page exists
    page_stmt = select(Page.id).where(Page.id == req.page_id)
    page_result = await session.execute(page_stmt)
    if page_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail=f"Page {req.page_id} not found")

    stmt = insert(VisionJob).values(page_id=req.page_id, status="queued").returning(VisionJob.id)
    result = await session.execute(stmt)
    job_id = result.scalar_one()
    await session.commit()

    return {"message": "Vision job queued", "page_id": req.page_id, "job_id": job_id}


@router.get("/page/{page_id}", response_model=PageVisionResult)
async def get_page_vision(page_id: int, session: AsyncSession = Depends(get_db_session)) -> PageVisionResult:
    return PageVisionResult(page=page_id, width=1000, height=1500, panels=[])


@router.get("/panels", response_model=List[PanelSchema])
async def list_panels(page_id: int, session: AsyncSession = Depends(get_db_session)) -> List[PanelSchema]:
    stmt = select(Panel).where(Panel.page_id == page_id)
    result = await session.execute(stmt)
    panels = result.scalars().all()
    return [PanelSchema.model_validate(p) for p in panels]


@router.get("/characters", response_model=List[CharacterDetectedSchema])
async def list_characters(
    page_id: int, session: AsyncSession = Depends(get_db_session)
) -> List[CharacterDetectedSchema]:
    stmt = select(CharacterDetected).join(Panel).where(Panel.page_id == page_id)
    result = await session.execute(stmt)
    chars = result.scalars().all()
    return [CharacterDetectedSchema.model_validate(c) for c in chars]


@router.get("/sound-effects", response_model=List[SoundEffectSchema])
async def list_sound_effects(page_id: int, session: AsyncSession = Depends(get_db_session)) -> List[SoundEffectSchema]:
    stmt = select(SoundEffect).join(Panel).where(Panel.page_id == page_id)
    result = await session.execute(stmt)
    sfx = result.scalars().all()
    return [SoundEffectSchema.model_validate(s) for s in sfx]


@router.get("/debug/{page_id}")
async def get_debug_overlay(page_id: int) -> Dict[str, str]:
    return {"overlay_url": f"/static/debug/{page_id}_overlay.png"}
