from typing import Optional

from sqlalchemy import JSON, Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class VoiceProfile(Base, TimestampMixin):
    __tablename__ = "voice_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    provider: Mapped[str] = mapped_column(String(100))  # e.g., elevenlabs, openai, local
    voice_id: Mapped[str] = mapped_column(String(255))
    gender: Mapped[Optional[str]] = mapped_column(String(50))  # Male, Female, Neutral
    language: Mapped[Optional[str]] = mapped_column(String(50), default="en")
    accent: Mapped[Optional[str]] = mapped_column(String(50))
    is_cloned: Mapped[bool] = mapped_column(Boolean, default=False)
    settings: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)


class AudioJob(Base, TimestampMixin):
    __tablename__ = "audio_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(
        String(50), index=True, default="queued"
    )  # queued, processing, completed, failed, interrupted
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    current_segment: Mapped[Optional[int]] = mapped_column(Integer)
    total_segments: Mapped[Optional[int]] = mapped_column(Integer)
    error: Mapped[Optional[str]] = mapped_column(Text)
    config: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)

    segments: Mapped[list["AudioSegment"]] = relationship(
        "AudioSegment", back_populates="job", cascade="all, delete-orphan"
    )


class AudioSegment(Base, TimestampMixin):
    __tablename__ = "audio_segments"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("audio_jobs.id", ondelete="CASCADE"), index=True)
    scene_id: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    chapter_id: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    sequence_number: Mapped[int] = mapped_column(Integer, index=True)
    text_content: Mapped[str] = mapped_column(Text)
    voice_profile_id: Mapped[Optional[int]] = mapped_column(ForeignKey("voice_profiles.id"))
    emotion: Mapped[Optional[str]] = mapped_column(String(50))
    speech_rate: Mapped[Optional[str]] = mapped_column(String(50))
    file_path: Mapped[Optional[str]] = mapped_column(String(1024))
    duration: Mapped[Optional[float]] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(50), default="pending")

    job: Mapped["AudioJob"] = relationship("AudioJob", back_populates="segments")


class PronunciationDictionary(Base, TimestampMixin):
    __tablename__ = "pronunciation_dictionary"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), index=True
    )  # Optional, could be global
    original_text: Mapped[str] = mapped_column(String(255), index=True)
    phonetic_spelling: Mapped[str] = mapped_column(String(255))
    is_global: Mapped[bool] = mapped_column(Boolean, default=False)


class TimestampIndex(Base, TimestampMixin):
    __tablename__ = "timestamp_index"

    id: Mapped[int] = mapped_column(primary_key=True)
    segment_id: Mapped[int] = mapped_column(ForeignKey("audio_segments.id", ondelete="CASCADE"), index=True)
    type: Mapped[str] = mapped_column(String(50))  # word, sentence, paragraph, scene, chapter
    text: Mapped[str] = mapped_column(Text)
    start_time: Mapped[float] = mapped_column(Float)
    end_time: Mapped[float] = mapped_column(Float)
    duration: Mapped[float] = mapped_column(Float)
    confidence: Mapped[Optional[float]] = mapped_column(Float)


class AudioVersion(Base, TimestampMixin):
    __tablename__ = "audio_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("audio_jobs.id", ondelete="CASCADE"), index=True)
    version_number: Mapped[int] = mapped_column(Integer)
    file_path: Mapped[str] = mapped_column(String(1024))
    format: Mapped[str] = mapped_column(String(20))  # wav, mp3, etc.
    type: Mapped[str] = mapped_column(String(50))  # master, normalized, stitched
    metadata_info: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)


class AudioQualityReport(Base, TimestampMixin):
    __tablename__ = "audio_quality_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("audio_jobs.id", ondelete="CASCADE"), index=True)
    segment_id: Mapped[Optional[int]] = mapped_column(ForeignKey("audio_segments.id", ondelete="CASCADE"))
    issue_type: Mapped[str] = mapped_column(String(100))  # clipping, missing_speech, etc.
    description: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(50))  # low, medium, high, critical
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
