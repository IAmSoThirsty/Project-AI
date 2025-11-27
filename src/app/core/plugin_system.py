"""
Plugin/Extension System for Project-AI
Allows dynamic loading and management of plugins to extend functionality
"""

import importlib.util
import inspect
import json
import os
import sys
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List


class PluginBase(ABC):
    """Base class for all plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Plugin description."""
        pass

    @abstractmethod
    def initialize(self, context: Dict[str, Any]) -> bool:
        """
        Initialize plugin with application context.

        Args:
            context: Application context dictionary

        Returns:
            True if initialization successful
        """
        pass

    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        """
        Execute plugin main functionality.

        Args:
            **kwargs: Plugin-specific arguments

        Returns:
            Plugin-specific result
        """
        pass

    def shutdown(self) -> None:
        """Clean up plugin resources."""
        pass


class PluginManager:
    """Manages plugin discovery, loading, and execution."""

    def __init__(self, plugins_dir: str = "plugins"):
        """
        Initialize plugin manager.

        Args:
            plugins_dir: Directory containing plugins
        """
        self.plugins_dir = plugins_dir
        self.plugins: Dict[str, PluginBase] = {}
        self.plugin_metadata: Dict[str, Dict[str, Any]] = {}
        self.hooks: Dict[str, List[Callable[..., Any]]] = {}

        os.makedirs(plugins_dir, exist_ok=True)
        self._load_plugins()

    def _load_plugins(self) -> None:
        """Discover and load all plugins from plugins directory."""
        if not os.path.exists(self.plugins_dir):
            return

        for item in os.listdir(self.plugins_dir):
            plugin_path = os.path.join(self.plugins_dir, item)

            # Load from .py files
            if item.endswith(".py") and not item.startswith("_"):
                self._load_plugin_from_file(plugin_path)

            # Load from directories (packages)
            elif os.path.isdir(plugin_path):
                init_file = os.path.join(plugin_path, "__init__.py")
                if os.path.exists(init_file):
                    self._load_plugin_from_file(init_file)

    def _load_plugin_from_file(self, file_path: str) -> None:
        """
        Load a plugin from a Python file.

        Args:
            file_path: Path to plugin file
        """
        try:
            # Load module
            spec = importlib.util.spec_from_file_location("plugin_module", file_path)
            if not spec or not spec.loader:
                return

            module = importlib.util.module_from_spec(spec)
            sys.modules["plugin_module"] = module
            spec.loader.exec_module(module)

            # Find plugin classes
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, PluginBase) and obj != PluginBase:
                    try:
                        plugin_instance = obj()
                        plugin_name = plugin_instance.name

                        self.plugins[plugin_name] = plugin_instance
                        self.plugin_metadata[plugin_name] = {
                            "version": plugin_instance.version,
                            "description": plugin_instance.description,
                            "file": file_path,
                            "loaded": True,
                        }

                        print(
                            f"Loaded plugin: {plugin_name} v{plugin_instance.version}"
                        )
                    except Exception as e:
                        print(f"Failed to instantiate plugin {name}: {e}")

        except Exception as e:
            print(f"Failed to load plugin from {file_path}: {e}")

    def initialize_plugin(self, plugin_name: str, context: Dict[str, Any]) -> bool:
        """
        Initialize a specific plugin.

        Args:
            plugin_name: Name of plugin to initialize
            context: Application context

        Returns:
            True if initialization successful
        """
        plugin = self.plugins.get(plugin_name)
        if not plugin:
            return False

        try:
            success = plugin.initialize(context)
            if success and plugin_name in self.plugin_metadata:
                self.plugin_metadata[plugin_name]["initialized"] = True
            return success
        except Exception as e:
            print(f"Failed to initialize plugin {plugin_name}: {e}")
            return False

    def initialize_all_plugins(self, context: Dict[str, Any]) -> None:
        """
        Initialize all loaded plugins.

        Args:
            context: Application context
        """
        for plugin_name in self.plugins:
            self.initialize_plugin(plugin_name, context)

    def execute_plugin(self, plugin_name: str, **kwargs: Any) -> Any:
        """
        Execute a plugin.

        Args:
            plugin_name: Name of plugin to execute
            **kwargs: Plugin-specific arguments

        Returns:
            Plugin execution result
        """
        plugin = self.plugins.get(plugin_name)
        if not plugin:
            raise ValueError(f"Plugin {plugin_name} not found")

        try:
            return plugin.execute(**kwargs)
        except Exception as e:
            print(f"Plugin execution error ({plugin_name}): {e}")
            raise

    def register_hook(self, hook_name: str, callback: Callable[..., Any]) -> None:
        """
        Register a callback for a hook point.

        Args:
            hook_name: Name of the hook
            callback: Function to call when hook is triggered
        """
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(callback)

    def trigger_hook(self, hook_name: str, *args: Any, **kwargs: Any) -> List[Any]:
        """
        Trigger all callbacks registered for a hook.

        Args:
            hook_name: Name of hook to trigger
            *args: Positional arguments for callbacks
            **kwargs: Keyword arguments for callbacks

        Returns:
            List of callback results
        """
        results = []
        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                try:
                    result = callback(*args, **kwargs)
                    results.append(result)
                except Exception as e:
                    print(f"Hook callback error ({hook_name}): {e}")
        return results

    def list_plugins(self) -> List[Dict[str, Any]]:
        """
        List all loaded plugins with their metadata.

        Returns:
            List of plugin information dictionaries
        """
        plugin_list = []
        for name, plugin in self.plugins.items():
            info = self.plugin_metadata.get(name, {}).copy()
            info["name"] = name
            plugin_list.append(info)
        return plugin_list

    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin.

        Args:
            plugin_name: Name of plugin to unload

        Returns:
            True if successful
        """
        plugin = self.plugins.get(plugin_name)
        if not plugin:
            return False

        try:
            plugin.shutdown()
            del self.plugins[plugin_name]
            if plugin_name in self.plugin_metadata:
                self.plugin_metadata[plugin_name]["loaded"] = False
            return True
        except Exception as e:
            print(f"Failed to unload plugin {plugin_name}: {e}")
            return False

    def reload_plugin(self, plugin_name: str, context: Dict[str, Any]) -> bool:
        """
        Reload a plugin.

        Args:
            plugin_name: Name of plugin to reload
            context: Application context

        Returns:
            True if successful
        """
        metadata = self.plugin_metadata.get(plugin_name)
        if not metadata or "file" not in metadata:
            return False

        # Unload
        self.unload_plugin(plugin_name)

        # Reload
        self._load_plugin_from_file(metadata["file"])

        # Initialize
        return self.initialize_plugin(plugin_name, context)

    def get_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
        """
        Get plugin configuration.

        Args:
            plugin_name: Name of plugin

        Returns:
            Configuration dictionary
        """
        config_file = os.path.join(self.plugins_dir, f"{plugin_name}_config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Failed to load config for {plugin_name}: {e}")
        return {}

    def save_plugin_config(self, plugin_name: str, config: Dict[str, Any]) -> bool:
        """
        Save plugin configuration.

        Args:
            plugin_name: Name of plugin
            config: Configuration to save

        Returns:
            True if successful
        """
        config_file = os.path.join(self.plugins_dir, f"{plugin_name}_config.json")
        try:
            with open(config_file, "w") as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save config for {plugin_name}: {e}")
            return False


# Example plugin implementation
class ExamplePlugin(PluginBase):
    """Example plugin demonstrating the plugin interface."""

    @property
    def name(self) -> str:
        return "example_plugin"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Example plugin for demonstration"

    def initialize(self, context: Dict[str, Any]) -> bool:
        """Initialize with application context."""
        self.context = context
        print(f"Example plugin initialized with context: {list(context.keys())}")
        return True

    def execute(self, **kwargs: Any) -> Any:
        """Execute plugin functionality."""
        action = kwargs.get("action", "default")

        if action == "hello":
            return "Hello from Example Plugin!"
        elif action == "info":
            return {
                "name": self.name,
                "version": self.version,
                "description": self.description,
            }
        else:
            return f"Unknown action: {action}"

    def shutdown(self) -> None:
        """Clean up resources."""
        print("Example plugin shutting down")
