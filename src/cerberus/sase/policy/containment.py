"""
SASE - Sovereign Adversarial Signal Engine
L8: Containment Orchestration Layer

Orchestrates execution of containment actions with integrity validation.

WORKFLOW:
1. Validate model reproducibility (version registry, SHA-256 hash)
2. Verify scoring integrity (confidence assessment match)
3. Verify actions against allowed PolicyAction set
4. Apply containment action (via L7 AdaptivePolicyEngine)
5. Log action metadata and hash
6. Append Merkle proof with inclusion path
7. Notify governance with structured event

STATUS: PRODUCTION
"""

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("SASE.L8.Containment")


@dataclass
class ContainmentRequest:
    """Containment action request."""

    event_id: str
    source_ip: str
    confidence_score: float
    actions: list
    model_version: str
    requestor: str  # System component requesting containment

    def to_hash(self) -> str:
        """Generate deterministic SHA-256 hash of request."""
        data = f"{self.event_id}:{self.source_ip}:{self.confidence_score}:{self.model_version}"
        return hashlib.sha256(data.encode()).hexdigest()


# ── Model Registry ──────────────────────────────────────────────


@dataclass
class _ModelRegistryEntry:
    """Registry entry for a known model version."""

    version: str
    sha256_hash: str
    deprecated: bool = False
    min_compatible: str = ""
    max_compatible: str = ""


class _ModelRegistry:
    """Thread-safe model version registry.

    Tracks known model versions, their SHA-256 hashes, and compatibility
    constraints.  The registry is seeded with a default entry and can be
    extended at runtime via ``register``.
    """

    def __init__(self) -> None:
        self._entries: dict[str, _ModelRegistryEntry] = {}
        # Seed with default entry
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
        """Register a model version with its integrity hash."""
        self._entries[version] = _ModelRegistryEntry(
            version=version,
            sha256_hash=sha256_hash,
            min_compatible=min_compatible,
            max_compatible=max_compatible,
        )
        logger.info("Model version '%s' registered (hash=%s...)", version, sha256_hash[:16])

    def lookup(self, version: str) -> _ModelRegistryEntry | None:
        """Look up a model version in the registry."""
        return self._entries.get(version)

    def deprecate(self, version: str) -> bool:
        """Mark a version as deprecated."""
        entry = self._entries.get(version)
        if entry:
            entry.deprecated = True
            return True
        return False

    def list_versions(self) -> list[str]:
        """Return all registered version strings."""
        return list(self._entries.keys())


# Singleton registry instance
_MODEL_REGISTRY = _ModelRegistry()


# ── Allowed action types ─────────────────────────────────────────

# Canonical allowlist of action type strings accepted by SASE L8.
ALLOWED_ACTION_TYPES: frozenset[str] = frozenset(
    {
        "monitor",
        "alert",
        "rotate_credentials",
        "revoke_token",
        "tighten_waf",
        "throttle_rate",
        "soc_notification",
        "session_invalidation",
        "escalation_freeze",
    }
)


