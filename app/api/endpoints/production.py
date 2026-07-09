from typing import Any, Dict, List

import psutil
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.models.core import Job, Project
from app.schemas.production import (
    BackupHistoryResponse,
    InstalledModelsResponse,
    StorageStatisticsResponse,
    SystemHealthResponse,
)

router = APIRouter()

@router.get("/dashboard", response_model=Dict[str, Any])
async def get_dashboard(db: AsyncSession = Depends(get_db_session)) -> Dict[str, Any]:
    """Retrieve main dashboard metrics."""
    # Note: scalar_one() raises if no result, but count() always returns at least 0.
    projects_count = await db.scalar(select(func.count(Project.id)))
    running_jobs = await db.scalar(select(func.count(Job.id)).where(Job.status == "running"))
    completed_jobs = await db.scalar(select(func.count(Job.id)).where(Job.status == "completed"))
    failed_jobs = await db.scalar(select(func.count(Job.id)).where(Job.status == "failed"))

    return {
        "projects_count": projects_count or 0,
        "running_jobs": running_jobs or 0,
        "completed_jobs": completed_jobs or 0,
        "failed_jobs": failed_jobs or 0,
        "storage_usage_bytes": 0,
    }

@router.get("/system/health", response_model=List[SystemHealthResponse])
async def get_system_health(db: AsyncSession = Depends(get_db_session)) -> List[SystemHealthResponse]:
    """Retrieve system health statistics (stub)."""
    return []

@router.get("/system/resources", response_model=Dict[str, Any])
async def get_system_resources(db: AsyncSession = Depends(get_db_session)) -> Dict[str, Any]:
    """Retrieve real-time resource usage metrics."""
    mem = psutil.virtual_memory()
    return {
        "cpu_usage": psutil.cpu_percent(interval=None),
        "gpu_usage": 0.0,
        "ram_usage": mem.percent,
        "vram_usage": 0.0,
    }

@router.get("/projects", response_model=List[Dict[str, Any]])
async def list_projects(db: AsyncSession = Depends(get_db_session)) -> List[Dict[str, Any]]:
    """List all projects for the dashboard (stub)."""
    return []

@router.post("/projects", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_project(project_data: Dict[str, Any], db: AsyncSession = Depends(get_db_session)) -> Dict[str, Any]:
    """Create a new project (stub)."""
    raise HTTPException(status_code=501, detail="Not implemented")

@router.post("/pipeline/run")
async def run_pipeline(config: Dict[str, Any], db: AsyncSession = Depends(get_db_session)) -> Dict[str, Any]:
    """Start the entire pipeline for a project (stub)."""
    return {"status": "started", "job_id": 1}

@router.post("/pipeline/resume")
async def resume_pipeline(job_id: int, db: AsyncSession = Depends(get_db_session)) -> Dict[str, Any]:
    """Resume an interrupted pipeline (stub)."""
    return {"status": "resumed", "job_id": job_id}

@router.post("/system/backup", response_model=BackupHistoryResponse)
async def create_backup(db: AsyncSession = Depends(get_db_session)) -> BackupHistoryResponse:
    """Create a system backup (stub)."""
    raise HTTPException(status_code=501, detail="Not implemented")

@router.post("/system/restore")
async def restore_backup(backup_id: int, db: AsyncSession = Depends(get_db_session)) -> Dict[str, Any]:
    """Restore from a backup (stub)."""
    return {"status": "restoring"}

@router.get("/models", response_model=List[InstalledModelsResponse])
async def list_models(db: AsyncSession = Depends(get_db_session)) -> List[InstalledModelsResponse]:
    """List installed models (stub)."""
    return []

@router.post("/models/install", response_model=InstalledModelsResponse)
async def install_model(model_data: Dict[str, Any], db: AsyncSession = Depends(get_db_session)) -> InstalledModelsResponse:
    """Install a new AI model (stub)."""
    raise HTTPException(status_code=501, detail="Not implemented")

@router.get("/storage", response_model=List[StorageStatisticsResponse])
async def get_storage_stats(db: AsyncSession = Depends(get_db_session)) -> List[StorageStatisticsResponse]:
    """Retrieve storage statistics (stub)."""
    return []

@router.post("/storage/cleanup")
async def cleanup_storage(db: AsyncSession = Depends(get_db_session)) -> Dict[str, Any]:
    """Clean up temporary files and caches (stub)."""
    return {"status": "cleaning"}

@router.get("/logs")
async def get_logs(db: AsyncSession = Depends(get_db_session)) -> List[Dict[str, Any]]:
    """Retrieve system and pipeline logs (stub)."""
    return []
