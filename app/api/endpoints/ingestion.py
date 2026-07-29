from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, field_validator
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.core.logger import get_logger
from app.database.session import get_db_session
from app.jobs.base import JobContext, JobStatus
from app.models.manga import DownloadJob, ImportJob, Manga
from modules.ingestion.agents.collection_agent import CollectionAgent
from modules.ingestion.agents.database_agent import DatabaseAgent
from modules.ingestion.agents.file_system_agent import FileSystemAgent
from modules.ingestion.agents.metadata_agent import MetadataAgent
from modules.ingestion.agents.validation_agent import ValidationAgent
from modules.ingestion.importers.remote_importer import RemoteProvider
from modules.ingestion.jobs.download_job import ProcessDownloadJob
from modules.ingestion.jobs.import_job import ProcessImportJob

logger = get_logger("amras.api.ingestion")
router = APIRouter()


class ImportRequest(BaseModel):
    source_path: str

    @field_validator("source_path")
    @classmethod
    def validate_source_path(cls, v: str) -> str:
        """Reject paths that escape the designated manga storage directory."""
        resolved = Path(v).resolve()
        manga_dir = settings.storage.manga_dir.resolve()
        if not str(resolved).startswith(str(manga_dir)):
            raise ValueError(
                f"source_path must be within the manga storage directory ({manga_dir}). "
                "Absolute paths outside that directory are not permitted."
            )
        return str(resolved)


class DownloadRequest(BaseModel):
    manga_id: str
    chapter_id: str
    dest_dir: str

    @field_validator("dest_dir")
    @classmethod
    def validate_dest_dir(cls, v: str) -> str:
        """Reject destination directories that escape the storage root."""
        resolved = Path(v).resolve()
        storage_root = settings.storage.base_dir.resolve()
        if not str(resolved).startswith(str(storage_root)):
            raise ValueError(
                f"dest_dir must be within the storage root ({storage_root}). "
                "Paths outside that directory are not permitted."
            )
        return str(resolved)


# --------------------------------------------------------------------------- #
# Background task helpers                                                      #
# --------------------------------------------------------------------------- #


async def _run_import_job(job_id: int, source_path: str) -> None:
    """Execute an import job in the background and persist its final status."""
    from app.database.session import async_session_maker

    async with async_session_maker() as session:
        metadata_agent = MetadataAgent()
        validation_agent = ValidationAgent()
        file_system_agent = FileSystemAgent()
        database_agent = DatabaseAgent(session)

        collection_agent = CollectionAgent(
            metadata_agent=metadata_agent,
            validation_agent=validation_agent,
            file_system_agent=file_system_agent,
            database_agent=database_agent,
        )

        context = JobContext(job_id=str(job_id))
        job = ProcessImportJob(context, collection_agent)

        try:
            await job.execute(source_path=source_path, import_job_id=job_id)
            await session.execute(
                update(ImportJob).where(ImportJob.id == job_id).values(status=JobStatus.COMPLETED.value)
            )
        except Exception as exc:
            logger.exception("import_job_failed", job_id=job_id, error=str(exc))
            await session.execute(
                update(ImportJob)
                .where(ImportJob.id == job_id)
                .values(status=JobStatus.FAILED.value, error=str(exc))
            )
        finally:
            await session.commit()


async def _run_download_job(job_id: int, manga_id: str, chapter_id: str, dest_dir: str) -> None:
    """Execute a download job in the background and persist its final status."""
    from app.database.session import async_session_maker

    async with async_session_maker() as session:
        remote_provider = RemoteProvider()
        context = JobContext(job_id=str(job_id))
        job = ProcessDownloadJob(context, remote_provider)

        try:
            await job.execute(manga_id=manga_id, chapter_id=chapter_id, dest_dir=dest_dir)
            await session.execute(
                update(DownloadJob).where(DownloadJob.id == job_id).values(status=JobStatus.COMPLETED.value)
            )
        except Exception as exc:
            logger.exception("download_job_failed", job_id=job_id, error=str(exc))
            await session.execute(
                update(DownloadJob)
                .where(DownloadJob.id == job_id)
                .values(status=JobStatus.FAILED.value, error=str(exc))
            )
        finally:
            await session.commit()


# --------------------------------------------------------------------------- #
# Endpoints                                                                    #
# --------------------------------------------------------------------------- #


@router.post("/import", status_code=status.HTTP_202_ACCEPTED)
async def import_manga(
    req: ImportRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Enqueue an import job from a local source path."""
    stmt = insert(ImportJob).values(status=JobStatus.QUEUED.value).returning(ImportJob.id)
    result = await session.execute(stmt)
    job_id = result.scalar_one()
    await session.commit()

    background_tasks.add_task(_run_import_job, job_id, req.source_path)

    logger.info("import_job_queued", job_id=job_id, source_path=req.source_path)
    return {"message": "Import job queued", "source_path": req.source_path, "job_id": job_id}


@router.post("/download", status_code=status.HTTP_202_ACCEPTED)
async def download_manga(
    req: DownloadRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Enqueue a download job for a specific chapter."""
    stmt = (
        insert(DownloadJob)
        .values(status=JobStatus.QUEUED.value, provider="remote")
        .returning(DownloadJob.id)
    )
    result = await session.execute(stmt)
    job_id = result.scalar_one()
    await session.commit()

    background_tasks.add_task(_run_download_job, job_id, req.manga_id, req.chapter_id, req.dest_dir)

    logger.info("download_job_queued", job_id=job_id, manga_id=req.manga_id, chapter_id=req.chapter_id)
    return {
        "message": "Download job queued",
        "manga_id": req.manga_id,
        "chapter_id": req.chapter_id,
        "job_id": job_id,
    }


@router.get("/manga")
async def list_manga(
    skip: int = 0,
    limit: int = 50,
    session: AsyncSession = Depends(get_db_session),
) -> List[Dict[str, Any]]:
    """List imported manga with pagination."""
    if limit > 200:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="limit cannot exceed 200")
    stmt = select(Manga).offset(skip).limit(limit)
    result = await session.execute(stmt)
    mangas = result.scalars().all()
    return [{"id": manga.id, "title": manga.title, "slug": manga.slug, "status": manga.status} for manga in mangas]
