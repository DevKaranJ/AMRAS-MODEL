import hashlib
import shutil
import zipfile
from pathlib import Path
from typing import Any, Dict, List

from app.core.logger import get_logger
from modules.ingestion.agents.base import BaseIngestionAgent

logger = get_logger("amras.ingestion.file_system_agent")


class FileSystemAgent(BaseIngestionAgent):
    async def process_source(self, source_path: Path, manga_title: str, manga_id: int) -> Dict[str, Any]:
        """Main entrypoint for processing file sources."""
        from modules.ingestion.importers.archive_importer import ArchiveImporter
        from modules.ingestion.importers.folder_importer import FolderImporter
        from modules.ingestion.importers.pdf_importer import PDFImporter

        # Determine which importer to use based on source type
        if source_path.is_dir():
            importer = FolderImporter()
        elif source_path.suffix.lower() in [".zip", ".cbz"]:
            importer = ArchiveImporter(self)
        elif source_path.suffix.lower() == ".pdf":
            importer = PDFImporter()
        else:
            raise ValueError(f"Unsupported source type: {source_path}")

        # Validate and import
        if not await importer.validate_source(source_path):
            raise ValueError(f"Invalid source for selected importer: {source_path}")

        result = await importer.import_manga(source_path, manga_id)

        # Normalize the result to include processed_chapters and processed_pages
        processed_chapters = result.get("imported_chapters", 0)
        processed_pages = result.get("imported_pages", 0)

        return {"processed_chapters": processed_chapters, "processed_pages": processed_pages}

    async def move_file(self, src: Path, dest: Path) -> None:
        """Safely moves a file, creating directories if needed."""
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))

    async def extract_zip(self, zip_path: Path, extract_dir: Path) -> List[Path]:
        """Extracts a ZIP archive to a temporary directory."""
        extract_dir.mkdir(parents=True, exist_ok=True)
        extracted_files = []
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            for name in zip_ref.namelist():
                # Validate path to prevent directory traversal
                target_path = (extract_dir / name).resolve()
                if not str(target_path).startswith(str(extract_dir.resolve())):
                    logger.warning("path_traversal_detected", name=name, zip_path=str(zip_path))
                    continue

                # Extract the member safely
                zip_ref.extract(name, extract_dir)
                extracted_files.append(target_path)
        return extracted_files

    async def extract_cbz(self, cbz_path: Path, extract_dir: Path) -> List[Path]:
        """Extracts a CBZ archive (which is just a ZIP file)."""
        return await self.extract_zip(cbz_path, extract_dir)

    async def generate_hash(self, file_path: Path) -> str:
        """Generates SHA256 hash for duplicate detection."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    async def normalize_image(self, src: Path, dest: Path) -> Dict[str, Any]:
        """Converts an image to a normalized PNG."""
        from PIL import Image

        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            with Image.open(src) as img:
                # Convert to RGB to normalize color space (removes alpha if not needed or normalizes palettes)
                if img.mode not in ("RGB", "RGBA"):
                    img = img.convert("RGB")  # type: ignore
                img.save(dest, format="PNG")
                return {"width": img.width, "height": img.height}
        except Exception as e:
            logger.error("image_normalization_failed", src=str(src), error=str(e))
            raise e

    def _is_agent(self) -> bool:
        return True
