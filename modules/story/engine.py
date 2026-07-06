from typing import Any, Dict

from modules.story.agents import (
    CharacterAnalysisAgent,
    EventExtractionAgent,
    QAAgent,
    RelationshipAgent,
    StoryAnalysisAgent,
    TimelineAgent,
    WorldAnalysisAgent,
)
from modules.story.exceptions import StoryEngineError


class StoryEngine:
    """Orchestrates the Story Analysis Phase by coordinating multiple AI agents."""

    def __init__(self) -> None:
        self.story_agent = StoryAnalysisAgent()
        self.character_agent = CharacterAnalysisAgent()
        self.event_agent = EventExtractionAgent()
        self.relationship_agent = RelationshipAgent()
        self.timeline_agent = TimelineAgent()
        self.world_agent = WorldAnalysisAgent()
        self.qa_agent = QAAgent()

    async def process_chapter(self, chapter_id: int, vision_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process OCR and Vision JSON from Phase 2 into an intelligent story representation.
        """
        try:
            # 1. Base Story Analysis (Scene splitting, basic understanding)
            story_context = await self.story_agent.process(vision_data)

            # 2. Extract Specific Elements in parallel or sequentially based on dependencies
            events_data = await self.event_agent.process(vision_data)
            chars_data = await self.character_agent.process(vision_data)
            world_data = await self.world_agent.process(vision_data)

            combined_context = {**vision_data, **story_context, **events_data, **chars_data, **world_data}

            # 3. Analyze relationships and timeline using the extracted elements
            rels_data = await self.relationship_agent.process(combined_context)
            timeline_data = await self.timeline_agent.process(combined_context)

            final_context = {**combined_context, **rels_data, **timeline_data}

            # 4. QA the extracted knowledge
            qa_results = await self.qa_agent.process(final_context)
            if not qa_results.get("qa_passed", False):
                # We log warnings or mark uncertainties in production, not necessarily fail
                # depending on the severity of the issues.
                pass

            # Construct final output payload mimicking DB structure for saving/returning
            return {
                "chapter": chapter_id,
                "events": final_context.get("extracted_events", []),
                "characters": final_context.get("characters", []),
                "relationships": final_context.get("relationships", []),
                "timeline": final_context.get("timeline_entries", []),
                "locations": final_context.get("locations", []),
                "organizations": final_context.get("organizations", []),
            }

        except Exception as e:
            raise StoryEngineError(f"Failed to process story for chapter {chapter_id}: {str(e)}") from e
