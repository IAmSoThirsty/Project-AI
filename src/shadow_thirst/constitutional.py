"""Shadow Thirst constitutional integration — commit/quarantine decisions."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class CommitDecision(Enum):
    COMMIT = "COMMIT"
    QUARANTINE = "QUARANTINE"
    ESCALATE = "ESCALATE"


@dataclass
class CommitResult:
    decision: CommitDecision
    audit_hash: str | None
    reason: str = ""


class ConstitutionalIntegration:
    def validate_and_commit(
        self,
        frame: Any,
        divergence_policy: str | None = None,
    ) -> CommitResult:
        if frame.divergence_detected and divergence_policy == "require_identical":
            return CommitResult(
                decision=CommitDecision.QUARANTINE,
                audit_hash=None,
                reason=(
                    f"Divergence of {frame.divergence_magnitude} detected with "
                    f"require_identical policy — execution quarantined"
                ),
            )

        payload = json.dumps(
            {
                "name": frame.name,
                "primary": str(frame.primary.return_value),
                "shadow": str(frame.shadow.return_value),
                "divergence": frame.divergence_detected,
            },
            sort_keys=True,
        ).encode("utf-8")
        audit_hash = hashlib.sha256(payload).hexdigest()

        return CommitResult(
            decision=CommitDecision.COMMIT,
            audit_hash=audit_hash,
            reason="Execution validated and committed to canonical ledger",
        )
