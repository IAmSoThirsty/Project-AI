# Source Documentation (recovered from Project-AI-vault)

Source-code documentation recovered from
``T:\00-Active\Project-AI-vault\source-docs\``.

58 files, 1.8 MB total, organized in 6 subdirectories:

  - ``agents/``        — agent deliverable summaries,
                         collaboration diagrams
  - ``core/``          — core-system documentation
  - ``core/constitutional/`` — constitutional layer docs
  - ``gui/``           — GUI module documentation
  - ``security/``      — security subsystem docs
  - ``supporting/``    — supporting infrastructure docs

Source documentation is reference material about the
canonical's packages and their intended behavior. It does
not change package code; it documents the design and
intent.

## Port provenance

This commit copies the 58 source-doc files from
``T:\00-Active\Project-AI-vault\source-docs\`` (the frozen
legacy source) into the canonical repo at
``docs/source-docs/``. The vault remains in place; this is
a one-way copy. The vault is the frozen source-of-record
(with Google Drive backup per the rebuild's data
preservation policy); the canonical has the working copies
that evolve with the project.

Verification (4 canonical gates, all green):
  pytest  2319 pass / 1 xfail (unchanged)
  T7      True 3eda3256049339cb069354cc81ee7c51d88e3e41e81ea707e5bf3d3e14ba478c
  ruff    All checks passed
  mypy    12 (pre-existing baseline, unchanged)
