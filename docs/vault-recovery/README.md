# Vault Recovery (recovered from Project-AI-vault)

> Recovery index for historical/reference material. Contents are not current
> release evidence or production approval; use the current pre-deployment
> checklist and CAB evidence bundle for successor status.
> Current deployment approval remains fail-closed until those successor gates pass.

Miscellaneous vault subdirectories and root-level documents
recovered from ``T:\00-Active\Project-AI-vault\``.

150 files total, organized in 6 subdirectories:

  - ``_indexes/``        31 files — vault index files
                          (architecture, security,
                          governance, development, etc.)
  - ``readmes/``         10 files — readme hub files
                          (vault overview, master readme
                          hub, indexes navigation, etc.)
  - ``schemas/``          2 files — metadata schemas
                          (JSON and YAML)
  - ``scripts/``          2 files — PowerShell scripts
                          (migrate-metadata-v1-to-v2,
                          validate-metadata)
  - ``copilot/``         39 files — copilot conversation
                          history, custom prompts, memory,
                          and system prompts
  - ``agent-reports/``   66 files — root-level agent
                          reports, indexes, dependency
                          graph, tag taxonomies, and
                          vault-rooted documents

This is reference material and tooling for the canonical's
documentation practices. It does not change package code.

## Port provenance

This commit copies the 150 files from
``T:\00-Active\Project-AI-vault\`` (the frozen legacy
source) into the canonical repo at
``docs/vault-recovery/``. The vault remains in place; this
is a one-way copy. The vault is the frozen source-of-record
(with Google Drive backup per the rebuild's data
preservation policy); the canonical has the working copies
that evolve with the project.

The vault's ``Project-AI/`` subdirectory (270 MB, 3916
files) is NOT included in this recovery — that is the
Obsidian-vault artifacts subdir, classified as DROP per
the inventory (it is a duplicate of the canonical's docs
with Obsidian-flavoured wikilinks that don't add value to
the canonical's Markdown-only doc tree).

## How to use

  - ``_indexes/`` — start with
    ``_indexes/00_INDEX.md`` for the master vault index
  - ``readmes/`` — start with
    ``readmes/Master-README-Hub.md``
  - ``agent-reports/`` — work history of agents
    AGENT-001 through AGENT-080+
  - ``copilot/`` — historical copilot session data and
    custom prompts (reference only; not for re-execution)
  - ``schemas/`` — JSON/YAML schemas for vault metadata
  - ``scripts/`` — PowerShell scripts for metadata
    migration and validation

Verification (4 canonical gates, all green):
  pytest  2319 pass / 1 xfail (unchanged)
  T7      True 3eda3256049339cb069354cc81ee7c51d88e3e41e81ea707e5bf3d3e14ba478c
  ruff    All checks passed
  mypy    12 (pre-existing baseline, unchanged)
