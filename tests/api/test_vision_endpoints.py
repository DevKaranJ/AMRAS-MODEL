from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.main import app as main_app
from app.database.session import get_db_session
from app.models.base import Base


@pytest.fixture
async def client() -> Any:
    # Setup in memory DB with schema
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db_session() -> Any:
        async with session_maker() as session:
            # Need a page_id=1 for ForeignKey constraints if needed
            from sqlalchemy import text

            await session.execute(
                text("INSERT INTO mangas (id, title, slug, status) VALUES (1, 'Test', 'test', 'ongoing')")
            )
            await session.execute(
                text("INSERT INTO chapters (id, manga_id, chapter_number, page_count, imported) VALUES (1, 1, 1, 1, 1)")
            )
            await session.execute(
                text("INSERT INTO pages (id, chapter_id, page_number, image_path) VALUES (1, 1, 1, 'test.png')")
            )

            # Need a panel for get operations to succeed smoothly without empty joins
            from sqlalchemy import insert

            from app.models.vision import Panel

            await session.execute(insert(Panel).values(page_id=1, panel_number=1, reading_order=1, bounding_box={}))

            await session.commit()

            yield session

    main_app.dependency_overrides[get_db_session] = override_get_db_session

    async with AsyncClient(transport=ASGITransport(app=main_app), base_url="http://test") as ac:
        yield ac

    main_app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_process_vision(client: AsyncClient) -> None:
    response = await client.post("/vision/process", json={"page_id": 1})
    assert response.status_code == 202
    data = response.json()
    assert data["message"] == "Vision job queued"
    assert data["page_id"] == 1
    assert "job_id" in data


@pytest.mark.asyncio
async def test_get_page_vision(client: AsyncClient) -> None:
    response = await client.get("/vision/page/1")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert "panels" in data


@pytest.mark.asyncio
async def test_process_ocr(client: AsyncClient) -> None:
    response = await client.post("/ocr/process", json={"page_id": 1})
    assert response.status_code == 202
    data = response.json()
    assert data["message"] == "OCR job queued"
    assert data["page_id"] == 1


@pytest.mark.asyncio
async def test_list_panels(client: AsyncClient) -> None:
    response = await client.get("/vision/panels?page_id=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["panel_number"] == 1


@pytest.mark.asyncio
async def test_list_characters(client: AsyncClient) -> None:
    response = await client.get("/vision/characters?page_id=1")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_sound_effects(client: AsyncClient) -> None:
    response = await client.get("/vision/sound-effects?page_id=1")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_debug_overlay(client: AsyncClient) -> None:
    response = await client.get("/vision/debug/1")
    assert response.status_code == 200
    data = response.json()
    assert "overlay_url" in data
