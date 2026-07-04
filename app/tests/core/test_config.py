from app.core.config import get_settings


def test_get_settings_default_values() -> None:
    settings = get_settings()
    assert settings.project_name == "AI Manga Recap Automation System (AMRAS)"
    assert settings.environment == "development"
    assert settings.debug is False
