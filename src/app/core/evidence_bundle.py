"""evidence_bundle.py — Upgrade 9: Evidence Bundle Format.

Every governed execution produces one canonical proof-carrying artifact.
Produced for every governed request (including denials, clarifications, halts).
JSON serializable, hashable, audit-chain linked, no raw sensitive data.
"""
from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class EvidenceBundle:
    """Canonical proof bundle for a single governed request."""

    bundle_id: str
    request_hash: str
    intent_classification: str
    risk_classification: str
    benign_validation: str
    policy_decision: str
    execution_authorization: str
    capability_token: str
    invariant_results: list[dict[str, Any]]
    continuity_proof: str
    conversation_threat_state: str
    policy_version: str
    policy_hash: str
    audit_chain_prev: str
    audit_chain_next: str          # filled in after chain linkage
    timestamp_token: str
    executor_result_hash: str
    final_outcome: str             # GovernanceOutcome.value
    timestamp: float = field(default_factory=time.time)

    # ------------------------------------------------------------------ #
    def to_dict(self) -> dict[str, Any]:
        return {
            "bundle_id": self.bundle_id,
            "request_hash": self.request_hash,
            "intent_classification": self.intent_classification,
            "risk_classification": self.risk_classification,
            "benign_validation": self.benign_validation,
            "policy_decision": self.policy_decision,
            "execution_authorization": self.execution_authorization,
            "capability_token": self.capability_token,
            "invariant_results": self.invariant_results,
            "continuity_proof": self.continuity_proof,
            "conversation_threat_state": self.conversation_threat_state,
            "policy_version": self.policy_version,
            "policy_hash": self.policy_hash,
            "audit_chain_prev": self.audit_chain_prev,
            "audit_chain_next": self.audit_chain_next,
            "timestamp_token": self.timestamp_token,
            "executor_result_hash": self.executor_result_hash,
            "final_outcome": self.final_outcome,
            "timestamp": self.timestamp,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)

    def bundle_hash(self) -> str:
        """Deterministic hash of bundle contents (excluding audit_chain_next)."""
        d = self.to_dict()
        d.pop("audit_chain_next", None)
        payload = json.dumps(d, sort_keys=True, default=str)
        return hashlib.sha256(payload.encode()).hexdigest()

    def is_valid(self) -> bool:
        """Basic structural validation."""
        required = [
            "bundle_id", "request_hash", "final_outcome",
            "policy_version", "timestamp",
        ]
        d = self.to_dict()
        return all(d.get(k) for k in required)


class EvidenceBundleWriter:
    """Builds EvidenceBundle instances from governance pipeline outputs."""

    def build(
        self,
        *,
        request_hash: str = "",
        intent_classification: str = "",
        risk_score: float = 0.0,
        benign_confidence: float = 0.0,
        policy_decision: Any = None,
        execution_authorization: Any = None,
        capability_token: Any = None,
        invariant_results: list[Any] | None = None,
        continuity_proof: str = "",
        conversation_threat_state: Any = None,
        executor_result: Any = None,
        final_outcome: str = "DENY",
        audit_chain_prev: str = "",
        timestamp_token: str = "",
        policy_version: str = "",
        policy_hash: str = "",
    ) -> EvidenceBundle:
        bundle_id = str(uuid.uuid4())

        # Serialize sub-components to hashes / redacted strings
        policy_version = policy_version or getattr(policy_decision, "policy_version", "") or ""
        policy_hash = policy_hash or getattr(policy_decision, "policy_hash", "") or ""

        # Auto-populate from active registry when not supplied by caller
        if not policy_version or not policy_hash:
            try:
                from .policy_registry import get_policy_registry
                reg = get_policy_registry()
                if not policy_version:
                    policy_version = reg.active_version
                if not policy_hash:
                    policy_hash = reg.active_hash
            except Exception:
                pass

        pd_str = self._safe_hash(policy_decision)
        ea_str = self._safe_hash(execution_authorization)
        ct_str = self._safe_hash(capability_token)
        cth_str = self._safe_serialize(conversation_threat_state)

        inv_results_dicts: list[dict[str, Any]] = []
        for r in (invariant_results or []):
            if hasattr(r, "to_dict"):
                inv_results_dicts.append(r.to_dict())
            elif isinstance(r, dict):
                inv_results_dicts.append(r)

        executor_hash = ""
        if executor_result is not None:
            try:
                executor_hash = hashlib.sha256(
                    json.dumps(executor_result, sort_keys=True, default=str).encode()
                ).hexdigest()[:32]
            except Exception:
                executor_hash = "unhashable"

        bundle = EvidenceBundle(
            bundle_id=bundle_id,
            request_hash=request_hash,
            intent_classification=intent_classification,
            risk_classification=f"score={risk_score:.3f}",
            benign_validation=f"confidence={benign_confidence:.3f}",
            policy_decision=pd_str,
            execution_authorization=ea_str,
            capability_token=ct_str,
            invariant_results=inv_results_dicts,
            continuity_proof=continuity_proof or "none",
            conversation_threat_state=cth_str,
            policy_version=policy_version,
            policy_hash=policy_hash,
            audit_chain_prev=audit_chain_prev,
            audit_chain_next="",           # set by chain linker
            timestamp_token=timestamp_token or "",
            executor_result_hash=executor_hash,
            final_outcome=final_outcome,
        )
        # Self-referential chain: next = hash of this bundle
        bundle.audit_chain_next = bundle.bundle_hash()
        logger.debug("EvidenceBundle created: id=%s outcome=%s", bundle_id, final_outcome)
        _EVIDENCE_STORE.record(bundle)
        return bundle

    def _safe_hash(self, obj: Any) -> str:
        if obj is None:
            return "none"
        try:
            if hasattr(obj, "to_json"):
                data = obj.to_json()
            elif hasattr(obj, "to_dict"):
                data = json.dumps(obj.to_dict(), sort_keys=True, default=str)
            else:
                data = str(obj)
            return hashlib.sha256(data.encode()).hexdigest()[:32]
        except Exception:
            return "error-hashing"

    def _safe_serialize(self, obj: Any) -> str:
        if obj is None:
            return "none"
        try:
            if hasattr(obj, "to_json"):
                return obj.to_json()[:256]     # bounded
            elif hasattr(obj, "to_dict"):
                return json.dumps(obj.to_dict(), sort_keys=True, default=str)[:256]
            return str(obj)[:256]
        except Exception:
            return "serialization-error"


