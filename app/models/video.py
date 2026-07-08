from typing import Any, Dict, Optional

from sqlalchemy import JSON, Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class EncodingProfile(Base, TimestampMixin):
    __tablename__ = "encoding_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    resolution: Mapped[str] = mapped_column(String(50))
    fps: Mapped[int] = mapped_column(Integer)
    video_codec: Mapped[str] = mapped_column(String(50))
    audio_codec: Mapped[str] = mapped_column(String(50))
    video_bitrate: Mapped[str] = mapped_column(String(50))
    audio_bitrate: Mapped[str] = mapped_column(String(50))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    config: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

class RenderJob(Base, TimestampMixin):
    __tablename__ = "render_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    timeline_id: Mapped[int] = mapped_column(ForeignKey("timelines.id"), index=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("encoding_profiles.id"), index=True)
    status: Mapped[str] = mapped_column(String(50), default="queued", index=True)
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    config: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

class RenderScene(Base, TimestampMixin):
    __tablename__ = "render_scenes"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("render_jobs.id"), index=True)
    scene_id: Mapped[int] = mapped_column(ForeignKey("timeline_scenes.id"), index=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    output_path: Mapped[Optional[str]] = mapped_column(String(1024))
    render_time_ms: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text)

class EncodedVideo(Base, TimestampMixin):
    __tablename__ = "encoded_videos"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("render_jobs.id"), index=True)
    file_path: Mapped[str] = mapped_column(String(1024))
    format: Mapped[str] = mapped_column(String(50))
    size_bytes: Mapped[int] = mapped_column(Integer)
    duration_ms: Mapped[int] = mapped_column(Integer)
    checksum: Mapped[Optional[str]] = mapped_column(String(255))
    metadata_info: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

class RenderReport(Base, TimestampMixin):
    __tablename__ = "render_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("render_jobs.id"), unique=True, index=True)
    total_time_ms: Mapped[int] = mapped_column(Integer, default=0)
    average_fps: Mapped[float] = mapped_column(Float, default=0.0)
    peak_ram_mb: Mapped[float] = mapped_column(Float, default=0.0)
    peak_gpu_mb: Mapped[float] = mapped_column(Float, default=0.0)
    dropped_frames: Mapped[int] = mapped_column(Integer, default=0)
    warnings: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    errors: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

class OutputFile(Base, TimestampMixin):
    __tablename__ = "output_files"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("render_jobs.id"), index=True)
    type: Mapped[str] = mapped_column(String(50))  # e.g., 'master', 'preview', 'scene', 'chapter', 'part'
    file_path: Mapped[str] = mapped_column(String(1024))
    size_bytes: Mapped[int] = mapped_column(Integer)

class RenderStatistic(Base, TimestampMixin):
    __tablename__ = "render_statistics"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("render_jobs.id"), index=True)
    timestamp: Mapped[int] = mapped_column(Integer) # Unix timestamp
    cpu_usage: Mapped[float] = mapped_column(Float, default=0.0)
    gpu_usage: Mapped[float] = mapped_column(Float, default=0.0)
    ram_usage_mb: Mapped[float] = mapped_column(Float, default=0.0)
    current_fps: Mapped[float] = mapped_column(Float, default=0.0)
