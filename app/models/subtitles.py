from typing import Any, Dict, List, Optional

from sqlalchemy import JSON, Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.core import Project
from app.models.timeline import Timeline


class SubtitleLanguage(Base):
    __tablename__ = "subtitle_languages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_supported: Mapped[bool] = mapped_column(Boolean, default=True)
    settings: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

    localization_profiles: Mapped[List["LocalizationProfile"]] = relationship(
        "LocalizationProfile", back_populates="language"
    )
    subtitle_jobs: Mapped[List["SubtitleJob"]] = relationship("SubtitleJob", back_populates="language")


class LocalizationProfile(Base):
    __tablename__ = "localization_profiles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    language_id: Mapped[int] = mapped_column(ForeignKey("subtitle_languages.id"), nullable=False)
    honorifics_strategy: Mapped[str] = mapped_column(String(50), default="keep")
    measurements_strategy: Mapped[str] = mapped_column(String(50), default="metric")
    currency_strategy: Mapped[str] = mapped_column(String(50), default="local")
    rules: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

    language: Mapped["SubtitleLanguage"] = relationship("SubtitleLanguage", back_populates="localization_profiles")
    translation_jobs: Mapped[List["TranslationJob"]] = relationship(
        "TranslationJob", back_populates="localization_profile"
    )


class CaptionStyle(Base):
    __tablename__ = "caption_styles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    font_family: Mapped[str] = mapped_column(String(100), default="Arial")
    font_size: Mapped[int] = mapped_column(Integer, default=42)
    color: Mapped[str] = mapped_column(String(20), default="#FFFFFF")
    outline_color: Mapped[str] = mapped_column(String(20), default="#000000")
    outline_width: Mapped[int] = mapped_column(Integer, default=2)
    shadow_color: Mapped[str] = mapped_column(String(20), default="#00000080")
    shadow_offset_x: Mapped[int] = mapped_column(Integer, default=2)
    shadow_offset_y: Mapped[int] = mapped_column(Integer, default=2)
    alignment: Mapped[str] = mapped_column(String(50), default="bottom-center")
    margin_bottom: Mapped[int] = mapped_column(Integer, default=20)
    safe_area_padding: Mapped[int] = mapped_column(Integer, default=10)


class SubtitleJob(Base):
    __tablename__ = "subtitle_jobs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    timeline_id: Mapped[int] = mapped_column(ForeignKey("timelines.id", ondelete="CASCADE"), nullable=False)
    language_id: Mapped[int] = mapped_column(ForeignKey("subtitle_languages.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    settings: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

    project: Mapped["Project"] = relationship("Project")
    timeline: Mapped["Timeline"] = relationship("Timeline")
    language: Mapped["SubtitleLanguage"] = relationship("SubtitleLanguage", back_populates="subtitle_jobs")
    segments: Mapped[List["SubtitleSegment"]] = relationship(
        "SubtitleSegment", back_populates="subtitle_job", cascade="all, delete-orphan"
    )
    versions: Mapped[List["SubtitleVersion"]] = relationship(
        "SubtitleVersion", back_populates="subtitle_job", cascade="all, delete-orphan"
    )
    translation_jobs: Mapped[List["TranslationJob"]] = relationship(
        "TranslationJob", back_populates="subtitle_job", cascade="all, delete-orphan"
    )


class SubtitleSegment(Base):
    __tablename__ = "subtitle_segments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subtitle_job_id: Mapped[int] = mapped_column(ForeignKey("subtitle_jobs.id", ondelete="CASCADE"), nullable=False)
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    end_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    speaker: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    reading_speed: Mapped[float] = mapped_column(Float, default=0.0)
    characters_count: Mapped[int] = mapped_column(Integer, default=0)

    subtitle_job: Mapped["SubtitleJob"] = relationship("SubtitleJob", back_populates="segments")


class TranslationJob(Base):
    __tablename__ = "translation_jobs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subtitle_job_id: Mapped[int] = mapped_column(ForeignKey("subtitle_jobs.id", ondelete="CASCADE"), nullable=False)
    source_language_id: Mapped[int] = mapped_column(ForeignKey("subtitle_languages.id"), nullable=False)
    target_language_id: Mapped[int] = mapped_column(ForeignKey("subtitle_languages.id"), nullable=False)
    localization_profile_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("localization_profiles.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(50), default="pending")
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    progress: Mapped[float] = mapped_column(Float, default=0.0)

    subtitle_job: Mapped["SubtitleJob"] = relationship("SubtitleJob", back_populates="translation_jobs")
    source_language: Mapped["SubtitleLanguage"] = relationship("SubtitleLanguage", foreign_keys=[source_language_id])
    target_language: Mapped["SubtitleLanguage"] = relationship("SubtitleLanguage", foreign_keys=[target_language_id])
    localization_profile: Mapped[Optional["LocalizationProfile"]] = relationship(
        "LocalizationProfile", back_populates="translation_jobs"
    )


class SubtitleVersion(Base):
    __tablename__ = "subtitle_versions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subtitle_job_id: Mapped[int] = mapped_column(ForeignKey("subtitle_jobs.id", ondelete="CASCADE"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, default=1)
    format_type: Mapped[str] = mapped_column(String(20), nullable=False)  # srt, vtt, ass
    content: Mapped[str] = mapped_column(Text, nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    subtitle_job: Mapped["SubtitleJob"] = relationship("SubtitleJob", back_populates="versions")
