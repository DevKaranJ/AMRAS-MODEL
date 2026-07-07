from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.api.main import app

client = TestClient(app)


@patch("modules.voice.engine.AudioProductionEngine.process_segments", new_callable=AsyncMock)
def test_generate_audio(mock_process_segments):
    mock_process_segments.return_value = "storage/audio/project/proj_1/part01/master_normalized.wav"

    response = client.post(
        "/audio/generate",
        json={"project_id": 1, "voice_profile_id": 1, "segments": [{"text": "Hello world", "emotion": "Happy"}]},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "master_audio_path" in response.json()


def test_get_voices():
    response = client.get("/audio/voices")
    assert response.status_code == 200
    voices = response.json()
    assert isinstance(voices, list)
    if voices:
        assert "voice_id" in voices[0]


def test_regenerate_audio():
    response = client.post("/audio/regenerate", json={"segment_ids": [1, 2]})
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_normalize_audio():
    response = client.post("/audio/normalize", json={"job_id": 1, "target_lufs": -14.0})
    assert response.status_code == 200
    assert response.json()["status"] == "success"
