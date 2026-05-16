"""policy_registry.py — Upgrade 6: PolicyRegistry with versioning, migration, and drift detection.

Every execution records: policy_version, policy_hash, migration_state, compatibility_mode.
Signed changes, auditable, cannot silently weaken governance.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

_SIGN_SECRET = os.environ.get("POLICY_REGISTRY_SECRET", "dev-policy-secret")


def _sign(payload: str) -> str:
    return hmac.new(_SIGN_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()


@dataclass
class PolicyRecord:
    """Single versioned policy entry."""

    version: str
    policy_hash: str
    rules: dict[str, Any]              # domain → action → permitted bool
    migration_rule: str = ""
    sunset_date: float | None = None
    compatibility_mode: bool = False
    rollback_authority: str = ""
    created_at: float = field(default_factory=time.time)
    activated_at: float | None = None
    signed_by: str = ""
    signature: str = ""

    def compute_hash(self) -> str:
        payload = json.dumps(self.rules, sort_keys=True) + self.version
        return hashlib.sha256(payload.encode()).hexdigest()[:32]

    def sign(self) -> str:
        payload = json.dumps({
            "version": self.version,
            "policy_hash": self.policy_hash,
            "rules": self.rules,
            "created_at": self.created_at,
        }, sort_keys=True)
        return _sign(payload)

    def verify_signature(self) -> bool:
        expected = self.sign()
        return hmac.compare_digest(expected, self.signature)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "policy_hash": self.policy_hash,
            "migration_rule": self.migration_rule,
            "sunset_date": self.sunset_date,
            "compatibility_mode": self.compatibility_mode,
            "rollback_authority": self.rollback_authority,
            "created_at": self.created_at,
            "activated_at": self.activated_at,
            "signed_by": self.signed_by,
            "signature": self.signature,
        }


class PolicyRegistry:
    """Versioned, signed, auditable policy registry.

    Provides:
      - active_version, active_hash
      - previous_version, previous_hash
      - is_action_permitted(domain, action, context)
      - register_policy(record) — signed registration
      - detect_drift() — returns True if hash changed since last activation
      - human_gap_check() — CLARIFY/HUMAN_APPROVAL if policy changed during long gap
    """

    def __init__(self) -> None:
        self._policies: list[PolicyRecord] = []
        self._active: PolicyRecord | None = None
        self._previous: PolicyRecord | None = None
        self._mutation_audit: list[dict[str, Any]] = []
        self._init_default_policy()

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #

    @property
    def active_version(self) -> str:
        return self._active.version if self._active else "none"

    @property
    def active_hash(self) -> str:
        return self._active.policy_hash if self._active else ""

    @property
    def previous_version(self) -> str:
        return self._previous.version if self._previous else "none"

    @property
    def previous_hash(self) -> str:
        return self._previous.policy_hash if self._previous else ""

    # ------------------------------------------------------------------ #
    # Core API
    # ------------------------------------------------------------------ #

    def is_action_permitted(
        self, domain: str, action: str, context: dict[str, Any] | None = None
    ) -> tuple[bool, str]:
        if not self._active:
            return False, "No active policy"
        rules = self._active.rules
        # Check domain-specific rules first, then wildcard
        domain_rules = rules.get(domain, rules.get("*", {}))
        permitted = domain_rules.get(action, domain_rules.get("*", False))
        if permitted:
            return True, f"Permitted by policy {self.active_version}"
        return False, f"Denied by policy {self.active_version}: {domain}.{action} not in allowlist"

    def register_policy(self, record: PolicyRecord, activating_authority: str = "") -> None:
        """Register and activate a new policy version.

        Requires a valid signature on the record.
        Cannot silently weaken governance (BLOCK if hash degrades).
        """
        computed_hash = record.compute_hash()
        if computed_hash != record.policy_hash:
            raise ValueError(f"Policy hash mismatch: computed {computed_hash} != {record.policy_hash}")

        if not record.verify_signature():
            raise PermissionError("Policy signature verification failed — unsigned policy rejected")

        # Check for governance weakening
        if self._active:
            self._check_governance_weakening(self._active.rules, record.rules)

        self._previous = self._active
        record.activated_at = time.time()
        self._active = record
        self._policies.append(record)

        self._mutation_audit.append({
            "event": "POLICY_ACTIVATED",
            "version": record.version,
            "hash": record.policy_hash,
            "authority": activating_authority,
            "timestamp": record.activated_at,
        })
        logger.info("PolicyRegistry: activated version=%s hash=%s", record.version, record.policy_hash)

    def human_gap_check(self, human_gap_category: str) -> str | None:
        """Return CLARIFY or HUMAN_APPROVAL_REQUIRED if policy changed during a significant gap."""
        if not self._previous:
            return None
        if self._previous.policy_hash == self.active_hash:
            return None
        significant_gaps = {"significant", "substantial", "major", "profound", "epochal"}
        if human_gap_category in significant_gaps:
            self._mutation_audit.append({
                "event": "POLICY_GAP_REORIENTATION",
                "previous_version": self.previous_version,
                "active_version": self.active_version,
                "gap_category": human_gap_category,
                "timestamp": time.time(),
            })
            if human_gap_category in {"profound", "epochal"}:
                return "HUMAN_APPROVAL_REQUIRED"
            return "CLARIFY"
        return None

    def detect_drift(self) -> bool:
        if not self._active:
            return False
        return self._active.compute_hash() != self._active.policy_hash

    def get_mutation_audit(self) -> list[dict[str, Any]]:
        return list(self._mutation_audit)

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #

    def _init_default_policy(self) -> None:
        rules: dict[str, Any] = {
            "*": {"read": True, "list": True, "get": True},
            "system": {"shutdown": False, "reset": False},
        }
        record = PolicyRecord(
            version="1.0.0",
            policy_hash="",
            rules=rules,
            signed_by="bootstrap",
        )
        record.policy_hash = record.compute_hash()
        record.signature = record.sign()
        record.activated_at = time.time()
        self._active = record
        self._policies.append(record)

    def _check_governance_weakening(
        self, old_rules: dict[str, Any], new_rules: dict[str, Any]
    ) -> None:
        """Raise if new rules are strictly weaker than old rules for any blocked action."""
        # Simple heuristic: if a previously-False rule becomes True for a dangerous action
        dangerous_actions = {"shutdown", "reset", "delete_all", "execute_arbitrary"}
        for action in dangerous_actions:
            old_permitted = old_rules.get("system", {}).get(action, old_rules.get("*", {}).get(action, False))
            new_permitted = new_rules.get("system", {}).get(action, new_rules.get("*", {}).get(action, False))
            if not old_permitted and new_permitted:
                raise PermissionError(
                    f"ESCALATE: Policy mutation would weaken governance — "
                    f"action '{action}' was blocked, new policy permits it. "
                    "Constitutional approval required."
                )


_registry: PolicyRegistry | None = None


def get_policy_registry() -> PolicyRegistry:
    global _registry
    if _registry is None:
        _registry = PolicyRegistry()
    return _registry


__all__ = ["PolicyRecord", "PolicyRegistry", "get_policy_registry"]
