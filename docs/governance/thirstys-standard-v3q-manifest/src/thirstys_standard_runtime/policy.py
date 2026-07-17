from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Protocol

from .authority import AuthorityError, verify_authority_proof
from .cel_runtime import CELRuntime


class NonceStore(Protocol):
    def contains(self, nonce: str) -> bool: ...

    def add(self, nonce: str) -> None: ...


class InMemoryNonceStore:
    def __init__(self) -> None:
        self._nonces: set[str] = set()

    def contains(self, nonce: str) -> bool:
        return nonce in self._nonces

    def add(self, nonce: str) -> None:
        self._nonces.add(nonce)


@dataclass(frozen=True)
class GateDecision:
    decision: str
    reason: str
    action_class: str
    control_ids: tuple[str, ...]

    @property
    def allowed(self) -> bool:
        return self.decision == "allow"

    def as_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "reason": self.reason,
            "action_class": self.action_class,
            "control_ids": list(self.control_ids),
        }


class RuntimePolicyEngine:
    def __init__(
        self,
        manifest: dict[str, Any],
        trusted_keys: dict[str, Any],
        nonce_store: NonceStore | None = None,
    ):
        self.manifest = manifest
        self.trusted_keys = trusted_keys
        self.nonce_store = nonce_store or InMemoryNonceStore()
        self.cel = CELRuntime()
        self.cel.compile_manifest_conditions(manifest)
        self.action_classes = {item["id"]: item for item in manifest["action_classes"]}
        self.action_type_classes = {
            action_type: item["id"]
            for item in manifest["action_classes"]
            for action_type in item.get("action_types", [])
        }

    def gate_action(
        self,
        task: dict[str, Any],
        action: dict[str, Any],
        authority_proof: dict[str, Any] | None,
        approval_proof: dict[str, Any] | None = None,
        *,
        consume_approval: bool = False,
    ) -> GateDecision:
        action_class = action.get("class", "unknown")
        action_type = action.get("type", "unknown")
        class_entry = self.action_classes.get(action_class)
        if class_entry is None:
            return GateDecision("deny", "Unknown action class fails closed.", action_class, ("Q-003-A",))
        expected_class = self.action_type_classes.get(action_type)
        if expected_class is None:
            return GateDecision("deny", "Unknown action type has no authoritative classification.", action_class, ("Q-003-A",))
        if expected_class != action_class:
            return GateDecision(
                "deny",
                f"Action type {action_type!r} is classified as {expected_class!r}, not {action_class!r}.",
                action_class,
                ("Q-003-A",),
            )
        if authority_proof is None:
            return GateDecision("deny", "Missing authenticated authority proof.", action_class, ("Q-002-B", "Q-003-A"))
        task_id = task.get("task_id")
        if not task_id:
            return GateDecision("deny", "Task identifier is missing.", action_class, ("Q-002-B",))
        try:
            verify_authority_proof(
                authority_proof,
                self.trusted_keys,
                required_action=action_type,
                required_scope=f"task:{task_id}",
                purpose="authority",
            )
        except AuthorityError as exc:
            return GateDecision("deny", f"Authority rejected: {exc}", action_class, ("Q-002-B",))

        if action.get("is_retry") and action.get("prior_outcome") == "unknown" and not action.get("external_state_verified"):
            return GateDecision(
                "deny",
                "Unknown external outcome must be verified before retry.",
                action_class,
                ("Q-007-B", "Q-007-C"),
            )
        expected_revision = action.get("expected_revision")
        current_revision = action.get("current_revision")
        if expected_revision is not None and current_revision is not None and expected_revision != current_revision:
            return GateDecision("deny", "State drift detected; expected revision does not match current revision.", action_class, ("Q-007-A",))

        rank = int(class_entry["rank"])
        if rank >= 3:
            if approval_proof is None:
                return GateDecision(
                    "require_approval",
                    "This action class requires explicit approval or a valid narrower standing authorization.",
                    action_class,
                    ("Q-003-B",),
                )
            try:
                verify_authority_proof(
                    approval_proof,
                    self.trusted_keys,
                    required_action=action_type,
                    required_scope=f"action:{action['action_id']}",
                    purpose="approval",
                )
            except AuthorityError as exc:
                return GateDecision("deny", f"Approval rejected: {exc}", action_class, ("Q-003-B",))
            if approval_proof.get("action_id") not in (None, action.get("action_id")):
                return GateDecision("deny", "Approval proof is bound to a different action ID.", action_class, ("Q-003-B",))
            nonce = approval_proof["nonce"]
            if self.nonce_store.contains(nonce):
                return GateDecision("deny", "Approval proof nonce has already been consumed.", action_class, ("Q-003-B", "Q-007-B"))
            if consume_approval:
                self.nonce_store.add(nonce)
        if rank == 1 and action.get("recovery_required") and not action.get("rollback_plan"):
            return GateDecision("deny", "Reversible action lacks a credible rollback plan.", action_class, ("Q-003-C",))

        return GateDecision("allow", "Authenticated, scoped, and permitted by the action-class gate.", action_class, ("Q-002-B", "Q-003-A", "Q-003-B"))

    def enforce(
        self,
        task: dict[str, Any],
        action: dict[str, Any],
        authority_proof: dict[str, Any] | None,
        approval_proof: dict[str, Any] | None,
        executor: Callable[[], Any],
    ) -> dict[str, Any]:
        decision = self.gate_action(
            task,
            action,
            authority_proof,
            approval_proof,
            consume_approval=True,
        )
        record: dict[str, Any] = {
            "gate": decision.as_dict(),
            "executed": False,
            "outcome_status": "not_executed",
            "outcome": None,
            "error": None,
        }
        if not decision.allowed:
            return record
        record["executed"] = True
        try:
            record["outcome"] = executor()
            record["outcome_status"] = "succeeded"
        except Exception as exc:
            record["outcome_status"] = "unknown"
            record["error"] = f"{type(exc).__name__}: {exc}"
        return record
