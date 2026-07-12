from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class AIGatewayProviderBase(BaseModel):
    name: str = Field(..., max_length=100)
    provider_type: str = Field(..., max_length=50)
    is_active: bool = Field(default=True)
    config: Dict[str, Any] = Field(default_factory=dict)


class AIGatewayProviderCreate(AIGatewayProviderBase):
    pass


class AIGatewayProviderRead(AIGatewayProviderBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AIModelBase(BaseModel):
    name: str = Field(..., max_length=255)
    provider_id: int
    version: str = Field(..., max_length=50)
    capabilities: List[str]
    supported_languages: List[str] = Field(default_factory=list)
    context_length: int = Field(default=4096)
    vram_requirement: Optional[int] = None
    ram_requirement: Optional[int] = None
    estimated_speed: Optional[float] = None
    estimated_cost: Optional[float] = None
    average_latency: Optional[float] = None
    average_accuracy: Optional[float] = None
    health_status: str = Field(default="healthy", max_length=50)
    availability: float = Field(default=1.0)
    license: Optional[str] = Field(default=None, max_length=100)
    priority: int = Field(default=0)
    is_active: bool = Field(default=True)


class AIModelCreate(AIModelBase):
    pass


class AIModelRead(AIModelBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class RoutingPolicyBase(BaseModel):
    task_type: str = Field(..., max_length=100)
    routing_mode: str = Field(default="balanced", max_length=50)
    preferred_providers: List[str] = Field(default_factory=list)
    fallback_providers: List[str] = Field(default_factory=list)
    max_retries: int = Field(default=3)
    timeout: int = Field(default=30)
    is_active: bool = Field(default=True)


class RoutingPolicyCreate(RoutingPolicyBase):
    pass


class RoutingPolicyRead(RoutingPolicyBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PromptTemplateBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    task_type: str = Field(..., max_length=100)
    is_active: bool = Field(default=True)


class PromptTemplateCreate(PromptTemplateBase):
    pass


class PromptTemplateRead(PromptTemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AIRequestBase(BaseModel):
    correlation_id: str = Field(..., max_length=100)
    task_type: str = Field(..., max_length=100)
    provider_id: Optional[int] = None
    model_id: Optional[int] = None
    prompt_version_id: Optional[int] = None
    payload: Dict[str, Any]
    status: str = Field(default="pending", max_length=50)


class AIRequestCreate(AIRequestBase):
    pass


class AIRequestRead(AIRequestBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AIResponseBase(BaseModel):
    request_id: int
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    latency: float
    retries: int = Field(default=0)
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    estimated_cost: Optional[float] = None


class AIResponseCreate(AIResponseBase):
    pass


class AIResponseRead(AIResponseBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
