"""
Stage 5: Commit — Canonical State Mutation.

Applies the approved mutation to canonical state.  In Phase 1, canonical
state is an in-memory dictionary.  In Phase 4, this will delegate to the
real CommitCoordinator backed by the existing governance modules.

Preconditions checked:
    1. CerberusDecision.commit_policy.allowed == True
    2. Shadow hash available in prior stage metadata
    3. Canonical snapshot freshness (stub in Phase 1)

Rollback on any post-precondition failure.
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

from psia.waterfall.engine import StageDecision, StageResult, WaterfallStage

logger = logging.getLogger(__name__)


class InMemoryCanonicalStore:
    """Phase 1 in-memory canonical state store.

    In production, this would be a durable, transactional store with
    snapshot isolation, WAL, and replication.
    """

    def __init__(self) -> None:
        self._state: dict[str, Any] = {}
        self._version: int = 0

    def get(self, key: str) -> Any:
        """Read a value from canonical state."""
        return self._state.get(key)

    def put(self, key: str, value: Any) -> str:
        """Write a value to canonical state and return diff hash.

        Args:
            key: State key (resource URI)
            value: New value

        Returns:
            SHA-256 hash of the applied diff
        """
        old_value = self._state.get(key)
        self._state[key] = value
        self._version += 1

        diff = json.dumps(
            {"key": key, "old": old_value, "new": value, "version": self._version},
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(diff.encode()).hexdigest()

    def rollback(self, key: str, old_value: Any) -> None:
        """Rollback a specific key to its previous value."""
        if old_value is None:
            self._state.pop(key, None)
        else:
            self._state[key] = old_value
        self._version += 1

    @property
    def version(self) -> int:
        """Current state version."""
        return self._version

    @property
    def snapshot(self) -> dict[str, Any]:
        """Return a shallow copy of the current state."""
        return dict(self._state)


class CommitStage:
    """Stage 5: Canonical commit.

    Validates preconditions from the CerberusDecision. Then applies
    the mutation to the canonical store, computing a canonical_diff_hash.
    On failure, rollback is attempted.
    """

    def __init__(self, *, store: InMemoryCanonicalStore | None = None) -> None:
        self.store = store or InMemoryCanonicalStore()

    def evaluate(self, envelope, prior_results: list[StageResult]) -> StageResult:
        """Apply canonical mutation if preconditions are met.

        Args:
            envelope: RequestEnvelope (source of mutation parameters)
            prior_results: Results from prior stages (must include gate stage)

        Returns:
            StageResult with canonical_diff_hash in metadata
        """
        reasons: list[str] = []

        # ── Precondition 1: Find CerberusDecision in prior results ──
        cerberus_decision = None
        shadow_hash = ""
        for pr in prior_results:
            if "cerberus_decision" in pr.metadata:
                cerberus_decision = pr.metadata["cerberus_decision"]
            if "shadow_hash" in pr.metadata:
                shadow_hash = pr.metadata["shadow_hash"]

        if cerberus_decision is None:
            reasons.append("no CerberusDecision found in prior stages")
            return StageResult(
                stage=WaterfallStage.COMMIT,
                decision=StageDecision.DENY,
                reasons=reasons,
            )

        # ── Precondition 2: Commit allowed ──
        if not cerberus_decision.commit_policy.allowed:
            reasons.append("CerberusDecision.commit_policy.allowed == false")
            return StageResult(
                stage=WaterfallStage.COMMIT,
                decision=StageDecision.DENY,
                reasons=reasons,
            )

        # ── Apply mutation ──
        resource = envelope.intent.resource
        parameters = envelope.intent.parameters
        old_value = self.store.get(resource)

        try:
            new_value = parameters.get("value", parameters)
            diff_hash = self.store.put(resource, new_value)
        except Exception as exc:
            # Rollback
            self.store.rollback(resource, old_value)
            reasons.append(f"commit failed, rolled back: {exc}")
            return StageResult(
                stage=WaterfallStage.COMMIT,
                decision=StageDecision.DENY,
                reasons=reasons,
                metadata={"rolled_back": True},
            )

        reasons.append(f"committed resource={resource} version={self.store.version}")

        return StageResult(
            stage=WaterfallStage.COMMIT,
            decision=StageDecision.ALLOW,
            reasons=reasons,
            metadata={
                "canonical_diff_hash": diff_hash,
                "shadow_hash": shadow_hash,
                "version": self.store.version,
            },
        )


__all__ = ["InMemoryCanonicalStore", "CommitStage"]
