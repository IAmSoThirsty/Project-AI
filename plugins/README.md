<!--                                        [2026-03-04 14:24]  -->
<!--                                       Productivity: Active  -->

# `plugins/` — Plugin System

> **Extensibility framework for Project-AI.** Plugins allow third-party or custom functionality to be loaded at runtime without modifying core code.

## Overview

The plugin system supports:

- **Runtime loading** — Plugins are discovered and loaded at engine startup
- **Sandboxed execution** — Plugins run within the Cerberus perimeter
- **Policy enforcement** — Plugin actions are subject to FourLaws and Triumvirate governance
- **Hot reload** — Plugins can be updated without restarting the engine

## Plugin Development

See `src/plugins/` for the plugin loader implementation and `tests/plugins/` for plugin test examples.

## Creating a Plugin

```python
from project_ai.engine.capabilities import PluginBase

class MyPlugin(PluginBase):
    name = "my-plugin"
    version = "1.0.0"

    def on_load(self, engine):
        """Called when plugin is loaded."""
        pass

    def on_message(self, message, context):
        """Called on each message."""
        pass
```
