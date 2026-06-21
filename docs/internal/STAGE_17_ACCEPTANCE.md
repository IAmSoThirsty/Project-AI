# Stage 17 Documentation Acceptance

**Status:** accepted

## Four Documents Created

| Document | Content | Agrees with runtime? |
|---|---|---|
| `docs/operator.md` | Prerequisites, quick-start commands, service endpoints, CI | Yes — commands verified against installed toolchain |
| `docs/architecture.md` | Package dependency graph, descriptions, container map | Yes — descriptions sourced from pyproject.toml; graph matches imports |
| `docs/security.md` | Governance model, container hardening, API auth, audit trail | Yes — container properties verified in Stage 15; gate logic verified in Stage 8 |
| `docs/provenance.md` | Frozen-history verification, paper manifest, merge reports, genesis chain | Yes — all referenced artifacts exist; verify commands are runnable |

## Runtime Agreement Checks

### Package descriptions match pyproject.toml

| Package | pyproject.toml description | docs/architecture.md |
|---|---|---|
| kernel | Deterministic evidence, invariant, state, replay, and time primitives | ✓ |
| security | Chimera security classification and audit relay | ✓ |
| governance | Fail-closed AI-side governance with unilateral veto | ✓ |
| capability | Signed, scoped, expiring capability tokens | ✓ |
| execution | Sole fail-closed governed actuation gate | ✓ |
| companion | Governed, revisioned companion state | ✓ |
| swr | Deterministic governed Sovereign War Room scenarios | ✓ |
| atlas | Subordinate deterministic analytical projections | ✓ |
| arbiter | Experimental operator-side governance substrate | ✓ |
| rlp | Experimental Reciprocal Legitimacy Protocol | ✓ |
| api | Fail-closed FastAPI gateway for development surfaces | ✓ |
| cli | API-bound operator CLI | ✓ |

### Service endpoints match compose.yaml

| Service | Host port in compose.yaml | docs/operator.md |
|---|---|---|
| api | 127.0.0.1:8000 | ✓ |
| docs-portal | 127.0.0.1:4173 | ✓ |
| proof-portal | 127.0.0.1:4174 | ✓ |
| swr / atlas / arbiter-rlp / genesis | internal only | ✓ |

### Container security properties match runtime (Stage 15 evidence)

All seven containers verified with `docker inspect` in Stage 15:
- `ReadonlyRootfs: true` → `docs/security.md: read_only` ✓
- `CapDrop: [ALL]` → `docs/security.md: All dropped` ✓
- `SecurityOpt: [no-new-privileges:true]` → `docs/security.md: Disallowed` ✓
- `/tmp emptyDir` → `docs/security.md: /tmp emptyDir only` ✓

### Verdict set matches implementation

`docs/architecture.md` states "Three outcomes: ALLOW, DENY, ESCALATE."
`REBUILD_EXECUTION_PLAN.md` confirms: "The canonical verdict set for this
development baseline is ALLOW, DENY, and ESCALATE." ✓

### Provenance artifact paths exist

```
docs/internal/frozen-history/      — present (Stage -1.5)
docs/reference/INGEST_MANIFEST.md  — present (Stage -1)
docs/reference/DOI_REGISTRY.md     — present (Stage -1)
docs/internal/STAGE_4_MERGE_REPORT.json — present (Stage 4)
```

All verified present via `ls`. ✓

Note: `governance/sovereign_data/` (compliance bundles, sovereign keypair) lives in
`T:\Project-AI-main` (the legacy source) and is not part of the rebuild repo. It is
referenced in `docs/reference/PROJECT_AI_SOVEREIGN_VERIFICATION_RUNBOOK.md` for
operators who need to verify legacy governance artifacts.
