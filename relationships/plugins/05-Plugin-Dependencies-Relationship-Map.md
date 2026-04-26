---
title: "Plugin Dependencies - Relationship Map"
agent: AGENT-067
created: 2026-04-20
status: Active
---

# Plugin Dependencies - Comprehensive Relationship Map

## Executive Summary

Plugin Dependencies enable plugins to declare requirements on other plugins, Python packages, and system resources, with automatic dependency resolution and validation.

## Dependency Types

### 1. Plugin Dependencies

```json
{
  "dependencies": {
    "plugins": [
      {"name": "base_plugin", "version": ">=1.0.0"},
      {"name": "utils_plugin", "version": "^2.0.0"}
    ]
  }
}
```

### 2. Package Dependencies

```json
{
  "dependencies": {
    "packages": [
      "networkx>=3.0",
      "matplotlib>=3.5",
      "numpy<2.0"
    ]
  }
}
```

### 3. System Dependencies

```json
{
  "dependencies": {
    "system": {
      "python": ">=3.11",
      "platform": ["linux", "darwin", "win32"],
      "arch": ["x86_64", "aarch64"]
    }
  }
}
```

## Dependency Resolution

### Topological Sort (Kahn's Algorithm)

```python
class DependencyResolver:
    def resolve(self) -> list[str]:
        '''Return plugins in dependency order.'''
        in_degree = {name: len(deps) for name, deps in self.graph.items()}
        queue = [name for name, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            plugin = queue.pop(0)
            result.append(plugin)
            
            for dependent in self.reverse_graph.get(plugin, []):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        if len(result) != len(self.graph):
            raise ValueError("Circular dependency detected")
        
        return result
```

### Circular Dependency Detection

```python
def detect_circular(self) -> list[str] | None:
    '''DFS-based cycle detection.'''
    visited = set()
    rec_stack = set()
    
    def dfs(node: str) -> bool:
        visited.add(node)
        rec_stack.add(node)
        
        for neighbor in self.graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True
        
        rec_stack.remove(node)
        return False
    
    for node in self.graph:
        if node not in visited:
            if dfs(node):
                return list(rec_stack)
    
    return None
```

## Version Compatibility

### Semantic Versioning Rules

| Spec | Matches | Example |
|------|---------|---------|
| >=1.0.0 | 1.0.0, 1.5.0, 2.0.0 | Minimum version |
| ^2.0.0 | 2.0.0, 2.9.9 (not 3.0.0) | Compatible |
| ~1.2.3 | 1.2.3, 1.2.9 (not 1.3.0) | Patch updates |
| 1.0.0 | Exactly 1.0.0 | Exact match |

### Version Validation

```python
def validate_version(installed: str, required: str) -> bool:
    '''Check if installed version satisfies requirement.'''
    if required.startswith(">="):
        return Version(installed) >= Version(required[2:])
    elif required.startswith("^"):
        base = Version(required[1:])
        return base.major == Version(installed).major and \
               Version(installed) >= base
    elif required.startswith("~"):
        base = Version(required[1:])
        return base.major == Version(installed).major and \
               base.minor == Version(installed).minor and \
               Version(installed) >= base
    else:
        return Version(installed) == Version(required)
```

## Dependency Graph Visualization

```
plugin_c
  ├─► plugin_a (>=1.0.0)
  └─► plugin_b (^2.0.0)
      └─► plugin_a (>=1.2.0)

Load Order: [plugin_a, plugin_b, plugin_c]
```

## References

- **Loading:** ./03-Plugin-Loading-Relationship-Map.md
- **Lifecycle:** ./06-Plugin-Lifecycle-Relationship-Map.md

---
**Status:** ✅ Complete
