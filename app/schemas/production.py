from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class UserPreferencesBase(BaseModel):
    user_id: Optional[str] = None
    theme: Optional[str] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)


class UserPreferencesCreate(UserPreferencesBase):
    pass


class UserPreferencesResponse(UserPreferencesBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectHistoryBase(BaseModel):
    project_id: int
    event_type: str
    details: Dict[str, Any] = Field(default_factory=dict)


class ProjectHistoryCreate(ProjectHistoryBase):
    pass


class ProjectHistoryResponse(ProjectHistoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PipelineHistoryBase(BaseModel):
    job_id: int
    stage: str
    status: str
    details: Dict[str, Any] = Field(default_factory=dict)


class PipelineHistoryCreate(PipelineHistoryBase):
    pass


class PipelineHistoryResponse(PipelineHistoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplicationSettingsBase(BaseModel):
    key: str
    value: Dict[str, Any]
    category: Optional[str] = None


class ApplicationSettingsCreate(ApplicationSettingsBase):
    pass


class ApplicationSettingsResponse(ApplicationSettingsBase):
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationHistoryBase(BaseModel):
    title: str
    message: str
    level: str
    is_read: bool = False
    details: Optional[Dict[str, Any]] = None


class NotificationHistoryCreate(NotificationHistoryBase):
    pass


class NotificationHistoryResponse(NotificationHistoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BackupHistoryBase(BaseModel):
    backup_type: str
    status: str
    file_path: Optional[str] = None
    size_bytes: Optional[int] = None


class BackupHistoryCreate(BackupHistoryBase):
    pass


class BackupHistoryResponse(BackupHistoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InstalledModelsBase(BaseModel):
    name: str
    version: Optional[str] = None
    provider: str
    status: str
    path: Optional[str] = None
    memory_usage_mb: Optional[int] = None


class InstalledModelsCreate(InstalledModelsBase):
    pass


class InstalledModelsResponse(InstalledModelsBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StorageStatisticsBase(BaseModel):
    category: str
    size_bytes: int = 0
    file_count: int = 0


class StorageStatisticsCreate(StorageStatisticsBase):
    pass


class StorageStatisticsResponse(StorageStatisticsBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SystemHealthBase(BaseModel):
    component: str
    status: str
    cpu_usage: Optional[float] = None
    ram_usage: Optional[float] = None
    details: Optional[Dict[str, Any]] = None


class SystemHealthCreate(SystemHealthBase):
    pass


class SystemHealthResponse(SystemHealthBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
