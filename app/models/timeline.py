from typing import Any, Dict, Optional

from sqlalchemy import JSON, Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class AnimationProfile(Base, TimestampMixin):
    __tablename__ = "animation_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    config: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

class Timeline(Base, TimestampMixin):
    __tablename__ = "timelines"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    status: Mapped[str] = mapped_column(String(50), default="draft", index=True)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    settings: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

class Transition(Base, TimestampMixin):
    __tablename__ = "transitions"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(100))
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    config: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

class SceneMetadata(Base, TimestampMixin):
    __tablename__ = "scene_metadata"

    id: Mapped[int] = mapped_column(primary_key=True)
    emotion: Mapped[Optional[str]] = mapped_column(String(100))
    intensity: Mapped[float] = mapped_column(Float, default=0.0)
    visual_complexity: Mapped[float] = mapped_column(Float, default=0.0)
    dialogue_density: Mapped[float] = mapped_column(Float, default=0.0)
    is_battle: Mapped[bool] = mapped_column(Boolean, default=False)
    is_flashback: Mapped[bool] = mapped_column(Boolean, default=False)
    config: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

class TimelineScene(Base, TimestampMixin):
    __tablename__ = "timeline_scenes"

    id: Mapped[int] = mapped_column(primary_key=True)
    timeline_id: Mapped[int] = mapped_column(ForeignKey("timelines.id"), index=True)
    sequence_number: Mapped[int] = mapped_column(Integer)
    start_time_ms: Mapped[int] = mapped_column(Integer)
    end_time_ms: Mapped[int] = mapped_column(Integer)
    duration_ms: Mapped[int] = mapped_column(Integer)
    page_id: Mapped[Optional[int]] = mapped_column(ForeignKey("pages.id"), index=True)
    transition_id: Mapped[Optional[int]] = mapped_column(ForeignKey("transitions.id"))
    metadata_id: Mapped[Optional[int]] = mapped_column(ForeignKey("scene_metadata.id"))

class CameraPath(Base, TimestampMixin):
    __tablename__ = "camera_paths"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(100))
    start_zoom: Mapped[float] = mapped_column(Float, default=1.0)
    end_zoom: Mapped[float] = mapped_column(Float, default=1.0)
    start_x: Mapped[float] = mapped_column(Float, default=0.0)
    start_y: Mapped[float] = mapped_column(Float, default=0.0)
    end_x: Mapped[float] = mapped_column(Float, default=0.0)
    end_y: Mapped[float] = mapped_column(Float, default=0.0)
    duration_ms: Mapped[int] = mapped_column(Integer)
    config: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

class TimelinePanel(Base, TimestampMixin):
    __tablename__ = "timeline_panels"

    id: Mapped[int] = mapped_column(primary_key=True)
    scene_id: Mapped[int] = mapped_column(ForeignKey("timeline_scenes.id"), index=True)
    panel_id: Mapped[Optional[int]] = mapped_column(ForeignKey("panels.id"), index=True)
    sequence_number: Mapped[int] = mapped_column(Integer)
    start_time_ms: Mapped[int] = mapped_column(Integer)
    end_time_ms: Mapped[int] = mapped_column(Integer)
    duration_ms: Mapped[int] = mapped_column(Integer)
    importance_score: Mapped[float] = mapped_column(Float, default=0.0)
    camera_path_id: Mapped[Optional[int]] = mapped_column(ForeignKey("camera_paths.id"))

class Synchronization(Base, TimestampMixin):
    __tablename__ = "synchronizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    scene_id: Mapped[int] = mapped_column(ForeignKey("timeline_scenes.id"), index=True)
    audio_segment_id: Mapped[Optional[int]] = mapped_column(ForeignKey("audio_segments.id"), index=True)
    narration_id: Mapped[Optional[int]] = mapped_column(ForeignKey("narration.id"), index=True)
    start_time_ms: Mapped[int] = mapped_column(Integer)
    end_time_ms: Mapped[int] = mapped_column(Integer)
    sync_accuracy: Mapped[float] = mapped_column(Float, default=1.0)
