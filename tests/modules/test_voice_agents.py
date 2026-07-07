import pytest

from modules.voice.agents import (
    AudioCleanupAgent,
    AudioStitchingAgent,
    AudioTimingAgent,
    EmotionAgent,
    PronunciationAgent,
    VoiceGenerationAgent,
)


@pytest.mark.asyncio
async def test_voice_generation_agent():
    agent = VoiceGenerationAgent()
    audio = await agent.generate_speech("Hello", 1, "Neutral", "Normal")
    # Verify we get the mock riff header + payload
    assert b"mock_audio_for: Hello" in audio


@pytest.mark.asyncio
async def test_emotion_agent():
    agent = EmotionAgent()
    assert await agent.determine_emotion("I will kill you") == "Angry"
    assert await agent.determine_emotion("This is a test.") == "Neutral"
    assert await agent.determine_emotion("Wow!") == "Excited"


def test_pronunciation_agent():
    dictionary = {"Gojo": "Go-Jo", "Luffy": "Loo-Fee"}
    agent = PronunciationAgent(dictionary)
    assert agent.apply_pronunciation("Gojo uses domain expansion") == "Go-Jo uses domain expansion"


def test_audio_timing_agent():
    agent = AudioTimingAgent()
    duration_normal = agent.estimate_duration("This is a test.", "Normal")
    duration_fast = agent.estimate_duration("This is a test.", "Fast")
    assert duration_fast < duration_normal


def test_audio_stitching_agent(tmp_path):
    agent = AudioStitchingAgent()
    f1 = tmp_path / "dummy1.wav"
    f2 = tmp_path / "dummy2.wav"
    f1.write_bytes(b"dummy_data_1_long_enough_to_strip")
    f2.write_bytes(b"dummy_data_2_long_enough_to_strip")

    out_file = tmp_path / "out.wav"
    assert agent.merge_audio([str(f1), str(f2)], str(out_file)) is True
    assert out_file.exists()


def test_audio_cleanup_agent(tmp_path):
    agent = AudioCleanupAgent()
    in_file = tmp_path / "in.wav"
    in_file.write_bytes(b"dummy_data")
    out_file = tmp_path / "out.wav"
    assert agent.normalize_audio(str(in_file), str(out_file)) is True
    assert out_file.exists()
