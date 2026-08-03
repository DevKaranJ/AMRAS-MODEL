import asyncio
import io
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import edge_tts

from app.core.logger import get_logger
from app.shared.providers.base import AIProviderInterface

logger = get_logger("amras.providers.edge_tts")


class EdgeTTSProvider(AIProviderInterface):
    """Free TTS provider using Microsoft Edge's online TTS service."""

    # Voice mapping for different emotions
    EMOTION_VOICES = {
        "neutral": "en-US-GuyNeural",
        "narrator": "en-US-GuyNeural",
        "happy": "en-US-AriaNeural",
        "sad": "en-US-AmandaNeural",
        "angry": "en-US-DavisNeural",
        "excited": "en-US-JennyNeural",
        "suspense": "en-US-GuyNeural",
        "serious": "en-US-DavisNeural",
        "dramatic": "en-US-DavisNeural",
    }

    # Japanese voices for manga
    JAPANESE_VOICES = {
        "neutral": "ja-JP-KeitaNeural",
        "narrator": "ja-JP-KeitaNeural",
        "female": "ja-JP-NanamiNeural",
        "male": "ja-JP-KeitaNeural",
    }

    def __init__(
        self,
        default_voice: str = "en-US-GuyNeural",
        default_rate: str = "+0%",
        default_volume: str = "+0%",
    ) -> None:
        self._default_voice = default_voice
        self._default_rate = default_rate
        self._default_volume = default_volume
        logger.info("edge_tts_provider_initialized", default_voice=default_voice)

    def _get_voice_for_emotion(self, emotion: str, language: str = "en") -> str:
        """Get the appropriate voice for the given emotion and language."""
        if language.startswith("ja"):
            return self.JAPANESE_VOICES.get(emotion, self.JAPANESE_VOICES["neutral"])
        return self.EMOTION_VOICES.get(emotion.lower(), self._default_voice)

    def _get_rate_string(self, speed: float) -> str:
        """Convert speed multiplier to Edge TTS rate string."""
        # Edge TTS uses percentage: +0%, +20%, -10%, etc.
        percentage = int((speed - 1.0) * 100)
        if percentage >= 0:
            return f"+{percentage}%"
        return f"{percentage}%"

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Edge TTS doesn't support text generation - use OpenRouter instead."""
        raise NotImplementedError(
            "Edge TTS doesn't support text generation. Use OpenRouterProvider for text."
        )

    async def generate_speech(
        self,
        text: str,
        voice_id: str,
        model: Optional[str] = None,
        speed: float = 1.0,
    ) -> bytes:
        """Generate speech using Edge TTS.

        Args:
            text: Text to convert to speech
            voice_id: Voice ID or emotion (e.g., "neutral", "happy", "ja-JP-KeitaNeural")
            model: Not used (Edge TTS handles model selection)
            speed: Speed multiplier (0.5 = half speed, 2.0 = double speed)

        Returns:
            Audio data as bytes (MP3 format)
        """
        # Determine voice
        if voice_id in self.EMOTION_VOICES or voice_id in self.JAPANESE_VOICES:
            voice = self._get_voice_for_emotion(voice_id)
        else:
            voice = voice_id  # Use as-is if it's a specific voice name

        rate = self._get_rate_string(speed)

        logger.info(
            "generating_speech",
            text_length=len(text),
            voice=voice,
            rate=rate,
        )

        try:
            communicate = edge_tts.Communicate(text, voice, rate=rate)
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]

            logger.info(
                "speech_generated",
                audio_size=len(audio_data),
                voice=voice,
            )
            return audio_data

        except Exception as e:
            logger.error("speech_generation_failed", error=str(e))
            raise

    async def generate_speech_segments(
        self,
        segments: List[Dict[str, Any]],
        output_dir: str,
    ) -> List[str]:
        """Generate speech for multiple segments and save to files.

        Args:
            segments: List of dicts with 'text', 'emotion', 'speed' keys
            output_dir: Directory to save audio files

        Returns:
            List of file paths to generated audio files
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        audio_files = []
        for i, segment in enumerate(segments):
            text = segment.get("text", "")
            emotion = segment.get("emotion", "neutral")
            speed = segment.get("speed", 1.0)

            if not text.strip():
                continue

            audio_data = await self.generate_speech(
                text=text,
                voice_id=emotion,
                speed=speed,
            )

            file_path = output_path / f"segment_{i:04d}.mp3"
            file_path.write_bytes(audio_data)
            audio_files.append(str(file_path))

            logger.info("segment_generated", index=i, file=str(file_path))

        return audio_files

    async def list_voices(self, language: Optional[str] = None) -> List[Dict[str, str]]:
        """List available Edge TTS voices.

        Args:
            language: Optional language filter (e.g., "en", "ja")

        Returns:
            List of voice info dicts
        """
        voices = await edge_tts.list_voices()

        if language:
            voices = [v for v in voices if v["Locale"].startswith(language)]

        return [
            {
                "name": v["ShortName"],
                "gender": v["Gender"],
                "locale": v["Locale"],
                "friendly_name": v["FriendlyName"],
            }
            for v in voices
        ]

    def get_supported_emotions(self) -> List[str]:
        """Get list of supported emotion presets."""
        return list(self.EMOTION_VOICES.keys())
