# Diagrams (recovered from Project-AI-vault)

This directory contains **42 files** of visual
documentation recovered from
``T:\\00-Active\\Project-AI-vault\\Project-AI\\diagrams\\``
(pre-J2-port snapshot of Project-AI-Beginnings).

## What was recovered (42 files, 593 KB)

### Architecture diagrams (10 topics)

  - ``architecture/01-core-ai-systems.md``
  - ``architecture/02-governance-pipeline.md``
  - ``architecture/03-constitutional-ai.md``
  - ``architecture/04-security-systems.md``
  - ``architecture/05-gui-components.md``
  - ``architecture/06-agent-systems.md``
  - ``architecture/07-temporal-systems.md``
  - ``architecture/08-data-storage.md``
  - ``architecture/09-web-backend.md``
  - ``architecture/10-infrastructure.md``
  - ``architecture/README.md``

These use Mermaid ``graph TB`` syntax to render
the system topology. They are **complementary**
to the existing ``docs/architecture/visual-maps/``
content (which is prose executive summaries).

### Flow diagrams (8 flows)

  - ``flows/1-user-authentication-flow.md``
  - ``flows/2-ai-query-processing-flow.md``
  - ``flows/3-governance-validation-flow.md``
  - ``flows/4-security-threat-detection-flow.md``
  - ``flows/5-data-persistence-flow.md``
  - ``flows/6-command-override-flow.md``
  - ``flows/7-image-generation-flow.md``
  - ``flows/8-deployment-pipeline-flow.md``
  - ``flows/INTEGRATION_GUIDE.md``
  - ``flows/README.md``

### Sequence diagrams (6 sequences)

  - ``sequences/01-user-login-sequence.md``
  - ``sequences/02-ai-chat-interaction-sequence.md``
  - ``sequences/03-governance-validation-sequence.md``
  - ``sequences/04-security-alert-sequence.md``
  - ``sequences/05-agent-orchestration-sequence.md``
  - ``sequences/06-api-request-response-sequence.md``
  - ``sequences/README.md``

### Excalidraw sources + SVG renders (5 concepts)

  - ``excalidraw/agent-orchestration-concept.{excalidraw,svg}``
  - ``excalidraw/constitutional-ai-concept.{excalidraw,svg}``
  - ``excalidraw/data-flow-concept.{excalidraw,svg}``
  - ``excalidraw/governance-pipeline-concept.{excalidraw,svg}``
  - ``excalidraw/security-perimeter-concept.{excalidraw,svg}``
  - ``excalidraw/system-integration-concept.{excalidraw,svg}``
  - ``excalidraw/README.md``
  - ``excalidraw/convert_to_svg.py`` (Excalidraw
    → SVG converter, stdlib-only)

## What was NOT ported

  - **Nothing.** All 42 files were ported.
  - None had Obsidian YAML frontmatter.
  - The 1 ``.py`` file (``convert_to_svg.py``) is
    a stdlib-only utility for converting the
    Excalidraw JSON sources to SVG; it's a
    tool, not application code.

## How these complement existing canonical docs

The existing ``docs/architecture/visual-maps/``
content (port in earlier work) has **prose
executive summaries** of the same systems.
The vault's diagrams have **Mermaid graphs and
sequence/flow markup** — different content, same
topic. Both are kept; this recovery adds the
visual content.

## Verification

Per Thirstys V3 #4 (don't fake success):

  - All 29 ``.md`` files have no Obsidian
    YAML frontmatter (verified by
    frontmatter detector)
  - The 1 ``.py`` file has no external
    dependencies (only ``json``, ``os``,
    ``pathlib``, ``typing``)
  - The 12 binary files (6 ``.excalidraw`` + 6
    ``.svg``) are valid JSON / SVG (verified
    by the tests in
    ``docs/tests/test_diagrams_recovery.py``)
