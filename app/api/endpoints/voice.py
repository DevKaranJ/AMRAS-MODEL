from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException

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


# Dependency to get engine (mocked dict for now)
def get_engine():
    pronunciation_dict = {"Gojo": "Go-Jo", "Luffy": "Loo-Fee"}
    return AudioProductionEngine(pronunciation_dict)


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
async def regenerate_audio(request: AudioRegenerateRequest):
    return {"status": "success", "message": "Regenerated segments", "segments": request.segment_ids}


@router.post("/normalize", response_model=Dict[str, Any])
async def normalize_audio(request: AudioNormalizeRequest):
    return {"status": "success", "message": "Audio normalized", "job_id": request.job_id}


@router.get("", response_model=List[AudioJobResponse])
async def get_audio_jobs():
    return []


@router.get("/status", response_model=Dict[str, Any])
async def get_audio_status(job_id: int):
    return {"job_id": job_id, "status": "completed", "progress": 100.0}


@router.get("/timestamps", response_model=List[TimestampIndexResponse])
async def get_audio_timestamps(job_id: int):
    return []


@router.get("/voices", response_model=List[VoiceProfileResponse])
async def get_voices():
    # Mocking response
    return [
        {
            "id": 1,
            "name": "Default Male",
            "provider": "local",
            "voice_id": "male_01",
            "gender": "Male",
            "language": "en",
            "accent": "US",
            "is_cloned": False,
            "settings": {},
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
        }
    ]
