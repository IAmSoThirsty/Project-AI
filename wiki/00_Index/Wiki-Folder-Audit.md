---
type: audit
priority: canonical
layer: index
status: active
domain:
  - operations
  - corpus
tags:
  - project-ai
  - type/audit
  - priority/canonical
  - layer/index
  - domain/operations
  - domain/corpus
graph_color: "#FEE440"
---

# Wiki Folder Audit

## Current Vault

- Active vault folder: `wiki/`
- Removed previous mistaken vault folder name.
- Removed accidental root vault marker: `.obsidian/`
- Active Obsidian config: `wiki/.obsidian/`

## Folder Layout

- `00_Index/` - navigation, journey, graph, canvas, audit notes
- `01_Governance/` - governance and identity models
- `02_Systems/` - canonical systems and runtime anchors
- `03_Security/` - security controls and runbooks
- `04_Architecture/` - architecture concepts and topology
- `05_Operations/` - deployment, monitoring, and maintenance notes
- `06_Concepts/` - reserved for future cross-domain concepts
- `07_Research/Publications/` - numbered provenance ring and named publication notes
- `08_Templates/` - Obsidian-ready creation templates

## Duplicate Candidates Outside Wiki

These are repo-level implementation folders, not wiki folders. Do not merge without a code-level migration plan.

- `gradle-evolution/` and `gradle_evolution/`
- `.venv/`, `.venv_prod/`, `venv/`
- `Project-AI/` and `Project-AI-Monorepo/`
- `Codex/` and `Claude/`

## Status

The wiki vault now has one canonical folder name and one Obsidian config root.
