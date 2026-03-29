<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ # -->
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>

# Thirsty-lang Plugin System 💧🔌

Extensible plugin architecture with dynamic loading and sandboxing.

## Features

- Plugin discovery & loading
- Dependency resolution  
- Lifecycle hooks
- Sandboxed execution
- Hot reload
- Plugin marketplace

## Plugin Definition

```thirsty
glass MyPlugin extends Plugin {
  drink name = "my-plugin"
  drink version = "1.0.0"
  drink dependencies = ["core"]
  
  glass onLoad() {
    pour "Plugin loaded"
    registerCommand("hello", glass() {
      pour "Hello from plugin!"
    })
  }
  
  glass onUnload() {
    cleanup resources
  }
}

export MyPlugin
```

## Plugin Manager

```thirsty
glass PluginManager {
  drink plugins
  
  glass async load(pluginPath) {
    shield pluginProtection {
      sanitize pluginPath
      
      drink PluginClass = await import(pluginPath)
      drink plugin = PluginClass()
      
      await plugin.onLoad()
      plugins[plugin.name] = plugin
    }
  }
  
  glass unload(name) {
    drink plugin = plugins[name]
    plugin.onUnload()
    delete plugins[name]
  }
}
```

## License

MIT
