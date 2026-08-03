"""Real story analysis agents using LLM via OpenRouter.

Each agent extracts specific story elements from manga chapters
using structured prompts and JSON output parsing.
"""

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.core.logger import get_logger
from app.shared.providers.base import ai_provider_manager

logger = get_logger("amras.story.agents")


class BaseStoryAgent(ABC):
    """Base class for story analysis agents."""

    @abstractmethod
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input context and return extracted story elements."""
        pass

    async def _call_llm(
        self,
        prompt: str,
        system_prompt: str,
        response_schema: Optional[Dict[str, Any]] = None,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """Call the LLM provider with structured output."""
        try:
            response = await ai_provider_manager.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                response_format=response_schema,
                temperature=temperature,
            )

            # Parse JSON response
            if isinstance(response, str):
                result = json.loads(response)
            else:
                result = response

            return result

        except json.JSONDecodeError as e:
            logger.warning("json_parse_failed", error=str(e))
            return {"error": "Failed to parse LLM response", "raw": response}
        except Exception as e:
            logger.error("llm_call_failed", error=str(e))
            return {"error": str(e)}


class StoryAnalysisAgent(BaseStoryAgent):
    """Analyzes manga chapter to understand the overall story."""

    SYSTEM_PROMPT = """You are an expert manga story analyst. Analyze the provided chapter data 
and extract the key story elements. Be concise and focus on what's important for a YouTube recap video.

Output JSON with this structure:
{
    "title": "Chapter title or summary",
    "summary": "2-3 sentence summary of what happens",
    "themes": ["action", "drama", etc],
    "tone": "serious/humorous/dramatic",
    "key_moments": [
        {"moment": "description", "importance": 0.0-1.0}
    ],
    "hook": "One sentence hook for the video intro"
}"""

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze story from chapter data.

        Context should contain:
            - chapter_data: dict with OCR text, panel info, etc.
            - previous_context: optional, from previous chapters
        """
        chapter_data = context.get("chapter_data", {})
        previous_context = context.get("previous_context", {})

        # Build prompt from available data
        prompt_parts = []

        if chapter_data.get("ocr_text"):
            prompt_parts.append(f"Chapter text content:\n{chapter_data['ocr_text'][:2000]}")

        if chapter_data.get("panels"):
            panel_count = len(chapter_data["panels"])
            prompt_parts.append(f"Number of panels: {panel_count}")

        if chapter_data.get("scene_types"):
            scenes = chapter_data["scene_types"]
            prompt_parts.append(f"Scene types detected: {', '.join(scenes[:10])}")

        if previous_context.get("summary"):
            prompt_parts.append(f"Previous chapters summary: {previous_context['summary'][:500]}")

        if not prompt_parts:
            prompt_parts.append("No detailed chapter data available. Create a general analysis.")

        prompt = "\n\n".join(prompt_parts)

        result = await self._call_llm(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.7,
        )

        # Ensure required fields
        result.setdefault("title", "Untitled Chapter")
        result.setdefault("summary", "No summary available")
        result.setdefault("themes", [])
        result.setdefault("tone", "neutral")
        result.setdefault("key_moments", [])
        result.setdefault("hook", "Watch what happens next!")

        logger.info("story_analysis_complete", themes=result.get("themes", []))
        return result


