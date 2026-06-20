"""Canonical, hash-bound evidence bundles for governance decisions."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from kernel.types import ActionRequest, Decision


def _canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode()


@dataclass(frozen=True)
class EvidenceBundle:
    action_id: str
    request_sha256: str
    decision_sha256: str
    bundle_sha256: str


def build_evidence_bundle(request: ActionRequest, decision: Decision) -> EvidenceBundle:
    request_record = {
        "action_id": request.action_id,
        "actor": request.actor,
        "operation": request.operation,
        "payload": dict(request.payload),
        "resource": request.resource,
    }
    decision_record = {
        "outcome": decision.outcome.value,
        "policy_version": decision.policy_version,
        "reasons": decision.reasons,
    }
    request_hash = hashlib.sha256(_canonical_json(request_record)).hexdigest()
    decision_hash = hashlib.sha256(_canonical_json(decision_record)).hexdigest()
    bundle_hash = hashlib.sha256(
        f"{request.action_id}:{request_hash}:{decision_hash}".encode()
    ).hexdigest()
    return EvidenceBundle(request.action_id, request_hash, decision_hash, bundle_hash)
