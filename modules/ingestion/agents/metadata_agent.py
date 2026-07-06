import re
from pathlib import Path

from app.schemas.manga import MangaMetadata
from modules.ingestion.agents.base import BaseIngestionAgent


class MetadataAgent(BaseIngestionAgent):
    async def extract_metadata(self, source_path: Path) -> MangaMetadata:
        """Extracts basic metadata from the folder or file name."""
        name = source_path.stem

        # Simple extraction logic for now
        title = name.replace("_", " ").title()
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")

        return MangaMetadata(
            title=title,
            slug=slug,
            language="en",  # Defaulting for now
            status="ongoing",
        )

    def _is_agent(self) -> bool:
        return True
