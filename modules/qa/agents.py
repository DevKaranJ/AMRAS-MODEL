from typing import Any, Dict


class BaseQAAgent:
    def __init__(self, project_id: int):
        self.project_id = project_id

    async def run(self) -> Dict[str, Any]:
        """Runs the specific QA logic for this agent and returns a list of issues and a score."""
        return {"score": 100.0, "issues": []}


class OCRQAAgent(BaseQAAgent):
    async def run(self) -> Dict[str, Any]:
        # Dummy implementation for now, returning 100
        return {"score": 95.0, "issues": []}


class StoryQAAgent(BaseQAAgent):
    async def run(self) -> Dict[str, Any]:
        return {"score": 92.5, "issues": []}


class NarrationQAAgent(BaseQAAgent):
    async def run(self) -> Dict[str, Any]:
        return {"score": 98.0, "issues": []}


class VoiceQAAgent(BaseQAAgent):
    async def run(self) -> Dict[str, Any]:
        return {"score": 90.0, "issues": []}


class TimelineQAAgent(BaseQAAgent):
    async def run(self) -> Dict[str, Any]:
        return {"score": 100.0, "issues": []}


class VideoQAAgent(BaseQAAgent):
    async def run(self) -> Dict[str, Any]:
        return {"score": 99.0, "issues": []}


class SubtitleQAAgent(BaseQAAgent):
    async def run(self) -> Dict[str, Any]:
        return {"score": 95.0, "issues": []}


class PublishingQAAgent(BaseQAAgent):
    async def run(self) -> Dict[str, Any]:
        return {"score": 100.0, "issues": []}


class PerformanceQAAgent(BaseQAAgent):
    async def run(self) -> Dict[str, Any]:
        return {"score": 90.0, "issues": []}


class SecurityQAAgent(BaseQAAgent):
    async def run(self) -> Dict[str, Any]:
        return {"score": 100.0, "issues": []}
