# Templates (recovered from Project-AI-vault)

> Recovered/reference material only: this directory is not current release
> evidence or deployment approval. The successor remains fail-closed until
> the current pre-deployment checklist and CAB evidence bundle pass.

Documentation templates recovered from
``T:\00-Active\Project-AI-vault\templates\``.

53 files, 804 KB total. Templates are reference material for
the canonical's documentation practices. They describe
document types used across the project (architecture ADRs,
module docs, agent reports, incident postmortems, etc.) and
provide fillable scaffolds.

## What's here

- 29 root-level files (templates for ADRs, design patterns,
  integration APIs, code-review checklists, agent docs,
  postmortems, etc.)
- 4 subdirectories: ``development/``, ``documentation/``,
  ``operations/``, ``scripts/`` (each with category-specific
  templates)

## How to use

These templates are not required by the canonical's tooling;
they are reference material for the project's documentation
style. Use them as starting points when authoring new docs
of the relevant type.

## Port provenance

This commit copies the 53 template files from
``T:\00-Active\Project-AI-vault\templates\`` (the frozen
legacy source) into the canonical repo at
``docs/templates/``. The vault remains in place; this is a
one-way copy. The vault is the frozen source-of-record (with
Google Drive backup per the rebuild's data preservation
policy); the canonical has the working copies that evolve
with the project.

Historical port baseline (not current release evidence):
  pytest  2319 pass / 1 xfail (at recovery time)
  T7      True 3eda3256049339cb069354cc81ee7c51d88e3e41e81ea707e5bf3d3e14ba478c
  ruff    All checks passed
  mypy    12 (at recovery time)

Current successor evidence is authoritative only in
`docs/deployment/PRE_DEPLOYMENT_CHECKLIST.md` and the CAB bundle.
