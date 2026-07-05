from pathlib import Path
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.models.base import Base
from app.models.manga import ImportJob
from modules.ingestion.agents.collection_agent import CollectionAgent
from modules.ingestion.agents.database_agent import DatabaseAgent
from modules.ingestion.agents.file_system_agent import FileSystemAgent
from modules.ingestion.agents.metadata_agent import MetadataAgent
from modules.ingestion.agents.validation_agent import ValidationAgent

# Use a dedicated test database engine to avoid affecting dev.db
test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)


@pytest_asyncio.fixture
async def setup_db() -> AsyncGenerator[None, None]:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_full_local_import_pipeline(tmp_path: Path, setup_db: None) -> None:
    async with AsyncSession(test_engine) as session:
        # Create a dummy import job
        stmt = insert(ImportJob).values(status="queued").returning(ImportJob.id)
        result_id = await session.execute(stmt)
        job_id = result_id.scalar_one()
        await session.commit()

        metadata_agent = MetadataAgent()
        validation_agent = ValidationAgent()
        file_system_agent = FileSystemAgent()
        database_agent = DatabaseAgent(session)

        agent = CollectionAgent(
            metadata_agent=metadata_agent,
            validation_agent=validation_agent,
            file_system_agent=file_system_agent,
            database_agent=database_agent
        )

        # Create dummy structure
        source_path = tmp_path / "Naruto"
        source_path.mkdir()
        (source_path / "Chapter 1").mkdir()

        agent_result = await agent.process_import(source_path, job_id)
        assert agent_result["status"] == "success"

        # Check job status
        stmt2 = select(ImportJob).where(ImportJob.id == job_id)
        job_result = await session.execute(stmt2)
        job = job_result.scalar_one()

        assert job.status == "completed"
        assert job.progress == 100.0
