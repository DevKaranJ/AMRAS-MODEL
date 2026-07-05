import tempfile
from pathlib import Path
from typing import Any, Dict

from pdf2image import convert_from_path

from app.core.logger import get_logger
from modules.ingestion.importers.base import BaseImporter

logger = get_logger("amras.ingestion.pdf_importer")

class PDFImporter(BaseImporter):

    async def import_manga(self, source: Path, manga_id: int) -> Dict[str, Any]:
        """Imports a manga from a PDF file."""
        logger.info("importing_from_pdf", source=str(source), manga_id=manga_id)

        extract_dir = Path(tempfile.mkdtemp())

        try:
            # We use pdf2image to convert PDF to images
            # This is a blocking call, in a real system we would use a ThreadPoolExecutor
            # or a specific async wrapper
            pages = convert_from_path(str(source), output_folder=str(extract_dir), fmt="png")

            return {"imported_pages": len(pages), "manga_id": manga_id}
        except Exception as e:
            logger.error("pdf_import_failed", source=str(source), error=str(e))
            raise e

    async def validate_source(self, source: Path) -> bool:
        """Validates if source is a PDF file."""
        return source.is_file() and source.suffix.lower() == ".pdf"
