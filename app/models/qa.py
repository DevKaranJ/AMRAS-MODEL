from typing import Any, Dict, Optional

from sqlalchemy import JSON, Boolean, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class QAReport(Base, TimestampMixin):
    __tablename__ = "qa_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    status: Mapped[str] = mapped_column(
        String(50), default="pending", index=True
    )  # pending, passed, failed, review_required
    overall_grade: Mapped[Optional[str]] = mapped_column(String(10))  # A, B, C, F
    summary: Mapped[Optional[str]] = mapped_column(Text)

    # Define relationships for easier querying
    scores: Mapped[Optional["QualityScore"]] = relationship("QualityScore", back_populates="report", uselist=False)
    issues: Mapped[list["IssueReport"]] = relationship("IssueReport", back_populates="report")
    performance: Mapped[Optional["PerformanceReport"]] = relationship(
        "PerformanceReport", back_populates="report", uselist=False
    )


class QualityScore(Base, TimestampMixin):
    __tablename__ = "qa_quality_scores"

    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("qa_reports.id"), unique=True)

    overall_score: Mapped[float] = mapped_column(Float, default=0.0)
    story_score: Mapped[float] = mapped_column(Float, default=0.0)
    narration_score: Mapped[float] = mapped_column(Float, default=0.0)
    voice_score: Mapped[float] = mapped_column(Float, default=0.0)
    timeline_score: Mapped[float] = mapped_column(Float, default=0.0)
    rendering_score: Mapped[float] = mapped_column(Float, default=0.0)
    subtitle_score: Mapped[float] = mapped_column(Float, default=0.0)
    performance_score: Mapped[float] = mapped_column(Float, default=0.0)
    seo_score: Mapped[float] = mapped_column(Float, default=0.0)
    security_score: Mapped[float] = mapped_column(Float, default=0.0)

    report: Mapped["QAReport"] = relationship("QAReport", back_populates="scores")


class IssueReport(Base, TimestampMixin):
    __tablename__ = "qa_issue_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("qa_reports.id"), index=True)
    agent: Mapped[str] = mapped_column(String(50), index=True)  # e.g., 'story', 'video'
    severity: Mapped[str] = mapped_column(String(20), index=True)  # critical, major, medium, minor, info
    category: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    is_fixed: Mapped[bool] = mapped_column(Boolean, default=False)

    report: Mapped["QAReport"] = relationship("QAReport", back_populates="issues")


class AutoFixHistory(Base, TimestampMixin):
    __tablename__ = "qa_auto_fix_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    issue_id: Mapped[int] = mapped_column(ForeignKey("qa_issue_reports.id"), index=True)
    action_taken: Mapped[str] = mapped_column(Text)
    success: Mapped[bool] = mapped_column(Boolean, default=False)
    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)


class ManualReview(Base, TimestampMixin):
    __tablename__ = "qa_manual_reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("qa_reports.id"), index=True)
    issue_id: Mapped[Optional[int]] = mapped_column(ForeignKey("qa_issue_reports.id"))
    reviewer_notes: Mapped[Optional[str]] = mapped_column(Text)
    decision: Mapped[str] = mapped_column(String(50))  # approved, rejected, fixed
    resolved_by: Mapped[Optional[str]] = mapped_column(String(100))


class PerformanceReport(Base, TimestampMixin):
    __tablename__ = "qa_performance_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("qa_reports.id"), unique=True)

    cpu_usage_avg: Mapped[Optional[float]] = mapped_column(Float)
    gpu_usage_avg: Mapped[Optional[float]] = mapped_column(Float)
    memory_usage_mb: Mapped[Optional[float]] = mapped_column(Float)
    disk_usage_mb: Mapped[Optional[float]] = mapped_column(Float)
    pipeline_duration_seconds: Mapped[Optional[float]] = mapped_column(Float)
    phase_durations: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)

    report: Mapped["QAReport"] = relationship("QAReport", back_populates="performance")


class ApprovalHistory(Base, TimestampMixin):
    __tablename__ = "qa_approval_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("qa_reports.id"))
    status: Mapped[str] = mapped_column(String(50))  # approved, rejected
    notes: Mapped[Optional[str]] = mapped_column(Text)


class ValidationMetric(Base, TimestampMixin):
    __tablename__ = "qa_validation_metrics"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    metric_name: Mapped[str] = mapped_column(String(100), index=True)
    metric_value: Mapped[float] = mapped_column(Float)
    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
