from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class PublishingJob(Base, TimestampMixin):
    __tablename__ = "publishing_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    status: Mapped[str] = mapped_column(String(50), default="queued", index=True)
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    config: Mapped[Dict[str, Any]] = mapped_column(MutableDict.as_mutable(JSON), default=dict)


class Thumbnail(Base, TimestampMixin):
    __tablename__ = "thumbnails"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("publishing_jobs.id", ondelete="CASCADE"), index=True)
    scene_id: Mapped[Optional[int]] = mapped_column(ForeignKey("timeline_scenes.id"))
    base_image_path: Mapped[str] = mapped_column(String(1024))
    score: Mapped[float] = mapped_column(Float, default=0.0)
    metadata_info: Mapped[Dict[str, Any]] = mapped_column(MutableDict.as_mutable(JSON), default=dict)

    variants: Mapped[List["ThumbnailVariant"]] = relationship(back_populates="thumbnail", cascade="all, delete-orphan")


class ThumbnailVariant(Base, TimestampMixin):
    __tablename__ = "thumbnail_variants"

    id: Mapped[int] = mapped_column(primary_key=True)
    thumbnail_id: Mapped[int] = mapped_column(ForeignKey("thumbnails.id", ondelete="CASCADE"), index=True)
    variant_name: Mapped[str] = mapped_column(String(50))  # e.g. A, B, C
    file_path: Mapped[str] = mapped_column(String(1024))
    composition_rules: Mapped[Dict[str, Any]] = mapped_column(MutableDict.as_mutable(JSON), default=dict)

    thumbnail: Mapped["Thumbnail"] = relationship(back_populates="variants")


class SEOProfile(Base, TimestampMixin):
    __tablename__ = "seo_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("publishing_jobs.id", ondelete="CASCADE"), index=True)
    language: Mapped[str] = mapped_column(String(10), default="en")
    target_keywords: Mapped[List[str]] = mapped_column(MutableList.as_mutable(JSON), default=list)


class Title(Base, TimestampMixin):
    __tablename__ = "video_titles"

    id: Mapped[int] = mapped_column(primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("seo_profiles.id", ondelete="CASCADE"), index=True)
    text: Mapped[str] = mapped_column(String(100))
    style: Mapped[str] = mapped_column(String(50))
    score: Mapped[float] = mapped_column(Float, default=0.0)


class Description(Base, TimestampMixin):
    __tablename__ = "video_descriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("seo_profiles.id", ondelete="CASCADE"), index=True)
    text: Mapped[str] = mapped_column(Text)
    has_chapters: Mapped[bool] = mapped_column(Boolean, default=True)


class Tag(Base, TimestampMixin):
    __tablename__ = "video_tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("seo_profiles.id", ondelete="CASCADE"), index=True)
    text: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(50))  # e.g. Primary, Secondary, Character
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0)


class Playlist(Base, TimestampMixin):
    __tablename__ = "playlists"

    id: Mapped[int] = mapped_column(primary_key=True)
    manga_id: Mapped[Optional[int]] = mapped_column(ForeignKey("mangas.id"), index=True, unique=True)
    youtube_playlist_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    visibility: Mapped[str] = mapped_column(String(20), default="public")


class Schedule(Base, TimestampMixin):
    __tablename__ = "publishing_schedules"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("publishing_jobs.id", ondelete="CASCADE"), index=True)
    publish_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    visibility: Mapped[str] = mapped_column(String(20), default="private")
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")


class VideoMetadata(Base, TimestampMixin):
    __tablename__ = "video_metadata"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("publishing_jobs.id", ondelete="CASCADE"), unique=True, index=True)
    chapters: Mapped[List[Dict[str, Any]]] = mapped_column(MutableList.as_mutable(JSON), default=list)
    license: Mapped[str] = mapped_column(String(50), default="standard")
    category_id: Mapped[int] = mapped_column(Integer, default=1)
    made_for_kids: Mapped[bool] = mapped_column(Boolean, default=False)


class PublishedVideo(Base, TimestampMixin):
    __tablename__ = "published_videos"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("publishing_jobs.id", ondelete="CASCADE"), index=True)
    youtube_video_id: Mapped[str] = mapped_column(String(50), unique=True)
    url: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(20))  # e.g. processed, active
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AnalyticsProfile(Base, TimestampMixin):
    __tablename__ = "analytics_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("publishing_jobs.id", ondelete="CASCADE"), unique=True)
    expected_ctr: Mapped[float] = mapped_column(Float, default=0.0)
    retention_markers: Mapped[List[Dict[str, Any]]] = mapped_column(MutableList.as_mutable(JSON), default=list)
    ab_testing_metadata: Mapped[Dict[str, Any]] = mapped_column(MutableDict.as_mutable(JSON), default=dict)
