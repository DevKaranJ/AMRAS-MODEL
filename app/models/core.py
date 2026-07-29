from typing import Any, Dict, Optional

from sqlalchemy import JSON, Boolean, Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.jobs.base import JobStatus
from app.models.base import Base, TimestampMixin


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="created")
    config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)


class Job(Base, TimestampMixin):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[Optional[int]] = mapped_column(ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    # Enforce valid values at the database level using the JobStatus enum.
    status: Mapped[str] = mapped_column(
        SAEnum(
            *[s.value for s in JobStatus],
            name="job_status_enum",
            create_type=True,
        ),
        default=JobStatus.QUEUED.value,
        index=True,
    )
    payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    error: Mapped[Optional[str]] = mapped_column(Text)


class JobLog(Base, TimestampMixin):
    __tablename__ = "job_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), index=True)
    level: Mapped[str] = mapped_column(String(20))
    message: Mapped[str] = mapped_column(Text)
    phase: Mapped[Optional[str]] = mapped_column(String(100))


class AIProvider(Base, TimestampMixin):
    __tablename__ = "ai_providers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # NOTE: Do NOT store raw API keys in this JSON column.
    # Use environment variables or a secrets manager instead.
    config: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)


class Setting(Base, TimestampMixin):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(255), primary_key=True)
    value: Mapped[Dict[str, Any]] = mapped_column(JSON)


class SystemState(Base, TimestampMixin):
    __tablename__ = "system_state"

    id: Mapped[int] = mapped_column(primary_key=True)
    component: Mapped[str] = mapped_column(String(100), unique=True)
    status: Mapped[str] = mapped_column(String(50))
    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
