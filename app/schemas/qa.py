from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class QARunRequest(BaseModel):
    project_id: int
    modules: Optional[List[str]] = Field(
        default=None,
        description="Optional list of specific modules to run QA on (e.g., ['ocr', 'story']). If null, run all.",
    )
    incremental: bool = Field(
        default=False, description="If true, only validate parts that have changed since the last QA run."
    )


class QARepairRequest(BaseModel):
    project_id: int
    issue_ids: Optional[List[int]] = Field(
        default=None,
        description="Optional list of specific issue IDs to repair. If null, attempt all auto-fixable issues.",
    )


class QualityScoreResponse(BaseModel):
    overall_score: float
    story_score: float
    narration_score: float
    voice_score: float
    timeline_score: float
    rendering_score: float
    subtitle_score: float
    performance_score: float
    seo_score: float
    security_score: float
    model_config = ConfigDict(from_attributes=True)


class IssueReportResponse(BaseModel):
    id: int
    agent: str
    severity: str
    category: str
    description: str
    details: Optional[Dict[str, Any]] = None
    is_fixed: bool
    model_config = ConfigDict(from_attributes=True)


class PerformanceReportResponse(BaseModel):
    cpu_usage_avg: Optional[float] = None
    gpu_usage_avg: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    disk_usage_mb: Optional[float] = None
    pipeline_duration_seconds: Optional[float] = None
    phase_durations: Optional[Dict[str, Any]] = None
    model_config = ConfigDict(from_attributes=True)


class QAReportResponse(BaseModel):
    id: int
    project_id: int
    status: str
    overall_grade: Optional[str] = None
    summary: Optional[str] = None
    scores: Optional[QualityScoreResponse] = None
    issues: List[IssueReportResponse] = []
    performance: Optional[PerformanceReportResponse] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AutoFixResult(BaseModel):
    issue_id: int
    success: bool
    action_taken: str
    details: Optional[Dict[str, Any]] = None
    model_config = ConfigDict(from_attributes=True)


class ApprovalRequest(BaseModel):
    project_id: int
    status: str = Field(..., description="'approved' or 'rejected'")
    notes: Optional[str] = None


class ValidationMetricResponse(BaseModel):
    metric_name: str
    metric_value: float
    details: Optional[Dict[str, Any]] = None
    model_config = ConfigDict(from_attributes=True)
