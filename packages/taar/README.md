# TAAR — Thirsty's Active Agent Runner

**A local-first, governed agent taskforce.** Part of the Project-AI
constitutional architecture. TAAR runs micro-agents against a repository
under strict registry law: one task per agent, minimal authority, maximum
evidence, fail closed, everything classified. Includes a **GitHub Workflow
Guardian** that verifies GitHub Actions workflows before they run.

## What TAAR does

- Runs reader agents that inspect your repo and facility (git state,
  secrets, stale paths, lint/type/test surface, GitHub workflows) and
  produce **hash-sealed evidence bundles**.
- Runs writer agents that turn validated evidence into Markdown reports
  and digests — every report cites its source evidence hash.
- Keeps an **append-only audit spine** (JSONL, hash per record) of every
  admission, denial, success, failure, and classification escalation.
- Classifies everything: `OPEN < CONTROLLED < RESTRICTED < SECRET <
  PHANTOM < BLACK`. Secrets are redacted at capture. Artifacts with no
  producing run record are phantoms and turn the lane BLACK.
- Detects unsafe GitHub Actions patterns: broad permissions, secret
  echoing, `pull_request_target` risk, unpinned actions, shell injection,
  self-hosted/privileged runners, ungated deploys.

## What TAAR does NOT do

The first swarm is report-only. It cannot and will not: merge, push,
publish, deploy, delete, apply patches, create branches, or mutate source.
These capabilities are rejected at registry validation — the constraint is
structural. `taar workflows harden` prints draft suggestions and writes no
patch files.

## Install

    pip install taar-agent-taskforce

Python 3.12+. Dependencies: pyyaml, typer, rich.

## Quick start

    cd your-repo
    taar init                      # seed registry/ + taar.toml (explicit, refuses overwrite)
    taar status                    # facility mode, 44 agents, validation state
    taar run heartbeat-reader      # evidence bundle
    taar run heartbeat-report-writer   # report citing the evidence hash
    taar evidence                  # list bundles
    cat .project-ai/automation/reports/facility/heartbeat-latest.md

## Workflow Guardian

    taar workflows explain         # what your workflows can do
    taar workflows scan            # findings (exit 1 on critical)
    taar workflows classify        # one-word risk verdict
    taar workflows harden          # draft suggestions, nothing applied
    taar workflows evidence        # governed run with full evidence bundle

Or in CI via the composite action — see `action.yml` and
`docs/TAAR_FOR_GITHUB_ACTIONS.md`.

## First swarm demo

    for a in heartbeat-reader heartbeat-report-writer git-status-reader \
             git-status-writer phantom-reader phantom-report-writer \
             governance-reader governance-digest-writer workflow-reader \
             workflow-report-writer; do taar run "$a"; done
    taar status && taar quarantine

## How governance works

Every run passes one gate (`taar/executor.py`): registry valid → agent and
task known and enabled → facility mode permits → capabilities granted →
every command declared, allowed, and granted (exact match) → output paths
in bounds → writer evidence present, hash-valid, and classification
admissible → no lock conflict. Any failure denies, and the denial is
audited. BLACK/PHANTOM evidence feeds no writer except the explicitly
granted handler. SECRET evidence feeds only the declared secret writer,
redacted.

## Layout

    taar/       runtime and CLI          registry/   the governed universe
    checks/     reader built-ins         writers/    writer built-ins
    tests/      87 contract tests        docs/       the canon
    examples/   real evidence samples + workflow examples
    scripts/    registry generator + Windows scheduler scripts

## Docs

Start with `docs/TAAR_REBUILD_DIRECTIVE.md`, then
`docs/LOCAL_AGENT_RULEBOOK.md`, `docs/RUNNER_CONTRACT.md`,
`docs/CLASSIFICATION_MODEL.md`, and
`docs/GITHUB_WORKFLOW_GUARDIAN.md`.

## License

MIT. Author: Jeremy "Thirsty" Karrick — Project-AI / Thirsty's Projects LLC.
