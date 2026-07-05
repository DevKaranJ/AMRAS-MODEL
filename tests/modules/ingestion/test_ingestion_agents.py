from pathlib import Path

import pytest

from modules.ingestion.agents.file_system_agent import FileSystemAgent
from modules.ingestion.agents.metadata_agent import MetadataAgent
from modules.ingestion.agents.validation_agent import ValidationAgent


@pytest.mark.asyncio
async def test_metadata_extraction(tmp_path: Path) -> None:
    agent = MetadataAgent()

    # Create a dummy folder with a specific name
    folder_path = tmp_path / "one_piece"
    folder_path.mkdir()

    metadata = await agent.extract_metadata(folder_path)
    assert metadata.title == "One Piece"
    assert metadata.slug == "one-piece"
    assert metadata.status == "ongoing"

@pytest.mark.asyncio
async def test_validation_agent(tmp_path: Path) -> None:
    agent = ValidationAgent()

    # Test non-existent file
    assert await agent.validate_page(tmp_path / "non_existent.png") is False

    # Test valid chapter and manga (mocked to true for now)
    assert await agent.validate_chapter(1) is True
    assert await agent.validate_manga(1) is True

@pytest.mark.asyncio
async def test_duplicate_hash_detection(tmp_path: Path) -> None:
    agent = FileSystemAgent()

    # Create a dummy file
    file_path = tmp_path / "dummy.txt"
    file_path.write_text("dummy content")

    hash1 = await agent.generate_hash(file_path)

    # Create another file with same content
    file_path2 = tmp_path / "dummy2.txt"
    file_path2.write_text("dummy content")

    hash2 = await agent.generate_hash(file_path2)

    assert hash1 == hash2
