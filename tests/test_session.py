import pytest

from app.database.session import get_db_session


@pytest.mark.asyncio
async def test_get_db_session() -> None:
    generator = get_db_session()
    session = await anext(generator)
    assert session is not None
    await session.close()

    with pytest.raises(StopAsyncIteration):
        await anext(generator)
