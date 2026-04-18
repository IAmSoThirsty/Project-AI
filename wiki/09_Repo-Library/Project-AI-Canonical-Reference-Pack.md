# Project-AI Canonical Reference Pack

**Generated:** 2026-04-17  
**Repository:** `IAmSoThirsty/Project-AI`  
**Branch:** `github/verified-poc-face`  
**Purpose:** Single-file copy/paste reference for architecture, governance, protocols, standards, APIs, deployment, and terminology.

---

## 1) Project-AI architecture overview

### High-level architecture (concise)

Project-AI is presented as a local-first, constitutionally governed AI ecosystem with a layered structure:

1. **Interface layer**: Desktop/UI and API entry surfaces.
2. **Governance layer**: TARL + Triumvirate evaluation before execution.
3. **Core systems layer**: AI systems, identity/memory/learning modules, and agent subsystems.
4. **Persistence layer**: JSON-backed runtime state and audit/memory records.
5. **Infrastructure layer**: Docker/Kubernetes/Helm/Terraform deployment paths and CI/CD governance checks.

### Canonical architecture sources

- `README.md`
- `.github/instructions/ARCHITECTURE_QUICK_REF.md`
- `docs/PRODUCTION_ARCHITECTURE.md`
- `ARCHITECT_MANIFEST.md`
- `SYSTEM_MANIFEST.md`
- `wiki/00_Index/Architecture-Map.md`
- `WHITEPAPER.md`

---

## 2) Repository map / module inventory

### Primary inventory documents

- `DIRECTORY_INDEX.md` (module-oriented repository map)
- `SYSTEM_MANIFEST.md` (comprehensive inventory and architecture index)
- `FULL_REPOSITORY_MANIFEST.md` (file-level exhaustive manifest)
- `wiki/00_Index/Repo-Folder-Inventory.md` (vault index view)
- `wiki/00_Index/Source-Document-Index.md` (doc source routing)

### Module families (quick inventory)

- **Core/source/runtime**: `src/`, `project_ai/`, `kernel/`, `cognition/`, `orchestrator/`
- **Governance/security**: `governance/`, `security/`, `policies/`, `.github/`
- **Language/protocol**: `tarl/`, `tarl_os/`, `src/thirsty_lang/`
- **API/integration**: `api/`, `integrations/`, `plugins/`
- **Deployment/ops**: `deploy/`, `k8s/`, `helm/`, `terraform/`, `monitoring/`
- **Validation/test**: `tests/`, `adversarial_tests/`, `e2e/`, `benchmarks/`
- **Docs/research**: `docs/`, `wiki/`, `CITATIONS.md`, `WHITEPAPER.md`

---

## 3) Governance charter and policy docs

### Charter / constitutional governance

- `docs/governance/AGI_CHARTER.md` (binding AGI charter)
- `docs/governance/README.md` (governance index and naming guidance)
- `docs/governance/AGI_IDENTITY_SPECIFICATION.md`
- `docs/governance/AI-INDIVIDUAL-ROLE-HUMANITY-ALIGNMENT.md`
- `docs/governance/GOVERNANCE_DOI_MAP.md`

### Active policy and enforcement docs

- `.github/Active_Governance_Policy.md` (highest-precedence active policy)
- `.github/THIRST_BRANCH_ACCEPTANCE_CRITERIA.md`
- `.github/instructions/README.md` (instruction precedence index)
- `.github/instructions/codacy.instructions.md`

---

## 4) Agent protocol specs

### Governance and agent protocol specifications

- `TAMS_SUPREME_SPECIFICATION.md` (meta-constitutional protocol)
- `docs/developer/api/CONSTITUTION.md` (governance kernel constitution/API behavior)
- `Sovereign_Agent_Standard.md`
- `docs/governance/LEGION_COMMISSION.md`
- `taar.toml` (agent runner/orchestration config)

### Wire/protocol/interface artifacts

- `api/sovereign_events.proto` (event protocol)
- `src/shared/proto/events.proto`
- `octoreflex/api/proto/envelope.proto`

---

## 5) Naming conventions and coding standards

### Code standards and tool enforcement

- `CONTRIBUTING.md` (contribution + quality expectations)
- `pyproject.toml` (Ruff/Black/Pytest canonical settings)
- `setup.cfg` (additional project/lint/test config)
- `.github/Active_Governance_Policy.md` (completeness/security standards)
- `.github/instructions/README.md` (instruction resolution order)

### Naming guidance found in governance docs

