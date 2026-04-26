---
title: TARL Build System
type: technical-reference
audience: [developers]
classification: P1-Developer
tags: [tarl, build-system, caching]
created: 2024-01-20
status: current
---

# TARL Build System

**Custom build caching and dependency management.**

## CLI Commands

```bash
npm run tarl:build   # Build all targets
npm run tarl:clean   # Clean build cache
npm run tarl:list    # List registered targets
npm run tarl:cache   # Show cache statistics
```

## Build Configuration

File: uild.tarl (YAML format)

```yaml
targets:
  tarl_runtime:
    type: python_module
    sources: [tarl/**/*.py]
    dependencies: []
    
cache:
  enabled: true
  strategy: content_hash
```

## Features

- Content-based caching (SHA-256)
- Incremental builds
- Dependency graph resolution
- Parallel execution

---

**AGENT-038: CLI & Automation Documentation Specialist**
