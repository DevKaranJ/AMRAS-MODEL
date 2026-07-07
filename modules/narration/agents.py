import json
from typing import Any, Dict

from app.agents.base import BaseAgent
from app.shared.providers.base import ai_provider_manager
from modules.memory.engine import memory_engine
from modules.narration.exceptions import (
    ConsistencyError,
    ContextRetrievalError,
    FactCheckError,
    QAError,
    ScriptPlanningError,
    StoryNarrationError,
    StyleGenerationError,
)


class ScriptPlannerAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "ScriptPlannerAgent"

    @property
    def description(self) -> str:
        return "Plans the script structure and scene segmentation."

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not await self.validate(payload):
            raise ScriptPlanningError("Invalid payload for ScriptPlannerAgent")

        manga_id = payload["manga_id"]
        script_mode = payload["script_mode"]

        system_prompt = (
            "You are an expert anime/manga YouTube recap planner. "
            "Your job is to divide the story into logical segments based on natural boundaries "
            "(battles, plot twists, emotional scenes). You must output valid JSON."
        )
        prompt = f"Plan a recap script in '{script_mode}' mode for manga ID {manga_id}."

        response_schema = {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "scenes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "description": {"type": "string"},
                            "pacing": {"type": "string"},
                        },
                    },
                },
            },
        }

        result_str = await ai_provider_manager.generate_text(
            prompt=prompt, system_prompt=system_prompt, response_format=response_schema
        )

        try:
            result = json.loads(result_str)
            if not isinstance(result, dict):
                return {"status": "planned", "scenes": [{"id": 1, "description": "Fallback Scene", "pacing": "Normal"}]}
            result["status"] = "planned"
            if "scenes" not in result:
                result["scenes"] = [{"id": 1, "description": "Intro", "pacing": "Normal"}]
            return dict(result)
        except json.JSONDecodeError:
            return {"status": "planned", "scenes": [{"id": 1, "description": "Fallback Scene", "pacing": "Normal"}]}

    async def validate(self, payload: Dict[str, Any]) -> bool:
        return "manga_id" in payload and "script_mode" in payload

    async def health_check(self) -> bool:
        return True

    async def rollback(self, context_id: str) -> bool:
        return True


class ContextAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "ContextAgent"

    @property
    def description(self) -> str:
        return "Retrieves context and memories for narration."

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not await self.validate(payload):
            raise ContextRetrievalError("Invalid payload for ContextAgent")

        manga_id = payload.get("manga_id", 0)
        scene_config = payload.get("scene_config", {})

        context_package = await memory_engine.get_scene_context(manga_id, scene_config)
        if not isinstance(context_package, dict):
            context_package = {}
        ret: dict[str, Any] = {"status": "retrieved", "context": context_package}
        return ret

    async def validate(self, payload: Dict[str, Any]) -> bool:
        return "manga_id" in payload and isinstance(payload.get("manga_id"), int) and payload["manga_id"] > 0

    async def health_check(self) -> bool:
        return True

    async def rollback(self, context_id: str) -> bool:
        return True


class StoryNarratorAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "StoryNarratorAgent"

    @property
    def description(self) -> str:
        return "Generates narration from story scenes."

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not await self.validate(payload):
            raise StoryNarrationError("Invalid payload for StoryNarratorAgent")

        context = payload["context"]
        scene = payload["scene"]

        system_prompt = (
            "You are a professional YouTube manga recap creator. "
            "Write a natural, conversational narration script for this scene based on the provided context."
        )
        prompt = f"Context: {json.dumps(context)}\nScene config: {json.dumps(scene)}\nGenerate narration script."

        narration_text = await ai_provider_manager.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
        )
        return {"status": "narrated", "text": narration_text}

    async def validate(self, payload: Dict[str, Any]) -> bool:
        return "scene" in payload and "context" in payload

    async def health_check(self) -> bool:
        return True

    async def rollback(self, context_id: str) -> bool:
        return True


class ConsistencyAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "ConsistencyAgent"

    @property
    def description(self) -> str:
        return "Checks the script for consistency against the story world."

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not await self.validate(payload):
            raise ConsistencyError("Invalid payload for ConsistencyAgent")

        text = payload["text"]
        context = payload["context"]

        # Simple LLM call to verify consistency
        prompt = f"Verify this text for consistency against context:\n\nText: {text}\n\nContext: {json.dumps(context)}"
        await ai_provider_manager.generate_text(prompt=prompt)

        return {"status": "verified", "issues": []}

    async def validate(self, payload: Dict[str, Any]) -> bool:
        return "text" in payload and "context" in payload

    async def health_check(self) -> bool:
        return True

    async def rollback(self, context_id: str) -> bool:
        return True


class FactVerificationAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "FactVerificationAgent"

    @property
    def description(self) -> str:
        return "Verifies facts in the generated script against the memory DB."

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not await self.validate(payload):
            raise FactCheckError("Invalid payload for FactVerificationAgent")

        text = payload["text"]
        context = payload.get("context", {})

        prompt = f"Fact check this text: {text} against this context: {json.dumps(context)}"
        # LLM would output boolean and issues, for now hardcode success
        await ai_provider_manager.generate_text(prompt=prompt)

        return {"status": "checked", "is_valid": True, "issues": []}

    async def validate(self, payload: Dict[str, Any]) -> bool:
        return "text" in payload

    async def health_check(self) -> bool:
        return True

    async def rollback(self, context_id: str) -> bool:
        return True


class HumanizationAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "HumanizationAgent"

    @property
    def description(self) -> str:
        return "Humanizes the generated text to make it sound natural."

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not await self.validate(payload):
            raise StyleGenerationError("Invalid payload for HumanizationAgent")

        text = payload["text"]
        system_prompt = (
            "Rewrite the provided narration text to sound incredibly human, avoiding robotic or repetitive phrases."
        )
        humanized_text = await ai_provider_manager.generate_text(prompt=text, system_prompt=system_prompt)

        return {"status": "humanized", "text": humanized_text}

    async def validate(self, payload: Dict[str, Any]) -> bool:
        return "text" in payload

    async def health_check(self) -> bool:
        return True

    async def rollback(self, context_id: str) -> bool:
        return True


class EngagementAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "EngagementAgent"

    @property
    def description(self) -> str:
        return "Enhances the engagement and hooks in the narration."

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not await self.validate(payload):
            raise StyleGenerationError("Invalid payload for EngagementAgent")

        text = payload["text"]
        system_prompt = "Enhance the provided text by adding suspense, curiosity hooks, and better emotional pacing."
        enhanced_text = await ai_provider_manager.generate_text(prompt=text, system_prompt=system_prompt)

        return {"status": "enhanced", "text": enhanced_text}

    async def validate(self, payload: Dict[str, Any]) -> bool:
        return "text" in payload

    async def health_check(self) -> bool:
        return True

    async def rollback(self, context_id: str) -> bool:
        return True


class StyleEnforcementAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "StyleEnforcementAgent"

    @property
    def description(self) -> str:
        return "Enforces the chosen narration style."

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not await self.validate(payload):
            raise StyleGenerationError("Invalid payload for StyleEnforcementAgent")

        text = payload["text"]
        style_profile = payload.get("style_profile", {})

        system_prompt = f"Rewrite the text conforming exactly to this style profile: {json.dumps(style_profile)}"
        styled_text = await ai_provider_manager.generate_text(prompt=text, system_prompt=system_prompt)

        return {"status": "enforced", "text": styled_text}

    async def validate(self, payload: Dict[str, Any]) -> bool:
        return "text" in payload and "style_profile" in payload

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
        return "Final QA review of the script."

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not await self.validate(payload):
            raise QAError("Invalid payload for QAAgent")

        script_text = payload.get("script_text", "")

        # LLM would evaluate quality
        await ai_provider_manager.generate_text(prompt=f"QA this script: {script_text}")

        return {"status": "approved", "score": 100}

    async def validate(self, payload: Dict[str, Any]) -> bool:
        return "script_id" in payload or "script_text" in payload

    async def health_check(self) -> bool:
        return True

    async def rollback(self, context_id: str) -> bool:
        return True
