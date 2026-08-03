import hashlib
import re
import shutil
from pathlib import Path
from typing import Any, Dict, List

from app.core.logger import get_logger
from modules.ingestion.importers.base import BaseImporter

logger = get_logger("amras.ingestion.folder_importer")

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}


class FolderImporter(BaseImporter):
    async def import_manga(self, source: Path, manga_id: int) -> Dict[str, Any]:
        """Imports a manga from a local folder, creating chapters and pages in the DB."""
        from app.database.session import async_session_maker
        from app.models.manga import Chapter, Page
        from sqlalchemy import select

        logger.info("importing_from_folder", source=str(source), manga_id=manga_id)

        # Collect all image files
        all_images = sorted([
            f for f in source.rglob("*")
            if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
        ])

        if not all_images:
            logger.warning("no_images_found", source=str(source))
            return {"imported_chapters": 0, "imported_pages": 0, "manga_id": manga_id}

        # Group images by chapter using naming convention or directory structure
        chapters_map = self._group_images_into_chapters(all_images, source)

        imported_chapters = 0
        imported_pages = 0

        async with async_session_maker() as session:
            for chapter_name, images in chapters_map.items():
                # Create chapter record
                chapter_num = self._extract_chapter_number(chapter_name)
                chapter = Chapter(
                    manga_id=manga_id,
                    chapter_number=chapter_num,
                    title=chapter_name,
                    page_count=len(images),
                    imported=True,
                )
                session.add(chapter)
                await session.flush()  # Get chapter.id

                # Create page records
                for page_num, img_path in enumerate(images, start=1):
                    image_hash = self._hash_file(img_path)
                    page = Page(
                        chapter_id=chapter.id,
                        page_number=page_num,
                        image_path=str(img_path),
                        image_hash=image_hash,
                    )
                    session.add(page)
                    imported_pages += 1

                imported_chapters += 1
                logger.info("chapter_imported", chapter=chapter_name, pages=len(images))

            await session.commit()

        logger.info(
            "folder_import_completed",
            manga_id=manga_id,
            chapters=imported_chapters,
            pages=imported_pages,
        )

        return {
            "imported_chapters": imported_chapters,
            "imported_pages": imported_pages,
            "manga_id": manga_id,
        }

    def _group_images_into_chapters(
        self, images: List[Path], source: Path
    ) -> Dict[str, List[Path]]:
        """Group images into chapters based on directory structure or naming pattern."""
        # If images are in subdirectories, use directories as chapters
        dirs = set()
        for img in images:
            rel = img.relative_to(source)
            if len(rel.parts) > 1:
                dirs.add(rel.parts[0])

        if dirs:
            # Multi-directory structure
            chapters: Dict[str, List[Path]] = {d: [] for d in sorted(dirs)}
            for img in images:
                rel = img.relative_to(source)
                if len(rel.parts) > 1:
                    chapters[rel.parts[0]].append(img)
            return chapters

        # Flat structure — group by chapter number pattern in filename
        # Pattern: c001, c002, etc.
        chapters = {}
        for img in images:
            match = re.search(r"c(\d+)", img.name, re.IGNORECASE)
            if match:
                ch_key = f"Chapter {match.group(1)}"
            else:
                ch_key = "Chapter 001"

            if ch_key not in chapters:
                chapters[ch_key] = []
            chapters[ch_key].append(img)

        return chapters

    def _extract_chapter_number(self, chapter_name: str) -> float:
        """Extract chapter number from name."""
        match = re.search(r"(\d+)", chapter_name)
        return float(match.group(1)) if match else 0.0

    def _hash_file(self, file_path: Path) -> str:
        """Generate SHA256 hash of a file."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for block in iter(lambda: f.read(8192), b""):
                sha256.update(block)
        return sha256.hexdigest()

    async def validate_source(self, source: Path) -> bool:
        """Validates if source is a folder."""
        return source.is_dir()
