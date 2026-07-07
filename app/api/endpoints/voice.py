from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.schemas.voice import (
    AudioGenerateRequest,
    AudioJobResponse,
    AudioNormalizeRequest,
    AudioRegenerateRequest,
    TimestampIndexResponse,
    VoiceProfileResponse,
)
from modules.voice.engine import AudioProductionEngine

router = APIRouter()


# Dependency to get engine with database session
def get_engine(db: AsyncSession = Depends(get_db_session)):
    return AudioProductionEngine(db)


@router.post("/generate", response_model=Dict[str, Any])
async def generate_audio(request: AudioGenerateRequest, engine: AudioProductionEngine = Depends(get_engine)):
    try:
        segments_dict = [s.model_dump() for s in request.segments]
        master_path = await engine.process_segments(
            project_id=request.project_id,
            segments=segments_dict,
            voice_profile_id=request.voice_profile_id,
            style_config=request.style_config,
        )
        return {"status": "success", "master_audio_path": master_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/regenerate", response_model=Dict[str, Any])
async def regenerate_audio(request: AudioRegenerateRequest, db: AsyncSession = Depends(get_db_session)):
    from sqlalchemy import select
    from app.models.voice import AudioSegment

    # Fetch segments to regenerate
    stmt = select(AudioSegment).where(AudioSegment.id.in_(request.segment_ids))
    result = await db.execute(stmt)
    segments = result.scalars().all()

    if not segments:
        raise HTTPException(status_code=404, detail="No segments found with provided IDs")

    # Update segment status to pending for regeneration
    for seg in segments:
        seg.status = "pending"
        if request.voice_profile_id:
            seg.voice_profile_id = request.voice_profile_id
        if request.emotion:
            seg.emotion = request.emotion

    await db.commit()

    return {"status": "success", "message": "Segments queued for regeneration", "segments": request.segment_ids}


@router.post("/normalize", response_model=Dict[str, Any])
async def normalize_audio(request: AudioNormalizeRequest, db: AsyncSession = Depends(get_db_session)):
    from sqlalchemy import select
    from app.models.voice import AudioJob, AudioVersion
    from modules.voice.agents import AudioCleanupAgent
    import os

    # Fetch the job
    stmt = select(AudioJob).where(AudioJob.id == request.job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail=f"Job {request.job_id} not found")

    # Find the master audio version
    version_stmt = select(AudioVersion).where(
        AudioVersion.job_id == request.job_id,
        AudioVersion.type == "master"
    ).order_by(AudioVersion.version_number.desc())
    version_result = await db.execute(version_stmt)
    master_version = version_result.scalar_one_or_none()

    if not master_version:
        raise HTTPException(status_code=404, detail="No master audio found for this job")

    # Normalize the audio
    cleanup_agent = AudioCleanupAgent()
    input_path = master_version.file_path
    normalized_path = input_path.replace(".wav", "_normalized.wav")

    success = cleanup_agent.normalize_audio(input_path, normalized_path, request.target_lufs)
    if not success:
        raise HTTPException(status_code=500, detail="Normalization failed")

    # Create new version entry for normalized audio
    new_version = AudioVersion(
        job_id=request.job_id,
        version_number=master_version.version_number + 1,
        file_path=normalized_path,
        format="wav",
        type="normalized",
        metadata_info={"target_lufs": request.target_lufs}
    )
    db.add(new_version)
    await db.commit()

    return {"status": "success", "message": "Audio normalized", "job_id": request.job_id, "file_path": normalized_path}


@router.get("", response_model=List[AudioJobResponse])
async def get_audio_jobs(db: AsyncSession = Depends(get_db_session)):
    from sqlalchemy import select
    from app.models.voice import AudioJob

    stmt = select(AudioJob).order_by(AudioJob.created_at.desc())
    result = await db.execute(stmt)
    jobs = result.scalars().all()

    return jobs


@router.get("/status", response_model=Dict[str, Any])
async def get_audio_status(job_id: int, db: AsyncSession = Depends(get_db_session)):
    from sqlalchemy import select
    from app.models.voice import AudioJob

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
        "error": job.error
    }


@router.get("/timestamps", response_model=List[TimestampIndexResponse])
async def get_audio_timestamps(job_id: int, db: AsyncSession = Depends(get_db_session)):
    from sqlalchemy import select
    from app.models.voice import TimestampIndex, AudioSegment

    # Get all segments for this job
    seg_stmt = select(AudioSegment).where(AudioSegment.job_id == job_id)
    seg_result = await db.execute(seg_stmt)
    segments = seg_result.scalars().all()

    if not segments:
        return []

    segment_ids = [seg.id for seg in segments]

    # Get timestamps for these segments
    ts_stmt = select(TimestampIndex).where(TimestampIndex.segment_id.in_(segment_ids))
    ts_result = await db.execute(ts_stmt)
    timestamps = ts_result.scalars().all()

    return timestamps


@router.get("/voices", response_model=List[VoiceProfileResponse])
async def get_voices(db: AsyncSession = Depends(get_db_session)):
    from sqlalchemy import select
    from app.models.voice import VoiceProfile

    stmt = select(VoiceProfile).order_by(VoiceProfile.name)
    result = await db.execute(stmt)
    voices = result.scalars().all()

    return voices
