from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Benchmarks(Base, TimestampMixin):
    __tablename__ = "benchmarks"

    id: Mapped[int] = mapped_column(primary_key=True)
    component: Mapped[str] = mapped_column(String(100), index=True)
    operation: Mapped[str] = mapped_column(String(100), index=True)
    execution_time: Mapped[float] = mapped_column(Float)
    memory_usage: Mapped[Optional[float]] = mapped_column(Float)
    cpu_usage: Mapped[Optional[float]] = mapped_column(Float)
    gpu_usage: Mapped[Optional[float]] = mapped_column(Float)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)


class OptimizationHistory(Base, TimestampMixin):
    __tablename__ = "optimization_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    optimization_type: Mapped[str] = mapped_column(String(100), index=True)
    original_value: Mapped[Optional[str]] = mapped_column(Text)
    new_value: Mapped[Optional[str]] = mapped_column(Text)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    rolled_back: Mapped[bool] = mapped_column(Boolean, default=False)
    metrics: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)


class PerformanceProfiles(Base, TimestampMixin):
    __tablename__ = "performance_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    cpu_threads: Mapped[int] = mapped_column(Integer, default=1)
    gpu_workers: Mapped[int] = mapped_column(Integer, default=0)
    memory_limit_mb: Mapped[int] = mapped_column(Integer, default=1024)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    config_overrides: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)


class ResourceUsage(Base, TimestampMixin):
    __tablename__ = "resource_usage"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[str] = mapped_column(String(100), index=True)
    cpu_usage_avg: Mapped[float] = mapped_column(Float)
    gpu_usage_avg: Mapped[Optional[float]] = mapped_column(Float)
    memory_peak_mb: Mapped[float] = mapped_column(Float)
    disk_io_mb: Mapped[Optional[float]] = mapped_column(Float)
    duration_seconds: Mapped[float] = mapped_column(Float)


class CostReports(Base, TimestampMixin):
    __tablename__ = "cost_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    period: Mapped[str] = mapped_column(String(50), index=True)
    total_cost: Mapped[float] = mapped_column(Float, default=0.0)
    gpu_hours: Mapped[float] = mapped_column(Float, default=0.0)
    cpu_hours: Mapped[float] = mapped_column(Float, default=0.0)
    storage_gb: Mapped[float] = mapped_column(Float, default=0.0)
    api_costs: Mapped[float] = mapped_column(Float, default=0.0)
    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)


class ModelBenchmarks(Base, TimestampMixin):
    __tablename__ = "model_benchmarks"

    id: Mapped[int] = mapped_column(primary_key=True)
    model_name: Mapped[str] = mapped_column(String(255), index=True)
    provider: Mapped[str] = mapped_column(String(100), index=True)
    accuracy: Mapped[Optional[float]] = mapped_column(Float)
    latency_ms: Mapped[float] = mapped_column(Float)
    cost_per_1k: Mapped[Optional[float]] = mapped_column(Float)
    vram_usage_mb: Mapped[Optional[float]] = mapped_column(Float)


class InferenceCache(Base, TimestampMixin):
    __tablename__ = "inference_cache"

    id: Mapped[int] = mapped_column(primary_key=True)
    cache_key: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    component: Mapped[str] = mapped_column(String(100), index=True)
    response_payload: Mapped[Dict[str, Any]] = mapped_column(JSON)
    hit_count: Mapped[int] = mapped_column(Integer, default=0)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True)


class DeploymentProfiles(Base, TimestampMixin):
    __tablename__ = "deployment_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    target_env: Mapped[str] = mapped_column(String(100), index=True)
    configuration: Mapped[Dict[str, Any]] = mapped_column(JSON)
    active: Mapped[bool] = mapped_column(Boolean, default=False)
    version: Mapped[str] = mapped_column(String(50))


class ArchiveHistory(Base, TimestampMixin):
    __tablename__ = "archive_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, index=True)
    archive_path: Mapped[str] = mapped_column(String(1024))
    size_mb: Mapped[float] = mapped_column(Float)
    compression_ratio: Mapped[Optional[float]] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(50), default="completed")


class DependencyGraph(Base, TimestampMixin):
    __tablename__ = "dependency_graph"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, index=True)
    node_id: Mapped[str] = mapped_column(String(100), index=True)
    dependencies: Mapped[Dict[str, Any]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    hash_state: Mapped[Optional[str]] = mapped_column(String(255))
