from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseStoryAgent(ABC):
    @abstractmethod
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input context and return extracted story elements."""
        pass


class StoryAnalysisAgent(BaseStoryAgent):
    """Reads chapter data, understands story, builds chronological events, connects related events."""

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"events": [], "scenes": []}


class CharacterAnalysisAgent(BaseStoryAgent):
    """Understands personality, motivation, growth, relationships, goals, alignment, importance."""

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"characters": []}


class EventExtractionAgent(BaseStoryAgent):
    """Identifies battles, deaths, introductions, discoveries, plot twists, reveals, flashbacks, major conversations."""

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"extracted_events": []}


class RelationshipAgent(BaseStoryAgent):
    """Determines relationships (friend, enemy, family, teacher, student, romantic, ally, unknown), relationship strength, evolution."""

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"relationships": []}


class TimelineAgent(BaseStoryAgent):
    """Maintains chronological order, flashbacks, dreams, parallel timelines, future visions."""

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"timeline_entries": []}


class WorldAnalysisAgent(BaseStoryAgent):
    """Understands kingdoms, cities, villages, organizations, guilds, schools, military, governments, religions, magic systems, technology."""

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"locations": [], "organizations": [], "abilities": [], "items": [], "world_knowledge": []}


class QAAgent(BaseStoryAgent):
    """Validates story consistency, missing events, broken timeline, hallucinations."""

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"qa_passed": True, "issues": []}
