from typing import Any, Optional

from sqlalchemy import JSON, Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class VisionJob(Base, TimestampMixin):
    __tablename__ = "vision_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    page_id: Mapped[int] = mapped_column(ForeignKey("pages.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(50), index=True, default="queued")
    error: Mapped[Optional[str]] = mapped_column(Text)


class Panel(Base, TimestampMixin):
    __tablename__ = "panels"

    id: Mapped[int] = mapped_column(primary_key=True)
    page_id: Mapped[int] = mapped_column(ForeignKey("pages.id", ondelete="CASCADE"), index=True)
    panel_number: Mapped[int] = mapped_column(Integer)
    reading_order: Mapped[int] = mapped_column(Integer)
    bounding_box: Mapped[Any] = mapped_column(JSON)
    scene_type: Mapped[Optional[str]] = mapped_column(String(100))
    emotion: Mapped[Optional[str]] = mapped_column(String(100))

    # Relationships
    speech_bubbles: Mapped[list["SpeechBubble"]] = relationship(
        "SpeechBubble", lazy="selectin", cascade="all, delete-orphan"
    )
    narrations: Mapped[list["Narration"]] = relationship("Narration", lazy="selectin", cascade="all, delete-orphan")
    characters: Mapped[list["CharacterDetected"]] = relationship(
        "CharacterDetected", lazy="selectin", cascade="all, delete-orphan"
    )
    objects: Mapped[list["ObjectDetected"]] = relationship(
        "ObjectDetected", lazy="selectin", cascade="all, delete-orphan"
    )
    actions: Mapped[list["ActionDetected"]] = relationship(
        "ActionDetected", lazy="selectin", cascade="all, delete-orphan"
    )
    sound_effects: Mapped[list["SoundEffect"]] = relationship(
        "SoundEffect", lazy="selectin", cascade="all, delete-orphan"
    )


class SpeechBubble(Base, TimestampMixin):
    __tablename__ = "speech_bubbles"
    id: Mapped[int] = mapped_column(primary_key=True)
    panel_id: Mapped[int] = mapped_column(ForeignKey("panels.id", ondelete="CASCADE"), index=True)
    speaker: Mapped[Optional[str]] = mapped_column(String(255))
    text: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float)
    language: Mapped[Optional[str]] = mapped_column(String(50))
    bubble_type: Mapped[str] = mapped_column(String(50))
    bounding_box: Mapped[Optional[Any]] = mapped_column(JSON)


class Narration(Base, TimestampMixin):
    __tablename__ = "narration"
    id: Mapped[int] = mapped_column(primary_key=True)
    panel_id: Mapped[int] = mapped_column(ForeignKey("panels.id", ondelete="CASCADE"), index=True)
    text: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(String(50), default="narration")


class CharacterDetected(Base, TimestampMixin):
    __tablename__ = "characters_detected"
    id: Mapped[int] = mapped_column(primary_key=True)
    panel_id: Mapped[int] = mapped_column(ForeignKey("panels.id", ondelete="CASCADE"), index=True)
    identity_estimate: Mapped[Optional[str]] = mapped_column(String(255))
    gender: Mapped[Optional[str]] = mapped_column(String(50))
    age_group: Mapped[Optional[str]] = mapped_column(String(50))
    clothing: Mapped[Optional[str]] = mapped_column(Text)
    expression: Mapped[Optional[str]] = mapped_column(String(100))
    pose: Mapped[Optional[str]] = mapped_column(String(100))
    confidence: Mapped[float] = mapped_column(Float)
    bounding_box: Mapped[Optional[Any]] = mapped_column(JSON)


class ObjectDetected(Base, TimestampMixin):
    __tablename__ = "objects_detected"
    id: Mapped[int] = mapped_column(primary_key=True)
    panel_id: Mapped[int] = mapped_column(ForeignKey("panels.id", ondelete="CASCADE"), index=True)
    label: Mapped[str] = mapped_column(String(255))
    confidence: Mapped[float] = mapped_column(Float)
    bounding_box: Mapped[Optional[Any]] = mapped_column(JSON)


class ActionDetected(Base, TimestampMixin):
    __tablename__ = "actions_detected"
    id: Mapped[int] = mapped_column(primary_key=True)
    panel_id: Mapped[int] = mapped_column(ForeignKey("panels.id", ondelete="CASCADE"), index=True)
    label: Mapped[str] = mapped_column(String(255))
    confidence: Mapped[float] = mapped_column(Float)


class SoundEffect(Base, TimestampMixin):
    __tablename__ = "sound_effects"
    id: Mapped[int] = mapped_column(primary_key=True)
    panel_id: Mapped[int] = mapped_column(ForeignKey("panels.id", ondelete="CASCADE"), index=True)
    text: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(100), default="sound_effect")
    ignore_for_summary: Mapped[bool] = mapped_column(Boolean, default=True)


class ConfidenceScore(Base, TimestampMixin):
    __tablename__ = "confidence_scores"
    id: Mapped[int] = mapped_column(primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(100))
    entity_id: Mapped[int] = mapped_column(Integer)
    score: Mapped[float] = mapped_column(Float)
