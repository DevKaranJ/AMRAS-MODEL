import pytest
from pydantic import ValidationError

from app.config.settings import AppSettings


def test_default_config() -> None:
    settings = AppSettings()
    assert settings.project_name == "AI Manga Recap Automation System (AMRAS)"
    assert settings.db.echo is False
    assert settings.log.level == "INFO"


def test_environment_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOG__LEVEL", "DEBUG")
    monkeypatch.setenv("DB__POOL_SIZE", "20")

    settings = AppSettings()

    assert settings.log.level == "DEBUG"
    assert settings.db.pool_size == 20


def test_invalid_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DB__POOL_SIZE", "not_an_int")

    with pytest.raises(ValidationError):
        AppSettings()


def test_missing_values(monkeypatch: pytest.MonkeyPatch) -> None:
    # All settings have defaults right now, but if we required a value:
    # monkeypatch.setenv("REQUIRED__SETTING", "")
    # with pytest.raises(ValidationError):
    #     AppSettings()
    pass
