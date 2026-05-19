<!-- markdownlint-disable MD012 -->
# Project-AI Instruction System Index

This index defines the purpose of each instruction artifact, its authority level, and how assistants must resolve overlap.

No instruction file should be dismissed without inspection.

## Instruction files and purpose levels

| Level | File | Purpose | Usage rule |
|---|---|---|---|
| P0 | `.github/Active_Governance_Policy.md` | Authoritative governance policy for quality, security, completeness, and production readiness | Mandatory and highest precedence |
| P0 | `.github/instructions/codacy.instructions.md` | Operational quality/security gate for Codacy-integrated analysis and dependency security checks | Mandatory when Codacy tooling is available |
| P1 | `.github/instructions/ARCHITECTURE_QUICK_REF.md` | Structural runtime reference: architecture, data flow, integration patterns, critical operational constraints | Mandatory for implementation alignment |
| P2 | `.github/instructions/IMPLEMENTATION_SUMMARY.md` | Implementation evidence ledger for instruction system evolution and coverage status | Informative, must remain accurate |
| P3 | `archive/.github/copilot-instructions.md` | Legacy technical context | Reference only, cannot override P0/P1 |

## Resolution order

When guidance overlaps, resolve in this exact order:

1. `.github/Active_Governance_Policy.md`
2. `.github/instructions/codacy.instructions.md`
3. `.github/instructions/ARCHITECTURE_QUICK_REF.md`
4. `.github/instructions/IMPLEMENTATION_SUMMARY.md`
5. `archive/.github/copilot-instructions.md`

## Concrete gating protocol

Before implementing or modifying code, assistants should execute these gates:

1. **Governance gate**: Validate that the intended output satisfies P0 governance requirements.
2. **Quality/security gate**: Apply Codacy policy behavior when Codacy tools are reachable.
3. **Architecture gate**: Validate structural coherence against architecture/runtime contracts.
4. **Evidence gate**: Reflect significant instruction-system updates in implementation summary.
5. **Legacy context gate**: Use legacy notes only as supplementary context.

## Monorepo integrity policy

Assistants must treat repository artifacts as potentially mission-critical unless maintainers explicitly classify otherwise.

## Maintenance expectations

- Keep this index synchronized with all instruction artifacts.
- Update purpose levels when new instruction files are added.
- Preserve stable resolution order semantics unless governance policy changes.

Instruction index baseline established and active.

