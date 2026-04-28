"""Iron Path Executor for deterministic mutation governance.

This module provides an explicit governance envelope for mutation-capable
operations. It enforces:
- immutable decision records
- explicit policy request/response contract
- complete mutation governance binding requirements
- append-only, replayable decision audit trails
- compensation-only rollback semantics
"""

from __future__ import annotations

import hashlib
import hmac
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
    actor: str = ""
    principal: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    inputs_hash: str = ""
    requested_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self) -> None:
        actor = self.actor or self.principal
        principal = self.principal or self.actor
        object.__setattr__(self, "actor", actor or "unknown")
        object.__setattr__(self, "principal", principal or "unknown")


@dataclass(frozen=True)
class PolicyEvaluationResponse:
    """Canonical policy evaluation response bound to decisions."""

    evaluation_id: str
    trace_id: str
    decision: str
    reason: str
    matched_policies: list[str]
    constraints: list[str]
    outputs_hash: str
    evaluated_at: str


# Backward-compatible alias retained for existing imports.
PolicyEvaluationResult = PolicyEvaluationResponse


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
    """Immutable, signed, linked decision artifact for governed actions."""

    # Canonical Caretaker-aligned fields
    decision_id: str
    trace_id: str
    evaluation_id: str
    actor: str
    action: str
    resource: str
    inputs_hash: str
    outputs_hash: str
    authority_chain: list[str]
    timestamp: str
    signature: str
    previous_hash: str

    # Runtime governance semantics
    mutation_class: str
    decision: str
    reason: str
    binding: MutationGovernanceBinding
    policy_result: PolicyEvaluationResponse
    decision_hash: str
    decision_type: str = "decision_record"
    metadata: dict[str, Any] = field(default_factory=dict)

    # Backward-compatible aliases
    @property
    def decision_record_id(self) -> str:
        return self.decision_id

    @property
    def principal(self) -> str:
        return self.actor

    @property
    def previous_decision_hash(self) -> str:
        return self.previous_hash

    @property
    def created_at(self) -> str:
        return self.timestamp


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _hmac_sha256_hex(secret: bytes, data: str) -> str:
    return hmac.new(secret, data.encode("utf-8"), hashlib.sha256).hexdigest()


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

                entry_previous_hash = data.get(
                    "previous_hash",
                    data.get("previous_decision_hash", "GENESIS"),
                )
                if entry_previous_hash != previous_hash:
                    raise RuntimeError("Decision hash chain broken")

                binding_data = data.get("binding") or {}
                evaluation_binding_data = binding_data.get("evaluation_binding") or {}

                policy_result_data = data.get("policy_result") or {}
                if not policy_result_data:
                    # Compatibility fallback for very old entries.
                    policy_result_data = {
                        "evaluation_id": data.get("evaluation_id", "unknown"),
                        "trace_id": data.get("trace_id", "unknown"),
                        "decision": data.get("decision", "deny"),
                        "reason": data.get("reason", "replayed"),
                        "matched_policies": [],
                        "constraints": [],
                        "outputs_hash": data.get("outputs_hash", ""),
                        "evaluated_at": data.get("timestamp", data.get("created_at", _utc_now_iso())),
                    }

                policy_result = PolicyEvaluationResponse(
                    evaluation_id=policy_result_data.get(
                        "evaluation_id",
                        evaluation_binding_data.get("evaluation_id", "unknown"),
                    ),
                    trace_id=policy_result_data.get("trace_id", data.get("trace_id", "unknown")),
                    decision=policy_result_data.get("decision", data.get("decision", "deny")),
                    reason=policy_result_data.get("reason", data.get("reason", "replayed")),
                    matched_policies=list(policy_result_data.get("matched_policies", [])),
                    constraints=list(policy_result_data.get("constraints", [])),
                    outputs_hash=policy_result_data.get(
                        "outputs_hash",
                        evaluation_binding_data.get("policy_result_fingerprint", ""),
                    ),
                    evaluated_at=policy_result_data.get(
                        "evaluated_at",
                        data.get("timestamp", data.get("created_at", _utc_now_iso())),
                    ),
                )

                request_fingerprint = evaluation_binding_data.get(
                    "request_fingerprint",
                    data.get("inputs_hash", ""),
                )
                response_fingerprint = evaluation_binding_data.get(
                    "policy_result_fingerprint",
                    data.get("outputs_hash", policy_result.outputs_hash),
                )

                binding = MutationGovernanceBinding(
                    trace_id=binding_data.get("trace_id", data.get("trace_id", "unknown")),
                    action=binding_data.get("action", data.get("action", "unknown.action")),
                    resource=binding_data.get("resource", data.get("resource", "resource://unknown")),
                    mutation_class=binding_data.get("mutation_class", data.get("mutation_class", "softMutation")),
                    capability_token=binding_data.get("capability_token", "replay"),
                    governance_context=binding_data.get("governance_context", {}),
                    evaluation_binding=GovernanceEvaluationBinding(
                        evaluation_id=evaluation_binding_data.get(
                            "evaluation_id",
                            policy_result.evaluation_id,
                        ),
                        trace_id=evaluation_binding_data.get("trace_id", data.get("trace_id", "unknown")),
                        request_fingerprint=request_fingerprint,
                        policy_result_fingerprint=response_fingerprint,
                        bound_at=evaluation_binding_data.get(
                            "bound_at",
                            data.get("timestamp", data.get("created_at", _utc_now_iso())),
                        ),
                    ),
                    resolution_policy=binding_data.get("resolution_policy", "default-deny-precedence"),
                    quorum_proof=binding_data.get("quorum_proof"),
                )

                record = DecisionRecord(
                    decision_id=data.get("decision_id", data.get("decision_record_id", f"dec_replay_{uuid.uuid4().hex}")),
                    trace_id=data.get("trace_id", binding.trace_id),
                    evaluation_id=data.get("evaluation_id", policy_result.evaluation_id),
                    actor=data.get("actor", data.get("principal", "unknown")),
                    action=data.get("action", binding.action),
                    resource=data.get("resource", binding.resource),
                    inputs_hash=data.get("inputs_hash", binding.evaluation_binding.request_fingerprint),
                    outputs_hash=data.get(
                        "outputs_hash",
                        binding.evaluation_binding.policy_result_fingerprint,
                    ),
                    authority_chain=list(data.get("authority_chain", [])),
                    timestamp=data.get("timestamp", data.get("created_at", _utc_now_iso())),
                    signature=data.get("signature", "unsigned"),
                    previous_hash=entry_previous_hash,
                    mutation_class=data.get("mutation_class", binding.mutation_class),
                    decision=data.get("decision", policy_result.decision),
                    reason=data.get("reason", policy_result.reason),
                    binding=binding,
                    policy_result=policy_result,
                    decision_hash=data.get("decision_hash", ""),
                    decision_type=data.get("decision_type", "decision_record"),
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

    _REQUIRED_SIGNATURES: dict[str, str] = {
        "softMutation": "1 domain",
        "hardMutation": "1 domain + evaluation",
        "governanceMutation": "all affected domains",
    }

    def __init__(
        self,
        decision_log_path: str = "data/runtime/iron_path_decisions.jsonl",
        signing_key: str | None = None,
    ):
        self.log = AppendOnlyDecisionLog(decision_log_path)
        key_material = signing_key or os.getenv("IRON_PATH_SIGNING_KEY", "iron-path-dev-key")
        self._signing_key = key_material.encode("utf-8")

    def classify_mutation(self, action: str) -> str:
        if action in self._GOVERNANCE_MUTATION_ACTIONS:
            return "governanceMutation"
        if action in self._HARD_MUTATION_ACTIONS:
            return "hardMutation"
        if action.startswith(self._READ_ONLY_PREFIXES):
            return "read"
        if action.startswith(self._SOFT_MUTATION_PREFIXES):
            return "softMutation"
        # Compatibility-safe default for unknown action names in kernel-local traces.
        return "softMutation"

    def required_signatures_for(self, mutation_class: str) -> str:
        return self._REQUIRED_SIGNATURES.get(mutation_class, "1 domain")

    def _extract_quorum_votes(self, quorum_proof: dict[str, Any] | None) -> list[str]:
        if not quorum_proof:
            return []

        votes = quorum_proof.get("votes", [])
        normalized: list[str] = []
        for vote in votes:
            if isinstance(vote, str):
                normalized.append(vote)
            elif isinstance(vote, dict):
                voter = vote.get("domain") or vote.get("id") or vote.get("name")
                if voter:
                    normalized.append(str(voter))

        deduped = sorted(set(normalized))
        return deduped

    def _build_policy_response(
        self,
        request: PolicyEvaluationRequest,
        decision: str,
        reason: str,
        matched_policies: list[str],
        constraints: list[str],
    ) -> PolicyEvaluationResponse:
        response_payload = {
            "evaluation_id": request.evaluation_id,
            "trace_id": request.trace_id,
            "decision": decision,
            "reason": reason,
            "matched_policies": matched_policies,
            "constraints": constraints,
        }

        outputs_hash = _sha256_hex(_stable_json(response_payload))
        return PolicyEvaluationResponse(
            evaluation_id=request.evaluation_id,
            trace_id=request.trace_id,
            decision=decision,
            reason=reason,
            matched_policies=matched_policies,
            constraints=constraints,
            outputs_hash=outputs_hash,
            evaluated_at=_utc_now_iso(),
        )

    def evaluate_policy(
        self,
        action: str,
        resource: str,
        principal: str,
        context: dict[str, Any],
    ) -> tuple[PolicyEvaluationRequest, PolicyEvaluationResponse]:
        trace_id = str(context.get("trace_id") or uuid.uuid4())
        evaluation_id = f"eval_{uuid.uuid4().hex}"

        actor = str(context.get("actor") or principal or "unknown")
        inputs_hash = _sha256_hex(
            _stable_json(
                {
                    "trace_id": trace_id,
                    "actor": actor,
                    "action": action,
                    "resource": resource,
                    "context": context,
                }
            )
        )

        req = PolicyEvaluationRequest(
            evaluation_id=evaluation_id,
            trace_id=trace_id,
            action=action,
            resource=resource,
            actor=actor,
            principal=principal,
            context=context,
            inputs_hash=inputs_hash,
            requested_at=_utc_now_iso(),
        )

        # Conservative default deny; explicit allow only for known registry actions.
        known_actions = set(context.get("valid_actions", []))
        if action not in known_actions:
            result = self._build_policy_response(
                request=req,
                decision="deny",
                reason="Action not in policy registry (default deny)",
                matched_policies=["default-deny"],
                constraints=[],
            )
            return req, result

        result = self._build_policy_response(
            request=req,
            decision="allow",
            reason="Action admitted by policy registry and upstream gate checks",
            matched_policies=["registry-allow", "upstream-rbac-rate-quota"],
            constraints=list(context.get("constraints", [])),
        )
        return req, result

    def build_response_from_decision(
        self,
        request: PolicyEvaluationRequest,
        approved: bool,
        reason: str,
        *,
        matched_policies: list[str] | None = None,
        constraints: list[str] | None = None,
    ) -> PolicyEvaluationResponse:
        return self._build_policy_response(
            request=request,
            decision="allow" if approved else "deny",
            reason=reason,
            matched_policies=matched_policies or ["kernel-governance"],
            constraints=constraints or [],
        )

    def bind_mutation(
        self,
        *,
        action: str,
        resource: str,
        capability_token: str,
        governance_context: dict[str, Any],
        resolution_policy: str,
        evaluation_request: PolicyEvaluationRequest,
        evaluation_result: PolicyEvaluationResponse,
        quorum_proof: dict[str, Any] | None,
    ) -> MutationGovernanceBinding:
        mutation_class = self.classify_mutation(action)

        req_fingerprint = _sha256_hex(_stable_json(asdict(evaluation_request)))
        result_fingerprint = _sha256_hex(_stable_json(asdict(evaluation_result)))

        normalized_quorum = quorum_proof
        if mutation_class == "softMutation" and not normalized_quorum:
            domain = (
                str(governance_context.get("domain"))
                if governance_context.get("domain")
                else "kernel"
            )
            normalized_quorum = {
                "votes": [domain],
                "affected_domains": [domain],
            }

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
            quorum_proof=normalized_quorum,
        )

        self._validate_binding(binding, evaluation_result)
        return binding

    def bind_observed_decision(
        self,
        *,
        action: str,
        resource: str,
        capability_token: str,
        governance_context: dict[str, Any],
        resolution_policy: str,
        evaluation_request: PolicyEvaluationRequest,
        evaluation_response: PolicyEvaluationResponse,
        quorum_proof: dict[str, Any] | None = None,
    ) -> MutationGovernanceBinding:
        """Bind an already-produced decision response without changing behavior.

        Used by kernel flows that already performed governance evaluation but need
        explicit request/response contract materialization and ledger linking.
        """
        mutation_class = self.classify_mutation(action)

        req_fingerprint = _sha256_hex(_stable_json(asdict(evaluation_request)))
        result_fingerprint = _sha256_hex(_stable_json(asdict(evaluation_response)))

        normalized_quorum = quorum_proof
        if mutation_class == "softMutation" and not normalized_quorum:
            domain = (
                str(governance_context.get("domain"))
                if governance_context.get("domain")
                else "kernel"
            )
            normalized_quorum = {
                "votes": [domain],
                "affected_domains": [domain],
            }

        binding = MutationGovernanceBinding(
            trace_id=evaluation_request.trace_id,
            action=action,
            resource=resource,
            mutation_class=mutation_class,
            capability_token=capability_token,
            governance_context=governance_context,
            evaluation_binding=GovernanceEvaluationBinding(
                evaluation_id=evaluation_response.evaluation_id,
                trace_id=evaluation_response.trace_id,
                request_fingerprint=req_fingerprint,
                policy_result_fingerprint=result_fingerprint,
                bound_at=_utc_now_iso(),
            ),
            resolution_policy=resolution_policy,
            quorum_proof=normalized_quorum,
        )

        self._validate_binding_shape(binding)
        if evaluation_response.decision == "allow":
            self._validate_binding(binding, evaluation_response)

        return binding

    def _validate_binding_shape(self, binding: MutationGovernanceBinding) -> None:
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

        if binding.evaluation_binding.trace_id != binding.trace_id:
            raise GovernanceBindingError("Evaluation binding trace mismatch")

    def _validate_binding(
        self,
        binding: MutationGovernanceBinding,
        evaluation_result: PolicyEvaluationResponse,
    ) -> None:
        if evaluation_result.decision != "allow":
            raise GovernanceBindingError(
                f"Policy evaluation denied mutation: {evaluation_result.reason}"
            )

        self._validate_binding_shape(binding)

        votes = self._extract_quorum_votes(binding.quorum_proof)

        if binding.mutation_class == "softMutation" and len(votes) < 1:
            raise GovernanceBindingError(
                "Soft mutation requires at least one domain signature"
            )

        if binding.mutation_class == "hardMutation":
            if not binding.quorum_proof:
                raise GovernanceBindingError(
                    "Quorum proof required for hard/governance mutation"
                )
            if len(votes) < 1:
                raise GovernanceBindingError(
                    "Hard mutation requires one domain signature"
                )
            if not binding.evaluation_binding.evaluation_id:
                raise GovernanceBindingError(
                    "Hard mutation requires evaluation binding"
                )

        if binding.mutation_class == "governanceMutation":
            if not binding.quorum_proof:
                raise GovernanceBindingError(
                    "Quorum proof required for hard/governance mutation"
                )
            affected_domains = []
            if binding.quorum_proof:
                affected_domains = [
                    str(domain)
                    for domain in binding.quorum_proof.get("affected_domains", [])
                ]

            if affected_domains:
                missing_domains = [domain for domain in affected_domains if domain not in votes]
                if missing_domains:
                    raise GovernanceBindingError(
                        "Governance mutation missing affected domain signatures: "
                        + ", ".join(missing_domains)
                    )
            elif len(votes) < 1:
                raise GovernanceBindingError(
                    "Governance mutation requires all affected domain signatures"
                )

    def _resolve_authority_chain(
        self,
        binding: MutationGovernanceBinding,
        policy_result: PolicyEvaluationResponse,
    ) -> list[str]:
        votes = self._extract_quorum_votes(binding.quorum_proof)
        chain: list[str] = list(votes)

        if binding.mutation_class in {"hardMutation", "governanceMutation"}:
            chain.append(f"evaluation:{policy_result.evaluation_id}")

        if not chain:
            chain = ["kernel", f"evaluation:{policy_result.evaluation_id}"]

        return sorted(set(chain))

    def record_decision(
        self,
        *,
        principal: str,
        binding: MutationGovernanceBinding,
        evaluation_result: PolicyEvaluationResponse,
        decision: str,
        reason: str,
        metadata: dict[str, Any] | None = None,
        decision_type: str = "decision_record",
    ) -> DecisionRecord:
        previous_hash = self.log._last_hash()
        timestamp = _utc_now_iso()
        decision_id = f"dec_{uuid.uuid4().hex}"

        authority_chain = self._resolve_authority_chain(binding, evaluation_result)
        inputs_hash = binding.evaluation_binding.request_fingerprint
        outputs_hash = binding.evaluation_binding.policy_result_fingerprint

        hash_payload = _stable_json(
            {
                "decision_id": decision_id,
                "trace_id": binding.trace_id,
                "evaluation_id": evaluation_result.evaluation_id,
                "actor": principal,
                "action": binding.action,
                "resource": binding.resource,
                "inputs_hash": inputs_hash,
                "outputs_hash": outputs_hash,
                "authority_chain": authority_chain,
                "timestamp": timestamp,
                "previous_hash": previous_hash,
                "decision": decision,
                "reason": reason,
                "decision_type": decision_type,
            }
        )
        decision_hash = _sha256_hex(hash_payload)
        signature_payload = _stable_json(
            {
                "decision_id": decision_id,
                "decision_hash": decision_hash,
                "previous_hash": previous_hash,
                "timestamp": timestamp,
            }
        )
        signature = _hmac_sha256_hex(self._signing_key, signature_payload)

        record = DecisionRecord(
            decision_id=decision_id,
            trace_id=binding.trace_id,
            evaluation_id=evaluation_result.evaluation_id,
            actor=principal,
            action=binding.action,
            resource=binding.resource,
            inputs_hash=inputs_hash,
            outputs_hash=outputs_hash,
            authority_chain=authority_chain,
            timestamp=timestamp,
            signature=signature,
            previous_hash=previous_hash,
            mutation_class=binding.mutation_class,
            decision=decision,
            reason=reason,
            binding=binding,
            policy_result=evaluation_result,
            decision_hash=decision_hash,
            decision_type=decision_type,
            metadata=metadata or {},
        )
        self.log.append(record)
        return record

    def record_commit_receipt(
        self,
        *,
        principal: str,
        binding: MutationGovernanceBinding,
        evaluation_result: PolicyEvaluationResponse,
        reason: str,
        metadata: dict[str, Any] | None = None,
    ) -> DecisionRecord:
        return self.record_decision(
            principal=principal,
            binding=binding,
            evaluation_result=evaluation_result,
            decision="allow",
            reason=reason,
            metadata=metadata,
            decision_type="commit_receipt",
        )

    def record_arbiter_ruling(
        self,
        *,
        principal: str,
        binding: MutationGovernanceBinding,
        evaluation_result: PolicyEvaluationResponse,
        decision: str,
        reason: str,
        metadata: dict[str, Any] | None = None,
    ) -> DecisionRecord:
        return self.record_decision(
            principal=principal,
            binding=binding,
            evaluation_result=evaluation_result,
            decision=decision,
            reason=reason,
            metadata=metadata,
            decision_type="arbiter_ruling",
        )

    def record_im_moment(
        self,
        *,
        principal: str,
        binding: MutationGovernanceBinding,
        evaluation_result: PolicyEvaluationResponse,
        reason: str,
        metadata: dict[str, Any] | None = None,
    ) -> DecisionRecord:
        return self.record_decision(
            principal=principal,
            binding=binding,
            evaluation_result=evaluation_result,
            decision="allow",
            reason=reason,
            metadata=metadata,
            decision_type="im_moment",
        )

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
            "actor": principal,
        }
        action = f"compensate:{prior_record.action}"
        resource = prior_record.resource
        req, result = self.evaluate_policy(action, resource, principal, context)
        if result.decision != "allow":
            # Explicitly allow compensation operations for valid prior record lineage.
            result = self._build_policy_response(
                request=req,
                decision="allow",
                reason="Compensation transaction allowed for prior immutable decision",
                matched_policies=["compensation-policy"],
                constraints=["non-destructive", "linked-to-prior-decision"],
            )

        binding = self.bind_observed_decision(
            action=action,
            resource=resource,
            capability_token=capability_token,
            governance_context={
                "compensates": prior_record.decision_id,
                "original_trace_id": prior_record.trace_id,
                "domain": "governance",
            },
            resolution_policy="default-deny-precedence",
            evaluation_request=req,
            evaluation_response=result,
            quorum_proof=quorum_proof,
        )

        return self.record_decision(
            principal=principal,
            binding=binding,
            evaluation_result=result,
            decision="allow",
            reason=reason,
            metadata={
                "compensation_for": prior_record.decision_id,
                "priorDecisionId": prior_record.decision_id,
                "effect": "forward-only correction",
            },
            decision_type="compensating_action",
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
