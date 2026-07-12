from typing import Any

from app.core.exceptions import AmrasException


class VoiceGenerationError(AmrasException):
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            error_code="VOICE_GENERATION_FAILED",
            message=message,
            debug_details=details,
            retryable=True,
            recovery_suggestion="Check TTS provider connection and retry.",
        )


class AudioStitchingError(AmrasException):
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            error_code="AUDIO_STITCHING_FAILED",
            message=message,
            debug_details=details,
            retryable=False,
            recovery_suggestion="Ensure input audio files exist and are valid.",
        )


class NormalizationError(AmrasException):
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            error_code="AUDIO_NORMALIZATION_FAILED",
            message=message,
            debug_details=details,
            retryable=False,
            recovery_suggestion="Check audio format and parameters.",
        )


class VoiceProfileNotFoundError(AmrasException):
    def __init__(self, voice_id: str):
        super().__init__(
            error_code="VOICE_PROFILE_NOT_FOUND",
            message=f"Voice profile with ID {voice_id} not found.",
            retryable=False,
            recovery_suggestion="Select a valid voice profile.",
        )
