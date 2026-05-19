---
type: security-control
priority: canonical
layer: systems
status: active
domain:
  - security
  - architecture
tags:
  - project-ai
  - type/security-control
  - priority/canonical
  - layer/systems
  - domain/security
  - domain/architecture
  - bridge/security-architecture
  - system/octoreflex
graph_color: "#FF9F1C"
---

# Syscall Firewall

Syscall-level filtering and enforcement mechanism introduced by OctoReflex.

## Connects
- [[OctoReflex]]
- [[PSIA]]
- [[Plane-Isolation]]
- [[Paper-01]]

## Repo Anchors
- `src/app/core/octoreflex.py`
- `policies/syscall_whitelist.json`
