from typing import Any, Dict

from app.agents.base import BaseAgent


class OCRAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "OCRAgent"

    @property
    def description(self) -> str:
        return "Extracts dialogue, narration, signs, labels, and background text."

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "dialogue": [
                {
                    "speaker": "Hero",
                    "text": "I'll defeat you.",
                    "confidence": 0.99,
                    "language": "English",
                    "bubble_type": "dialogue",
                }
            ],
            "narration": [{"text": "The battle began.", "type": "narration"}],
        }

    async def validate(self, payload: Dict[str, Any]) -> bool:
        return True

    async def health_check(self) -> bool:
        return True

    async def rollback(self, context_id: str) -> bool:
        return True


class SoundEffectAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "SoundEffectAgent"

    @property
    def description(self) -> str:
        return "Detects sound effects and categorizes them separately from dialogue."

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"sound_effects": [{"text": "BOOM", "category": "sound_effect", "ignore_for_summary": True}]}

    async def validate(self, payload: Dict[str, Any]) -> bool:
        return True

    async def health_check(self) -> bool:
        return True

    async def rollback(self, context_id: str) -> bool:
        return True
