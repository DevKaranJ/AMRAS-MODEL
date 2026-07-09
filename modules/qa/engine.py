import asyncio
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.qa import QAReport, QualityScore
from modules.qa.agents import (
    NarrationQAAgent,
    OCRQAAgent,
    PerformanceQAAgent,
    PublishingQAAgent,
    SecurityQAAgent,
    StoryQAAgent,
    SubtitleQAAgent,
    TimelineQAAgent,
    VideoQAAgent,
    VoiceQAAgent,
)
from modules.qa.autofix import AutoFixEngine


class QAEngine:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.autofix = AutoFixEngine(db)

    async def run_pipeline(self, project_id: int, modules: Optional[List[str]] = None) -> QAReport:
        agents = {
            "ocr": OCRQAAgent(project_id),
            "story": StoryQAAgent(project_id),
            "narration": NarrationQAAgent(project_id),
            "voice": VoiceQAAgent(project_id),
            "timeline": TimelineQAAgent(project_id),
            "video": VideoQAAgent(project_id),
            "subtitle": SubtitleQAAgent(project_id),
            "publishing": PublishingQAAgent(project_id),
            "performance": PerformanceQAAgent(project_id),
            "security": SecurityQAAgent(project_id),
        }

        # Filter modules if specified
        if modules:
            agents = {k: v for k, v in agents.items() if k in modules}

        # Run agents in parallel
        results = await asyncio.gather(*(agent.run() for agent in agents.values()))

        # Calculate scores
        scores = {}
        for agent_name, result in zip(agents.keys(), results, strict=False):
            scores[f"{agent_name}_score"] = result.get("score", 0.0)

        overall_score = sum(scores.values()) / len(scores) if scores else 0.0

        quality_score = QualityScore(
            overall_score=overall_score,
            story_score=scores.get("story_score", 0.0),
            narration_score=scores.get("narration_score", 0.0),
            voice_score=scores.get("voice_score", 0.0),
            timeline_score=scores.get("timeline_score", 0.0),
            rendering_score=scores.get("video_score", 0.0),
            subtitle_score=scores.get("subtitle_score", 0.0),
            performance_score=scores.get("performance_score", 0.0),
            seo_score=scores.get("publishing_score", 0.0),
            security_score=scores.get("security_score", 0.0),
        )

        # Create report (fake object creation for logic structure)
        report = QAReport(
            project_id=project_id,
            status="passed",
            overall_grade="A" if overall_score > 90 else "B",
            scores=quality_score,
        )
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def run_autofix(self, project_id: int, issue_ids: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        if not issue_ids:
            return []

        return await self.autofix.fix_issues(issue_ids)