class CharacterAnalysisAgent(BaseStoryAgent):
    """Analyzes characters in the manga chapter."""

    SYSTEM_PROMPT = """You are an expert manga character analyst. Analyze the provided data 
and extract information about each character that appears.

Output JSON with this structure:
{
    "characters": [
        {
            "name": "Character name (or 'Unknown' if not named)",
            "role": "protagonist/antagonist/supporting/minor",
            "traits": ["brave", "cunning", etc],
            "motivation": "What they want in this chapter",
            "emotional_state": "Their main emotion",
            "importance": 0.0-1.0,
            "description": "Brief physical description"
        }
    ]
}"""

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze characters from chapter data."""
        chapter_data = context.get("chapter_data", {})
        previous_characters = context.get("known_characters", [])

        prompt_parts = []

        if chapter_data.get("ocr_text"):
            prompt_parts.append(f"Dialogue and narration:\n{chapter_data['ocr_text'][:2000]}")

        if chapter_data.get("characters"):
            chars = chapter_data["characters"]
            prompt_parts.append(f"Characters detected in panels: {json.dumps(chars[:5], indent=2)}")

        if previous_characters:
            names = [c.get("name", "Unknown") for c in previous_characters[:5]]
            prompt_parts.append(f"Previously known characters: {', '.join(names)}")

        if not prompt_parts:
            prompt_parts.append("No character data available. Make educated guesses based on typical manga patterns.")

        prompt = "\n\n".join(prompt_parts)

        result = await self._call_llm(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.7,
        )

        result.setdefault("characters", [])

        logger.info("character_analysis_complete", character_count=len(result.get("characters", [])))
        return result


class EventExtractionAgent(BaseStoryAgent):
    """Extracts key events from the chapter."""

    SYSTEM_PROMPT = """You are an expert manga event extractor. Identify the key events 
that happen in this chapter, ordered chronologically.

Focus on events important for a YouTube recap:
- Battles and fights
- Character introductions/deaths
- Plot reveals and twists
- Important conversations
- Emotional moments

Output JSON with this structure:
{
    "events": [
        {
            "id": 1,
            "type": "battle/introduction/death/reveal/conversation/emotion",
            "description": "What happens",
            "characters_involved": ["name1", "name2"],
            "importance": 0.0-1.0,
            "emotion": "exciting/sad/happy/tense",
            "is_flashback": false
        }
    ]
}"""

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract events from chapter data."""
        chapter_data = context.get("chapter_data", {})
        previous_events = context.get("previous_events", [])

        prompt_parts = []

        if chapter_data.get("ocr_text"):
            prompt_parts.append(f"Chapter content:\n{chapter_data['ocr_text'][:2000]}")

        if chapter_data.get("scene_types"):
            scenes = chapter_data["scene_types"]
            prompt_parts.append(f"Scene types: {', '.join(scenes)}")

        if previous_events:
            recent = previous_events[-3:]  # Last 3 events
            event_summaries = [e.get("description", "")[:100] for e in recent]
            prompt_parts.append(f"Recent previous events: {'; '.join(event_summaries)}")

        if not prompt_parts:
            prompt_parts.append("No event data available. Create placeholder events.")

        prompt = "\n\n".join(prompt_parts)

        result = await self._call_llm(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.7,
        )

        result.setdefault("events", [])

        logger.info("events_extracted", event_count=len(result.get("events", [])))
        return result


class RelationshipAgent(BaseStoryAgent):
    """Analyzes character relationships."""

    SYSTEM_PROMPT = """You are an expert manga relationship analyst. Analyze the relationships 
between characters in this chapter.

Output JSON with this structure:
{
    "relationships": [
        {
            "character1": "name",
            "character2": "name",
            "type": "friend/enemy/family/teacher/student/romantic/ally",
            "strength": 0.0-1.0,
            "evolution": "strengthening/weakening/stable/new"
        }
    ]
}"""

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze relationships from chapter data."""
        chapter_data = context.get("chapter_data", {})
        known_characters = context.get("known_characters", [])

        prompt_parts = []

        if chapter_data.get("ocr_text"):
            prompt_parts.append(f"Dialogue showing relationships:\n{chapter_data['ocr_text'][:1500]}")

        if known_characters:
            char_info = [
                f"{c.get('name', 'Unknown')}: {c.get('role', 'unknown')}"
                for c in known_characters[:5]
            ]
            prompt_parts.append(f"Known characters:\n" + "\n".join(char_info))

        if not prompt_parts:
            prompt_parts.append("No relationship data available.")

        prompt = "\n\n".join(prompt_parts)

        result = await self._call_llm(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.7,
        )

        result.setdefault("relationships", [])

        logger.info("relationships_analyzed", count=len(result.get("relationships", [])))
        return result


class TimelineAgent(BaseStoryAgent):
    """Maintains chronological order of events."""

    SYSTEM_PROMPT = """You are an expert manga timeline analyzer. Organize the events 
