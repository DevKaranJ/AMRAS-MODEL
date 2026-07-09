from typing import Any, List
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session

logger = logging.getLogger(__name__)
from app.models.subtitles import (
    CaptionStyle,
    SubtitleJob,
    SubtitleLanguage,
    SubtitleSegment,
    TranslationJob,
)
from app.schemas.subtitles import (
    CaptionStyleResponse,
    SubtitleGenerateRequest,
    SubtitleJobResponse,
    SubtitleRegenerateRequest,
    SubtitleSegmentResponse,
    SubtitleTranslateRequest,
    TranslationJobResponse,
)
from modules.subtitles.engine import SubtitleEngine

router = APIRouter()


@router.post("/generate", response_model=SubtitleJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_subtitles(
    request: SubtitleGenerateRequest,
    db: AsyncSession = Depends(get_db_session),
) -> Any:
    """
    Queue a job to generate subtitles for a timeline.
    """
    try:
        # Resolve Language ID
        lang_res = await db.execute(select(SubtitleLanguage).where(SubtitleLanguage.code == request.language_code))
        lang = lang_res.scalar_one_or_none()
        if not lang:
            lang = SubtitleLanguage(code=request.language_code, name=request.language_code.upper())
            db.add(lang)
            try:
                await db.flush()
            except IntegrityError:
                await db.rollback()
                lang_res = await db.execute(select(SubtitleLanguage).where(SubtitleLanguage.code == request.language_code))
                lang = lang_res.scalar_one_or_none()
                if not lang:
                    raise

        engine = SubtitleEngine(db_session=db)
        job = await engine.create_subtitle_job(
            project_id=request.project_id,
            timeline_id=request.timeline_id,
            language_id=lang.id,
            settings=request.settings or {},
        )

        # In a real app this would be dispatched to a background worker.
        # For testing purposes, we'll return the queued job.

        return job
    except Exception as e:
        logger.exception("Failed to create subtitle generation job")
        raise HTTPException(status_code=500, detail="Failed to create subtitle job") from e


@router.post("/translate", response_model=TranslationJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def translate_subtitles(
    request: SubtitleTranslateRequest,
    db: AsyncSession = Depends(get_db_session),
) -> Any:
    """
    Queue a job to translate an existing subtitle job into another language.
    """
    try:
        # Resolve target Language ID
        lang_res = await db.execute(
            select(SubtitleLanguage).where(SubtitleLanguage.code == request.target_language_code)
        )
        target_lang = lang_res.scalar_one_or_none()
        if not target_lang:
            target_lang = SubtitleLanguage(code=request.target_language_code, name=request.target_language_code.upper())
            db.add(target_lang)
            try:
                await db.flush()
            except IntegrityError:
                await db.rollback()
                lang_res = await db.execute(
                    select(SubtitleLanguage).where(SubtitleLanguage.code == request.target_language_code)
                )
                target_lang = lang_res.scalar_one_or_none()
                if not target_lang:
                    raise

        # Get source job language
        src_job_res = await db.execute(select(SubtitleJob).where(SubtitleJob.id == request.subtitle_job_id))
        src_job = src_job_res.scalar_one_or_none()
        if not src_job:
            raise HTTPException(status_code=404, detail="Source Subtitle Job not found")

        job = TranslationJob(
            subtitle_job_id=request.subtitle_job_id,
            source_language_id=src_job.language_id,
            target_language_id=target_lang.id,
            localization_profile_id=request.localization_profile_id,
            status="pending",
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)

        return job
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to create translation job")
        raise HTTPException(status_code=500, detail="Failed to translate subtitles") from e


@router.post("/regenerate", response_model=SubtitleJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def regenerate_subtitles(
    request: SubtitleRegenerateRequest,
    db: AsyncSession = Depends(get_db_session),
) -> Any:
    """
    Queue a job to regenerate specific segments or the entire subtitle track.
    """
    # Stub for future implementation
    src_job_res = await db.execute(select(SubtitleJob).where(SubtitleJob.id == request.subtitle_job_id))
    src_job = src_job_res.scalar_one_or_none()
    if not src_job:
        raise HTTPException(status_code=404, detail="Subtitle Job not found")

    src_job.status = "regenerating"
    await db.commit()
    return src_job


@router.get("/", response_model=List[SubtitleSegmentResponse])
async def list_subtitles(
    job_id: int,
    db: AsyncSession = Depends(get_db_session),
) -> Any:
    """List subtitle segments for a specific job."""
    result = await db.execute(
        select(SubtitleSegment)
        .where(SubtitleSegment.subtitle_job_id == job_id)
        .order_by(SubtitleSegment.sequence_number)
    )
    return result.scalars().all()


@router.get("/status", response_model=SubtitleJobResponse)
async def get_subtitle_job_status(
    job_id: int,
    db: AsyncSession = Depends(get_db_session),
) -> Any:
    """Get the status of a subtitle job."""
    result = await db.execute(select(SubtitleJob).where(SubtitleJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Subtitle Job not found")
    return job


@router.get("/translations", response_model=List[TranslationJobResponse])
async def list_translations(
    job_id: int,
    db: AsyncSession = Depends(get_db_session),
) -> Any:
    """List all translation jobs tied to a root subtitle job."""
    result = await db.execute(select(TranslationJob).where(TranslationJob.subtitle_job_id == job_id))
    return result.scalars().all()


@router.get("/caption/styles", response_model=List[CaptionStyleResponse])
async def list_caption_styles(
    db: AsyncSession = Depends(get_db_session),
) -> Any:
    """List available caption styles."""
    result = await db.execute(select(CaptionStyle).limit(100))
    return result.scalars().all()
