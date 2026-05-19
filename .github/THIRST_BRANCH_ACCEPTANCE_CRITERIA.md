# Thirst of Gods Branch Operating Model (Project‑AI)

**Scope:** Repository branch architecture, promotion controls, runtime invariants, and production acceptance gates for Project‑AI.

**Canonical Naming Vocabulary:**

- **Thirsty‑Lang**: sovereign orchestration language contract for cross-lane work intent.
- **Thirst of Gods**: governance doctrine for branch promotion, proof, and release authority.
- **T.A.R.L.**: trusted execution/runtime abstraction used for governed execution and replay.
- **Shadow Thirst**: simulation/what-if validation plane before irreversible promotion.
- **TSCG**: symbolic governance grammar for human-readable policy contracts.
- **TSCG+B**: binary canonicalization profile for deterministic transport and audit trace compactness.

---

## 1) Branch Topology Contract (Diagram-aligned)

Mandatory branch lanes and intents:

1. `main`
2. `dev`
3. `experiment/*`
4. `heal/repair`
5. `legacy/*`
6. `release/*`
7. `hotfix/*`
8. `governance-lock`
9. `security-hardening`

### 1.1 Current concrete lane heads in Project‑AI

- `main`
- `dev`
- `experiment/bootstrap`
- `heal/repair`
- `legacy/master-archive-2026-04-15` (archive intent)
- `release/v-next`
- `hotfix/urgent-template`
- `governance-lock`
- `security-hardening`

> Policy: wildcard lanes (`experiment/*`, `release/*`, `hotfix/*`, `legacy/*`) **must** have at least one maintained concrete branch.

---

## 2) Lane Responsibilities and Interfaces

### 2.1 `main` (Trunk of Record)

**Responsibility:** Production-grade, signed, promotion-authorized code only.

**Inbound interfaces:**

- `release/*` (standard promotions)
- `hotfix/*` (emergency promotions)
- `governance-lock` (constitution/rule updates with quorum)

**Outbound interfaces:**

- `dev` refresh baseline
- artifact publication and immutable tags

**Non-negotiables:**

- protected branch
- required status checks
- no direct force-push
- traceable PR lineage

### 2.2 `dev` (Integration Plane)

**Responsibility:** Feature convergence, pre-release stabilization.

**Inbound:** `experiment/*`, `heal/repair`, `security-hardening`.

**Outbound:** `release/*`.

**Non-negotiables:**

- governed CI required
- no unresolved architecture conflicts

### 2.3 `experiment/*` (Exploration Plane)

**Responsibility:** High-velocity prototyping for Thirsty‑Lang/T.A.R.L./Shadow Thirst evolutions.

**Inbound:** trunk snapshot from `main` or `dev`.

**Outbound:** PR to `dev` only (no direct `main`).

**Non-negotiables:**

- experiment charter present
- rollback plan present
- feature flags default OFF

### 2.4 `heal/repair` (Recovery Plane)

**Responsibility:** Invariant correction, data/ledger repair, emergency stabilizers.

**Inbound:** incident findings, postmortems, runtime SLO breach reports.

**Outbound:** PR to `dev` (or `hotfix/*` when severity demands).

**Non-negotiables:**

- explicit repaired invariant statement
- before/after proof artifact

### 2.5 `legacy/*` (Archive & Compatibility Plane)

**Responsibility:** Legacy archival retention and compatibility references.

**Inbound:** historical branch snapshots.

**Outbound:** no normal promotion; selective compatibility patches only.

**Non-negotiables:**

- immutable intent by default
- risk acceptance note required for any write

### 2.6 `release/*` (Release Candidate Plane)

**Responsibility:** Candidate hardening, final verification, artifact integrity.

**Inbound:** `dev`.

**Outbound:** `main`.

**Non-negotiables:**

- signed artifacts
- SBOM + vulnerability gate
- reproducible build proof

### 2.7 `hotfix/*` (Emergency Plane)

**Responsibility:** Critical production remediation.

**Inbound:** `main` snapshot + incident context.

**Outbound:** `main` and back-merge to `dev`.

**Non-negotiables:**

- issue/incident ID mandatory
- blast radius analysis mandatory

### 2.8 `governance-lock` (Constitution Plane)

**Responsibility:** AGI Charter, Sovereign Covenant, TSCG/TSCG+B policy contract changes.

**Inbound:** governance RFCs, audit outcomes.

**Outbound:** controlled merge to `main` with quorum.

