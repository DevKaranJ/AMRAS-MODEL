import logging
from typing import Any, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.youtube import Description, SEOProfile, Tag, Title

logger = logging.getLogger(__name__)


class SEOAgent:
    """
    Generates Titles, Descriptions, Tags, Keywords, and Hashtags for SEO optimization.
    """

    def __init__(self, ai_provider_manager: Any = None) -> None:
        self.ai = ai_provider_manager

    async def generate_seo_profile(
        self, db: AsyncSession, job_id: int, language: str = "en", keywords: Optional[List[str]] = None
    ) -> SEOProfile:
        logger.info(f"Generating SEO Profile for job {job_id}")
        profile = SEOProfile(job_id=job_id, language=language, target_keywords=keywords or [])
        db.add(profile)
        await db.flush()
        return profile

    async def generate_titles(
        self, db: AsyncSession, profile_id: int, story_context: str, count: int = 5
    ) -> List[Title]:
        """Generate multiple title styles and save to DB."""
        logger.info(f"Generating {count} titles for context: {story_context[:50]}...")
        styles = ["SEO", "Curiosity", "Story-focused", "Character-focused", "Minimal"]
        titles = []
        for i in range(count):
            style = styles[i % len(styles)]
            # Real impl would ask AI provider
            title = Title(
                profile_id=profile_id,
                text=f"Sample Title {i + 1} ({style})",
                style=style,
                score=95.0 - (i * 2.0),
            )
            db.add(title)
            titles.append(title)

        await db.flush()
        return titles

    async def generate_description(
        self, db: AsyncSession, profile_id: int, story_summary: str, timestamps: str, links: Optional[List[str]] = None
    ) -> Description:
        """Generate formatted description including Intro, Summary, Timestamps, Hashtags, Disclaimer and save to DB."""
        logger.info("Generating SEO description.")

        desc_parts = [
            "Welcome to another amazing episode!",
            f"Summary: {story_summary}",
            "Timestamps:\n" + timestamps,
        ]

        if links:
            desc_parts.append("Links:\n" + "\n".join(links))

        desc_parts.append("#anime #manga #recap")
        desc_parts.append("Disclaimer: This is a fan-made recap.")

        description = Description(
            profile_id=profile_id, text="\n\n".join(desc_parts), has_chapters=bool(timestamps)
        )
        db.add(description)
        await db.flush()
        return description

    async def generate_tags(self, db: AsyncSession, profile_id: int, story_context: str) -> List[Tag]:
        """Generate Primary, Secondary, Character, Series, Genre Tags and save to DB."""
        logger.info("Generating SEO tags.")
        # Mock logic, normally AI extraction
        tags_data = [
            ("manga recap", "Primary", 99.0),
            ("anime summary", "Secondary", 95.0),
            ("hero", "Character", 90.0),
            ("shonen", "Genre", 85.0),
        ]
        tags = []
        for text, category, score in tags_data:
            tag = Tag(profile_id=profile_id, text=text, category=category, relevance_score=score)
            db.add(tag)
            tags.append(tag)

        await db.flush()
        return tags
