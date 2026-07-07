# Identity Registry

Minimal actor identity registry for Project-AI's
execution-governance spine.

## What this is

A keyed registry of actor identities with a `verify()` call
that returns an `IdentityVerification` (allowed bool + reason
+ optional record).

The identity model is intentionally minimal:

  - `IdentityRecord` — frozen dataclass with `actor_id` (str)
    and `active` (bool, default True)
  - `IdentityRegistry` — `add(record)`, `records()`,
    `verify(actor_id)`
  - `IdentityVerification` — `allowed`, `reason`,
    optional `record`

There is no concept of credentials, roles, or permissions
here. Those live in:

  - `packages/capability/` — capability tokens (canonical,
    already in the repo)
  - `packages/governance/` — policy engine (canonical)
  - `packages/audit/` — hash-chained audit log (Phase B-1)

The identity registry is the FIRST of the three checks in
the `submit_action` governance kernel: identity → capability
→ policy → audit → execute.

## Run it

```python
from identity import IdentityRecord, IdentityRegistry

registry = IdentityRegistry([
    IdentityRecord("actor-1", active=True),
    IdentityRecord("actor-2", active=False),
])

result = registry.verify("actor-1")
assert result.allowed is True
assert result.reason == "identity active"

result = registry.verify("actor-2")
assert result.allowed is False
assert result.reason == "identity inactive"

result = registry.verify("unknown")
assert result.allowed is False
assert result.reason == "identity not found"
```

## Port provenance

This package was recovered from
`T:\08-Archive\Project-AI-Canonical\project_ai\identity\records.py`
(dated 2026-06-17) during the Phase B recovery. The
original file was 60 lines; the port preserves it 1:1
because it is the canonical implementation referenced by
`docs/SOURCE_BOUNDARY.md` as the first-pass rebuild source.

The only changes from the source:
  - Module path: `project_ai.identity.records` →
    `identity.records` (workspace-member-name)
  - Imports rewritten: `from project_ai.*` → `from identity.*`
    (intra-package only; identity has no external
    non-stdlib dependencies)
  - PEP 561 marker (`py.typed`) added for downstream typing
  - `packages/identity/src` and `packages/identity/tests`
    added to `pyproject.toml [tool.mypy] exclude` (same
    pattern as the J2 scenario engine ports)

## See also

- `packages/audit/` — hash-chained audit log (Phase B-1)
- `packages/canonical/` — canonical state that composes
  identity, capability, and policy (Phase B-3)
- `packages/capability/` — capability tokens
- `packages/governance/` — higher-level governance
  primitives
