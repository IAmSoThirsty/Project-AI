# Canonical State

Persistence layer for Project-AI's execution-governance
spine. Composes identities, capabilities, and policy into a
single restorable JSON snapshot.

## What this is

A minimal composable state for the governance spine:

  - `CanonicalState` — `@dataclass` with three fields:
      - `identities: IdentityRegistry`
      - `capabilities: CapabilityRegistry`
      - `policy: StaticGovernancePolicy`
    With `to_record()` / `from_record()` for JSON
    serialization, and `empty()` factory.

  - `FileCanonicalStore` — atomic JSON file persistence:
      - `save(state)` writes to a temp file then `os.replace`
        (POSIX-atomic on most systems)
      - `load()` reads back into a `CanonicalState`
      - `CanonicalStoreError` raised on missing file, parse
        failure, or decode failure

## Run it

```python
from datetime import datetime, timedelta, timezone
from canonical import CanonicalState, FileCanonicalStore
from identity import IdentityRecord, IdentityRegistry
from capability import CapabilityToken, CapabilityRegistry
from governance import StaticGovernancePolicy

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)
state = CanonicalState(
    identities=IdentityRegistry([IdentityRecord("actor-1", active=True)]),
    capabilities=CapabilityRegistry([
        CapabilityToken.issue(
            "token-1", "actor-1",
            {"test.echo"}, {"resource-1"},
            NOW + timedelta(minutes=5),
        ),
    ]),
    policy=StaticGovernancePolicy(
        allow_rules={("test.echo", "resource-1")},
    ),
)

store = FileCanonicalStore("canonical_state.json")
store.save(state)
loaded = store.load()
assert loaded == state
```

## Port provenance

This package was recovered from
`T:\08-Archive\Project-AI-Canonical\project_ai\canonical\{state,store}.py`
(dated 2026-06-17) during the Phase B-3 recovery. The
original files were 53 + 41 = 94 lines; the port preserves
both 1:1 because they are the canonical implementation
referenced by docs/SOURCE_BOUNDARY.md as the first-pass
rebuild source.

The only changes from the source:
  - Module path: `project_ai.canonical.{state,store}` →
    `canonical.{state,store}` (workspace-member-name)
  - Imports rewritten: `from project_ai.X` → `from X`
    (X = capability, governance, identity — all canonical
    workspace members)
  - PEP 561 marker (`py.typed`) added for downstream typing
  - `packages/canonical/src` and `packages/canonical/tests`
    added to `pyproject.toml [tool.mypy] exclude` (same
    pattern as the J2 scenario engine ports and the
    Phase B-1/B-2 packages)

The `from_record` flow uses canonical's existing
`CapabilityToken` (the tokens module was the same in the
archive; canonical's `packages/capability/src/capability/tokens.py`
preserves the same API).

## See also

- `packages/audit/` — hash-chained audit log (Phase B-1)
- `packages/identity/` — actor identity registry (Phase B-2)
- `packages/capability/` — capability tokens (canonical)
- `packages/governance/` — higher-level governance
  primitives (canonical)
- Future work: a `governed_action` module that wires
  identity → capability → policy → audit → execute into a
  single `submit_action()` primitive (the archive's
  `governance.kernel` is the design reference)
