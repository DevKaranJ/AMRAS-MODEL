from typing import Any, Dict, Optional

from sqlalchemy import JSON, Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class UserPreferences(Base, TimestampMixin):
    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    theme: Mapped[Optional[str]] = mapped_column(String(50))
    preferences: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)


class ProjectHistory(Base, TimestampMixin):
    __tablename__ = "project_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(100))
    details: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)


class PipelineHistory(Base, TimestampMixin):
    __tablename__ = "pipeline_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), index=True)
    stage: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50))
    details: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)


class ApplicationSettings(Base, TimestampMixin):
    __tablename__ = "application_settings"

    key: Mapped[str] = mapped_column(String(255), primary_key=True)
    value: Mapped[Dict[str, Any]] = mapped_column(JSON)
    category: Mapped[Optional[str]] = mapped_column(String(100))


class NotificationHistory(Base, TimestampMixin):
    __tablename__ = "notification_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text)
    level: Mapped[str] = mapped_column(String(50))
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)


class BackupHistory(Base, TimestampMixin):
    __tablename__ = "backup_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    backup_type: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50))
    file_path: Mapped[Optional[str]] = mapped_column(Text)
    size_bytes: Mapped[Optional[int]] = mapped_column(Integer)


class InstalledModels(Base, TimestampMixin):
    __tablename__ = "installed_models"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    version: Mapped[Optional[str]] = mapped_column(String(100))
    provider: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50))
    path: Mapped[Optional[str]] = mapped_column(Text)
    memory_usage_mb: Mapped[Optional[int]] = mapped_column(Integer)


class StorageStatistics(Base, TimestampMixin):
    __tablename__ = "storage_statistics"

    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column(String(100))
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    file_count: Mapped[int] = mapped_column(Integer, default=0)


class SystemHealth(Base, TimestampMixin):
    __tablename__ = "system_health_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    component: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50))
    cpu_usage: Mapped[Optional[float]] = mapped_column(Float)
    ram_usage: Mapped[Optional[float]] = mapped_column(Float)
    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
