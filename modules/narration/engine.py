import logging
from typing import Any, Dict

from modules.narration.agents import (
    ConsistencyAgent,
    ContextAgent,
    EngagementAgent,
    FactVerificationAgent,
    HumanizationAgent,
    QAAgent,
    ScriptPlannerAgent,
    StoryNarratorAgent,
    StyleEnforcementAgent,
)
from modules.narration.exceptions import NarrationException

logger = logging.getLogger(__name__)


class NarrationEngine:
    """Orchestrates the narration generation process using multiple AI agents."""

    def __init__(self) -> None:
        self.planner = ScriptPlannerAgent()
        self.narrator = StoryNarratorAgent()
        self.humanizer = HumanizationAgent()
        self.context_agent = ContextAgent()
        self.consistency = ConsistencyAgent()
        self.engagement = EngagementAgent()
        self.fact_checker = FactVerificationAgent()
        self.style_enforcer = StyleEnforcementAgent()
        self.qa_agent = QAAgent()

    async def generate_script(self, manga_id: int, script_mode: str, style_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main pipeline to generate a full script for a manga.

        Args:
            manga_id: The ID of the manga.
            script_mode: The desired script mode (e.g. "Short", "Complete Manga").
            style_profile: The style configuration.

        Returns:
            A dictionary containing the generated script.
        """
        try:
            logger.info(f"Starting script generation for manga {manga_id} with mode {script_mode}")

            # 1. Plan the script
            plan = await self.planner.execute({"manga_id": manga_id, "script_mode": script_mode})

            # 2. Iterate through scenes (Dummy logic for now)
            generated_scenes = []
            for scene_config in plan.get("scenes", []):
                # Retrieve context
                context = await self.context_agent.execute({"scene_config": scene_config})

                # Narrate
                narration = await self.narrator.execute({"scene": scene_config, "context": context})

                # Check consistency
                await self.consistency.execute({"text": narration.get("text"), "context": context})

                # Humanize and enforce style
                humanized = await self.humanizer.execute({"text": narration.get("text")})
                styled = await self.style_enforcer.execute(
                    {"text": humanized.get("text"), "style_profile": style_profile}
                )

                # Enhance engagement
                engaged = await self.engagement.execute({"text": styled.get("text")})

                # Verify facts
                fact_check = await self.fact_checker.execute({"text": engaged.get("text")})
                if not fact_check.get("is_valid"):
                    logger.warning(f"Fact check failed for scene: {fact_check.get('issues')}")
                    # In a real scenario, we might retry or correct here.

                generated_scenes.append(engaged.get("text"))

            # 3. Final QA
            # Dummy script ID
            qa_result = await self.qa_agent.execute({"script_id": 1})
            if qa_result.get("status") != "approved":
                logger.warning("QA check did not approve the script.")

            logger.info("Script generation completed.")
            return {"status": "success", "script": "Generated script content..."}

        except Exception as e:
            logger.error(f"Failed to generate script: {e}")
            raise NarrationException(f"Pipeline execution failed: {e}") from e
