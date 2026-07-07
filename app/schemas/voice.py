from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# Base schemas
class VoiceProfileBase(BaseModel):
    name: str
    provider: str
    voice_id: str
    gender: Optional[str] = None
    language: Optional[str] = "en"
    accent: Optional[str] = None
    is_cloned: bool = False
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict)


class VoiceProfileCreate(VoiceProfileBase):
    pass


class VoiceProfileUpdate(BaseModel):
    name: Optional[str] = None
    provider: Optional[str] = None
    voice_id: Optional[str] = None
    gender: Optional[str] = None
    language: Optional[str] = None
    accent: Optional[str] = None
    is_cloned: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None


class VoiceProfileResponse(VoiceProfileBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---
class PronunciationDictionaryBase(BaseModel):
    project_id: Optional[int] = None
    original_text: str
    phonetic_spelling: str
    is_global: bool = False


class PronunciationDictionaryCreate(PronunciationDictionaryBase):
    pass


class PronunciationDictionaryResponse(PronunciationDictionaryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---
class AudioSegmentBase(BaseModel):
    scene_id: Optional[str] = None
    chapter_id: Optional[str] = None
    sequence_number: int
    text_content: str
    voice_profile_id: Optional[int] = None
    emotion: Optional[str] = None
    speech_rate: Optional[str] = None
    file_path: Optional[str] = None
    duration: Optional[float] = None
    status: str = "pending"


class AudioSegmentCreate(AudioSegmentBase):
    job_id: int


class AudioSegmentResponse(AudioSegmentBase):
    id: int
    job_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---
class TimestampIndexBase(BaseModel):
    segment_id: int
    type: str  # word, sentence, paragraph, scene, chapter
    text: str
    start_time: float
    end_time: float
    duration: float
    confidence: Optional[float] = None


class TimestampIndexCreate(TimestampIndexBase):
    pass


class TimestampIndexResponse(TimestampIndexBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---
class AudioVersionBase(BaseModel):
    job_id: int
    version_number: int
    file_path: str
    format: str
    type: str
    metadata_info: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AudioVersionCreate(AudioVersionBase):
    pass


class AudioVersionResponse(AudioVersionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---
class AudioQualityReportBase(BaseModel):
    job_id: int
    segment_id: Optional[int] = None
    issue_type: str
    description: str
    severity: str
    resolved: bool = False


class AudioQualityReportCreate(AudioQualityReportBase):
    pass


class AudioQualityReportResponse(AudioQualityReportBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---
class AudioJobBase(BaseModel):
    project_id: int
    status: str = "queued"
    progress: float = 0.0
    current_segment: Optional[int] = None
    total_segments: Optional[int] = None
    error: Optional[str] = None
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AudioJobCreate(AudioJobBase):
    pass


class AudioJobUpdate(BaseModel):
    status: Optional[str] = None
    progress: Optional[float] = None
    current_segment: Optional[int] = None
    error: Optional[str] = None


class AudioJobResponse(AudioJobBase):
    id: int
    segments: List[AudioSegmentResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Request schemas for APIs
class NarrationSegmentInput(BaseModel):
    text: str
    emotion: Optional[str] = None
    character_name: Optional[str] = None
    scene_id: Optional[str] = None
    chapter_id: Optional[str] = None


class AudioGenerateRequest(BaseModel):
    project_id: int
    segments: List[NarrationSegmentInput]
    voice_profile_id: int
    style_config: Optional[Dict[str, Any]] = None


class AudioRegenerateRequest(BaseModel):
    segment_ids: List[int]
    voice_profile_id: Optional[int] = None
    emotion: Optional[str] = None


class AudioNormalizeRequest(BaseModel):
    job_id: int
    target_lufs: Optional[float] = -14.0
