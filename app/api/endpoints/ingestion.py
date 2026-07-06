from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.jobs.base import JobContext
from app.models.manga import DownloadJob, ImportJob, Manga
from modules.ingestion.agents.collection_agent import CollectionAgent
from modules.ingestion.agents.database_agent import DatabaseAgent
from modules.ingestion.agents.file_system_agent import FileSystemAgent
from modules.ingestion.agents.metadata_agent import MetadataAgent
from modules.ingestion.agents.validation_agent import ValidationAgent
from modules.ingestion.importers.remote_importer import RemoteProvider
from modules.ingestion.jobs.download_job import ProcessDownloadJob
from modules.ingestion.jobs.import_job import ProcessImportJob

router = APIRouter()


class ImportRequest(BaseModel):
    source_path: str


class DownloadRequest(BaseModel):
    manga_id: str
    chapter_id: str
    dest_dir: str


@router.post("/import", status_code=202)
async def import_manga(req: ImportRequest, session: AsyncSession = Depends(get_db_session)) -> Dict[str, Any]:
    """Starts an import job from a local source path."""
    # Create import job in database
    stmt = insert(ImportJob).values(status="queued").returning(ImportJob.id)
    result = await session.execute(stmt)
    job_id = result.scalar_one()
    await session.commit()

    # Create agents and job
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

    # Execute job asynchronously (in production, this would be enqueued to a background worker)
    context = JobContext(job_id=str(job_id))
    job = ProcessImportJob(context, collection_agent)

    try:
        await job.execute(source_path=req.source_path, import_job_id=job_id)
    except Exception:
        pass  # Error already logged and persisted by the job

    return {"message": "Import job queued", "source_path": req.source_path, "job_id": job_id}


@router.post("/download", status_code=202)
async def download_manga(req: DownloadRequest, session: AsyncSession = Depends(get_db_session)) -> Dict[str, Any]:
    """Starts a download job for a specific chapter."""
    # Create download job in database
    stmt = insert(DownloadJob).values(status="queued", provider="remote").returning(DownloadJob.id)
    result = await session.execute(stmt)
    job_id = result.scalar_one()
    await session.commit()

    # Create remote provider and job
    remote_provider = RemoteProvider()

    # Execute job asynchronously (in production, this would be enqueued to a background worker)
    context = JobContext(job_id=str(job_id))
    job = ProcessDownloadJob(context, remote_provider)

    try:
        await job.execute(manga_id=req.manga_id, chapter_id=req.chapter_id, dest_dir=req.dest_dir)
    except Exception:
        pass  # Error already logged by the job

    return {"message": "Download job queued", "manga_id": req.manga_id, "chapter_id": req.chapter_id, "job_id": job_id}


@router.get("/manga")
async def list_manga(session: AsyncSession = Depends(get_db_session)) -> List[Dict[str, Any]]:
    """Lists imported manga."""
    stmt = select(Manga)
    result = await session.execute(stmt)
    mangas = result.scalars().all()

    return [{"id": manga.id, "title": manga.title, "slug": manga.slug, "status": manga.status} for manga in mangas]
