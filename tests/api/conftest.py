import pytest
from app.database.session import get_db_session
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.api.main import app
from app.models.base import Base
from app.models.core import Project


@pytest.fixture
async def db_session() -> AsyncSession:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    Session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with Session() as session:
        # Create a test project to avoid foreign key issues
        p = Project(name="Test Project", status="created")
        session.add(p)
        await session.commit()
        yield session


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncClient:
    app.dependency_overrides[get_db_session] = lambda: db_session
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()
