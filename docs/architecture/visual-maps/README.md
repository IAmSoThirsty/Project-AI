# Visual Maps (recovered from Project-AI-vault)

Architecture, data-flow, and dependency visual maps authored
by AGENT-047 (Visual Relationship Maps Specialist) and
recovered from ``T:\00-Active\Project-AI-vault\visual-maps\``.

## What's here

10 documents (414 KB total), all in Obsidian-style Markdown
with YAML frontmatter (title, id, type, version, dates,
status, author, area, tags, component, related_docs,
audience, priority).

### `architecture/` (6 files)

  - `system-overview.md` — 752 lines, complete-system
    architecture map
  - `ai-systems.md` — AI-systems architecture
  - `governance.md` — governance architecture
  - `memory-system.md` — enhanced memory architecture schematic
    spanning working memory, long-term memory, companion
    intelligence, TAAR, Shadow Thirst, containment, and
    governance memory
  - `desktop-app.md` — desktop application architecture
  - `web-app.md` — web application architecture

### `data-flows/` (3 files)

  - `ai-query.md` — AI query processing flow
  - `authentication.md` — authentication flow
  - `image-generation.md` — image generation flow

### `dependencies/` (1 file)

  - `module-dependencies.md` — module dependency map

## Author and provenance

All 9 documents are by **AGENT-047 (Visual Relationship
Maps Specialist)**, created 2026-04-20, version 1.0.0,
status: active.

The vault was the working source where AGENT-047's maps
lived; the canonical repo (which split from the vault
into its own git-tracked home) did not have these
documents. This is a real recovery — the maps are
authored, dated, and relate to the canonical's actual
package structure (16 packages, governance, capability,
etc.).

## How to read

These documents are Obsidian-style Markdown. Each has a
header block with metadata, a `# Document Classification`
section with tags and components, a `# Relationships`
section with cross-references to other docs, and the
architecture/data-flow body.

The maps are reference material. They do not change
package behavior; they describe the as-built architecture
in human-readable form.

## Port provenance

This commit copies the 9 visual-maps files from
``T:\00-Active\Project-AI-vault\visual-maps\`` (the
frozen legacy source) into the canonical repo at
``docs/architecture/visual-maps/``. The vault itself
remains in place; this is a one-way copy. The vault
becomes a frozen source-of-record for the maps (with
Google Drive backup per the rebuild's data preservation
policy), and the canonical has the working copies that
evolve with the project.

The original Obsidian frontmatter (``%% --- %%`` style
links, ``[[wikilinks]]``, etc.) is preserved verbatim
because the canonical's docs/ already mixes
Obsidian-flavoured Markdown and conventional Markdown
(see ``docs/operations/CONTINUITY_MAP.md``).

## What this commit does NOT do

  - Does NOT add, remove, or edit any source code
  - Does NOT modify any package or schema
  - Does NOT change any test
  - Does NOT change the T7 convergence hash
  - Does NOT touch any other vault subdir
    (those are separate commits in the vault recovery
    series)

## See also

  - ``docs/internal/LEGACY_TO_CANONICAL_INVENTORY.md``
    §9 — the satellite inventory
  - ``docs/operations/CONTINUITY_MAP.md`` — the
    operational continuity map (similar style, also
    Obsidian-flavoured)
  - ``docs/deployment/HELM_DEPLOY.md`` and
    ``docs/deployment/PRODUCTION_DEPLOY.md`` — also
    recovered from the same era

Verification (4 canonical gates, all green):
  pytest  2319 pass / 1 xfail (unchanged)
  T7      True 3eda3256049339cb069354cc81ee7c51d88e3e41e81ea707e5bf3d3e14ba478c
  ruff    All checks passed
  mypy    12 (pre-existing baseline, unchanged)