from this chapter into chronological order.

Consider:
- Flashbacks (marked as such)
- Parallel events
- Time skips

Output JSON with this structure:
{
    "timeline": [
        {
            "event_id": 1,
            "chronological_order": 1,
            "time_reference": "present/past/future",
            "description": "What happens"
        }
    ]
}"""

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create timeline from events."""
        events = context.get("events", [])
        chapter_data = context.get("chapter_data", {})

        if not events and chapter_data.get("ocr_text"):
            # Create basic timeline from available data
            prompt = f"Create a timeline for this chapter:\n{chapter_data['ocr_text'][:1500]}"
        elif events:
            prompt = f"Organize these events chronologically:\n{json.dumps(events[:10], indent=2)}"
        else:
            return {"timeline": [{"event_id": 1, "chronological_order": 1, "time_reference": "present", "description": "Events occur"}]}

        result = await self._call_llm(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.5,
        )

        result.setdefault("timeline", [])

        logger.info("timeline_created", entries=len(result.get("timeline", [])))
        return result


class WorldAnalysisAgent(BaseStoryAgent):
    """Analyzes world-building elements."""

    SYSTEM_PROMPT = """You are an expert manga world analyst. Extract world-building 
elements from this chapter.

Focus on:
- Locations (kingdoms, cities, specific places)
- Organizations (guilds, schools, military)
- Magic systems or technology
- Important items or artifacts

Output JSON with this structure:
{
    "locations": [{"name": "...", "description": "...", "importance": 0.0-1.0}],
    "organizations": [{"name": "...", "type": "...", "importance": 0.0-1.0}],
    "abilities": [{"name": "...", "user": "...", "description": "..."}],
    "items": [{"name": "...", "significance": "..."}]
}"""

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze world elements."""
        chapter_data = context.get("chapter_data", {})
        previous_world = context.get("known_world", {})

        prompt_parts = []

        if chapter_data.get("ocr_text"):
            prompt_parts.append(f"Chapter content:\n{chapter_data['ocr_text'][:1500]}")

        if previous_world:
            if previous_world.get("locations"):
                locs = [l.get("name", "") for l in previous_world["locations"][:5]]
                prompt_parts.append(f"Known locations: {', '.join(locs)}")

        if not prompt_parts:
            prompt_parts.append("No world data available.")

        prompt = "\n\n".join(prompt_parts)

        result = await self._call_llm(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.7,
        )

        result.setdefault("locations", [])
        result.setdefault("organizations", [])
        result.setdefault("abilities", [])
        result.setdefault("items", [])

        logger.info("world_analysis_complete",
                     locations=len(result.get("locations", [])))
        return result


class QAAgent(BaseStoryAgent):
    """Validates story consistency."""

    SYSTEM_PROMPT = """You are a story quality assurance agent. Check the analysis 
for consistency and issues.

Look for:
- Missing important events
- Character inconsistencies
- Timeline contradictions
- Missing context

Output JSON with this structure:
{
    "qa_passed": true/false,
    "issues": ["issue1", "issue2"],
    "suggestions": ["suggestion1"]
}"""

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate story analysis."""
        analysis = context.get("analysis", {})

        if not analysis:
            return {"qa_passed": True, "issues": [], "suggestions": []}

        prompt = f"Validate this story analysis:\n{json.dumps(analysis, indent=2)[:2000]}"

        result = await self._call_llm(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.3,
        )

        result.setdefault("qa_passed", True)
        result.setdefault("issues", [])
        result.setdefault("suggestions", [])

        logger.info("qa_complete", passed=result.get("qa_passed", True))
        return result
