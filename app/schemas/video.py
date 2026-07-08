from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class EncodingProfileBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    resolution: str = Field(..., max_length=50)
    fps: int = Field(..., gt=0)
    video_codec: str = Field(..., max_length=50)
    audio_codec: str = Field(..., max_length=50)
    video_bitrate: str = Field(..., max_length=50)
    audio_bitrate: str = Field(..., max_length=50)
    is_default: bool = False
    config: Dict[str, Any] = Field(default_factory=dict)

class EncodingProfileCreate(EncodingProfileBase):
    pass

class EncodingProfileResponse(EncodingProfileBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class RenderJobBase(BaseModel):
    project_id: int
    timeline_id: int
    profile_id: int
    status: str = Field(default="queued", max_length=50)
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    error_message: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)

class RenderJobCreate(RenderJobBase):
    pass

class RenderJobResponse(RenderJobBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class RenderSceneBase(BaseModel):
    job_id: int
    scene_id: int
    status: str = Field(default="pending", max_length=50)
    output_path: Optional[str] = Field(None, max_length=1024)
    render_time_ms: int = Field(default=0, ge=0)
    error_message: Optional[str] = None

class RenderSceneCreate(RenderSceneBase):
    pass

class RenderSceneResponse(RenderSceneBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class EncodedVideoBase(BaseModel):
    job_id: int
    file_path: str = Field(..., max_length=1024)
    format: str = Field(..., max_length=50)
    size_bytes: int = Field(..., ge=0)
    duration_ms: int = Field(..., ge=0)
    checksum: Optional[str] = Field(None, max_length=255)
    metadata_info: Dict[str, Any] = Field(default_factory=dict)

class EncodedVideoCreate(EncodedVideoBase):
    pass

class EncodedVideoResponse(EncodedVideoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class RenderReportBase(BaseModel):
    job_id: int
    total_time_ms: int = Field(default=0, ge=0)
    average_fps: float = Field(default=0.0, ge=0.0)
    peak_ram_mb: float = Field(default=0.0, ge=0.0)
    peak_gpu_mb: float = Field(default=0.0, ge=0.0)
    dropped_frames: int = Field(default=0, ge=0)
    warnings: Dict[str, Any] = Field(default_factory=dict)
    errors: Dict[str, Any] = Field(default_factory=dict)

class RenderReportCreate(RenderReportBase):
    pass

class RenderReportResponse(RenderReportBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class OutputFileBase(BaseModel):
    job_id: int
    type: str = Field(..., max_length=50)
    file_path: str = Field(..., max_length=1024)
    size_bytes: int = Field(..., ge=0)

class OutputFileCreate(OutputFileBase):
    pass

class OutputFileResponse(OutputFileBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class RenderStatisticBase(BaseModel):
    job_id: int
    timestamp: int
    cpu_usage: float = Field(default=0.0, ge=0.0, le=100.0)
    gpu_usage: float = Field(default=0.0, ge=0.0, le=100.0)
    ram_usage_mb: float = Field(default=0.0, ge=0.0)
    current_fps: float = Field(default=0.0, ge=0.0)

class RenderStatisticCreate(RenderStatisticBase):
    pass

class RenderStatisticResponse(RenderStatisticBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class RenderStartRequest(BaseModel):
    project_id: int
    timeline_id: int
    profile_id: int
    config: Optional[Dict[str, Any]] = None

class RenderResumeRequest(BaseModel):
    job_id: int

class RenderCancelRequest(BaseModel):
    job_id: int

class RenderStatusResponse(BaseModel):
    job_id: int
    status: str
    progress: float
    message: Optional[str] = None
