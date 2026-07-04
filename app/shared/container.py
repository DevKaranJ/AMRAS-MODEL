from dependency_injector import containers, providers

from app.core.config import get_settings


class Container(containers.DeclarativeContainer):
    """
    Dependency Injection Container for AMRAS.
    """

    # Enable autowiring for easy dependency injection
    wiring_config = containers.WiringConfiguration(packages=["app"])

    # Core Providers
    config = providers.Singleton(get_settings)

    # More providers (services, repositories, clients) will be added here
    # Example:
    # database = providers.Singleton(Database, db_url=config.provided.database_url)
