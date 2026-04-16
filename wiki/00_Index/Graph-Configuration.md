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
| `#legacy` | warning amber | Captured legacy evidence, not canonical doctrine |
| `#priority/canonical` | solar gold | Source-of-truth notes |
| `#priority/supporting` | slate gray | Supporting notes and evidence |

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
- `#system/codex`
- `#system/four-laws`
- `#system/thirsty-lang`

## Obsidian Setup

This wiki vault includes `.obsidian/graph.json` with the live clash palette for the Graph view in Obsidian.

Keep color groups ordered from specific to broad:

1. Root, bridge, and legacy tags.
2. System tags.
3. Domain tags.
4. Layer and type tags.
5. Priority and status tags.
6. Path fallbacks.

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

## Tag Highlight Layer

The vault enables the CSS snippet `project-ai-tag-colors`.

- Rendered tags are color-coded by domain, layer, type, priority, and legacy status.
- System tags use electric cyan unless a more specific graph group overrides them.
- The file explorer uses folder-path fallback colors because Obsidian CSS cannot inspect a note's frontmatter tags from the file tree.

## Glow Layer

The vault also enables the CSS snippet `sovereign-glow`.

- Nodes are scaled heavier in graph settings.
- Graph links use bright white variables where Obsidian exposes them.
- Canvas links are set to white, with CSS glow and thicker stroke rules.
- Color groups remain saturated so each node reads as a heavy color core.

## Orbit View

For the native Obsidian orbital layout, open [[Sovereign-Orbit.canvas]].

