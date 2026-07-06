# Project-AI Rebuild Execution Ledger

**Status:** LOCAL ACCEPTANCE COMPLETE; DEVELOPMENT CHECKPOINT IN PROGRESS
**Canonical repository:** `T:\00-Active\Project-AI-Beginnings`
**Working branch:** `main` (current development checkpoint; previous rebuild
work landed from `codex/rebuild-continuation`)
**Legacy source:** `T:\00-Active\Project-AI-main` (read-only input by policy)
**Python:** 3.12.10
**Package manager:** uv
**Development version:** `0.0.0.dev0`
**License:** MIT

## Authority

This ledger is the active execution authority for the rebuild. The external
Hermes plan remains the detailed provenance source, but its earlier path,
stage-count, package-count, lockfile, release, and unanswered-question text is
superseded where it conflicts with this ledger.

No existing commit will be rewritten. Existing Stage 0 commits jointly satisfy
the bootstrap and repository-skeleton work; acceptance evidence will record the
mapping without relabeling history.

## Safety Boundaries

- Preserve all user files, local changes, ignored files, branches, and tags.
- Never write to `T:\00-Active\Project-AI-main` during rebuild execution.
- Soft-freeze the legacy repository by recording state and hashes, not by
  changing ACLs, Git configuration, attributes, or files.
- Keep all work local until the complete acceptance gate passes.
- Do not create a version tag, GitHub Release, deployment, package publication,
  container publication, or production-readiness claim.
- After local acceptance, push a fresh `main` branch to the existing remote;
  do not modify legacy `master`, existing tags, or the remote default branch.

## Authoritative Gates

| Gate | Deliverable | Exit condition |
|---|---|---|
| -1.5 | Frozen history | 2,264/2,264 chain links verify |
| -1 | Corpus and wiki evidence | Hash, provenance, dropped-file, DOI, and discrepancy evidence complete |
| 0 | Bootstrap evidence | Repository, Git state, and Python 3.12.10 verified |
| 1 | Skeleton evidence | Root policy, metadata, MIT license, and ignore rules verified |
| 2 | Root workspace | `uv sync`, editable install, lock, lint configuration, and smoke tests pass |
| 3 | Soft freeze | Legacy HEAD/origin/dirty hashes recorded; zero legacy writes |
| 4 | Duplicate merge | SWR and Atlas deterministic merge reports pass |
| 4.5 | Arbiter | Experimental package and boundary tests pass |
| 4.6 | RLP | Experimental package and policy tests pass |
| 4.7 | Web source and Chimera | Selective OMPT and reusable security package tests pass |
| 4.8 | Governance framework | Selective policy assets and compliance tests pass |
| 5 | Kernel | Install, imports, strict typing, tests, and coverage pass |
| 6 | Governance | Three-outcome, veto, and fail-closed tests pass |
| 7 | Capability | Signed, scoped, expiring-token tests pass |
| 8 | Execution | Every actuation requires governance and authority |
| 9 | Companion | State restoration and governed companion tests pass |
| 9.5 | Android | Scoped read-only DOI/replay client builds/tests pass; Unity deferred by user decision on 2026-06-21 |
| 10 | SWR | Scenario and governed-operation tests pass |
| 11 | Atlas and Genesis | Subordination and Rust-emitter tests pass |
| 12 | API | Health, replay, audit, and authenticated Chimera routes pass |
| 13 | CLI | Operator commands and bypass-prevention tests pass |
| 14 | Web portals | Both React portal lint/test/build pipelines pass |
| 14.5 | Desktop | PyQt6 offscreen smoke and development build pass |
| 15 | Containers | Seven Compose services build and become healthy |
| 16 | CI | Local CI-equivalent checks and workflow validation pass |
| 16.5 | Kubernetes | Helm lint and client-side manifest validation pass |
| 17 | Documentation | Operator, architecture, security, and provenance docs agree with runtime |
| 18 | Acceptance | PowerShell and POSIX gates pass from a clean checkout |
| checkpoint | Development remote | Fresh `main` pushed and CI green; no tag or release |

## Package And Application Boundaries

Python packages follow a downward-only dependency graph:

`kernel/security -> governance/capability -> execution -> companion/SWR/Atlas/Genesis -> API/CLI`

Arbiter and RLP are experimental operator-side governance packages. They may
invoke AI-side execution only through the same execution gate and cannot grant
themselves authority. Web, desktop, and Android are applications that
consume read-only or explicitly authorized API surfaces; they do not embed
governance authority.

The previously planned Unity 3DOF client is superseded and deferred by the
user's 2026-06-21 instruction to skip the Unity section. No Unity repository
surface is required by this development checkpoint.

The canonical verdict set for this development baseline is `ALLOW`, `DENY`,
and `ESCALATE`. Seven-outcome proposals remain reference material only.

## Validation Contract

Every gate ends with the narrowest relevant deterministic tests, a reviewed
diff, an updated acceptance record, and a stage-scoped commit. The final gate
also requires the canonical 5/5 replay, all 312 asymmetric-security cases, the
Arbiter baseline, Chimera relay evidence, frontend/application builds,
container health, and infrastructure validation.
