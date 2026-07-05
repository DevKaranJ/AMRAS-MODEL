from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ImportJobCreate(BaseModel):
    status: str = "queued"
    progress: float = 0.0
    current_file: Optional[str] = None


class ImportJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    progress: float
    current_file: Optional[str]
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    error: Optional[str]
    created_at: datetime
    updated_at: datetime


class DownloadJobCreate(BaseModel):
    provider: str
    status: str = "queued"
    progress: float = 0.0
    retries: int = 0
    bandwidth: Optional[float] = None


class DownloadJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    provider: str
    status: str
    progress: float
    retries: int
    bandwidth: Optional[float]
    error: Optional[str]
    created_at: datetime
    updated_at: datetime
