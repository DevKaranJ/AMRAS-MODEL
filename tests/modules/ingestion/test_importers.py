from pathlib import Path

import pytest

from modules.ingestion.agents.file_system_agent import FileSystemAgent
from modules.ingestion.importers.archive_importer import ArchiveImporter
from modules.ingestion.importers.folder_importer import FolderImporter
from modules.ingestion.importers.pdf_importer import PDFImporter


@pytest.mark.asyncio
async def test_folder_importer_success(tmp_path: Path) -> None:
    importer = FolderImporter()

    # Create a dummy structure
    (tmp_path / "Chapter 1").mkdir()
    (tmp_path / "Chapter 2").mkdir()

    assert await importer.validate_source(tmp_path) is True

    result = await importer.import_manga(tmp_path, manga_id=1)
    assert result["imported_chapters"] == 2
    assert result["manga_id"] == 1

@pytest.mark.asyncio
async def test_folder_importer_invalid_source(tmp_path: Path) -> None:
    importer = FolderImporter()
    file_path = tmp_path / "dummy.txt"
    file_path.touch()

    assert await importer.validate_source(file_path) is False

@pytest.mark.asyncio
async def test_archive_importer_validate_source(tmp_path: Path) -> None:
    # Dummy FileSystemAgent is fine for this test since we only test validation
    importer = ArchiveImporter(FileSystemAgent())

    zip_path = tmp_path / "dummy.zip"
    zip_path.touch()
    assert await importer.validate_source(zip_path) is True

    cbz_path = tmp_path / "dummy.cbz"
    cbz_path.touch()
    assert await importer.validate_source(cbz_path) is True

    txt_path = tmp_path / "dummy.txt"
    txt_path.touch()
    assert await importer.validate_source(txt_path) is False

@pytest.mark.asyncio
async def test_pdf_importer_validate_source(tmp_path: Path) -> None:
    importer = PDFImporter()

    pdf_path = tmp_path / "dummy.pdf"
    pdf_path.touch()
    assert await importer.validate_source(pdf_path) is True

    txt_path = tmp_path / "dummy.txt"
    txt_path.touch()
    assert await importer.validate_source(txt_path) is False
