from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# Default free model chain for OpenRouter
DEFAULT_MODEL_CHAIN = [
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-nano-12b-v2-vl:free",
]

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_STORAGE_DIR = BASE_DIR / "storage"


class DatabaseSettings(BaseModel):
    url: str = Field(default=f"sqlite+aiosqlite:///{BASE_DIR}/dev.db")
    echo: bool = Field(default=False)
    # pool_size / max_overflow are ignored by SQLite's StaticPool; they apply
    # only when DATABASE__URL points to PostgreSQL / MySQL.
    pool_size: int = Field(default=5)
    max_overflow: int = Field(default=10)

    @property
    def is_sqlite(self) -> bool:
        return self.url.startswith("sqlite")


class LoggingSettings(BaseModel):
    level: str = Field(default="INFO")
    format: str = Field(default="json")
    file: Optional[str] = Field(default=None)
    # Accepts "10 MB", "10MB", "100 MB" etc.
    rotation: str = Field(default="10 MB")

    @property
    def rotation_bytes(self) -> int:
        """Return rotation threshold as bytes (parses '<N> MB' or '<N>MB')."""
        raw = self.rotation.replace(" ", "").upper()
        try:
            if raw.endswith("MB"):
                return int(raw[:-2]) * 1024 * 1024
            if raw.endswith("GB"):
                return int(raw[:-2]) * 1024 * 1024 * 1024
            if raw.endswith("KB"):
                return int(raw[:-2]) * 1024
        except (ValueError, IndexError):
            pass
        return 10 * 1024 * 1024  # fallback 10 MB


class AIProviderSettings(BaseModel):
    provider: str = Field(default="local")
    api_key: Optional[str] = Field(default=None)
    model: str = Field(default="llama3")
    base_url: Optional[str] = Field(default=None)


class OpenRouterSettings(BaseModel):
    """OpenRouter multi-key provider settings."""

    # Multiple API keys for rotation (comma-separated in .env)
    api_keys: List[str] = Field(default_factory=list)

    # Model fallback chain (primary → fallbacks)
    model_chain: List[str] = Field(default=DEFAULT_MODEL_CHAIN)

    # Rate limits (free tier)
    rate_limit_rpm: int = Field(default=20)
    rate_limit_rpd: int = Field(default=50)

    @field_validator("api_keys", mode="before")
    @classmethod
    def parse_api_keys(cls, v: object) -> List[str]:
        if isinstance(v, str):
            return [k.strip() for k in v.split(",") if k.strip()]
        return list(v) if v else []

    @field_validator("model_chain", mode="before")
    @classmethod
    def parse_model_chain(cls, v: object) -> List[str]:
        if isinstance(v, str):
            return [m.strip() for m in v.split(",") if m.strip()]
        return list(v) if v else DEFAULT_MODEL_CHAIN


class TTSSettings(BaseModel):
    """Text-to-Speech provider settings."""

    provider: str = Field(default="edge", alias="TTS_PROVIDER")
    default_voice: str = Field(default="en-US-GuyNeural")
    default_rate: str = Field(default="+0%")

    # ElevenLabs (future upgrade)
    elevenlabs_api_key: Optional[str] = Field(default=None)
    elevenlabs_voice_id: Optional[str] = Field(default=None)


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

    # ------------------------------------------------------------------ #
    # Security                                                             #
    # ------------------------------------------------------------------ #
    # Set AMRAS_API_KEY in your environment / .env file.
    # If unset, all API requests will be rejected with HTTP 503.
    api_key: Optional[str] = Field(default=None, alias="AMRAS_API_KEY")

    # CORS — comma-separated list of allowed origins, e.g.
    # AMRAS_ALLOWED_ORIGINS="http://localhost:3000,https://myapp.example.com"
    allowed_origins: List[str] = Field(default=["*"], alias="AMRAS_ALLOWED_ORIGINS")

    # ------------------------------------------------------------------ #
    # Sub-settings                                                         #
    # ------------------------------------------------------------------ #
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    log: LoggingSettings = Field(default_factory=LoggingSettings)
    ai: AIProviderSettings = Field(default_factory=AIProviderSettings)
    openrouter: OpenRouterSettings = Field(default_factory=OpenRouterSettings)
    tts: TTSSettings = Field(default_factory=TTSSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    video: VideoSettings = Field(default_factory=VideoSettings)
    ocr: OCRSettings = Field(default_factory=OCRSettings)
    gpu: GPUSettings = Field(default_factory=GPUSettings)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        populate_by_name=True,
    )

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, v: object) -> List[str]:
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return list(v)  # type: ignore[arg-type]


def get_settings() -> AppSettings:
    return AppSettings()


settings = get_settings()
