import importlib
import inspect
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type

from app.core.exceptions import PluginError


class PluginInterface(ABC):
    """Base interface that all plugins must implement."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the plugin."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Version of the plugin."""
        pass

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration."""
        pass


class PluginManager:
    """Manages the discovery, registration, and lifecycle of plugins."""

    def __init__(self) -> None:
        self._plugins: Dict[str, Dict[str, PluginInterface]] = {}

    def register_plugin(self, category: str, plugin: PluginInterface) -> None:
        """Register an instantiated plugin under a category."""
        if category not in self._plugins:
            self._plugins[category] = {}

        if plugin.name in self._plugins[category]:
            raise PluginError(f"Plugin {plugin.name} is already registered in category {category}")

        self._plugins[category][plugin.name] = plugin

    def get_plugin(self, category: str, name: str) -> Optional[PluginInterface]:
        """Retrieve a registered plugin."""
        return self._plugins.get(category, {}).get(name)

    def list_plugins(self, category: str) -> Dict[str, PluginInterface]:
        """List all plugins in a category."""
        return self._plugins.get(category, {}).copy()


# Global plugin manager instance
plugin_manager = PluginManager()
