from typing import Any, Dict, Optional

from sqlalchemy import JSON, Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class AIGatewayProvider(Base, TimestampMixin):
    __tablename__ = "ai_gateway_providers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    provider_type: Mapped[str] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    config: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    models: Mapped[list["AIModel"]] = relationship(back_populates="provider")


class AIModel(Base, TimestampMixin):
    __tablename__ = "ai_models"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    provider_id: Mapped[int] = mapped_column(ForeignKey("ai_gateway_providers.id"), index=True)
    version: Mapped[str] = mapped_column(String(50))
    capabilities: Mapped[list[str]] = mapped_column(JSON)
    supported_languages: Mapped[list[str]] = mapped_column(JSON, default=list)
    context_length: Mapped[int] = mapped_column(Integer, default=4096)
    vram_requirement: Mapped[Optional[int]] = mapped_column(Integer)
    ram_requirement: Mapped[Optional[int]] = mapped_column(Integer)
    estimated_speed: Mapped[Optional[float]] = mapped_column(Float)
    estimated_cost: Mapped[Optional[float]] = mapped_column(Float)
    average_latency: Mapped[Optional[float]] = mapped_column(Float)
    average_accuracy: Mapped[Optional[float]] = mapped_column(Float)
    health_status: Mapped[str] = mapped_column(String(50), default="healthy")
    availability: Mapped[float] = mapped_column(Float, default=1.0)
    license: Mapped[Optional[str]] = mapped_column(String(100))
    priority: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    provider: Mapped["AIGatewayProvider"] = relationship(back_populates="models")
    benchmarks: Mapped[list["ModelBenchmark"]] = relationship(back_populates="model")


class ModelBenchmark(Base, TimestampMixin):
    __tablename__ = "model_benchmarks"
    id: Mapped[int] = mapped_column(primary_key=True)
    model_id: Mapped[int] = mapped_column(ForeignKey("ai_models.id"), index=True)
    task_type: Mapped[str] = mapped_column(String(100), index=True)
    latency: Mapped[float] = mapped_column(Float)
    accuracy: Mapped[float] = mapped_column(Float)
    memory_usage: Mapped[Optional[int]] = mapped_column(Integer)
    vram_usage: Mapped[Optional[int]] = mapped_column(Integer)
    cpu_usage: Mapped[Optional[float]] = mapped_column(Float)
    gpu_usage: Mapped[Optional[float]] = mapped_column(Float)
    token_speed: Mapped[Optional[float]] = mapped_column(Float)
    inference_speed: Mapped[Optional[float]] = mapped_column(Float)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    model: Mapped["AIModel"] = relationship(back_populates="benchmarks")


class RoutingPolicy(Base, TimestampMixin):
    __tablename__ = "routing_policies"
    id: Mapped[int] = mapped_column(primary_key=True)
    task_type: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    routing_mode: Mapped[str] = mapped_column(String(50), default="balanced")
    preferred_providers: Mapped[list[str]] = mapped_column(JSON, default=list)
    fallback_providers: Mapped[list[str]] = mapped_column(JSON, default=list)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    timeout: Mapped[int] = mapped_column(Integer, default=30)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class PromptTemplate(Base, TimestampMixin):
    __tablename__ = "prompt_templates"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    task_type: Mapped[str] = mapped_column(String(100), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    versions: Mapped[list["PromptVersion"]] = relationship(back_populates="template")


class PromptVersion(Base, TimestampMixin):
    __tablename__ = "prompt_versions"
    id: Mapped[int] = mapped_column(primary_key=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("prompt_templates.id"), index=True)
    version_number: Mapped[int] = mapped_column(Integer)
    system_prompt: Mapped[str] = mapped_column(Text)
    user_prompt: Mapped[str] = mapped_column(Text)
    variables: Mapped[list[str]] = mapped_column(JSON, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    template: Mapped["PromptTemplate"] = relationship(back_populates="versions")


class AIRequest(Base, TimestampMixin):
    __tablename__ = "ai_requests"
    id: Mapped[int] = mapped_column(primary_key=True)
    correlation_id: Mapped[str] = mapped_column(String(100), index=True)
    task_type: Mapped[str] = mapped_column(String(100), index=True)
    provider_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ai_gateway_providers.id"))
    model_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ai_models.id"))
    prompt_version_id: Mapped[Optional[int]] = mapped_column(ForeignKey("prompt_versions.id"))
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    responses: Mapped[list["AIResponse"]] = relationship(back_populates="request")


class AIResponse(Base, TimestampMixin):
    __tablename__ = "ai_responses"
    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("ai_requests.id"), index=True)
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    error: Mapped[Optional[str]] = mapped_column(Text)
    latency: Mapped[float] = mapped_column(Float)
    retries: Mapped[int] = mapped_column(Integer, default=0)
    prompt_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    completion_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    total_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    estimated_cost: Mapped[Optional[float]] = mapped_column(Float)
    request: Mapped["AIRequest"] = relationship(back_populates="responses")


class CacheEntry(Base, TimestampMixin):
    __tablename__ = "ai_cache_entries"
    id: Mapped[int] = mapped_column(primary_key=True)
    cache_key: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    task_type: Mapped[str] = mapped_column(String(100), index=True)
    response_data: Mapped[Dict[str, Any]] = mapped_column(JSON)
    expires_at: Mapped[Optional[float]] = mapped_column(Float)
    hits: Mapped[int] = mapped_column(Integer, default=0)
    last_accessed: Mapped[Optional[float]] = mapped_column(Float)


class HealthReport(Base, TimestampMixin):
    __tablename__ = "ai_health_reports"
    id: Mapped[int] = mapped_column(primary_key=True)
    provider_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ai_gateway_providers.id"), index=True)
    model_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ai_models.id"), index=True)
    status: Mapped[str] = mapped_column(String(50))
    latency: Mapped[Optional[float]] = mapped_column(Float)
    error_rate: Mapped[Optional[float]] = mapped_column(Float)
    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)


class UsageStatistic(Base, TimestampMixin):
    __tablename__ = "ai_usage_statistics"
    id: Mapped[int] = mapped_column(primary_key=True)
    model_id: Mapped[int] = mapped_column(ForeignKey("ai_models.id"), index=True)
    task_type: Mapped[str] = mapped_column(String(100), index=True)
    total_requests: Mapped[int] = mapped_column(Integer, default=0)
    successful_requests: Mapped[int] = mapped_column(Integer, default=0)
    failed_requests: Mapped[int] = mapped_column(Integer, default=0)
    total_prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_cost: Mapped[float] = mapped_column(Float, default=0.0)


class FailureHistory(Base, TimestampMixin):
    __tablename__ = "ai_failure_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ai_requests.id"), index=True)
    model_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ai_models.id"), index=True)
    error_type: Mapped[str] = mapped_column(String(100))
    error_message: Mapped[Text] = mapped_column(Text)
    stack_trace: Mapped[Optional[Text]] = mapped_column(Text)
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
