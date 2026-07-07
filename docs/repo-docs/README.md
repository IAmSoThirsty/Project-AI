# Repo Documentation (recovered from Project-AI-vault)

Comprehensive repository documentation recovered from
``T:\00-Active\Project-AI-vault\repo-docs\``.

936 files, 16 MB total, organized in 70+ subdirectories
covering the full breadth of Project-AI's documentation
taxonomy. This is the bulk of the vault's reference
material.

## What's here

Major subdirectories (sized in MB):

  - ``reports/``                5.0 MB, 263 files
  - ``internal/``               3.0 MB, 211 files
  - ``developer/``              1.3 MB,  92 files
  - ``architecture/``           989 K,  58 files
  - ``security_compliance/``    870 K,  51 files
  - ``project_ai_god_tier_diagrams/``  844 K, 44 files
  - ``assets/``                 512 K,  10 files
  - ``governance/``             624 K,  29 files
  - ``executive/``              424 K,   9 files
  - ``archive/``                236 K,   4 files
  - ``legal/``                  216 K,  21 files
  - ``whitepapers/``            116 K,   7 files
  - ``architecture/formal_verification/`` (under architecture)
  - ``dataview-examples/``       84 K,   9 files
  - ``security/``                12 K,   3 files
  - Plus ~30 smaller subdirectories covering agents,
    AI/ML, API, design, formal, gradle, hardware,
    integration, language, nirl, operations, papers,
    plan, research, shadow_thirst, spec, sre,
    templates, testing, ui_ux.

This is reference material about the canonical's design,
governance, security posture, and operational practices.
It does not change package code; it documents the
system in human-readable form.

## Port provenance

This commit copies the 936 repo-doc files from
``T:\00-Active\Project-AI-vault\repo-docs\`` (the frozen
legacy source) into the canonical repo at
``docs/repo-docs/``. The vault remains in place; this
is a one-way copy. The vault is the frozen
source-of-record (with Google Drive backup per the
rebuild's data preservation policy); the canonical has
the working copies that evolve with the project.

A single 900+ file commit is appropriate here because:
  - All 936 files are pure documentation (Markdown, plus
    a few small assets in ``assets/``)
  - No executable code, no tests, no schema, no config
  - The 4 canonical gates are unaffected
  - This is the standard THIRSTYS V3 "sweep the
    recoverable data" pattern applied to a doc-heavy
    subtree

## How to navigate

Start with ``docs/repo-docs/00_INDEX.md`` (the master
navigation hub) or ``docs/repo-docs/DOCUMENTATION_STRUCTURE_GUIDE.md``
(the structure overview).

Verification (4 canonical gates, all green):
  pytest  2319 pass / 1 xfail (unchanged)
  T7      True 3eda3256049339cb069354cc81ee7c51d88e3e41e81ea707e5bf3d3e14ba478c
  ruff    All checks passed
  mypy    12 (pre-existing baseline, unchanged)
