"""
Containment Orchestration Layer (L8) — SASE policy enforcement.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

ALLOWED_ACTION_TYPES: frozenset[str] = frozenset({
    "monitor",
    "alert",
    "block",
    "quarantine",
    "isolate",
    "redirect",
    "throttle",
    "log",
    "notify",
})

_KNOWN_MODEL_VERSIONS = {"1.0.0", "1.1.0", "2.0.0"}
_CONFIDENCE_TOLERANCE = 0.05


@dataclass
class ContainmentRequest:
    event_id: str
    source_ip: str
    confidence_score: float
    actions: list
    model_version: str
    requestor: str

    def to_hash(self) -> str:
        canonical = json.dumps(
            {
                "event_id": self.event_id,
                "source_ip": self.source_ip,
                "confidence_score": self.confidence_score,
                "actions": [
                    a.value if hasattr(a, "value") else a for a in self.actions
                ],
                "model_version": self.model_version,
                "requestor": self.requestor,
            },
            sort_keys=True,
        )
        return hashlib.sha256(canonical.encode()).hexdigest()


class ActionValidator:
    def __init__(self) -> None:
        self.validation_log: list[dict] = []

    def validate(
        self,
        request: ContainmentRequest,
        context: dict,
        model_metadata: dict,
    ) -> tuple[bool, str]:
        if request.model_version not in _KNOWN_MODEL_VERSIONS:
            result = (False, f"Unknown model version: {request.model_version}")
            self._log(request, False)
            return result

        expected_confidence = model_metadata.get("confidence_score", 0.0)
        if abs(request.confidence_score - expected_confidence) > _CONFIDENCE_TOLERANCE:
            result = (False, "Confidence score mismatch")
            self._log(request, False)
            return result

        for action in request.actions:
            action_str = action.value if hasattr(action, "value") else action
            if action_str not in ALLOWED_ACTION_TYPES:
                result = (False, f"Unauthorized action: {action_str}")
                self._log(request, False)
                return result

        self._log(request, True)
        return (True, "OK")

    def _log(self, request: ContainmentRequest, valid: bool) -> None:
        self.validation_log.append(
            {"event_id": request.event_id, "valid": valid}
        )


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


class MerkleProofGenerator:
    def generate_proof(self, action_input: str, policy_input: str) -> dict:
        node1 = _sha(action_input)
        node2 = _sha(policy_input)
        root = _sha(node1 + node2)
        return {
            "action_hash": action_input,
            "policy_hash": policy_input,
            "inclusion_path": [node1, node2],
            "merkle_root": root,
        }

    def verify_proof(self, proof: dict) -> bool:
        try:
            expected_node1 = _sha(proof["action_hash"])
            if expected_node1 != proof["inclusion_path"][0]:
                return False
            expected_root = _sha(proof["inclusion_path"][0] + proof["inclusion_path"][1])
            return expected_root == proof["merkle_root"]
        except (KeyError, IndexError, TypeError):
            return False


class ContainmentOrchestrator:
    def __init__(self) -> None:
        self._validator = ActionValidator()
        self._proof_gen = MerkleProofGenerator()
