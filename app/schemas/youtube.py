from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ThumbnailVariantBase(BaseModel):
    variant_name: str
    file_path: str
    composition_rules: Dict[str, Any] = Field(default_factory=dict)


class ThumbnailVariantCreate(ThumbnailVariantBase):
    thumbnail_id: int


class ThumbnailVariantResponse(ThumbnailVariantBase):
    id: int
    thumbnail_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ThumbnailBase(BaseModel):
    scene_id: Optional[int] = None
    base_image_path: str
    score: float = 0.0
    metadata_info: Dict[str, Any] = Field(default_factory=dict)


class ThumbnailCreate(ThumbnailBase):
    job_id: int


class ThumbnailResponse(ThumbnailBase):
    id: int
    job_id: int
    variants: List[ThumbnailVariantResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TitleBase(BaseModel):
    text: str = Field(..., max_length=100)
    style: str
    score: float = 0.0


class TitleCreate(TitleBase):
    profile_id: int


class TitleResponse(TitleBase):
    id: int
    profile_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DescriptionBase(BaseModel):
    text: str
    has_chapters: bool = True


class DescriptionCreate(DescriptionBase):
    profile_id: int


class DescriptionResponse(DescriptionBase):
    id: int
    profile_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TagBase(BaseModel):
    text: str = Field(..., max_length=100)
    category: str
    relevance_score: float = 0.0


class TagCreate(TagBase):
    profile_id: int


class TagResponse(TagBase):
    id: int
    profile_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SEOProfileBase(BaseModel):
    language: str = "en"
    target_keywords: List[str] = Field(default_factory=list)


class SEOProfileCreate(SEOProfileBase):
    job_id: int


class SEOProfileResponse(SEOProfileBase):
    id: int
    job_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PlaylistBase(BaseModel):
    manga_id: Optional[int] = None
    youtube_playlist_id: Optional[str] = None
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    visibility: str = "public"


class PlaylistCreate(PlaylistBase):
    pass


class PlaylistResponse(PlaylistBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ScheduleBase(BaseModel):
    publish_at: Optional[datetime] = None
    visibility: str = "private"
    timezone: str = "UTC"


class ScheduleCreate(ScheduleBase):
    job_id: int


class ScheduleResponse(ScheduleBase):
    id: int
    job_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VideoMetadataBase(BaseModel):
    chapters: List[Dict[str, Any]] = Field(default_factory=list)
    license: str = "standard"
    category_id: int = 1
    made_for_kids: bool = False


class VideoMetadataCreate(VideoMetadataBase):
    job_id: int


class VideoMetadataResponse(VideoMetadataBase):
    id: int
    job_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PublishedVideoBase(BaseModel):
    youtube_video_id: str
    url: str
    status: str
    published_at: datetime


class PublishedVideoCreate(PublishedVideoBase):
    job_id: int


class PublishedVideoResponse(PublishedVideoBase):
    id: int
    job_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnalyticsProfileBase(BaseModel):
    expected_ctr: float = 0.0
    retention_markers: List[Dict[str, Any]] = Field(default_factory=list)
    ab_testing_metadata: Dict[str, Any] = Field(default_factory=dict)


class AnalyticsProfileCreate(AnalyticsProfileBase):
    job_id: int


class AnalyticsProfileResponse(AnalyticsProfileBase):
    id: int
    job_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PublishingJobBase(BaseModel):
    status: str = "queued"
    progress: float = 0.0
    error_message: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)


class PublishingJobCreate(PublishingJobBase):
    project_id: int


class PublishingJobResponse(PublishingJobBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# API Endpoint Request/Response Schemas


class GenerateThumbnailRequest(BaseModel):
    project_id: int
    number_of_variants: int = 5
    style: str = "default"


class GenerateSEORequest(BaseModel):
    project_id: int
    language: str = "en"
    title_count: int = 5


class UploadPackageRequest(BaseModel):
    job_id: int


class SchedulePackageRequest(BaseModel):
    job_id: int
    publish_at: datetime
    visibility: str = "public"
    timezone: str = "UTC"
