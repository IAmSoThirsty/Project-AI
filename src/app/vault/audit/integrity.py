"""
Tamper-evident audit integrity verification via Merkle-root pinning.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path


class AuditIntegrityVerifier:
    """Pins a Merkle root and verifies it has not changed since pinning."""

    def __init__(self, audit_dir: str) -> None:
        self.audit_dir = Path(audit_dir)

    def pin_current_state(self, merkle_root: str) -> dict[str, object]:
        pin = {
            "merkle_root": merkle_root,
            "timestamp": time.time(),
            "audit_dir": str(self.audit_dir),
            "pin_hash": hashlib.sha256(merkle_root.encode()).hexdigest(),
        }
        return pin

    def verify_integrity_on_mount(
        self, pin: dict[str, object], current_merkle_root: str
    ) -> bool:
        expected_hash = hashlib.sha256(
            str(pin.get("merkle_root", "")).encode()
        ).hexdigest()
        current_hash = hashlib.sha256(current_merkle_root.encode()).hexdigest()
        return expected_hash == current_hash