class ActionValidator:
    """Validates containment actions before execution.

    Validation pipeline:
    1. Model version known + not deprecated + hash check
    2. Confidence score matches assessment within tolerance
    3. All requested actions are in the allowed set
    """

    def __init__(self, model_registry: _ModelRegistry | None = None) -> None:
        self.registry = model_registry or _MODEL_REGISTRY
        self.validation_log: list[dict[str, Any]] = []

    def validate(
        self,
        request: ContainmentRequest,
        feature_vector: Any,
        confidence_assessment: dict,
    ) -> tuple[bool, str]:
        """Validate containment request.

        Returns:
            (valid, reason) tuple
        """
        logger.info("Validating containment request %s...", request.event_id)

        # 1. Validate model reproducibility
        model_valid, model_reason = self._validate_model(request)
        if not model_valid:
            self._record(request, False, f"model: {model_reason}")
            return False, f"Model validation failed: {model_reason}"

        # 2. Verify scoring integrity
        score_valid, score_reason = self._verify_scoring(
            request, feature_vector, confidence_assessment
        )
        if not score_valid:
            self._record(request, False, f"scoring: {score_reason}")
            return False, f"Scoring validation failed: {score_reason}"

        # 3. Verify actions are authorised
        actions_valid, actions_reason = self._verify_actions(request)
        if not actions_valid:
            self._record(request, False, f"actions: {actions_reason}")
            return False, f"Actions validation failed: {actions_reason}"

        self._record(request, True, "OK")
        logger.info("Containment request %s validated successfully", request.event_id)
        return True, "Validation passed"

    # ── Model validation ──────────────────────────────────────

    def _validate_model(self, request: ContainmentRequest) -> tuple[bool, str]:
        """Validate model version, deprecation status, and hash.

        Checks:
        1. Version must be registered in the model registry
        2. Version must not be deprecated
        3. If ``model_hash`` is present on the request, compare with registered hash
        """
        entry = self.registry.lookup(request.model_version)

        if entry is None:
            return False, f"Unknown model version: {request.model_version}"

        if entry.deprecated:
            return (
                False,
                f"Model version {request.model_version} is deprecated",
            )

        # Hash validation (if request carries a model hash field)
        model_hash = getattr(request, "model_hash", None)
        if model_hash and entry.sha256_hash != "default":
            if model_hash != entry.sha256_hash:
                return (
                    False,
                    f"Model hash mismatch: expected {entry.sha256_hash[:16]}..., "
                    f"got {model_hash[:16]}...",
                )

        return True, "Model valid"

    # ── Scoring verification ──────────────────────────────────

    def _verify_scoring(
        self,
        request: ContainmentRequest,
        feature_vector: Any,
        confidence_assessment: dict,
    ) -> tuple[bool, str]:
        """Verify scoring integrity (confidence match within tolerance)."""
        expected_conf = confidence_assessment.get("confidence_score", 0.0)
        actual_conf = request.confidence_score

        if abs(expected_conf - actual_conf) > 0.01:
            return False, f"Confidence mismatch: {expected_conf} vs {actual_conf}"

        return True, "Scoring verified"

    # ── Action authorisation ─────────────────────────────────

    def _verify_actions(self, request: ContainmentRequest) -> tuple[bool, str]:
        """Verify requested actions against the allowed action set.

        Accepts both ``PolicyAction`` enum instances (``action.value``)
        and plain strings.  Any action whose resolved value is not in
        ``ALLOWED_ACTION_TYPES`` is rejected.
        """
        for action in request.actions:
            # Resolve enum value or plain string
            action_value = getattr(action, "value", action) if not isinstance(action, str) else action

            if action_value not in ALLOWED_ACTION_TYPES:
                return False, f"Unauthorized action type: {action_value}"

        return True, "Actions authorized"

    # ── Internal recording ───────────────────────────────────

    def _record(self, request: ContainmentRequest, valid: bool, detail: str) -> None:
        self.validation_log.append(
            {
                "event_id": request.event_id,
                "valid": valid,
                "detail": detail,
                "timestamp": time.time(),
            }
        )


# ── Merkle Proof Generator ──────────────────────────────────────


