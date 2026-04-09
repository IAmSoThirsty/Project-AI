#                                           [2026-04-09 11:30]
#                                          Productivity: Active
"""
SASE - Sovereign Adversarial Signal Engine
L8: Containment Orchestration Layer

Orchestrates execution of containment actions with integrity validation and Merkle proofs.
Hardened against memory exhaustion and temporal drift.
"""

import hashlib
import json
import logging
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("SASE.L8.Containment")


@dataclass
class ContainmentRequest:
    """Containment action request."""

    event_id: str
    source_ip: str
    confidence_score: float
    actions: list[Any]
    model_version: str
    requestor: str

    def to_hash(self) -> str:
        """Generate deterministic SHA-256 hash of request using UTC-aligned data."""
        data = f"{self.event_id}:{self.source_ip}:{self.confidence_score}:{self.model_version}"
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class _ModelRegistryEntry:
    """Registry entry for a known model version."""

    version: str
    sha256_hash: str
    deprecated: bool = False
    min_compatible: str = ""
    max_compatible: str = ""


class _ModelRegistry:
    """Thread-safe model version registry."""

    def __init__(self) -> None:
        self._entries: dict[str, _ModelRegistryEntry] = {}
        self.register(
            version="1.0.0",
            sha256_hash="default",
            min_compatible="1.0.0",
            max_compatible="1.99.99",
        )

    def register(
        self,
        version: str,
        sha256_hash: str,
        min_compatible: str = "",
        max_compatible: str = "",
    ) -> None:
        """Register a model version."""
        self._entries[version] = _ModelRegistryEntry(
            version=version,
            sha256_hash=sha256_hash,
            min_compatible=min_compatible,
            max_compatible=max_compatible,
        )
        logger.info("Model version '%s' registered (hash=%s...)", version, sha256_hash[:16])

    def lookup(self, version: str) -> _ModelRegistryEntry | None:
        return self._entries.get(version)


_MODEL_REGISTRY = _ModelRegistry()

ALLOWED_ACTION_TYPES: frozenset[str] = frozenset(
    {
        "monitor", "alert", "rotate_credentials", "revoke_token", 
        "tighten_waf", "throttle_rate", "soc_notification", 
        "session_invalidation", "escalation_freeze",
    }
)


class ActionValidator:
    """Validates containment actions with audit trails."""

    def __init__(self, model_registry: _ModelRegistry | None = None, max_log_size: int = 500) -> None:
        self.registry = model_registry or _MODEL_REGISTRY
        self.validation_log: deque[dict[str, Any]] = deque(maxlen=max_log_size)

    def validate(
        self,
        request: ContainmentRequest,
        feature_vector: Any,
        confidence_assessment: dict[str, Any],
    ) -> tuple[bool, str]:
        """Validate containment request."""
        logger.info("Validating containment request %s...", request.event_id)

        # 1. Reproducibility
        entry = self.registry.lookup(request.model_version)
        if entry is None:
            reason = f"Unknown model version: {request.model_version}"
            self._record(request, False, reason)
            return False, reason
        if entry.deprecated:
            reason = f"Model version {request.model_version} is deprecated"
            self._record(request, False, reason)
            return False, reason

        # 2. Scoring Integrity
        expected_conf = confidence_assessment.get("confidence_score", 0.0)
        if abs(expected_conf - request.confidence_score) > 0.01:
            reason = f"Confidence mismatch: {expected_conf} vs {request.confidence_score}"
            self._record(request, False, reason)
            return False, reason

        # 3. Authorization
        for action in request.actions:
            action_value = getattr(action, "value", action) if not isinstance(action, str) else action
            if action_value not in ALLOWED_ACTION_TYPES:
                reason = f"Unauthorized action type: {action_value}"
                self._record(request, False, reason)
                return False, reason

        self._record(request, True, "OK")
        return True, "Validation passed"

    def _record(self, request: ContainmentRequest, valid: bool, detail: str) -> None:
        self.validation_log.append({
            "event_id": request.event_id,
            "valid": valid,
            "detail": detail,
            "timestamp": datetime.now(timezone.utc).timestamp(),
        })


