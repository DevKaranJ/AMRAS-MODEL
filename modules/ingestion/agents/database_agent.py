from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.models.manga import ImportJob, Manga
from app.schemas.manga import MangaMetadata
from modules.ingestion.agents.base import BaseIngestionAgent

logger = get_logger("amras.ingestion.database_agent")


class DatabaseAgent(BaseIngestionAgent):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_or_get_manga(self, metadata: MangaMetadata) -> int:
        """Retrieves an existing manga or creates a new one."""
        # Check if exists by slug
        stmt = select(Manga).where(Manga.slug == metadata.slug)
        result = await self.session.execute(stmt)
        manga = result.scalar_one_or_none()

        if not manga:
            manga = Manga(
                title=metadata.title,
                slug=metadata.slug,
                language=metadata.language,
                author=metadata.author,
                artist=metadata.artist,
                status=metadata.status,
                hash=metadata.hash,
            )
            self.session.add(manga)
            try:
                await self.session.commit()
                await self.session.refresh(manga)
                logger.info("created_manga", manga_id=manga.id, slug=manga.slug)
            except IntegrityError:
                # Race condition: another process created the manga with this slug
                await self.session.rollback()
                # Re-query to get the existing manga
                result = await self.session.execute(stmt)
                manga = result.scalar_one()
                logger.info("manga_already_exists", manga_id=manga.id, slug=manga.slug)

        return manga.id

    async def update_import_job(
        self, job_id: int, status: str, progress: Optional[float] = None, error: Optional[str] = None
    ) -> None:
        """Updates the status and progress of an import job."""
        stmt = update(ImportJob).where(ImportJob.id == job_id).values(status=status)
        if progress is not None:
            stmt = stmt.values(progress=progress)
        if error is not None:
            stmt = stmt.values(error=error)

        await self.session.execute(stmt)
        await self.session.commit()

    def _is_agent(self) -> bool:
        return True
