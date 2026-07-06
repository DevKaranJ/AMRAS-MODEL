import shutil
from pathlib import Path
from typing import IO, Union

from app.config.settings import settings
from app.core.exceptions import StorageError


class StorageManager:
    def __init__(self, base_dir: Union[str, Path]):
        self.base_dir = Path(base_dir).resolve()
        self._directories_initialized = False

    def _ensure_directories(self) -> None:
        """Create necessary subdirectories lazily on first access."""
        if not self._directories_initialized:
            for subdir in [
                "manga",
                "extracted",
                "ocr",
                "scripts",
                "audio",
                "subtitles",
                "videos",
                "thumbnails",
                "cache",
            ]:
                dir_path = self.base_dir / subdir
                dir_path.mkdir(parents=True, exist_ok=True)
            self._directories_initialized = True

    def _validate_path(self, path: Union[str, Path]) -> Path:
        """Ensure the path is within the base directory to prevent traversal attacks."""
        resolved_path = Path(path).resolve()
        if not resolved_path.is_relative_to(self.base_dir):
            raise StorageError(f"Path traversal detected: {path}")
        return resolved_path

    def save_file(self, dest_path: Union[str, Path], content: Union[bytes, str, IO[bytes]]) -> Path:
        """Save file safely."""
        self._ensure_directories()
        full_dest = self._validate_path(dest_path)
        full_dest.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(content, str):
            full_dest.write_text(content)
        elif isinstance(content, bytes):
            full_dest.write_bytes(content)
        else:
            with open(full_dest, "wb") as f:
                shutil.copyfileobj(content, f)

        return full_dest

    def read_file(self, file_path: Union[str, Path]) -> bytes:
        self._ensure_directories()
        full_path = self._validate_path(file_path)
        if not full_path.exists():
            raise StorageError(f"File not found: {full_path}")
        return full_path.read_bytes()

    def delete_file(self, file_path: Union[str, Path]) -> None:
        self._ensure_directories()
        full_path = self._validate_path(file_path)
        if full_path.exists():
            full_path.unlink()

    def ensure_safe_filename(self, filename: str) -> str:
        """Sanitize a filename to be safe for saving."""
        keepcharacters = (" ", ".", "_", "-")
        return "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip()


# Default storage manager
storage_manager = StorageManager(settings.storage.base_dir)
