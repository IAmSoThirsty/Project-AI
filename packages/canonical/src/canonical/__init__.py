"""Project-AI Canonical State (Phase B-3 recovery from Project-AI-Canonical).

This package was missing from canonical Project-AI-Beginnings
before this commit. It was recovered from the
``T:\\08-Archive\\Project-AI-Canonical\\`` archive
(the first-pass rebuild source per docs/SOURCE_BOUNDARY.md).

Public surface:
  - CanonicalState        — composes identities + capabilities
                            + policy into a single snapshot
  - FileCanonicalStore    — JSON file persistence with atomic
                            write (tmp + replace)
  - CanonicalStoreError   — raised on persistence / decode
                            failures

The canonical state is the **persistence layer** of the
execution-governance spine. The audit log (Phase B-1) and
identity registry (Phase B-2) are the per-event and
per-actor layers; canonical state composes them into a
single restorable snapshot.

Dependencies:
  - identity (Phase B-2)    — IdentityRecord, IdentityRegistry
  - canonical._internal     — vendored CapabilityRegistry,
                              CapabilityToken (from the
                              archive's project_ai.capability.
                              tokens), and vendored
                              StaticGovernancePolicy (from
                              the archive's project_ai.
                              governance.policy)

The canonical `capability` and `governance` packages in
this workspace have evolved past the archive's interface
(CapabilityAuthority, GovernanceEngine, etc.). The archive's
`CanonicalState` depends on the older CapabilityRegistry /
CapabilityToken / StaticGovernancePolicy types which are
no longer exposed in canonical's public surface, so they
are vendored here as ``canonical._internal``.

If/when the canonical capability and governance packages
are aligned to re-expose the legacy types, the vendored
copies can be removed. Until then, this vendoring is the
honest way to keep ``CanonicalState`` self-contained and
runnable without touching canonical's later primitives.
"""

from __future__ import annotations

from canonical.state import CanonicalState
from canonical.store import CanonicalStoreError, FileCanonicalStore

__version__ = "0.0.0.dev0"

__all__ = [
    "CanonicalState",
    "CanonicalStoreError",
    "FileCanonicalStore",
]
