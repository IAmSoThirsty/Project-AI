# T6: Naming-collision audit for `tarl` (SKIPPED)

## Status: SHIPPED AS DOCUMENTED NON-COLLISION. No rename required.

## TL;DR

`packages/tarl/` (Beginnings' **Threat-Adaptive Rule Language**)
and Thirsty-Lang's `tarl` tier (5th tier, installed as `utf.tarl`)
**coexist without any Python import collision**. T6 is shipped as
a documented finding + a side-by-side import test that proves
the isolation. The rename plan from the discovery document was
**explicitly not executed** because the problem it solves does
not exist.

## What the discovery said

`docs/internal/PHASE_T_DISCOVERY.md` described T6 as:

  > T6: Rename `packages/tarl/` to avoid Python import collision
  > with the language's `tarl` tier.

This was authored before the integration began, as a defensive
hypothesis: "if Thirsty-Lang's `tarl` tier is imported as a top-
level `tarl` module, it will shadow Beginnings' TARL." The
hypothesis was wrong, and the reason is the language's packaging.

## Why there is no collision

The Thirsty-Lang 0.8.1 PyPI wheel ships its sub-modules under
the `utf` namespace:

  - `utf.tarl`     (5th tier)
  - `utf.tscg`     (3rd tier)
  - `utf.tscg_b`   (4th tier)
  - `utf.thirst`   (1st tier)
  - `utf.thirsty`  (base, tier 0)
  - `utf.shadow_thirst` (6th tier)

Beginnings' `packages/tarl/src/tarl/` is a top-level Python
module named `tarl`. The two namespaces are distinct:

  - `import tarl`        -> Beginnings' Threat-Adaptive Rule Language
  - `import utf.tarl`    -> Thirsty-Lang's 5th tier (TARL spec language)

Side-by-side imports work without any rename, shadowing, or
ordering tricks. This is verified by the integration test
`tests/test_t6_namespace_isolation.py`.

## Discovery verification

A live import check confirms the isolation:

```python
$ uv run python -c "
import tarl
import utf.tarl
import utf.tarl.core
print('Beginnings tarl:', tarl.__name__)
print('Thirsty tarl:', utf.tarl.__name__)
print('PolicyParser:', utf.tarl.core.PolicyParser)
"
Beginnings tarl: tarl
Thirsty tarl: utf.tarl
PolicyParser: <class 'utf.tarl.core.PolicyParser'>
```

The two `tarl` namespaces are siblings, not parent/child. The
dotted namespace `utf.tarl` is the language's tier 5; the bare
`tarl` is Beginnings' own language. They are different projects
that happen to share a 4-letter name.

## How to access each

  - **Beginnings' TARL (Threat-Adaptive Rule Language)**:
    `import tarl`, `from tarl import Compiler, Policy, TarlConfig`
    (See `packages/tarl/README.md` and `docs/internal/PHASE_H_DISCOVERY.md`.)

  - **Thirsty-Lang's TARL (5th tier spec language)**:
    `import utf.tarl`, `from utf.tarl.core import PolicyParser`,
    `from utf.tarl.runtime import TarlRuntime`. (See
    `docs/internal/PHASE_T_DISCOVERY.md` and the bridge module
    `packages/governance/src/governance/tarl_bridge.py`.)

## Rationale for skipping the rename

1. **No actual problem.** The integration test confirms both
   imports succeed simultaneously.
2. **The rename would break existing public surface.** `tarl.Compiler`,
   `tarl.Policy`, `tarl.TarlConfig` are public API; renaming the
   package would force a deprecation cycle on every consumer.
3. **The Phase T2 bridge is already unambiguous.** The bridge
   `packages/governance/src/governance/tarl_bridge.py` uses
   `utf.tarl.runtime.TarlRuntime` and `utf.tarl.core.PolicyParser`
   to access the language. The two namespaces are not
   confusable from the bridge's point of view.
4. **Both languages are pre-existing.** Beginnings' TARL is the
   project's own language (a "Threat-Adaptive Rule Language"
   per the `packages/tarl/README.md`). Thirsty-Lang's TARL is
   its own language (a tier-5 spec language). The names are
   coincidental, not contested. Both projects exist independently
   of each other.

## What ships in T6

1. **`docs/internal/T6_NAMING.md`** (this file)
2. **`tests/test_t6_namespace_isolation.py`** — proves the
   side-by-side import works
3. **MODIFIED `packages/tarl/pyproject.toml`** — adds
   `thirsty-lang==0.8.1` as a dep so the side-by-side test
   can import `utf.tarl` in the same process

## What is NOT shipped in T6

1. **No rename of `packages/tarl/`.** The bare `tarl` Python
   module remains Beginnings' Threat-Adaptive Rule Language.
2. **No deprecation cycle.** The public API of `import tarl`
   is unchanged.
3. **No code review of `packages/tarl/` for naming clashes.**
   The Beginnings TARL is a separate language and is not
   expected to be renamed to disambiguate from Thirsty-Lang's
   tier 5.
