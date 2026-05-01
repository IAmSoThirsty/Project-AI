"""Governance quorum engine — quorum-based decisions for high-impact actions."""

from __future__ import annotations

import hashlib
import json
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


class QuorumDecision(Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    INCONCLUSIVE = "inconclusive"


@dataclass
class QuorumPolicy:
    decision_type: str
    validator_ids: Set[str]
    min_participation_fraction: float = 0.67
    min_approval_fraction: float = 0.67
    high_impact: bool = True
    description: str = ""


@dataclass
class QuorumVote:
    decision_id: str
    validator_id: str
    approved: bool
    reason: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "validator_id": self.validator_id,
            "approved": self.approved,
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class QuorumProof:
    decision_id: str
    decision_type: str
    decision_context_hash: str
    final_decision: QuorumDecision
    participating_validators: List[str]
    approving_validators: List[str]
    rejecting_validators: List[str]
    votes: List[QuorumVote]
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "decision_type": self.decision_type,
            "decision_context_hash": self.decision_context_hash,
            "final_decision": self.final_decision.value,
            "participating_validators": self.participating_validators,
            "approving_validators": self.approving_validators,
            "rejecting_validators": self.rejecting_validators,
            "votes": [v.to_dict() for v in self.votes],
            "created_at": self.created_at.isoformat(),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)


class QuorumError(Exception):
    pass


class UnknownPolicyError(QuorumError):
    pass


class QuorumEngine:
    """
    Quorum engine for GOVERNANCE_DECISION events.

    Intentionally decoupled from the event spine — call directly from
    GovernanceKernel / AdvancedBootSystem, or subscribe to events and feed in.
    """

    def __init__(self) -> None:
        self._policies: Dict[str, QuorumPolicy] = {}
        self._votes: Dict[str, List[QuorumVote]] = {}
        self._proofs: Dict[str, QuorumProof] = {}
        self._waiters: Dict[str, threading.Event] = {}
        self._lock = threading.RLock()

    def register_policy(self, policy: QuorumPolicy) -> None:
        with self._lock:
            self._policies[policy.decision_type] = policy

    def get_policy(self, decision_type: str) -> QuorumPolicy:
        with self._lock:
            policy = self._policies.get(decision_type)
        if policy is None:
            raise UnknownPolicyError(
                f"No quorum policy for decision_type={decision_type}"
            )
        return policy

    def _decision_context_hash(self, context: Dict[str, Any]) -> str:
        serialized = json.dumps(context, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def start_decision(
        self,
        decision_id: str,
        decision_type: str,
        context: Dict[str, Any],
    ) -> str:
        _ = self.get_policy(decision_type)
        context_hash = self._decision_context_hash(context)
        with self._lock:
            if decision_id not in self._votes:
                self._votes[decision_id] = []
            if decision_id not in self._waiters:
                self._waiters[decision_id] = threading.Event()
        return context_hash

    def submit_vote(self, vote: QuorumVote) -> None:
        policy = self.get_policy(
            self._infer_decision_type_from_id(vote.decision_id)
        )
        with self._lock:
            existing = self._votes.setdefault(vote.decision_id, [])
            if any(v.validator_id == vote.validator_id for v in existing):
                return
            existing.append(vote)
            proof = self._evaluate_quorum(vote.decision_id, policy)
            if proof is not None:
                self._proofs[vote.decision_id] = proof
                if vote.decision_id in self._waiters:
                    self._waiters[vote.decision_id].set()

    def wait_for_quorum(
        self,
        decision_id: str,
        decision_type: str,
        context: Dict[str, Any],
        timeout_seconds: Optional[float] = None,
    ) -> QuorumProof:
        policy = self.get_policy(decision_type)
        context_hash = self.start_decision(decision_id, decision_type, context)

        with self._lock:
            waiter = self._waiters.setdefault(decision_id, threading.Event())

        with self._lock:
            existing_proof = self._proofs.get(decision_id)
        if existing_proof is not None:
            return existing_proof

        waiter.wait(timeout=timeout_seconds)

        with self._lock:
            proof = self._proofs.get(decision_id)
            votes = list(self._votes.get(decision_id, []))

        if proof is not None:
            return proof

        return self._build_inconclusive_proof(
            decision_id=decision_id,
            decision_type=decision_type,
            context_hash=context_hash,
            policy=policy,
            votes=votes,
        )

    def get_proof(self, decision_id: str) -> Optional[QuorumProof]:
        with self._lock:
            return self._proofs.get(decision_id)

    def _infer_decision_type_from_id(self, decision_id: str) -> str:
        raise UnknownPolicyError(
            f"Cannot infer decision_type from decision_id={decision_id}; "
            "use wait_for_quorum/start_decision with explicit decision_type."
        )

    def _evaluate_quorum(
        self,
        decision_id: str,
        policy: QuorumPolicy,
    ) -> Optional[QuorumProof]:
        # Proof construction requires the context hash stored by the caller;
        # signal completion to wait_for_quorum via waiter, which builds the proof.
        votes = list(self._votes.get(decision_id, []))
        if not votes:
            return None

        validator_ids = policy.validator_ids
        participating_ids = {
            v.validator_id for v in votes if v.validator_id in validator_ids
        }
        total_validators = len(validator_ids)
        total_participating = len(participating_ids)

        if total_validators == 0 or total_participating == 0:
            return None

        participation_fraction = total_participating / total_validators
        if participation_fraction < policy.min_participation_fraction:
            return None

        approving_ids = {
            v.validator_id
            for v in votes
            if v.approved and v.validator_id in validator_ids
        }
        approval_fraction = len(approving_ids) / total_participating

        if approval_fraction >= policy.min_approval_fraction:
            return None  # Wake waiter; let wait_for_quorum build the proof
        if (1.0 - approval_fraction) >= policy.min_approval_fraction:
            return None

        return None

    def _build_inconclusive_proof(
        self,
        decision_id: str,
        decision_type: str,
        context_hash: str,
        policy: QuorumPolicy,
        votes: List[QuorumVote],
    ) -> QuorumProof:
        validator_ids = policy.validator_ids
        participating_ids = {
            v.validator_id for v in votes if v.validator_id in validator_ids
        }
        approving_ids = {
            v.validator_id
            for v in votes
            if v.approved and v.validator_id in validator_ids
        }
        rejecting_ids = {
            v.validator_id
            for v in votes
            if not v.approved and v.validator_id in validator_ids
        }
        return QuorumProof(
            decision_id=decision_id,
            decision_type=decision_type,
            decision_context_hash=context_hash,
            final_decision=QuorumDecision.INCONCLUSIVE,
            participating_validators=sorted(participating_ids),
            approving_validators=sorted(approving_ids),
            rejecting_validators=sorted(rejecting_ids),
            votes=votes,
        )


_quorum_engine_instance: QuorumEngine | None = None


def get_quorum_engine() -> QuorumEngine:
    global _quorum_engine_instance
    if _quorum_engine_instance is None:
        _quorum_engine_instance = QuorumEngine()
    return _quorum_engine_instance


__all__ = [
    "QuorumDecision",
    "QuorumPolicy",
    "QuorumVote",
    "QuorumProof",
    "QuorumError",
    "UnknownPolicyError",
    "QuorumEngine",
    "get_quorum_engine",
]
