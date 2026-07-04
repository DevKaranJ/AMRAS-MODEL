from typing import Any, Dict

import pytest

from app.core.exceptions import PluginError
from app.core.plugins import PluginInterface, plugin_manager


class DummyPlugin(PluginInterface):
    @property
    def name(self) -> str:
        return "dummy_plugin"

    @property
    def version(self) -> str:
        return "1.0.0"

    def initialize(self, config: Dict[str, Any]) -> None:
        pass


def test_plugin_registration() -> None:
    plugin = DummyPlugin()
    plugin_manager.register_plugin("dummy_category", plugin)

    assert plugin_manager.get_plugin("dummy_category", "dummy_plugin") is plugin
    assert len(plugin_manager.list_plugins("dummy_category")) == 1

    # Test duplicate registration
    with pytest.raises(PluginError):
        plugin_manager.register_plugin("dummy_category", plugin)

    # Test missing plugin
    assert plugin_manager.get_plugin("dummy_category", "missing_plugin") is None
