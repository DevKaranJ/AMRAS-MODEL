from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings, loaded from environment variables and/or a .env file.
    """
    project_name: str = "AI Manga Recap Automation System (AMRAS)"
    environment: str = "development"
    debug: bool = False

    # Example Database configuration (to be extended later)
    # database_url: str = "sqlite:///./amras.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

def get_settings() -> Settings:
    """
    Returns the application settings.
    """
    return Settings()