class EvidenceBundleValidator:
    """Validates an EvidenceBundle for structural completeness."""

    VALID_OUTCOMES = {
        "ALLOW", "DENY", "CLARIFY",
        "HUMAN_APPROVAL_REQUIRED", "DEGRADED_READ_ONLY",
        "HALT", "ESCALATE",
    }

    def validate(self, bundle: EvidenceBundle) -> tuple[bool, list[str]]:
        errors: list[str] = []

        if not bundle.bundle_id:
            errors.append("Missing bundle_id")
        if not bundle.request_hash:
            errors.append("Missing request_hash")
        if bundle.final_outcome not in self.VALID_OUTCOMES:
            errors.append(f"Invalid final_outcome: {bundle.final_outcome!r}")
        if not bundle.policy_version:
            errors.append("Missing policy_version")
        if bundle.timestamp <= 0:
            errors.append("Invalid timestamp")

        # Must be JSON serializable
        try:
            bundle.to_json()
        except Exception as e:
            errors.append(f"Not JSON serializable: {e}")

        return len(errors) == 0, errors


__all__ = [
    "EvidenceBundle",
    "EvidenceBundleWriter",
    "EvidenceBundleValidator",
]


# ---------------------------------------------------------------------------
# In-process evidence store — lightweight audit ring buffer.
# Populated automatically by EvidenceBundleWriter.build() via record().
# Not persisted across process restarts (use external audit log for durable storage).
# ---------------------------------------------------------------------------

class _EvidenceStore:
    """Thread-safe in-memory ring buffer for evidence bundles (max 10k)."""

    _MAX = 10_000

    def __init__(self) -> None:
        import threading
        self._lock = threading.Lock()
        self._bundles: list[dict] = []

    def record(self, bundle: EvidenceBundle) -> None:
        with self._lock:
            if len(self._bundles) >= self._MAX:
                self._bundles.pop(0)
            self._bundles.append(bundle.to_dict())

    def all(self) -> list[dict]:
        with self._lock:
            return list(self._bundles)

    def latest(self) -> dict | None:
        with self._lock:
            return self._bundles[-1] if self._bundles else None

    def by_session(self, session_id: str) -> list[dict]:
        with self._lock:
            return [b for b in self._bundles if b.get("session_id") == session_id]

    def __len__(self) -> int:
        with self._lock:
            return len(self._bundles)


_EVIDENCE_STORE = _EvidenceStore()



def get_evidence_store() -> "_EvidenceStore":
    """Return the singleton in-process evidence store."""
    return _EVIDENCE_STORE
