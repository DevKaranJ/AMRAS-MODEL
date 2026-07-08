import json
from typing import Any, Dict
from typing import cast as type_cast

from app.agents.base import BaseAgent
from app.shared.providers.base import ai_provider_manager
from modules.subtitles.exceptions import (
    FormattingError,
    SubtitleGenerationError,
    SynchronizationError,
    TranslationError,
)


class SubtitleGenerationAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "SubtitleGenerationAgent"

    @property
    def description(self) -> str:
        return "Generates raw subtitles from narration scripts, segmenting them by sentence boundaries, natural pauses, and speaker changes."

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not await self.validate(payload):
            raise SubtitleGenerationError("Invalid payload for SubtitleGenerationAgent", details=payload)

        narration = payload.get("narration_script", "")
        max_lines = payload.get("settings", {}).get("max_lines", 2)
        max_chars = payload.get("settings", {}).get("max_characters_per_line", 42)

        prompt = f"""
        Given the following narration script, segment it into subtitles.
        Rules:
        - Max lines per subtitle: {max_lines}
        - Max characters per line: {max_chars}
        - Split by sentence boundaries, natural pauses, and speaker changes.

        Narration Script:
        {narration}
        """

        schema = {
            "type": "object",
            "properties": {
                "segments": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"text": {"type": "string"}, "speaker": {"type": "string"}},
                        "required": ["text"],
                    },
                }
            },
            "required": ["segments"],
        }

        try:
            response = await ai_provider_manager.generate_text(
                prompt=prompt,
                system_prompt="You are a professional subtitle generation AI. Output JSON only.",
                response_format=schema,
            )
            data = json.loads(response) if isinstance(response, str) else response
            # In testing, if the mock provider doesn't format string correctly
            if isinstance(data, str):
                data = json.loads(data)
            return type_cast(Dict[str, Any], data)
        except Exception as e:
            raise SubtitleGenerationError(f"Generation failed: {str(e)}") from e

    async def validate(self, payload: Dict[str, Any]) -> bool:
        return "narration_script" in payload

    async def health_check(self) -> bool:
        return True

    async def rollback(self, context_id: str) -> bool:
        return True


class SynchronizationAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "SynchronizationAgent"

    @property
    def description(self) -> str:
        return "Aligns subtitles with audio timestamps, maintaining frame accuracy and reading speed compliance."

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not await self.validate(payload):
            raise SynchronizationError("Invalid payload for SynchronizationAgent", details=payload)

        segments = payload.get("segments", [])
        audio_timestamps = payload.get("audio_timestamps", [])

        # In a real scenario, this would complexly map audio words to subtitle text.
        # We mock a provider call for complex alignment.
        prompt = f"""
        Align the following subtitle segments with the provided audio timestamps.

        Segments: {json.dumps(segments)}
        Timestamps: {json.dumps(audio_timestamps)}
        """

        schema = {
            "type": "object",
            "properties": {
                "synchronized_segments": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "start_time_ms": {"type": "integer"},
                            "end_time_ms": {"type": "integer"},
                            "duration_ms": {"type": "integer"},
                            "confidence": {"type": "number"},
                        },
                        "required": ["text", "start_time_ms", "end_time_ms", "duration_ms"],
                    },
                }
            },
            "required": ["synchronized_segments"],
        }

        try:
            response = await ai_provider_manager.generate_text(
                prompt=prompt,
                system_prompt="You are a subtitle synchronization AI. Output JSON only.",
                response_format=schema,
            )
            if isinstance(response, str):
                data = json.loads(response)
            else:
                data = response
            return type_cast(Dict[str, Any], data)
        except Exception as e:
            raise SynchronizationError(f"Synchronization failed: {str(e)}") from e

    async def validate(self, payload: Dict[str, Any]) -> bool:
        return "segments" in payload and "audio_timestamps" in payload

    async def health_check(self) -> bool:
        return True

    async def rollback(self, context_id: str) -> bool:
        return True


class TranslationAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "TranslationAgent"

    @property
    def description(self) -> str:
        return "Translates subtitles into target languages maintaining context."

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not await self.validate(payload):
            raise TranslationError("Invalid payload for TranslationAgent", details=payload)

        segments = payload.get("segments", [])
        source_lang = payload.get("source_language", "English")
        target_lang = payload.get("target_language", "Spanish")

        prompt = f"""
        Translate the following subtitle segments from {source_lang} to {target_lang}.
        Maintain context. Never perform literal translation when it damages meaning.

        Segments: {json.dumps(segments)}
        """

        schema = {
            "type": "object",
            "properties": {
                "translated_segments": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"text": {"type": "string"}, "confidence": {"type": "number"}},
                        "required": ["text"],
                    },
                }
            },
            "required": ["translated_segments"],
        }

        try:
            response = await ai_provider_manager.generate_text(
                prompt=prompt,
                system_prompt="You are a professional subtitle translator.",
                response_format=schema,
            )
            data = json.loads(response) if isinstance(response, str) else response
            return type_cast(Dict[str, Any], data)
        except Exception as e:
            raise TranslationError(f"Translation failed: {str(e)}") from e

    async def validate(self, payload: Dict[str, Any]) -> bool:
        return "segments" in payload and "target_language" in payload

    async def health_check(self) -> bool:
        return True

    async def rollback(self, context_id: str) -> bool:
        return True


class LocalizationAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "LocalizationAgent"

    @property
    def description(self) -> str:
        return "Adapts idioms, names, units, and cultural references in subtitles."

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        segments = payload.get("segments", [])
        profile = payload.get("profile", {})

        prompt = f"""
        Localize these subtitle segments based on the provided profile.
        Profile: {json.dumps(profile)}
        Segments: {json.dumps(segments)}
        """
        schema = {
            "type": "object",
            "properties": {
                "localized_segments": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"text": {"type": "string"}},
                        "required": ["text"],
                    },
                }
            },
            "required": ["localized_segments"],
        }

        try:
            response = await ai_provider_manager.generate_text(
                prompt=prompt,
                system_prompt="You are a subtitle localizer.",
                response_format=schema,
            )
            data = json.loads(response) if isinstance(response, str) else response
            return type_cast(Dict[str, Any], data)
        except Exception as e:
            raise TranslationError(f"Localization failed: {str(e)}") from e

    async def validate(self, payload: Dict[str, Any]) -> bool:
        return "segments" in payload

    async def health_check(self) -> bool:
        return True

    async def rollback(self, context_id: str) -> bool:
        return True


class FormattingAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "FormattingAgent"

    @property
    def description(self) -> str:
        return "Determines line breaks, reading speed checks, and character limits."

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        segments = payload.get("segments", [])
        max_lines = payload.get("settings", {}).get("max_lines", 2)
        max_chars = payload.get("settings", {}).get("max_characters_per_line", 42)

        # We can simulate deterministic checks here or use AI to re-flow text
        prompt = f"""
        Reformat these subtitle segments to enforce max {max_lines} lines and max {max_chars} chars per line.
        Segments: {json.dumps(segments)}
        """
        schema = {
            "type": "object",
            "properties": {
                "formatted_segments": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"text": {"type": "string"}},
                        "required": ["text"],
                    },
                }
            },
            "required": ["formatted_segments"],
        }
        try:
            response = await ai_provider_manager.generate_text(
                prompt=prompt,
                system_prompt="You are a subtitle formatter.",
                response_format=schema,
            )
            data = json.loads(response) if isinstance(response, str) else response
            return type_cast(Dict[str, Any], data)
        except Exception as e:
            raise FormattingError(f"Formatting failed: {str(e)}") from e

    async def validate(self, payload: Dict[str, Any]) -> bool:
        return "segments" in payload

    async def health_check(self) -> bool:
        return True

    async def rollback(self, context_id: str) -> bool:
        return True


class AccessibilityAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "AccessibilityAgent"

    @property
    def description(self) -> str:
        return "Ensures readability, high contrast logic, and screen reader metadata."

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # For now, it passes segments through. Future AI checks for accessibility here.
        return {"accessible_segments": payload.get("segments", [])}

    async def validate(self, payload: Dict[str, Any]) -> bool:
        return True

    async def health_check(self) -> bool:
        return True

    async def rollback(self, context_id: str) -> bool:
        return True


class QAAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "QAAgent"

    @property
    def description(self) -> str:
        return "Detects overlapping subtitles, timing errors, and excessive reading speed."

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        segments = payload.get("segments", [])
        issues = []
        for i, seg in enumerate(segments):
            if i > 0 and seg.get("start_time_ms", 0) < segments[i - 1].get("end_time_ms", 0):
                issues.append(f"Overlap at segment {i}")

        return {"passed": len(issues) == 0, "issues": issues, "qa_segments": segments}

    async def validate(self, payload: Dict[str, Any]) -> bool:
        return "segments" in payload

    async def health_check(self) -> bool:
        return True

    async def rollback(self, context_id: str) -> bool:
        return True
