from typing import Any

import pytest
from sqlalchemy import insert, select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models.base import Base
from app.models.vision import Narration, Panel, SoundEffect, SpeechBubble
from modules.ocr.pipeline import OCRPipeline


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

        # Need a panel for OCR to attach to
        stmt = insert(Panel).values(page_id=1, panel_number=1, reading_order=1, bounding_box={})
        await session.execute(stmt)

        await session.commit()
        yield session


@pytest.mark.asyncio
async def test_ocr_pipeline_execute(async_session: Any) -> None:
    pipeline = OCRPipeline()
    res = await pipeline.execute(1, 1, async_session)
    assert res["status"] == "success"

    bubbles = (await async_session.execute(select(SpeechBubble))).scalars().all()
    assert len(bubbles) == 1
    assert bubbles[0].speaker == "Hero"

    narrations = (await async_session.execute(select(Narration))).scalars().all()
    assert len(narrations) == 1

    sfx = (await async_session.execute(select(SoundEffect))).scalars().all()
    assert len(sfx) == 1
