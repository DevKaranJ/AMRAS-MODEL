from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.logger import get_logger
from app.database.session import get_db_session
from app.models.voice import AudioJob, AudioSegment, AudioVersion, TimestampIndex, VoiceProfile
from app.schemas.voice import (
    AudioGenerateRequest,
    AudioJobResponse,
    AudioNormalizeRequest,
    AudioRegenerateRequest,
    TimestampIndexResponse,
    VoiceProfileResponse,
)
from modules.voice.engine import AudioProductionEngine

logger = get_logger("amras.api.voice")
router = APIRouter()


# Dependency to get engine with database session
def get_engine(db: AsyncSession = Depends(get_db_session)) -> AudioProductionEngine:
    return AudioProductionEngine(db)


@router.post("/generate", response_model=Dict[str, Any])
async def generate_audio(
    request: AudioGenerateRequest,
    engine: AudioProductionEngine = Depends(get_engine),
) -> Any:
    try:
        segments_dict = [s.model_dump() for s in request.segments]
        master_path = await engine.process_segments(
            project_id=request.project_id,
            segments=segments_dict,
            voice_profile_id=request.voice_profile_id,
            style_config=request.style_config,
        )
        return {"status": "success", "master_audio_path": master_path}
    except Exception as exc:
        logger.exception("audio_generation_failed", error=str(exc))
        raise HTTPException(status_code=500, detail="Audio generation failed. Please retry.") from exc


@router.post("/regenerate", response_model=Dict[str, Any])
async def regenerate_audio(
    request: AudioRegenerateRequest,
    db: AsyncSession = Depends(get_db_session),
) -> Any:
    stmt = select(AudioSegment).where(AudioSegment.id.in_(request.segment_ids))
    result = await db.execute(stmt)
    segments = result.scalars().all()

    if not segments:
        raise HTTPException(status_code=404, detail="No segments found with provided IDs")

    # Validate all requested IDs exist
    found_ids = {seg.id for seg in segments}
    requested_ids = set(request.segment_ids)
    missing_ids = requested_ids - found_ids
    if missing_ids:
        raise HTTPException(
            status_code=404,
            detail=f"Segment IDs not found: {sorted(missing_ids)}"
        )

    for seg in segments:
        seg.status = "pending"
        if request.voice_profile_id:
            seg.voice_profile_id = request.voice_profile_id
        if request.emotion:
            seg.emotion = request.emotion

    await db.commit()
    return {"status": "success", "message": "Segments queued for regeneration", "segments": list(found_ids)}


@router.post("/normalize", response_model=Dict[str, Any])
async def normalize_audio(
    request: AudioNormalizeRequest,
    db: AsyncSession = Depends(get_db_session),
) -> Any:
    from modules.voice.agents import AudioCleanupAgent

    stmt = select(AudioJob).where(AudioJob.id == request.job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {request.job_id} not found")

    version_stmt = (
        select(AudioVersion)
        .where(AudioVersion.job_id == request.job_id, AudioVersion.type == "master")
        .order_by(AudioVersion.version_number.desc())
        .limit(1)
    )
    version_result = await db.execute(version_stmt)
    master_version = version_result.scalar_one_or_none()
    if not master_version:
        raise HTTPException(status_code=404, detail="No master audio found for this job")

    cleanup_agent = AudioCleanupAgent()
    input_path = master_version.file_path
    normalized_path = input_path.replace(".wav", "_normalized.wav")

    try:
        success = cleanup_agent.normalize_audio(input_path, normalized_path, request.target_lufs)
    except Exception as exc:
        logger.exception("audio_normalization_failed", job_id=request.job_id, error=str(exc))
        raise HTTPException(status_code=500, detail="Audio normalization failed. Please retry.") from exc

    if not success:
        raise HTTPException(status_code=500, detail="Audio normalization failed. Please retry.")

    new_version = AudioVersion(
        job_id=request.job_id,
        version_number=master_version.version_number + 1,
        file_path=normalized_path,
        format="wav",
        type="normalized",
        metadata_info={"target_lufs": request.target_lufs},
    )
    db.add(new_version)
    await db.commit()

    return {
        "status": "success",
        "message": "Audio normalized",
        "job_id": request.job_id,
        "file_path": normalized_path,
    }


@router.get("", response_model=List[AudioJobResponse])
async def get_audio_jobs(db: AsyncSession = Depends(get_db_session)) -> Any:
    stmt = select(AudioJob).options(selectinload(AudioJob.segments)).order_by(AudioJob.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/status", response_model=Dict[str, Any])
async def get_audio_status(job_id: int, db: AsyncSession = Depends(get_db_session)) -> Any:
    stmt = select(AudioJob).where(AudioJob.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return {
        "job_id": job.id,
        "status": job.status,
        "progress": job.progress,
        "current_segment": job.current_segment,
        "total_segments": job.total_segments,
        "error": job.error,
    }


@router.get("/timestamps", response_model=List[TimestampIndexResponse])
async def get_audio_timestamps(job_id: int, db: AsyncSession = Depends(get_db_session)) -> Any:
    seg_stmt = select(AudioSegment).where(AudioSegment.job_id == job_id)
    seg_result = await db.execute(seg_stmt)
    segments = seg_result.scalars().all()
    if not segments:
        return []

    segment_ids = [seg.id for seg in segments]
    ts_stmt = select(TimestampIndex).where(TimestampIndex.segment_id.in_(segment_ids))
    ts_result = await db.execute(ts_stmt)
    return ts_result.scalars().all()


@router.get("/voices", response_model=List[VoiceProfileResponse])
async def get_voices(db: AsyncSession = Depends(get_db_session)) -> Any:
    stmt = select(VoiceProfile).order_by(VoiceProfile.name)
    result = await db.execute(stmt)
    return result.scalars().all()
