from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class TTSProviderInterface(ABC):
    """Abstract interface for TTS providers.

    Implement this interface to add new TTS providers:
    - EdgeTTSProvider (free, current)
    - ElevenLabsProvider (paid, high quality)
    - OpenAITTSProvider (paid, good quality)
    - CoquiProvider (free, local, requires GPU)
    """

    @abstractmethod
    async def generate_speech(
        self,
        text: str,
        voice_id: str,
        model: Optional[str] = None,
        speed: float = 1.0,
    ) -> bytes:
        """Generate speech audio from text.

        Args:
            text: Text to convert to speech
            voice_id: Voice identifier (emotion name or specific voice ID)
            model: Optional model override
            speed: Speed multiplier (0.5 = half, 1.0 = normal, 2.0 = double)

        Returns:
            Audio data as bytes (format depends on provider)
        """
        pass

    @abstractmethod
    async def list_voices(self, language: Optional[str] = None) -> List[Dict[str, str]]:
        """List available voices.

        Args:
            language: Optional language filter

        Returns:
            List of voice info dicts with at least 'name' and 'gender' keys
        """
        pass

    @abstractmethod
    def get_supported_emotions(self) -> List[str]:
        """Get list of supported emotion presets."""
        pass

    async def generate_speech_segments(
        self,
        segments: List[Dict[str, Any]],
        output_dir: str,
    ) -> List[str]:
        """Generate speech for multiple segments. Default implementation calls generate_speech."""
        from pathlib import Path

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

        return audio_files


class TTSProviderFactory:
    """Factory to create TTS providers based on configuration."""

    _providers: Dict[str, type] = {}

    @classmethod
    def register(cls, name: str, provider_class: type) -> None:
        cls._providers[name] = provider_class

    @classmethod
    def create(cls, name: str, **kwargs: Any) -> TTSProviderInterface:
        if name not in cls._providers:
            raise ValueError(
                f"Unknown TTS provider: {name}. "
                f"Available: {list(cls._providers.keys())}"
            )
        return cls._providers[name](**kwargs)

    @classmethod
    def list_providers(cls) -> List[str]:
        return list(cls._providers.keys())


# Register built-in providers
def _register_builtin_providers() -> None:
    from app.shared.providers.edge_tts_provider import EdgeTTSProvider

    TTSProviderFactory.register("edge", EdgeTTSProvider)

    # Future providers can be registered here:
    # TTSProviderFactory.register("elevenlabs", ElevenLabsProvider)
    # TTSProviderFactory.register("openai", OpenAITTSProvider)


_register_builtin_providers()
