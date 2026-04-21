---
title: "Plugin Configuration - Relationship Map"
agent: AGENT-067
created: 2026-04-20
status: Active
---

# Plugin Configuration - Comprehensive Relationship Map

## Executive Summary

Plugin Configuration provides schema validation, persistence, hot-reload, and environment-based configuration for all plugin systems.

## Configuration Sources (Priority Order)

```
1. Runtime Arguments (highest priority)
2. Environment Variables
3. Config Files (plugin_config.json)
4. Manifest Defaults (plugin.json)
5. Hardcoded Defaults (lowest priority)
```

## Configuration Schema

### Plugin-Specific Config

```json
{
  "plugins": {
    "graph_analysis_plugin": {
      "enabled": true,
      "config": {
        "default_layout": "spring",
        "max_nodes": 1000,
        "timeout": 30,
        "output_format": "png"
      }
    },
    "excalidraw_plugin": {
      "enabled": true,
      "config": {
        "canvas_size": [1920, 1080],
        "theme": "light",
        "autosave": true
      }
    }
  }
}
```

### Global Config

```json
{
  "plugin_system": {
    "auto_discover": true,
    "plugins_dir": "plugins/",
    "trust_level": 1,
    "timeout": 5.0,
    "max_concurrent": 10,
    "enable_hot_reload": false
  }
}
```

## Configuration Loading

### Cascading Configuration

```python
class PluginConfig:
    '''Manage plugin configuration with cascading sources.'''
    
    def __init__(self, plugin_name: str):
        self.plugin_name = plugin_name
        self.config = {}
    
    def load(self) -> dict:
        '''Load config from all sources.'''
        # 1. Hardcoded defaults
        self.config = self._get_defaults()
        
        # 2. Manifest defaults
        manifest = self._load_manifest()
        self.config.update(manifest.get("configuration", {}))
        
        # 3. Config file
        config_file = self._load_config_file()
        if self.plugin_name in config_file.get("plugins", {}):
            self.config.update(config_file["plugins"][self.plugin_name].get("config", {}))
        
        # 4. Environment variables
        env_config = self._load_env_vars()
        self.config.update(env_config)
        
        # 5. Runtime arguments (passed to execute)
        # Applied at execution time
        
        return self.config
    
    def _load_env_vars(self) -> dict:
        '''Load config from environment variables.'''
        prefix = f"PLUGIN_{self.plugin_name.upper()}_"
        config = {}
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                config[config_key] = value
        
        return config
```

### Schema Validation

```python
def validate_config(config: dict, schema: dict) -> tuple[bool, str]:
    '''Validate configuration against JSON schema.'''
    try:
        jsonschema.validate(config, schema)
        return True, "Valid"
    except jsonschema.ValidationError as e:
        return False, str(e)

# Example schema
schema = {
    "type": "object",
    "properties": {
        "timeout": {"type": "number", "minimum": 0},
        "max_nodes": {"type": "integer", "minimum": 1},
        "output_format": {"enum": ["png", "svg", "pdf"]}
    },
    "required": ["timeout", "max_nodes"]
}
```

## Hot-Reload

### File Watcher

```python
class ConfigFileWatcher:
    '''Watch config file for changes and reload.'''
    
    def __init__(self, config_path: Path, registry: PluginRegistry):
        self.config_path = config_path
        self.registry = registry
        self.last_modified = config_path.stat().st_mtime
    
    def watch(self):
        '''Poll for file changes.'''
        while True:
            current_mtime = self.config_path.stat().st_mtime
            if current_mtime > self.last_modified:
                logger.info("Config file changed, reloading...")
                self.reload_config()
                self.last_modified = current_mtime
            time.sleep(1.0)
    
    def reload_config(self):
        '''Reload plugin configurations.'''
        with open(self.config_path) as f:
            new_config = json.load(f)
        
        for plugin_name, plugin_config in new_config.get("plugins", {}).items():
            plugin = self.registry.get_plugin(plugin_name)
            if plugin and hasattr(plugin, 'reload_config'):
                plugin.reload_config(plugin_config.get("config", {}))
                logger.info(f"Reloaded config for {plugin_name}")
```

## Configuration API

### Plugin Configuration Interface

```python
class ConfigurablePlugin(PluginInterface):
    '''Plugin with configuration support.'''
    
    def __init__(self):
        self.config = PluginConfig(self.get_name())
        self.settings = self.config.load()
    
    def get_config_schema(self) -> dict:
        '''Return JSON schema for configuration.'''
        return {
            "type": "object",
            "properties": {
                "timeout": {"type": "number", "minimum": 0},
                "enabled": {"type": "boolean"}
            }
        }
    
    def validate_config(self, config: dict) -> bool:
        '''Validate configuration.'''
        schema = self.get_config_schema()
        valid, _ = validate_config(config, schema)
        return valid
    
    def reload_config(self, new_config: dict) -> None:
        '''Hot-reload configuration.'''
        if self.validate_config(new_config):
            self.settings.update(new_config)
            logger.info(f"Config reloaded for {self.get_name()}")
        else:
            raise ValueError("Invalid configuration")
    
    def execute(self, context: dict) -> dict:
        '''Execute with runtime config override.'''
        # Merge runtime config
        runtime_config = context.get("config", {})
        effective_config = {**self.settings, **runtime_config}
        
        # Use effective_config for execution
        timeout = effective_config.get("timeout", 5.0)
        # ...
```

## Environment Variables

### Supported Patterns

```bash
# Plugin-specific
export PLUGIN_GRAPH_ANALYSIS_TIMEOUT=30
export PLUGIN_GRAPH_ANALYSIS_MAX_NODES=1000

# Global plugin system
export PLUGIN_SYSTEM_AUTO_DISCOVER=true
export PLUGIN_SYSTEM_TRUST_LEVEL=1

# Override config file path
export PLUGIN_CONFIG_PATH=/custom/path/plugin_config.json
```

## Persistence

### Save Configuration

```python
def save_config(config: dict, path: Path) -> None:
    '''Save plugin configuration to file.'''
    # Atomic write
    temp_path = path.with_suffix('.tmp')
    with open(temp_path, 'w') as f:
        json.dump(config, f, indent=2)
    temp_path.replace(path)
    logger.info(f"Configuration saved to {path}")
```

## References

- **Loading:** ./03-Plugin-Loading-Relationship-Map.md
- **Lifecycle:** ./06-Plugin-Lifecycle-Relationship-Map.md

---
**Status:** ✅ Complete
