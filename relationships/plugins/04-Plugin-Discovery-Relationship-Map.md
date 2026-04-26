---
title: "Plugin Discovery - Relationship Map"
agent: AGENT-067
created: 2026-04-20
status: Active
---

# Plugin Discovery - Comprehensive Relationship Map

## Executive Summary

Plugin Discovery automates the process of finding, validating, and cataloging available plugins from filesystem, package managers, and remote repositories.

## Discovery Mechanisms

### 1. Filesystem Scanning

```python
def discover_filesystem_plugins(plugins_dir: str) -> list[dict]:
    '''Scan directory for plugin manifests.'''
    discovered = []
    for manifest_path in Path(plugins_dir).rglob("plugin.json"):
        with open(manifest_path) as f:
            manifest = json.load(f)
        discovered.append({
            "manifest": manifest,
            "path": manifest_path.parent,
            "source": "filesystem"
        })
    return discovered
```

### 2. Package Discovery (pip/conda)

```python
def discover_installed_packages() -> list[dict]:
    '''Find plugins installed via pip.'''
    plugins = []
    for dist in importlib.metadata.distributions():
        if dist.name.startswith("project-ai-plugin-"):
            plugins.append({
                "name": dist.name,
                "version": dist.version,
                "source": "package"
            })
    return plugins
```

### 3. Directory Conventions

```
plugins/
├── official/          # Bundled official plugins
├── community/         # User-installed community plugins
├── local/             # Local development plugins
└── marketplace/       # Downloaded from marketplace
```

### 4. Discovery Workflow

```
SCAN → PARSE → VALIDATE → INDEX → REGISTER
 │       │        │          │        │
 ▼       ▼        ▼          ▼        ▼
*.py  manifest  schema   catalog  registry
```

## Manifest Schema

```json
{
  "name": "plugin_name",
  "version": "1.0.0",
  "entry_point": "main.py",
  "class_name": "MyPlugin",
  "trust_level": 1,
  "capabilities": ["feature_x"],
  "dependencies": {
    "plugins": [],
    "packages": []
  }
}
```

## References

- **Loading:** ./03-Plugin-Loading-Relationship-Map.md
- **Configuration:** ./07-Plugin-Configuration-Relationship-Map.md

---
**Status:** ✅ Complete