**Non-negotiables:**

- quorum approval
- immutable audit trail
- policy migration notes

### 2.9 `security-hardening` (Security Plane)

**Responsibility:** threat mitigation, policy hardening, zero-trust upgrades.

**Inbound:** findings from static analysis, dependency scans, adversarial tests.

**Outbound:** `dev` (and `hotfix/*` if emergency).

**Non-negotiables:**

- vulnerability closure evidence
- threat model delta summary

---

## 3) Information Transfer Contract (“Relevant Information”)

Every lane carries a minimum common transfer set:

1. **Architecture context**
   - Core system map (PSIA, Triumvirate, OctoReflex, Iron Path)
   - Runtime map (T.A.R.L., Thirsty‑Lang, Shadow Thirst, Canonical State)

2. **Governance context**
   - AGI Charter / Sovereign Covenant references
   - TSCG policy contract references

3. **Operational context**
   - build/test entry points
   - CI gate expectations
   - rollback/recovery paths

4. **Security context**
   - authN/authZ touchpoints
   - secret and key handling constraints
   - supply-chain scan expectations

5. **Data contract context**
   - migration compatibility notes
   - audit and retention implications

This repository-level file and `.github/branch-transfer-matrix.yaml` are the authoritative transfer manifests for these requirements.

---

## 4) Acceptance Criteria (Production-grade)

### 4.1 Build/Quality

- deterministic builds or documented non-determinism
- no failing required tests in target lane
- lint/type baselines enforced by lane policy

### 4.2 Security

- dependency risk reviewed
- high/critical findings triaged before promotion
- secret exposure check passed

### 4.3 Governance

- policy-impacting changes include TSCG contract delta
- governance-lock required for constitutional edits

### 4.4 Reliability

- retries/backoff documented for changed network paths
- idempotency behavior declared for changed mutation APIs
- timeout/concurrency limits declared for new services/jobs

### 4.5 Observability

- logs include traceable request/build IDs
- metrics and failure counters defined for new code paths

### 4.6 Release/Recovery

- rollback strategy documented (hard reset tag, revert, or roll-forward)
- release lanes include SBOM and artifact checksum record

---

## 5) Failure Modes and Required Countermeasures

1. **Network partition / remote outage**
   - use local checkpoint tags
   - delayed push strategy; avoid force-push

2. **Version skew (dev vs release)**
   - back-merge policy enforced after hotfix

3. **Policy drift across branches**
   - governance-lock lane is single source for constitutional deltas

4. **Corrupted or orphaned Git objects**
   - scheduled `git fsck --full --strict`
   - periodic maintenance/gc

5. **Adversarial input / unsafe execution changes**
   - security-hardening lane first
   - cannot bypass required checks on main

---

## 6) Branch Promotion Flow (Thirst of Gods)

1. `experiment/*` → `dev`
2. `heal/repair` → `dev`
3. `security-hardening` → `dev`
4. `dev` → `release/*`
5. `release/*` → `main`
6. `hotfix/*` → `main` + back-merge to `dev`
7. `governance-lock` → `main` (quorum path)
8. `legacy/*` remains archival unless explicit compatibility exception

---

## 7) Mandatory Metadata for New Branches in Wildcard Lanes

When creating new branches under wildcard lanes, include:

- branch rationale
- expected lifetime
- promotion target
- rollback trigger
- owner/team
- incident/RFC linkage (if applicable)

Suggested naming:

- `experiment/<initiative>`
- `release/vX.Y-rcN`
- `hotfix/<incident-id>-<slug>`
- `legacy/<archive-purpose>`

---

## 8) Project‑AI Tailoring Notes

This model is explicitly tuned for:

- governance-first evolution (AGI Charter + Sovereign Covenant)
- runtime sovereignty (`T.A.R.L.` + Shadow Thirst)
- policy portability (`TSCG` + `TSCG+B`)
- production incident recoverability through clear lane semantics

If any lane semantics conflict with infrastructure constraints, governance-lock takes precedence for policy resolution.

---

## 9) Immediate Repository-Level Completion Status

- [x] `main` trunk set and remote default validated
- [x] branch lanes created for all diagram categories
- [x] legacy archival posture established (`legacy/master-archive-2026-04-15`)
- [x] transfer manifests implemented (`.github/THIRST_BRANCH_ACCEPTANCE_CRITERIA.md`, `.github/branch-transfer-matrix.yaml`)
