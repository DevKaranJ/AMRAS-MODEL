from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class SubtitleLanguageBase(BaseModel):
    code: str = Field(..., max_length=10, description="Language code e.g. en, ja, es")
    name: str = Field(..., max_length=100, description="Human readable name e.g. English, Japanese")
    is_supported: bool = Field(default=True)
    settings: Dict[str, Any] = Field(default_factory=dict)


class SubtitleLanguageCreate(SubtitleLanguageBase):
    pass


class SubtitleLanguageResponse(SubtitleLanguageBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class LocalizationProfileBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    language_id: int
    honorifics_strategy: str = Field(default="keep", max_length=50)
    measurements_strategy: str = Field(default="metric", max_length=50)
    currency_strategy: str = Field(default="local", max_length=50)
    rules: Dict[str, Any] = Field(default_factory=dict)


class LocalizationProfileCreate(LocalizationProfileBase):
    pass


class LocalizationProfileResponse(LocalizationProfileBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CaptionStyleBase(BaseModel):
    name: str = Field(..., max_length=255)
    font_family: str = Field(default="Arial", max_length=100)
    font_size: int = Field(default=42, ge=1)
    color: str = Field(default="#FFFFFF", max_length=20)
    outline_color: str = Field(default="#000000", max_length=20)
    outline_width: int = Field(default=2, ge=0)
    shadow_color: str = Field(default="#00000080", max_length=20)
    shadow_offset_x: int = Field(default=2)
    shadow_offset_y: int = Field(default=2)
    alignment: str = Field(default="bottom-center", max_length=50)
    margin_bottom: int = Field(default=20, ge=0)
    safe_area_padding: int = Field(default=10, ge=0)


class CaptionStyleCreate(CaptionStyleBase):
    pass


class CaptionStyleResponse(CaptionStyleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class SubtitleJobBase(BaseModel):
    project_id: int
    timeline_id: int
    status: str = Field(default="pending", max_length=50)
    language_id: int
    settings: Dict[str, Any] = Field(default_factory=dict)


class SubtitleJobCreate(SubtitleJobBase):
    pass


class SubtitleJobResponse(SubtitleJobBase):
    id: int
    error_message: Optional[str] = None
    progress: float = Field(default=0.0)
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TranslationJobBase(BaseModel):
    subtitle_job_id: int
    source_language_id: int
    target_language_id: int
    localization_profile_id: Optional[int] = None
    status: str = Field(default="pending", max_length=50)


class TranslationJobCreate(TranslationJobBase):
    pass


class TranslationJobResponse(TranslationJobBase):
    id: int
    error_message: Optional[str] = None
    progress: float = Field(default=0.0)
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class SubtitleSegmentBase(BaseModel):
    subtitle_job_id: int
    sequence_number: int = Field(..., ge=1)
    start_time_ms: int = Field(..., ge=0)
    end_time_ms: int = Field(..., ge=0)
    duration_ms: int = Field(..., ge=0)
    text: str
    speaker: Optional[str] = Field(None, max_length=255)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    reading_speed: float = Field(default=0.0, ge=0.0)
    characters_count: int = Field(default=0, ge=0)


class SubtitleSegmentCreate(SubtitleSegmentBase):
    pass


class SubtitleSegmentResponse(SubtitleSegmentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class SubtitleVersionBase(BaseModel):
    subtitle_job_id: int
    version_number: int = Field(default=1, ge=1)
    format_type: str = Field(..., max_length=20)  # srt, vtt, ass
    content: str
    file_path: Optional[str] = Field(None, max_length=1024)


class SubtitleVersionCreate(SubtitleVersionBase):
    pass


class SubtitleVersionResponse(SubtitleVersionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class SubtitleGenerateRequest(BaseModel):
    project_id: int
    timeline_id: int
    language_code: str = Field(default="en")
    settings: Optional[Dict[str, Any]] = None


class SubtitleTranslateRequest(BaseModel):
    subtitle_job_id: int
    target_language_code: str
    localization_profile_id: Optional[int] = None


class SubtitleRegenerateRequest(BaseModel):
    subtitle_job_id: int
    segment_ids: Optional[List[int]] = None
