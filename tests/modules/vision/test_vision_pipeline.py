from typing import Any

import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models.base import Base
from app.models.vision import CharacterDetected, Panel
from modules.vision.pipeline import VisionPipeline


@pytest.fixture
async def async_session() -> Any:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    async with session_maker() as session:
        await session.execute(
            text("INSERT INTO mangas (id, title, slug, status) VALUES (1, 'Test', 'test', 'ongoing')")
        )
        await session.execute(
            text("INSERT INTO chapters (id, manga_id, chapter_number, page_count, imported) VALUES (1, 1, 1, 1, 1)")
        )
        await session.execute(
            text("INSERT INTO pages (id, chapter_id, page_number, image_path) VALUES (1, 1, 1, 'test.png')")
        )
        await session.commit()
        yield session


@pytest.mark.asyncio
async def test_vision_pipeline_execute(async_session: Any) -> None:
    pipeline = VisionPipeline()
    res = await pipeline.execute(1, 1, async_session)
    assert res["status"] == "success"

    panels = (await async_session.execute(select(Panel))).scalars().all()
    assert len(panels) == 1

    chars = (await async_session.execute(select(CharacterDetected))).scalars().all()
    assert len(chars) == 1
    assert chars[0].identity_estimate == "Hero"
