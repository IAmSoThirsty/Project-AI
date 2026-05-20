"""
AuditManager — unified interface for operational and sovereign-grade audit logging.

Two modes:
- Operational (default): lightweight in-memory event store, no cryptography.
- Sovereign: wraps SovereignAuditLog for Ed25519-signed, HMAC-protected,
  Merkle-anchored constitutional-grade logging.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .sovereign_audit_log import SovereignAuditLog


class _OperationalLog:
    """Minimal in-memory event store for non-sovereign operational mode."""

    def __init__(self) -> None:
        self._events: list[dict[str, Any]] = []

    def append(self, event_type: str, data: dict[str, Any]) -> None:
        self._events.append({"event_type": event_type, "data": data})

    @property
    def total_events(self) -> int:
        return len(self._events)

    def verify_integrity(self) -> tuple[bool, str]:
        return True, "Operational mode: integrity check passed"


class AuditManager:
    """
    Unified audit manager with operational and sovereign modes.

    Operational mode (sovereign_mode=False):
      - Lightweight in-memory store, no cryptographic overhead.
      - Suitable for development and non-critical deployments.

    Sovereign mode (sovereign_mode=True):
      - Delegates to SovereignAuditLog.
      - Ed25519 signatures, HMAC, Merkle anchoring, file persistence.
      - Required for constitutional-grade audit trails.
    """

    def __init__(
        self,
        data_dir: str | Path,
        sovereign_mode: bool = False,
        deterministic_mode: bool = False,
    ) -> None:
        self._data_dir = Path(data_dir)
        self.sovereign_mode = sovereign_mode

        if sovereign_mode:
            self.audit_log = SovereignAuditLog(
                data_dir=self._data_dir,
                deterministic_mode=deterministic_mode,
                enable_notarization=False,
                enable_external_anchoring=False,
            )
            self._op_log: _OperationalLog | None = None
        else:
            self.audit_log = None  # type: ignore[assignment]
            self._op_log = _OperationalLog()

    # ── logging ────────────────────────────────────────────────────────────────

    def log_system_event(
        self, event_type: str, data: dict[str, Any] | None = None
    ) -> bool:
        if self.sovereign_mode:
            return self.audit_log.log_event(event_type, data or {}, actor="system")
        self._op_log.append(event_type, data or {})
        return True

    def log_security_event(
        self,
        event_type: str,
        data: dict[str, Any] | None = None,
        severity: str = "info",
    ) -> bool:
        payload = dict(data or {})
        payload.setdefault("severity", severity)
        return self.log_system_event(event_type, payload)

    def log_governance_event(
        self, event_type: str, data: dict[str, Any] | None = None
    ) -> bool:
        return self.log_system_event(event_type, data)

    # ── sovereign-only ─────────────────────────────────────────────────────────

    def get_genesis_id(self) -> str | None:
        if self.sovereign_mode:
            return self.audit_log.genesis_keypair.genesis_id
        return None

    def generate_proof_bundle(self, event_id: str) -> dict[str, Any] | None:
        if self.sovereign_mode:
            return self.audit_log.generate_proof_bundle(event_id)
        return None

    def verify_proof_bundle(self, proof: dict[str, Any]) -> tuple[bool, str]:
        if self.sovereign_mode:
            return self.audit_log.verify_proof_bundle(proof)
        return False, "Proof bundles not available in operational mode"

    # ── shared ─────────────────────────────────────────────────────────────────

    def verify_integrity(self) -> tuple[bool, str]:
        if self.sovereign_mode:
            return self.audit_log.verify_integrity()
        return self._op_log.verify_integrity()

    def get_statistics(self) -> dict[str, Any]:
        if self.sovereign_mode:
            s = self.audit_log.get_statistics()
            return {
                "mode": "sovereign",
                "genesis_id": s["genesis_id"],
                "main_log": {
                    "event_count": s["event_count"],
                    "signature_count": s["signature_count"],
                },
            }
        return {
            "mode": "operational",
            "main_log": {
                "total_events": self._op_log.total_events,
            },
        }
