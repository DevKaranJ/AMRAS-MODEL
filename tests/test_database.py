from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.models.base import Base
from app.models.core import Project

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def async_engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture
async def async_session(async_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    session_maker = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)
    async with session_maker() as session:
        yield session

@pytest.mark.asyncio
async def test_database_connection(async_session: AsyncSession) -> None:
    result = await async_session.execute(text("SELECT 1"))
    assert result.scalar() == 1

@pytest.mark.asyncio
async def test_migration_and_rollback(async_session: AsyncSession) -> None:
    # Test that we can insert a project
    new_project = Project(name="Test Project", description="A test project")
    async_session.add(new_project)
    await async_session.commit()

    # Retrieve it
    result = await async_session.execute(text("SELECT name FROM projects WHERE id = 1"))
    assert result.scalar() == "Test Project"

    # Test Rollback
    try:
        async with async_session.begin_nested():
            failed_project = Project(name=None)
            async_session.add(failed_project)
            await async_session.flush() # Force flush to DB to trigger constraint violation
    except Exception:
        pass

    # Verify rollback by checking count
    result = await async_session.execute(text("SELECT COUNT(*) FROM projects"))
    assert result.scalar() == 1