- `docs/governance/README.md` includes explicit audience/naming guidance, e.g.:
  - External-facing preference for **"Governing Council"** over internal codename **"Triumvirate"**.
  - External-facing preference for **"Governance System"** over **"Codex Deus Maximus"** where appropriate.

---

## 6) ADRs / design decisions

### Status

A formal active ADR corpus (e.g., `docs/adr/ADR-*.md`) was **not found**.

### Closest design-decision artifacts currently present

- `docs/project_ai_god_tier_diagrams/data_flow/governance_decision_flow.md` (decision-flow architecture)
- `wiki/05_Operations/Legacy/Triumvirate-Decisions-2026-04-16.md` (legacy decision evidence)
- `ARCHITECT_MANIFEST.md` (architecture/design posture declaration)

> Practical note: if you want strict ADR discipline, create `docs/adr/` and promote future design decisions there.

---

## 7) Published papers / whitepapers / abstracts

### Canonical publication registry

- `CITATIONS.md` (complete 21-paper DOI catalog + BibTeX)
- `wiki/07_Research/Publications/Publications Index.md` (canonical publication index)
- `wiki/07_Research/Publications/DOI-Registry.md` (DOI source-of-truth)
- `docs/governance/GOVERNANCE_DOI_MAP.md` (governance-paper mapping)

### Whitepaper corpus

- `WHITEPAPER.md` (public canonical whitepaper)
- `docs/executive/whitepapers/PROJECT_AI_COMPREHENSIVE_WHITEPAPER.md`
- `docs/executive/whitepapers/README.md`

### Abstract availability

- Abstract-style metadata is represented through publication indexing/DOI mappings and whitepaper summaries rather than one dedicated `abstracts/` directory.

---

## 8) API contracts / schemas / interface docs

### Primary API contracts

- `api/openapi.json` (OpenAPI 3.1 contract)
- `docs/api/openapi.yaml` (OpenAPI YAML surface)
- `api/project-ai.postman_collection.json` (Postman contract examples)
- `api/README.md` (endpoint semantics and usage)

### Protocol and schema files

- `api/sovereign_events.proto`
- `src/shared/proto/events.proto`
- `octoreflex/api/proto/envelope.proto`
- `config/schemas/defense_engine.schema.json`
- `engines/atlas/schemas/claim.schema.json`
- `engines/atlas/schemas/opinion.schema.json`
- `engines/atlas/schemas/organization.schema.json`
- `engines/atlas/schemas/world_state.schema.json`
- `engines/atlas/schemas/influence_graph.schema.json`
- `engines/atlas/schemas/projection_pack.schema.json`
- `tarl/schema.json`

---

## 9) Deployment and infra notes

### Core deployment runbooks/docs

- `PRODUCTION_DEPLOYMENT.md`
- `deploy/README.md`
- `k8s/README.md`
- `helm/README.md`
- `PRODUCTION_QUALIFICATION_REVIEW.md`
- `PRODUCTION_ROADMAP.md`

### Infrastructure artifacts

- `Dockerfile`
- `Dockerfile.sovereign`
- `docker-compose.yml`
- `docker-compose.override.yml`
- `docker-compose.monitoring.yml`
- `k8s/` (base + overlays)
- `helm/project-ai/`
- `terraform/`
- `monitoring/`

---

## 10) Canonical glossary for Project-AI terminology

### Canonical glossary sources (currently embedded, not standalone)

- `TECHNICAL_SPECIFICATION.md` → **"Glossary of Terms & Translation Layer"**
- `docs/executive/whitepapers/PROJECT_AI_COMPREHENSIVE_WHITEPAPER.md` → **Section 37: GLOSSARY** and **Appendix A: GLOSSARY**
- `docs/executive/whitepapers/README.md` (glossary references)

### Status note

A dedicated standalone canonical glossary file (e.g., `GLOSSARY.md`) was **not found** at top-level canonical docs. Glossary content is currently distributed across specification/whitepaper documents.

---

## Suggested canonical bundle (minimal copy/paste list)

If you need one compact set to hand to reviewers:

- `README.md`
- `DIRECTORY_INDEX.md`
- `SYSTEM_MANIFEST.md`
- `.github/Active_Governance_Policy.md`
- `docs/governance/AGI_CHARTER.md`
- `TAMS_SUPREME_SPECIFICATION.md`
- `TECHNICAL_SPECIFICATION.md`
- `CITATIONS.md`
- `api/openapi.json`
- `api/sovereign_events.proto`
- `PRODUCTION_DEPLOYMENT.md`
- `WHITEPAPER.md`

---

**End of canonical reference pack.**
