from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class BenchmarkBase(BaseModel):
    component: str = Field(..., max_length=100)
    operation: str = Field(..., max_length=100)
    execution_time: float
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None
    gpu_usage: Optional[float] = None
    metadata_json: Optional[Dict[str, Any]] = None


class BenchmarkCreate(BenchmarkBase):
    pass


class BenchmarkResponse(BenchmarkBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OptimizationHistoryBase(BaseModel):
    project_id: Optional[int] = None
    optimization_type: str = Field(..., max_length=100)
    original_value: Optional[str] = None
    new_value: Optional[str] = None
    success: bool = True
    rolled_back: bool = False
    metrics: Optional[Dict[str, Any]] = None


class OptimizationHistoryCreate(OptimizationHistoryBase):
    pass


class OptimizationHistoryResponse(OptimizationHistoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PerformanceProfileBase(BaseModel):
    name: str = Field(..., max_length=100)
    cpu_threads: int = 1
    gpu_workers: int = 0
    memory_limit_mb: int = 1024
    priority: int = 0
    config_overrides: Optional[Dict[str, Any]] = None


class PerformanceProfileCreate(PerformanceProfileBase):
    pass


class PerformanceProfileResponse(PerformanceProfileBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResourceUsageBase(BaseModel):
    job_id: str = Field(..., max_length=100)
    cpu_usage_avg: float
    gpu_usage_avg: Optional[float] = None
    memory_peak_mb: float
    disk_io_mb: Optional[float] = None
    duration_seconds: float


class ResourceUsageCreate(ResourceUsageBase):
    pass


class ResourceUsageResponse(ResourceUsageBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CostReportBase(BaseModel):
    period: str = Field(..., max_length=50)
    total_cost: float = 0.0
    gpu_hours: float = 0.0
    cpu_hours: float = 0.0
    storage_gb: float = 0.0
    api_costs: float = 0.0
    details: Optional[Dict[str, Any]] = None


class CostReportCreate(CostReportBase):
    pass


class CostReportResponse(CostReportBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ModelBenchmarkBase(BaseModel):
    model_name: str = Field(..., max_length=255)
    provider: str = Field(..., max_length=100)
    accuracy: Optional[float] = None
    latency_ms: float
    cost_per_1k: Optional[float] = None
    vram_usage_mb: Optional[float] = None


class ModelBenchmarkCreate(ModelBenchmarkBase):
    pass


class ModelBenchmarkResponse(ModelBenchmarkBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InferenceCacheBase(BaseModel):
    cache_key: str = Field(..., max_length=255)
    component: str = Field(..., max_length=100)
    response_payload: Dict[str, Any]
    hit_count: int = 0
    expires_at: Optional[datetime] = None


class InferenceCacheCreate(InferenceCacheBase):
    pass


class InferenceCacheResponse(InferenceCacheBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DeploymentProfileBase(BaseModel):
    target_env: str = Field(..., max_length=100)
    configuration: Dict[str, Any]
    active: bool = False
    version: str = Field(..., max_length=50)


class DeploymentProfileCreate(DeploymentProfileBase):
    pass


class DeploymentProfileResponse(DeploymentProfileBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ArchiveHistoryBase(BaseModel):
    project_id: int
    archive_path: str = Field(..., max_length=1024)
    size_mb: float
    compression_ratio: Optional[float] = None
    status: str = Field("completed", max_length=50)


class ArchiveHistoryCreate(ArchiveHistoryBase):
    pass


class ArchiveHistoryResponse(ArchiveHistoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DependencyGraphBase(BaseModel):
    project_id: int
    node_id: str = Field(..., max_length=100)
    dependencies: Dict[str, Any]
    status: str = Field("pending", max_length=50)
    hash_state: Optional[str] = Field(None, max_length=255)


class DependencyGraphCreate(DependencyGraphBase):
    pass


class DependencyGraphResponse(DependencyGraphBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
