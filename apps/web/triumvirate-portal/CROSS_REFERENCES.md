# The Triumvirate → Project-AI Beginnings Cross-Reference

This document maps each pillar of The Triumvirate manifesto to its
implementation in the Project-AI Beginnings package ecosystem.

## Pillar 1: Project AI (Cognitive Engine)

| Triumvirate Page | Beginnings Package | Key Module |
|-----------------|-------------------|------------|
| `pages/project_ai_cognitive_engine.html` | `packages/companion/` | `companion/cognition.py` |
| | `packages/kernel/` | `kernel/evidence.py`, `kernel/invariant.py` |
| | `packages/governance/` | `governance/triumvirate.py` (TriumvirateGovernor) |

**Runtime:** The cognitive engine's governance layer is implemented as
`TriumvirateGovernor` in `packages/governance/src/governance/triumvirate.py`
— a three-vote consensus governor with `Quorum.UNANIMOUS`,
`Quorum.MAJORITY`, and `Quorum.SUPERMAJORITY` rules, inheriting
`GovernanceEngine`'s fail-closed guarantees.

## Pillar 2: Cerberus (Security Fortress)

| Triumvirate Page | Beginnings Package | Key Module |
|-----------------|-------------------|------------|
| `pages/cerberus_security_fortress.html` | `packages/cerberus/` | `cerberus/agent.py` (spawn-constrained agents) |
| | | `cerberus/lockdown.py` (lockdown controller) |
| | `packages/security/` | `security/chimera.py` (Chimera classification) |
| | `packages/identity/` | `identity/registry.py` (actor identity registry) |
| | `packages/capability/` | `capability/tokens.py` (signed, scoped, expiring tokens) |

## Pillar 3: Codex Deus Maximus (Knowledge Repository)

| Triumvirate Page | Beginnings Package | Key Module |
|-----------------|-------------------|------------|
| `pages/codex_deus_maximus_repository.html` | `packages/audit/` | `audit/chain.py` (tamper-evident hash-chained audit log) |
| | `packages/canonical/` | `canonical/state.py` (canonical execution-governance state) |
| | `packages/tarl/` | `tarl/compiler.py` (Threat-Adaptive Rule Language) |

## Governance Bridge

The Triumvirate's three-judge constitutional council concept (Ethics
Judge, Security Judge, Compliance Judge) is implemented in:

- `packages/governance/src/governance/triumvirate.py` — `TriumvirateGovernor`
  with configurable quorum rules
- `packages/governance/src/governance/iron_path.py` — Iron Path risk
  enforcement
- `packages/governance/src/governance/asymmetric_security.py` — asymmetric
  security primitives
- `packages/execution/src/execution/gate.py` — sole fail-closed governed
  actuation gate

## Related Pages

| Page | Related Beginnings Concept |
|------|---------------------------|
| `pages/manifesto_gateway.html` | `docs/reference/AGI_Charter_for_Project-AI_v2_3.pdf` |
| `pages/trinity_deep_dive.html` | `docs/architecture/visual-maps/architecture/governance.md` |
| `pages/scenario_demonstrations.html` | `packages/swr/` (Sovereign War Room) |
| `pages/trust_transparency_center.html` | `packages/audit/` (tamper-evident ledger) |
| `pages/future_architectures.html` | `docs/architecture/` |
| `pages/research_center.html` | `docs/reference/` |
| `pages/jeremy_karrick_founder_profile.html` | Author bio — Jeremy Karrick (IAmSoThirsty) |

## CI Integration

The triumvirate-portal is wired into the Beginnings CI pipeline via
the root `package.json` scripts:

- `pnpm web:test` — runs Jest tests for triumvirate-portal alongside
  docs-portal and proof-portal
- `pnpm web:build` — runs Tailwind CSS build for triumvirate-portal
  alongside other web apps

The `node` CI job in `.github/workflows/ci.yaml` executes these scripts
on every push and pull request.
