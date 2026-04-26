"""Iron Path Executor for deterministic mutation governance.

This module provides an explicit governance envelope for mutation-capable
operations. It enforces:
- immutable decision records
- policy-evaluation binding to every mutation decision
- complete mutation governance binding requirements
- append-only, replayable decision audit trails
- compensation-only rollback semantics
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class GovernanceBindingError(PermissionError):
    """Raised when a mutation request does not satisfy governance bindings."""


@dataclass(frozen=True)
class PolicyEvaluationRequest:
    """Policy evaluation request snapshot for governance traceability."""

    evaluation_id: str
    trace_id: str
    action: str
    resource: str
    principal: str
    context: dict[str, Any]
    requested_at: str


@dataclass(frozen=True)
class PolicyEvaluationResult:
    """Policy evaluation result that must be bound to mutation decisions."""

    evaluation_id: str
    trace_id: str
    decision: str
    reason: str
    matched_policies: list[str]
    constraints: list[str]
    evaluated_at: str


@dataclass(frozen=True)
class GovernanceEvaluationBinding:
    """Binding between mutation operation and policy evaluation result."""

    evaluation_id: str
    trace_id: str
    request_fingerprint: str
    policy_result_fingerprint: str
    bound_at: str


@dataclass(frozen=True)
class MutationGovernanceBinding:
    """Complete governance envelope for mutation-capable operations."""

    trace_id: str
    action: str
    resource: str
    mutation_class: str
    capability_token: str
    governance_context: dict[str, Any]
    evaluation_binding: GovernanceEvaluationBinding
    resolution_policy: str
    quorum_proof: dict[str, Any] | None = None


@dataclass(frozen=True)
class DecisionRecord:
    """Immutable decision artifact for every governed mutation."""

    decision_record_id: str
    trace_id: str
    action: str
    resource: str
    mutation_class: str
    principal: str
    decision: str
    reason: str
    binding: MutationGovernanceBinding
    policy_result: PolicyEvaluationResult
    previous_decision_hash: str
    decision_hash: str
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class AppendOnlyDecisionLog:
    """Append-only hash-chained decision log for replayable governance audit."""

    def __init__(self, log_path: str = "data/runtime/iron_path_decisions.jsonl"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def _last_hash(self) -> str:
        if not self.log_path.exists() or self.log_path.stat().st_size == 0:
            return "GENESIS"

        last_line = ""
        with self.log_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    last_line = line

        if not last_line:
            return "GENESIS"

        try:
            entry = json.loads(last_line)
        except json.JSONDecodeError as e:
            raise RuntimeError("Decision log corruption detected") from e

        return str(entry.get("decision_hash", "GENESIS"))

    def append(self, record: DecisionRecord) -> None:
        payload = _stable_json(asdict(record))
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(payload)
            f.write("\n")

    def replay(self) -> list[DecisionRecord]:
        records: list[DecisionRecord] = []
        if not self.log_path.exists():
            return records

        previous_hash = "GENESIS"
        with self.log_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)

                if data.get("previous_decision_hash") != previous_hash:
                    raise RuntimeError("Decision hash chain broken")

                binding_data = data["binding"]
                evaluation_binding_data = binding_data["evaluation_binding"]
                policy_result_data = data["policy_result"]

                binding = MutationGovernanceBinding(
                    trace_id=binding_data["trace_id"],
                    action=binding_data["action"],
                    resource=binding_data["resource"],
                    mutation_class=binding_data["mutation_class"],
                    capability_token=binding_data["capability_token"],
                    governance_context=binding_data["governance_context"],
                    evaluation_binding=GovernanceEvaluationBinding(
                        evaluation_id=evaluation_binding_data["evaluation_id"],
                        trace_id=evaluation_binding_data["trace_id"],
                        request_fingerprint=evaluation_binding_data["request_fingerprint"],
                        policy_result_fingerprint=evaluation_binding_data[
                            "policy_result_fingerprint"
                        ],
                        bound_at=evaluation_binding_data["bound_at"],
                    ),
                    resolution_policy=binding_data["resolution_policy"],
                    quorum_proof=binding_data.get("quorum_proof"),
                )

                policy_result = PolicyEvaluationResult(
                    evaluation_id=policy_result_data["evaluation_id"],
                    trace_id=policy_result_data["trace_id"],
                    decision=policy_result_data["decision"],
                    reason=policy_result_data["reason"],
                    matched_policies=policy_result_data.get("matched_policies", []),
                    constraints=policy_result_data.get("constraints", []),
                    evaluated_at=policy_result_data["evaluated_at"],
                )

                record = DecisionRecord(
                    decision_record_id=data["decision_record_id"],
                    trace_id=data["trace_id"],
                    action=data["action"],
                    resource=data["resource"],
                    mutation_class=data["mutation_class"],
                    principal=data["principal"],
                    decision=data["decision"],
                    reason=data["reason"],
                    binding=binding,
                    policy_result=policy_result,
                    previous_decision_hash=data["previous_decision_hash"],
                    decision_hash=data["decision_hash"],
                    created_at=data["created_at"],
                    metadata=data.get("metadata", {}),
                )

                records.append(record)
                previous_hash = record.decision_hash

        return records


class IronPathExecutor:
    """Deterministic mutation governance executor with conservative default-deny."""

    _READ_ONLY_PREFIXES = (
        "system.status",
        "data.query",
        "ecosystem.",
    )

    _SOFT_MUTATION_PREFIXES = (
        "persona.",
        "learning.",
        "ai.",
        "agent.",
        "temporal.",
    )

    _HARD_MUTATION_ACTIONS = {
        "user.create",
        "user.update",
        "user.delete",
        "system.config",
        "system.shutdown",
        "access.grant",
        "agents.toggle",
        "codex.activate",
    }

    _GOVERNANCE_MUTATION_ACTIONS = {
        "audit.export",
    }

    def __init__(self, decision_log_path: str = "data/runtime/iron_path_decisions.jsonl"):
        self.log = AppendOnlyDecisionLog(decision_log_path)

    def classify_mutation(self, action: str) -> str:
        if action in self._GOVERNANCE_MUTATION_ACTIONS:
            return "governanceMutation"
        if action in self._HARD_MUTATION_ACTIONS:
            return "hardMutation"
        if action.startswith(self._READ_ONLY_PREFIXES):
            return "read"
        if action.startswith(self._SOFT_MUTATION_PREFIXES):
            return "softMutation"
        return "governanceMutation"

    def evaluate_policy(
        self,
        action: str,
        resource: str,
        principal: str,
        context: dict[str, Any],
    ) -> tuple[PolicyEvaluationRequest, PolicyEvaluationResult]:
        trace_id = str(context.get("trace_id") or uuid.uuid4())
        evaluation_id = f"eval_{uuid.uuid4().hex}"

        req = PolicyEvaluationRequest(
            evaluation_id=evaluation_id,
            trace_id=trace_id,
            action=action,
            resource=resource,
            principal=principal,
            context=context,
            requested_at=_utc_now_iso(),
        )

        # Conservative default deny; explicit allow only for known registry actions.
        known_actions = set(context.get("valid_actions", []))
        if action not in known_actions:
            result = PolicyEvaluationResult(
                evaluation_id=evaluation_id,
                trace_id=trace_id,
                decision="deny",
                reason="Action not in policy registry (default deny)",
                matched_policies=["default-deny"],
                constraints=[],
                evaluated_at=_utc_now_iso(),
            )
            return req, result

        result = PolicyEvaluationResult(
            evaluation_id=evaluation_id,
            trace_id=trace_id,
            decision="allow",
            reason="Action admitted by policy registry and upstream gate checks",
            matched_policies=["registry-allow", "upstream-rbac-rate-quota"],
            constraints=context.get("constraints", []),
            evaluated_at=_utc_now_iso(),
        )
        return req, result

    def bind_mutation(
        self,
        *,
        action: str,
        resource: str,
        capability_token: str,
        governance_context: dict[str, Any],
        resolution_policy: str,
        evaluation_request: PolicyEvaluationRequest,
        evaluation_result: PolicyEvaluationResult,
        quorum_proof: dict[str, Any] | None,
    ) -> MutationGovernanceBinding:
        mutation_class = self.classify_mutation(action)

        req_fingerprint = hashlib.sha256(_stable_json(asdict(evaluation_request)).encode("utf-8")).hexdigest()
        result_fingerprint = hashlib.sha256(_stable_json(asdict(evaluation_result)).encode("utf-8")).hexdigest()

        binding = MutationGovernanceBinding(
            trace_id=evaluation_request.trace_id,
            action=action,
            resource=resource,
            mutation_class=mutation_class,
            capability_token=capability_token,
            governance_context=governance_context,
            evaluation_binding=GovernanceEvaluationBinding(
                evaluation_id=evaluation_result.evaluation_id,
                trace_id=evaluation_result.trace_id,
                request_fingerprint=req_fingerprint,
                policy_result_fingerprint=result_fingerprint,
                bound_at=_utc_now_iso(),
            ),
            resolution_policy=resolution_policy,
            quorum_proof=quorum_proof,
        )

        self._validate_binding(binding, evaluation_result)
        return binding

    def _validate_binding(
        self,
        binding: MutationGovernanceBinding,
        evaluation_result: PolicyEvaluationResult,
    ) -> None:
        if evaluation_result.decision != "allow":
            raise GovernanceBindingError(f"Policy evaluation denied mutation: {evaluation_result.reason}")

        required = {
            "trace_id": binding.trace_id,
            "action": binding.action,
            "resource": binding.resource,
            "mutation_class": binding.mutation_class,
            "capability_token": binding.capability_token,
            "resolution_policy": binding.resolution_policy,
        }
        missing = [k for k, v in required.items() if not v]
        if missing:
            raise GovernanceBindingError(
                f"Incomplete MutationGovernanceBinding, missing: {', '.join(missing)}"
            )

        if binding.mutation_class in {"hardMutation", "governanceMutation"}:
            if not binding.quorum_proof:
                raise GovernanceBindingError(
                    "Quorum proof required for hard/governance mutation"
                )

        if binding.evaluation_binding.trace_id != binding.trace_id:
            raise GovernanceBindingError("Evaluation binding trace mismatch")

    def record_decision(
        self,
        *,
        principal: str,
        binding: MutationGovernanceBinding,
        evaluation_result: PolicyEvaluationResult,
        decision: str,
        reason: str,
        metadata: dict[str, Any] | None = None,
    ) -> DecisionRecord:
        previous_hash = self.log._last_hash()
        created_at = _utc_now_iso()
        decision_record_id = f"dec_{uuid.uuid4().hex}"

        hash_payload = _stable_json(
            {
                "decision_record_id": decision_record_id,
                "trace_id": binding.trace_id,
                "action": binding.action,
                "resource": binding.resource,
                "mutation_class": binding.mutation_class,
                "principal": principal,
                "decision": decision,
                "reason": reason,
                "binding": asdict(binding),
                "policy_result": asdict(evaluation_result),
                "previous_decision_hash": previous_hash,
                "created_at": created_at,
            }
        )
        decision_hash = hashlib.sha256(hash_payload.encode("utf-8")).hexdigest()

        record = DecisionRecord(
            decision_record_id=decision_record_id,
            trace_id=binding.trace_id,
            action=binding.action,
            resource=binding.resource,
            mutation_class=binding.mutation_class,
            principal=principal,
            decision=decision,
            reason=reason,
            binding=binding,
            policy_result=evaluation_result,
            previous_decision_hash=previous_hash,
            decision_hash=decision_hash,
            created_at=created_at,
            metadata=metadata or {},
        )
        self.log.append(record)
        return record

    def compensate(
        self,
        *,
        principal: str,
        prior_record: DecisionRecord,
        capability_token: str,
        reason: str,
        quorum_proof: dict[str, Any] | None,
    ) -> DecisionRecord:
        # Compensation is the only rollback path; no destructive reversal.
        context = {
            "trace_id": str(uuid.uuid4()),
            "valid_actions": [f"compensate:{prior_record.action}"],
            "constraints": ["compensation-only-rollback"],
        }
        action = f"compensate:{prior_record.action}"
        resource = prior_record.resource
        req, result = self.evaluate_policy(action, resource, principal, context)
        if result.decision != "allow":
            # Explicitly allow compensation operations for valid prior record lineage.
            result = PolicyEvaluationResult(
                evaluation_id=req.evaluation_id,
                trace_id=req.trace_id,
                decision="allow",
                reason="Compensation transaction allowed for prior immutable decision",
                matched_policies=["compensation-policy"],
                constraints=["non-destructive", "linked-to-prior-decision"],
                evaluated_at=_utc_now_iso(),
            )

        binding = MutationGovernanceBinding(
            trace_id=req.trace_id,
            action=action,
            resource=resource,
            mutation_class="governanceMutation",
            capability_token=capability_token,
            governance_context={
                "compensates": prior_record.decision_record_id,
                "original_trace_id": prior_record.trace_id,
            },
            evaluation_binding=GovernanceEvaluationBinding(
                evaluation_id=result.evaluation_id,
                trace_id=result.trace_id,
                request_fingerprint=hashlib.sha256(_stable_json(asdict(req)).encode("utf-8")).hexdigest(),
                policy_result_fingerprint=hashlib.sha256(
                    _stable_json(asdict(result)).encode("utf-8")
                ).hexdigest(),
                bound_at=_utc_now_iso(),
            ),
            resolution_policy="default-deny-precedence",
            quorum_proof=quorum_proof,
        )

        self._validate_binding(binding, result)
        return self.record_decision(
            principal=principal,
            binding=binding,
            evaluation_result=result,
            decision="allow",
            reason=reason,
            metadata={"compensation_for": prior_record.decision_record_id},
        )


_iron_path_executor: IronPathExecutor | None = None


def get_iron_path_executor() -> IronPathExecutor:
    """Get singleton Iron Path executor."""
    global _iron_path_executor
    if _iron_path_executor is None:
        decision_log_path = os.getenv(
            "IRON_PATH_DECISION_LOG",
            "data/runtime/iron_path_decisions.jsonl",
        )
        _iron_path_executor = IronPathExecutor(decision_log_path=decision_log_path)
    return _iron_path_executor
