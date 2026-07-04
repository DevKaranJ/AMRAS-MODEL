import pytest

from app.core.config import Settings
from app.shared.container import Container


@pytest.fixture
def test_settings() -> Settings:
    return Settings(environment="testing", debug=True)

@pytest.fixture
def container(test_settings: Settings) -> Container:
    container = Container()
    container.config.override(test_settings)
    return container
