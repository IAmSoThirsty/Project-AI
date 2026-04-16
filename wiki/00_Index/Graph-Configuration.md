---
priority: canonical
type: control-node
role: graph-configuration
layer: index
status: active
tags:
  - project-ai
  - type/control-node
  - priority/canonical
  - role/navigation
  - role/graph
  - layer/index
graph_color: "#FF3D7F"
---

# Graph Configuration

Parent: [[System-Map]]

## Color Language

Use tags and folder paths as color signals. Tags create the intentional blends; folder paths are the fallback so every region of the vault stays colored even when a note has sparse metadata.

| Tag | Color | Meaning |
|---|---|---|
| `#role/root` | solar gold | Graph center and root spine |
| `#domain/governance` | hot rose | Constitutional authority, agents, policy |
| `#domain/security` | vital green | Runtime defense, audit, cryptography |
| `#domain/architecture` | ignition yellow | Runtime structure, language, topology |
| `#domain/systems` | electric cyan | Built systems and production machinery |
| `#domain/research` | violet | Theory, papers, formal framing |
| `#domain/corpus` | ember orange | Origin corpus and motive record |
| `#domain/operations` | charged purple | Deployment, runbooks, monitoring |

## Bridge Colors

Native Obsidian graph groups choose the first matching color group rather than blending gradients. Bridge tags make the blend explicit by giving cross-domain notes their own clash color.

| Bridge Tag | Blend |
|---|---|
| `#bridge/governance-security` | violet plus orange |
| `#bridge/security-architecture` | orange plus cyan |
| `#bridge/architecture-systems` | cyan plus mint |
| `#bridge/governance-architecture` | violet plus cyan |
| `#bridge/governance-research` | violet plus acid green |
| `#bridge/corpus-governance` | corpus gold plus violet |
| `#bridge/security-systems` | orange plus mint |
| `#bridge/security-research` | orange plus acid green |
| `#bridge/systems-governance` | mint plus violet |
| `#bridge/sovereign-core` | whole-system prism |

## System Tags

Use `#system/name` tags to pull system clusters together:

- `#system/psia`
- `#system/octoreflex`
- `#system/triumvirate`
- `#system/tarl`
- `#system/tscg`
- `#system/tscg-b`
- `#system/state-register`
- `#system/audit`
- `#system/cerberus`
- `#system/sovereign-runtime`
- `#system/sovereign-vault`
- `#system/governance-pipeline`
- `#system/yggdrasil-dns`
- `#system/constitutional-code-store`

## Obsidian Setup

This wiki vault includes `.obsidian/graph.json` with the live clash palette for the Graph view in Obsidian.

Keep bridge color groups above domain color groups so cross-domain nodes take the intended mixed color first.

Path groups sit underneath the tag groups:

- `path:01_Governance`
- `path:02_Systems`
- `path:03_Security`
- `path:04_Architecture`
- `path:05_Operations`
- `path:06_Concepts`
- `path:07_Research/Publications`
- `path:08_Templates`
- `path:00_Index`

This makes the graph structurally colored even before every note has perfect tags.

## Glow Layer

The vault enables the CSS snippet `sovereign-glow`.

- Nodes are scaled heavier in graph settings.
- Graph links use bright white variables where Obsidian exposes them.
- Canvas links are set to white, with CSS glow and thicker stroke rules.
- Color groups remain saturated so each node reads as a heavy color core.

## Orbit View

For the native Obsidian orbital layout, open [[Sovereign-Orbit.canvas]].