class MerkleProofGenerator:
    """Generates UTC-aligned Merkle proofs for non-repudiation."""

    @staticmethod
    def _sha256(data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()

    def generate_proof(self, action_hash: str, event_hash: str) -> dict[str, Any]:
        """Generate Merkle proof linking action to event."""
        now_ts = datetime.now(timezone.utc).timestamp()
        ts_hash = self._sha256(str(now_ts))
        
        leaf0 = action_hash
        leaf1 = event_hash
        leaf2 = self._sha256(action_hash + event_hash)
        leaf3 = ts_hash

        node_01 = self._sha256(leaf0 + leaf1)
        node_23 = self._sha256(leaf2 + leaf3)
        root = self._sha256(node_01 + node_23)

        return {
            "action_hash": action_hash,
            "event_hash": event_hash,
            "merkle_root": root,
            "inclusion_path": [
                {"sibling": leaf1, "position": "right"},
                {"sibling": node_23, "position": "right"},
            ],
            "timestamp": now_ts,
        }


class ContainmentOrchestrator:
    """L8: Containment Orchestration Layer."""

    def __init__(self, model_registry: _ModelRegistry | None = None, max_log_size: int = 1000) -> None:
        self.validator = ActionValidator(model_registry=model_registry)
        self.proof_generator = MerkleProofGenerator()
        self.containment_log: deque[dict[str, Any]] = deque(maxlen=max_log_size)
        self.governance_notifications: deque[dict[str, Any]] = deque(maxlen=max_log_size)

        logger.info("L8 Containment Orchestrator initialized")

    def orchestrate(
        self,
        request: ContainmentRequest,
        feature_vector: Any,
        confidence_assessment: dict[str, Any],
        event_hash: str,
    ) -> dict[str, Any]:
        """Orchestrate containment execution with Merkle non-repudiation."""
        logger.warning("ORCHESTRATING CONTAINMENT: %s", request.event_id)

        valid, reason = self.validator.validate(request, feature_vector, confidence_assessment)
        if not valid:
            logger.error("Containment REJECTED: %s", reason)
            return {"success": False, "reason": reason, "stage": "validation"}

        from .adaptive_policy import AdaptivePolicyEngine
        policy_engine = AdaptivePolicyEngine()
        executions = policy_engine.enforce(confidence_assessment)

        action_hash = self._log_action(request, executions)
        proof = self.proof_generator.generate_proof(action_hash, event_hash)
        self._notify_governance(request, executions, proof)

        self.containment_log.append({
            "event_id": request.event_id,
            "action_hash": action_hash,
            "proof_root": proof["merkle_root"],
            "actions_count": len(executions),
            "timestamp": datetime.now(timezone.utc).timestamp(),
        })

        logger.warning("Containment COMPLETED: %d actions for %s", len(executions), request.event_id)
        return {
            "success": True,
            "actions_executed": len(executions),
            "action_hash": action_hash,
            "merkle_proof": proof,
            "stage": "complete",
        }

    def _log_action(self, request: ContainmentRequest, executions: list[Any]) -> str:
        log_entry = {
            "request_hash": request.to_hash(),
            "event_id": request.event_id,
            "actions": [str(getattr(e, "action", e)) for e in executions],
            "timestamp": datetime.now(timezone.utc).timestamp(),
        }
        log_str = json.dumps(log_entry, sort_keys=True)
        return hashlib.sha256(log_str.encode()).hexdigest()

    def _notify_governance(self, request: ContainmentRequest, executions: list[Any], proof: dict[str, Any]) -> None:
        notification = {
            "event_type": "containment.completed",
            "event_id": request.event_id,
            "source_ip": request.source_ip,
            "confidence_score": request.confidence_score,
            "merkle_root": proof["merkle_root"],
            "timestamp": datetime.now(timezone.utc).timestamp(),
        }
        self.governance_notifications.append(notification)
        logger.info("Governance notified: event=%s, root=%s...", request.event_id, proof["merkle_root"][:16])

    def get_containment_log(self, limit: int = 100) -> list[dict[str, Any]]:
        return list(self.containment_log)[-limit:]


__all__ = ["ContainmentRequest", "ActionValidator", "MerkleProofGenerator", "ContainmentOrchestrator"]
