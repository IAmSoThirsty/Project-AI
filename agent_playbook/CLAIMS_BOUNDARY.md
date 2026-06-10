# Claims Boundary

**Version**: 1.1
**Date**: 2026-06-10
**Status**: Active control
**Scope**: Defines what the Agent Playbook may and may not claim before Project-AI Main handoff.

## Purpose

This file prevents the roadmap, README, external review package, and future technical work from overstating readiness. It is the boundary between aspiration, documented scaffold, implemented substrate, and audit-hardened evidence.

## Claim Levels

| Level | Name | Allowed wording | Required evidence |
| --- | --- | --- |
| C0 | Proposal | Proposed, planned, roadmap item | Roadmap or review entry |
| C1 | Documented scaffold | Documented, specified, governed by template/protocol | Existing file and index link |
| C2 | Implemented manual capability | Script/tool/template exists and can be run or followed manually | File exists and manual command/procedure is documented |
| C3 | Machine-validated capability | Validated, enforced by validator, CLI check, or schema | Passing command output or evidence bundle |
| C4 | Handoff candidate | Ready for Project-AI handoff review | Passing `PROJECT_AI_HANDOFF_READINESS.md` evidence bundle |
| C5 | External audit hardened | Independently reviewable, signed, reproducible, externally challenged | Signed release, independent review record, reproducible evidence |

## Current Allowed Claims

The Agent Playbook may currently claim:

- It is a staging governance playbook intended for eventual Project-AI integration.
- It has an excellent governance scaffold: constitution, templates, anti-patterns, failure memory, protocols, metrics seed, risk register, and roadmap.
- It has a no-silent-pass validator script that reports checks run, files inspected, warnings, failures, known blind spots, and final status.
- It has a thin CLI package seed with advisory keyword-based `classify` support and diagnostic `doctor` support.
- It supports `python -m agent_playbook.cli` from a source checkout through a local import shim.
- It has a machine-readable governance core and advisory load profiles under `governance/`.
- It has provenance scripts for manifests, Merkle tree generation, and Ed25519 signing.
- It has hash-backed provenance verification through `ap verify-provenance` and `ap validate --verify-provenance`.
- It has signature-capable Ed25519 manifest verification.
- It has a documented provenance root-of-trust process and configured public key under `provenance/public_key.pem`.
- It has signature-backed seed evidence for `evidence/2026-06-08-playbook-seeding/`.
- It has a signed legacy Project-AI promotion-readiness candidate bundle under `evidence/2026-06-09-project-ai-promotion-readiness/`.
- It has a signed final handoff readiness bundle under `evidence/2026-06-10-final-handoff-readiness/`.
- It has promotion evidence and human signoff templates with validator-enforced section coverage.
- It has active async review, authority continuity, review debt, and second-human review protocols.
- It has core Markdown template schemas and validator-required schema coverage.
- It has heuristic semantic checks for failure records and human signoff records.
- It has a deprecation review register and deprecation record template.
- It has second-human/external-review readiness artifacts for requesting and recording review.
- It has portable agent prompting standards and a runtime training pack as guidance for non-Grok runtimes.
- It has a roadmap integration review and Option C governance controls.
- Per owner directive on 2026-06-10, the Agent Playbook content has been integrated into Project-AI Main at `agent_playbook/`. The prior "handoff readiness candidate, not applied" language is superseded for this integration.

## Claims That Are Blocked

The Agent Playbook must not claim (historical; superseded by owner directive 2026-06-10 for the integration action):

- Approved for Project-AI Main handoff or integration.   [SUPERSEDED: owner has now directed and integration is being executed]
- Already handed off to or integrated into Project-AI Main.   [SUPERSEDED: owner has now directed the integration]

(Other blocked claims from original retained for historical context in this copy.)

## Provenance Status Levels

Every evidence or release claim must use one of these levels:

| Status | Meaning | Allowed claim |
| --- | --- | --- |
| absent | No provenance artifact exists | No provenance claim |
| descriptive only | Text describes origin or process | Described source/process only |
| hash-backed | Hashes or Merkle roots exist and can be recomputed | Tamper-evident at hash level |
| signature-backed | Real signature verifies against documented public key | Signed by named key owner |
| externally timestamped | Signature/hash is anchored by external timestamp or independent service | Externally timestamped evidence |

No document may imply a higher provenance status than the artifacts actually support.

## Scope and Out of Scope

In scope:

- Governance artifacts in this staging repo.
- Project-AI handoff readiness.
- Claims made by root docs, roadmap docs, external review docs, protocols, validator output, and CLI output.
- Evidence status language.

Out of scope for this pass:

- Modifying Project-AI Main.
- Generating or committing production signing keys.
- Treating hash-backed or unsigned provenance as signature-backed or externally timestamped provenance.
- Treating classifier output as approval or enforcement.
- Treating `ap doctor` as Project-AI Main handoff approval.
- Treating portable prompting guidance as proof that each runtime has been validated.
- Creating external benchmark or challenge results.
- Claiming third-party review.

## Public Claims Discipline

External-facing language must include the current maturity band from `CANT_COMPARE_STANDARD.md` and must name limitations. Strong comparative language is allowed only as an aspiration unless evidence exists.

## Misuse and Cargo-Cult Warning

Copying these documents without validator enforcement, evidence discipline, human signoff, and change control does not reproduce the governance system. The power is in the controls, not in the presence of impressive-looking files.

## Review Rule

Any root document, external document, roadmap item, or release note that changes readiness language must be checked against this boundary before publication.
