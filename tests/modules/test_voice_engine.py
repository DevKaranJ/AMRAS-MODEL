import os
from unittest.mock import AsyncMock, MagicMock

import pytest

from modules.voice.engine import AudioProductionEngine


@pytest.fixture
def db_session_mock():
    mock = MagicMock()
    # Mock the execute/scalars/all chain for _get_pronunciation_dict
    result_mock = MagicMock()
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = []
    result_mock.scalars.return_value = scalars_mock

    mock.execute = AsyncMock(return_value=result_mock)
    mock.commit = AsyncMock()
    mock.refresh = AsyncMock()
    return mock


@pytest.fixture
def engine(db_session_mock):
    return AudioProductionEngine(db=db_session_mock)


@pytest.mark.asyncio
async def test_engine_process_segments(engine, tmp_path):
    engine.storage_base_path = str(tmp_path)

    segments = [
        {"text": "Hello world", "emotion": "Happy", "scene_id": "scene1"},
        {"text": "This is a test", "scene_id": "scene2"},
    ]

    master_file = await engine.process_segments(project_id=1, segments=segments, voice_profile_id=1)

    assert os.path.exists(master_file)
    assert master_file.endswith("master_normalized.wav")
    assert engine.db.add.called
    assert engine.db.commit.called


@pytest.mark.asyncio
async def test_engine_empty_segments(engine, tmp_path):
    engine.storage_base_path = str(tmp_path)
    segments = [{"text": "", "scene_id": "scene1"}]
    master_file = await engine.process_segments(project_id=1, segments=segments, voice_profile_id=1)

    assert os.path.exists(master_file)