class MerkleProofGenerator:
    """Generates Merkle proofs for containment actions.

    Builds a real Merkle tree from leaf hashes and returns inclusion
    proof paths.  Used by L9 evidence vault.
    """

    @staticmethod
    def _sha256(data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()

    def generate_proof(self, action_hash: str, event_hash: str) -> dict:
        """Generate Merkle proof linking action to event.

        Constructs a 4-leaf Merkle tree:
            leaf0 = action_hash
            leaf1 = event_hash
            leaf2 = H(action_hash || event_hash)
            leaf3 = H(timestamp)

        Returns proof structure with root and inclusion path for leaf0.
        """
        ts_hash = self._sha256(str(time.time()))
        leaf0 = action_hash
        leaf1 = event_hash
        leaf2 = self._sha256(action_hash + event_hash)
        leaf3 = ts_hash

        # Build tree bottom-up
        node_01 = self._sha256(leaf0 + leaf1)
        node_23 = self._sha256(leaf2 + leaf3)
        root = self._sha256(node_01 + node_23)

        # Inclusion path for leaf0: sibling leaf1, then sibling node_23
        proof = {
            "action_hash": action_hash,
            "event_hash": event_hash,
            "merkle_root": root,
            "inclusion_path": [
                {"sibling": leaf1, "position": "right"},
                {"sibling": node_23, "position": "right"},
            ],
            "leaf_index": 0,
            "tree_size": 4,
            "timestamp": time.time(),
        }

        logger.debug("Merkle proof generated: root=%s...", root[:16])
        return proof

    @staticmethod
    def verify_proof(proof: dict) -> bool:
        """Verify a Merkle inclusion proof.

        Re-computes the root from the leaf and the inclusion path
        and checks it matches the stored root.
        """
        current = proof["action_hash"]
        for step in proof["inclusion_path"]:
            if step["position"] == "right":
                combined = current + step["sibling"]
            else:
                combined = step["sibling"] + current
            current = hashlib.sha256(combined.encode()).hexdigest()

        return current == proof["merkle_root"]


# ── Containment Orchestrator ────────────────────────────────────


class ContainmentOrchestrator:
    """L8: Containment Orchestration Layer.

    Orchestrates validated, auditable containment actions.

    Pipeline:
        validate → enforce (L7) → log hash → Merkle proof → governance notify
    """

    def __init__(self, model_registry: _ModelRegistry | None = None) -> None:
        self.validator = ActionValidator(model_registry=model_registry)
        self.proof_generator = MerkleProofGenerator()
        self.containment_log: list[dict[str, Any]] = []
        self.governance_notifications: list[dict[str, Any]] = []

        logger.info("L8 Containment Orchestrator initialized")

    def orchestrate(
        self,
        request: ContainmentRequest,
        feature_vector: Any,
        confidence_assessment: dict,
        event_hash: str,
    ) -> dict:
        """Orchestrate containment action execution.

        Pipeline:
        1. Validate model + scoring + actions
        2. Apply containment via L7 AdaptivePolicyEngine
        3. Log action hash
        4. Append Merkle proof
        5. Notify governance

        Returns:
            Orchestration result dict
        """
        logger.warning("ORCHESTRATING CONTAINMENT: %s", request.event_id)

        # 1. Validate
        valid, reason = self.validator.validate(
            request, feature_vector, confidence_assessment
        )

        if not valid:
            logger.error("Containment REJECTED: %s", reason)
            return {"success": False, "reason": reason, "stage": "validation"}

        # 2. Apply actions via L7
        from .adaptive_policy import AdaptivePolicyEngine

        policy_engine = AdaptivePolicyEngine()
        executions = policy_engine.enforce(confidence_assessment)

        # 3. Log action hash
        action_hash = self._log_action(request, executions)

        # 4. Generate Merkle proof
        proof = self.proof_generator.generate_proof(action_hash, event_hash)

        # 5. Notify governance
        self._notify_governance(request, executions, proof)

        # Record containment
        self.containment_log.append(
            {
                "event_id": request.event_id,
                "action_hash": action_hash,
                "proof_root": proof["merkle_root"],
                "actions_count": len(executions),
                "timestamp": time.time(),
            }
        )

        logger.warning("Containment COMPLETED: %d actions", len(executions))

        return {
            "success": True,
            "actions_executed": len(executions),
            "action_hash": action_hash,
            "merkle_proof": proof,
            "stage": "complete",
        }

    def _log_action(self, request: ContainmentRequest, executions: list) -> str:
        """Log containment action and return deterministic hash."""
        log_entry = {
            "request_hash": request.to_hash(),
            "event_id": request.event_id,
            "actions": [
                getattr(e, "action", {}).value
                if hasattr(getattr(e, "action", None), "value")
                else str(e)
                for e in executions
            ],
            "timestamp": time.time(),
        }

        # Deterministic hash via sorted JSON
        log_str = json.dumps(log_entry, sort_keys=True)
        action_hash = hashlib.sha256(log_str.encode()).hexdigest()

        logger.info("Action logged: %s...", action_hash[:16])
        return action_hash

    def _notify_governance(
        self,
        request: ContainmentRequest,
        executions: list,
        proof: dict,
    ) -> None:
        """Notify governance layer with structured containment event."""
        notification = {
            "event_type": "containment.completed",
            "event_id": request.event_id,
            "source_ip": request.source_ip,
            "requestor": request.requestor,
            "confidence_score": request.confidence_score,
            "model_version": request.model_version,
            "actions_executed": len(executions),
            "merkle_root": proof["merkle_root"],
            "timestamp": time.time(),
        }

        self.governance_notifications.append(notification)
        logger.info(
            "Governance notified: event=%s, actions=%d, root=%s...",
            request.event_id,
            len(executions),
            proof["merkle_root"][:16],
        )

    # ── Convenience ──────────────────────────────────────────

    def get_containment_log(self, limit: int = 100) -> list[dict[str, Any]]:
        """Return the most recent containment log entries."""
        return self.containment_log[-limit:]

    def get_governance_notifications(self, limit: int = 50) -> list[dict[str, Any]]:
        """Return the most recent governance notifications."""
        return self.governance_notifications[-limit:]


__all__ = [
    "ContainmentRequest",
    "ActionValidator",
    "MerkleProofGenerator",
    "ContainmentOrchestrator",
    "ALLOWED_ACTION_TYPES",
]
