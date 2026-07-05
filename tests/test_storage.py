from pathlib import Path

import pytest

from app.core.exceptions import StorageError
from app.core.storage import StorageManager


def test_storage_manager_initialization(tmp_path: Path) -> None:
    manager = StorageManager(tmp_path)
    # Validate some dirs got created lazily
    manager._ensure_directories()
    assert (tmp_path / "manga").exists()
    assert (tmp_path / "videos").exists()

def test_save_and_read_file(tmp_path: Path) -> None:
    manager = StorageManager(tmp_path)

    # Save a file
    file_path = tmp_path / "test.txt"
    manager.save_file(file_path, "Hello AMRAS")

    assert file_path.exists()

    # Read the file
    content = manager.read_file(file_path)
    assert content == b"Hello AMRAS"

def test_delete_file(tmp_path: Path) -> None:
    manager = StorageManager(tmp_path)
    file_path = tmp_path / "test2.txt"
    manager.save_file(file_path, "To delete")
    assert file_path.exists()

    manager.delete_file(file_path)
    assert not file_path.exists()

def test_path_traversal_protection(tmp_path: Path) -> None:
    manager = StorageManager(tmp_path)

    # Attempt to write outside the base directory
    outside_path = tmp_path / ".." / "outside.txt"

    with pytest.raises(StorageError) as exc_info:
        manager.save_file(outside_path, "Malicious content")

    assert "Path traversal detected" in str(exc_info.value)

def test_ensure_safe_filename(tmp_path: Path) -> None:
    manager = StorageManager(tmp_path)
    safe = manager.ensure_safe_filename("my bad/file*name?.txt")
    assert safe == "my badfilename.txt"
