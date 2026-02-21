"""
SASE - Sovereign Adversarial Signal Engine
L8: Containment Orchestration Layer

Orchestrates execution of containment actions with integrity validation.

WORKFLOW:
1. Validate model reproducibility
2. Verify scoring integrity
3. Apply containment action
4. Log action metadata
5. Append Merkle proof
6. Notify governance
"""

import hashlib
import logging
import time
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger("SASE.L8.Containment")


@dataclass
class ContainmentRequest:
    """Containment action request"""

    event_id: str
    source_ip: str
    confidence_score: float
    actions: list
    model_version: str
    requestor: str  # System component requesting containment

    def to_hash(self) -> str:
        """Generate deterministic hash of request"""
        data = f"{self.event_id}:{self.source_ip}:{self.confidence_score}:{self.model_version}"
        return hashlib.sha256(data.encode()).hexdigest()


class ActionValidator:
    """
    Validates containment actions before execution

    Ensures model reproducibility and scoring integrity
    """

    def __init__(self):
        self.validation_log = []

    def validate(
        self,
        request: ContainmentRequest,
        feature_vector: Any,
        confidence_assessment: dict,
    ) -> tuple[bool, str]:
        """
        Validate containment request

        Returns (valid, reason)
        """
        logger.info("Validating containment request...")

        # 1. Validate model reproducibility
        model_valid, model_reason = self._validate_model(request)
        if not model_valid:
            return False, f"Model validation failed: {model_reason}"

        # 2. Verify scoring integrity
        score_valid, score_reason = self._verify_scoring(request, feature_vector, confidence_assessment)
        if not score_valid:
            return False, f"Scoring validation failed: {score_reason}"

        # 3. Verify actions are authorized
        actions_valid, actions_reason = self._verify_actions(request)
        if not actions_valid:
            return False, f"Actions validation failed: {actions_reason}"

        logger.info("Containment request validated successfully")
        return True, "Validation passed"

    def _validate_model(self, request: ContainmentRequest) -> tuple[bool, str]:
        """Validate model version and reproducibility"""
        # Check model version is known
        expected_version = "1.0.0"  # TODO: Dynamic version management

        if request.model_version != expected_version:
            return False, f"Unknown model version: {request.model_version}"

        # TODO: Validate model hash/signature for reproducibility

        return True, "Model valid"

    def _verify_scoring(
        self,
        request: ContainmentRequest,
        feature_vector: Any,
        confidence_assessment: dict,
    ) -> tuple[bool, str]:
        """Verify scoring integrity"""
        # Check confidence matches assessment
        expected_conf = confidence_assessment.get("confidence_score", 0.0)
        actual_conf = request.confidence_score

        # Allow small floating point tolerance
        if abs(expected_conf - actual_conf) > 0.01:
            return False, f"Confidence mismatch: {expected_conf} vs {actual_conf}"

        return True, "Scoring verified"

    def _verify_actions(self, request: ContainmentRequest) -> tuple[bool, str]:
        """Verify requested actions are authorized"""
        from .adaptive_policy import PolicyAction

        # All SASE policy actions are authorized
        for action in request.actions:
            if not isinstance(action, PolicyAction):
                return False, f"Unauthorized action type: {type(action)}"

        return True, "Actions authorized"


class MerkleProofGenerator:
    """
    Generates Merkle proofs for containment actions

    Used by L9 evidence vault
    """

    def generate_proof(self, action_hash: str, event_hash: str) -> dict:
        """
        Generate Merkle proof linking action to event

        Returns proof structure for verification
        """
        # Combine hashes
        combined = hashlib.sha256((action_hash + event_hash).encode()).hexdigest()

        proof = {
            "action_hash": action_hash,
            "event_hash": event_hash,
            "merkle_root": combined,  # Simplified; real impl uses tree
            "timestamp": time.time(),
        }

        logger.debug(f"Merkle proof generated: {proof['merkle_root'][:16]}")

        return proof


class ContainmentOrchestrator:
    """
    L8: Containment Orchestration Layer

    Orchestrates validated, auditable containment actions
    """

    def __init__(self):
        self.validator = ActionValidator()
        self.proof_generator = MerkleProofGenerator()
        self.containment_log: list[dict] = []

        logger.info("L8 Containment Orchestrator initialized")

    def orchestrate(
        self,
        request: ContainmentRequest,
        feature_vector: Any,
        confidence_assessment: dict,
        event_hash: str,
    ) -> dict:
        """
        Orchestrate containment action execution

        PIPELINE:
        1. Validate model reproducibility
        2. Verify scoring integrity
        3. Apply containment action (via L7)
        4. Log action hash
        5. Append Merkle proof
        6. Notify governance

        Returns orchestration result
        """
        logger.warning(f"ORCHESTRATING CONTAINMENT: {request.event_id}")

        # 1. Validate
        valid, reason = self.validator.validate(request, feature_vector, confidence_assessment)

        if not valid:
            logger.error(f"Containment REJECTED: {reason}")
            return {"success": False, "reason": reason, "stage": "validation"}

        # 2. Verify scoring integrity (already done in validation)

        # 3. Apply actions (delegate to L7)
        from .adaptive_policy import AdaptivePolicyEngine

        policy_engine = AdaptivePolicyEngine()
        executions = policy_engine.enforce(confidence_assessment)

        # 4. Log action hash
        action_hash = self._log_action(request, executions)

        # 5. Generate Merkle proof
        proof = self.proof_generator.generate_proof(action_hash, event_hash)

        # 6. Notify governance (TODO: integrate with L10)
        self._notify_governance(request, executions, proof)

        # Record containment
        self.containment_log.append(
            {
                "request": request,
                "executions": executions,
                "proof": proof,
                "timestamp": time.time(),
            }
        )

        logger.warning(f"Containment COMPLETED: {len(executions)} actions")

        return {
            "success": True,
            "actions_executed": len(executions),
            "action_hash": action_hash,
            "merkle_proof": proof,
            "stage": "complete",
        }

    def _log_action(self, request: ContainmentRequest, executions: list) -> str:
        """Log containment action and return hash"""
        log_entry = {
            "request_hash": request.to_hash(),
            "event_id": request.event_id,
            "actions": [e.action.value for e in executions],
            "timestamp": time.time(),
        }

        # Hash log entry
        log_str = str(sorted(log_entry.items()))
        action_hash = hashlib.sha256(log_str.encode()).hexdigest()

        logger.info(f"Action logged: {action_hash[:16]}")

        return action_hash

    def _notify_governance(self, request: ContainmentRequest, executions: list, proof: dict):
        """Notify governance layer of containment"""
        logger.info("Governance notified of containment action")
        # TODO: Integrate with L10 governance RBAC


__all__ = [
    "ContainmentRequest",
    "ActionValidator",
    "MerkleProofGenerator",
    "ContainmentOrchestrator",
]
