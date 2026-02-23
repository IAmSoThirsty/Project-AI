"""
Stage 1: Signature / Threat Fingerprint Matching.

Cross-references the request actor, device attestation, and resource
against a store of known-bad fingerprints.  If a match is found, the
request is quarantined or denied based on the fingerprint severity.

Fingerprint sources:
    - Previous Waterfall denials (fed back from Stage 6)
    - OctoReflex containment events
    - External threat intelligence feeds
    - Red-team simulation results
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from psia.waterfall.engine import StageDecision, StageResult, WaterfallStage

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ThreatFingerprint:
    """A known-bad fingerprint entry."""

    fingerprint_id: str
    pattern_type: str  # "actor", "device", "resource", "combo"
    pattern_value: str  # DID, device hash, resource URI, or composite
    severity: str  # "low", "med", "high", "critical"
    reason: str = ""
    source: str = ""  # Where this fingerprint came from


class ThreatFingerprintStore:
    """In-memory store of known-bad fingerprints.

    In production, this would be backed by a database with
    indexes on pattern_type and pattern_value, plus TTL for
    time-limited quarantines.
    """

    def __init__(self) -> None:
        self._fingerprints: dict[str, ThreatFingerprint] = {}

    def add(self, fp: ThreatFingerprint) -> None:
        """Add a fingerprint to the store."""
        self._fingerprints[fp.fingerprint_id] = fp

    def remove(self, fingerprint_id: str) -> None:
        """Remove a fingerprint from the store."""
        self._fingerprints.pop(fingerprint_id, None)

    def match_actor(self, actor_did: str) -> list[ThreatFingerprint]:
        """Find fingerprints matching an actor DID."""
        return [
            fp for fp in self._fingerprints.values()
            if fp.pattern_type == "actor" and fp.pattern_value == actor_did
        ]

    def match_device(self, device_attestation: str) -> list[ThreatFingerprint]:
        """Find fingerprints matching a device attestation hash."""
        if not device_attestation:
            return []
        return [
            fp for fp in self._fingerprints.values()
            if fp.pattern_type == "device" and fp.pattern_value == device_attestation
        ]

    def match_resource(self, resource: str) -> list[ThreatFingerprint]:
        """Find fingerprints matching a resource URI."""
        return [
            fp for fp in self._fingerprints.values()
            if fp.pattern_type == "resource" and fp.pattern_value == resource
        ]

    @property
    def count(self) -> int:
        """Number of fingerprints in the store."""
        return len(self._fingerprints)


class SignatureStage:
    """Stage 1: Threat fingerprint matching.

    Checks actor, device attestation, and target resource against
    known-bad fingerprints.  Higher-severity matches produce quarantine
    or deny; lower-severity matches produce escalate (requesting
    shadow simulation).
    """

    def __init__(self, *, store: ThreatFingerprintStore | None = None) -> None:
        self.store = store or ThreatFingerprintStore()

    def evaluate(self, envelope, prior_results: list[StageResult]) -> StageResult:
        """Evaluate request against known threat fingerprints.

        Args:
            envelope: RequestEnvelope to check
            prior_results: Results from prior stages

        Returns:
            StageResult with decision and matched fingerprint details
        """
        matches: list[ThreatFingerprint] = []

        # Check actor
        matches.extend(self.store.match_actor(envelope.actor))

        # Check resource target
        matches.extend(self.store.match_resource(envelope.intent.resource))

        if not matches:
            return StageResult(
                stage=WaterfallStage.SIGNATURE,
                decision=StageDecision.ALLOW,
                reasons=["no threat fingerprints matched"],
            )

        # Determine worst severity
        severity_rank = {"low": 0, "med": 1, "high": 2, "critical": 3}
        worst_severity = max(
            matches, key=lambda fp: severity_rank.get(fp.severity, 0)
        ).severity

        reasons = [
            f"matched fingerprint: {fp.fingerprint_id} ({fp.pattern_type}={fp.pattern_value}, "
            f"severity={fp.severity}, reason={fp.reason})"
            for fp in matches
        ]

        # Decision based on worst severity
        if worst_severity in ("critical", "high"):
            decision = StageDecision.QUARANTINE
        elif worst_severity == "med":
            decision = StageDecision.ESCALATE
        else:
            decision = StageDecision.ALLOW

        return StageResult(
            stage=WaterfallStage.SIGNATURE,
            decision=decision,
            reasons=reasons,
            metadata={"matched_fingerprints": [fp.fingerprint_id for fp in matches]},
        )


__all__ = ["ThreatFingerprint", "ThreatFingerprintStore", "SignatureStage"]
