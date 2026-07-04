from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_STORAGE_DIR = BASE_DIR / "storage"


class DatabaseSettings(BaseModel):
    url: str = Field(default=f"sqlite+aiosqlite:///{BASE_DIR}/dev.db")
    echo: bool = Field(default=False)
    pool_size: int = Field(default=5)
    max_overflow: int = Field(default=10)


class LoggingSettings(BaseModel):
    level: str = Field(default="INFO")
    format: str = Field(default="json")
    file: Optional[str] = Field(default=None)
    rotation: str = Field(default="10 MB")


class AIProviderSettings(BaseModel):
    provider: str = Field(default="local")
    api_key: Optional[str] = Field(default=None)
    model: str = Field(default="llama3")
    base_url: Optional[str] = Field(default=None)


class StorageSettings(BaseModel):
    base_dir: Path = Field(default=DEFAULT_STORAGE_DIR)
    manga_dir: Path = Field(default=DEFAULT_STORAGE_DIR / "manga")
    extracted_dir: Path = Field(default=DEFAULT_STORAGE_DIR / "extracted")
    ocr_dir: Path = Field(default=DEFAULT_STORAGE_DIR / "ocr")
    scripts_dir: Path = Field(default=DEFAULT_STORAGE_DIR / "scripts")
    audio_dir: Path = Field(default=DEFAULT_STORAGE_DIR / "audio")
    subtitles_dir: Path = Field(default=DEFAULT_STORAGE_DIR / "subtitles")
    videos_dir: Path = Field(default=DEFAULT_STORAGE_DIR / "videos")
    thumbnails_dir: Path = Field(default=DEFAULT_STORAGE_DIR / "thumbnails")
    cache_dir: Path = Field(default=DEFAULT_STORAGE_DIR / "cache")


class VideoSettings(BaseModel):
    resolution: str = Field(default="1920x1080")
    fps: int = Field(default=30)
    ffmpeg_path: str = Field(default="ffmpeg")
    ffprobe_path: str = Field(default="ffprobe")


class OCRSettings(BaseModel):
    engine: str = Field(default="tesseract")
    tesseract_path: str = Field(default="tesseract")
    language: str = Field(default="eng")


class GPUSettings(BaseModel):
    enabled: bool = Field(default=True)
    device: str = Field(default="cuda")
    memory_fraction: float = Field(default=0.8)


class AppSettings(BaseSettings):
    project_name: str = "AI Manga Recap Automation System (AMRAS)"
    version: str = "0.1.0"
    debug: bool = False

    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    log: LoggingSettings = Field(default_factory=LoggingSettings)
    ai: AIProviderSettings = Field(default_factory=AIProviderSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    video: VideoSettings = Field(default_factory=VideoSettings)
    ocr: OCRSettings = Field(default_factory=OCRSettings)
    gpu: GPUSettings = Field(default_factory=GPUSettings)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
    )


def get_settings() -> AppSettings:
    return AppSettings()


settings = get_settings()
