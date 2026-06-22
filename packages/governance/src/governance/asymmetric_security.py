"""Fail-closed asymmetric-security evidence governor and deterministic test catalog."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType

from governance.types import Vote
from kernel import ActionRequest, JsonValue, Outcome


class AttackCategory(StrEnum):
    PROMPT_INJECTION = "prompt_injection"
    JAILBREAK = "jailbreak"
    MULTI_TURN_MANIPULATION = "multi_turn_manipulation"
    CONSTITUTIONAL_BYPASS = "constitutional_bypass"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    TEMPORAL_ATTACK = "temporal_attack"
    REWARD_HACKING = "reward_hacking"
    AGENT_EXFILTRATION = "agent_exfiltration"
    SUPPLY_CHAIN_POISONING = "supply_chain_poisoning"


class SecurityProof(StrEnum):
    INPUT_TRUSTED = "input_trusted"
    INSTRUCTION_HIERARCHY_INTACT = "instruction_hierarchy_intact"
    MULTI_TURN_STATE_CONSISTENT = "multi_turn_state_consistent"
    GOVERNANCE_AUTHORIZED = "governance_authorized"
    CAPABILITY_VALID = "capability_valid"
    SCOPE_VALID = "scope_valid"
    TEMPORAL_ORDER_VALID = "temporal_order_valid"
    REPLAY_FRESH = "replay_fresh"
    REWARD_INTEGRITY = "reward_integrity"
    EGRESS_AUTHORIZED = "egress_authorized"
    AUDIT_BOUND = "audit_bound"
    SUPPLY_CHAIN_VERIFIED = "supply_chain_verified"


REQUIRED_PROOFS = tuple(SecurityProof)

CATEGORY_COUNTS: Mapping[AttackCategory, int] = MappingProxyType(
    {
        AttackCategory.PROMPT_INJECTION: 38,
        AttackCategory.JAILBREAK: 44,
        AttackCategory.MULTI_TURN_MANIPULATION: 52,
        AttackCategory.CONSTITUTIONAL_BYPASS: 31,
        AttackCategory.PRIVILEGE_ESCALATION: 29,
        AttackCategory.TEMPORAL_ATTACK: 41,
        AttackCategory.REWARD_HACKING: 27,
        AttackCategory.AGENT_EXFILTRATION: 22,
        AttackCategory.SUPPLY_CHAIN_POISONING: 28,
    }
)

_CATEGORY_FAILURES: Mapping[AttackCategory, tuple[SecurityProof, ...]] = MappingProxyType(
    {
        AttackCategory.PROMPT_INJECTION: (
            SecurityProof.INPUT_TRUSTED,
            SecurityProof.INSTRUCTION_HIERARCHY_INTACT,
        ),
        AttackCategory.JAILBREAK: (
            SecurityProof.INSTRUCTION_HIERARCHY_INTACT,
            SecurityProof.GOVERNANCE_AUTHORIZED,
            SecurityProof.AUDIT_BOUND,
        ),
        AttackCategory.MULTI_TURN_MANIPULATION: (
            SecurityProof.MULTI_TURN_STATE_CONSISTENT,
            SecurityProof.REPLAY_FRESH,
            SecurityProof.INSTRUCTION_HIERARCHY_INTACT,
        ),
        AttackCategory.CONSTITUTIONAL_BYPASS: (
            SecurityProof.GOVERNANCE_AUTHORIZED,
            SecurityProof.AUDIT_BOUND,
        ),
        AttackCategory.PRIVILEGE_ESCALATION: (
            SecurityProof.CAPABILITY_VALID,
            SecurityProof.SCOPE_VALID,
            SecurityProof.GOVERNANCE_AUTHORIZED,
        ),
        AttackCategory.TEMPORAL_ATTACK: (
            SecurityProof.TEMPORAL_ORDER_VALID,
            SecurityProof.REPLAY_FRESH,
        ),
        AttackCategory.REWARD_HACKING: (
            SecurityProof.REWARD_INTEGRITY,
            SecurityProof.GOVERNANCE_AUTHORIZED,
        ),
        AttackCategory.AGENT_EXFILTRATION: (
            SecurityProof.EGRESS_AUTHORIZED,
            SecurityProof.SCOPE_VALID,
            SecurityProof.AUDIT_BOUND,
        ),
        AttackCategory.SUPPLY_CHAIN_POISONING: (
            SecurityProof.SUPPLY_CHAIN_VERIFIED,
            SecurityProof.INPUT_TRUSTED,
        ),
    }
)


@dataclass(frozen=True)
class AttackVector:
    vector_id: str
    category: AttackCategory
    failed_proofs: tuple[SecurityProof, ...]

    def payload(self) -> Mapping[str, JsonValue]:
        evidence: dict[str, JsonValue] = {proof.value: True for proof in REQUIRED_PROOFS}
        for proof in self.failed_proofs:
            evidence[proof.value] = False
        return {
            "attack_vector_id": self.vector_id,
            "attack_category": self.category.value,
            "security_evidence": evidence,
        }


def build_attack_catalog() -> tuple[AttackVector, ...]:
    """Reconstruct the published 312-vector category matrix deterministically."""
    vectors: list[AttackVector] = []
    for category, count in CATEGORY_COUNTS.items():
        failures = _CATEGORY_FAILURES[category]
        prefix = "".join(part[0] for part in category.value.split("_")).upper()
        for index in range(1, count + 1):
            primary = failures[(index - 1) % len(failures)]
            selected: tuple[SecurityProof, ...] = (primary,)
            if index % 5 == 0 and len(failures) > 1:
                secondary = failures[index % len(failures)]
                if secondary is not primary:
                    selected = (primary, secondary)
            vectors.append(AttackVector(f"{prefix}-{index:03d}", category, selected))
    return tuple(vectors)


class AsymmetricSecurityGovernor:
    """Veto actions unless every asymmetric-security proof is explicit and valid."""

    name = "asymmetric-security"

    def evaluate(self, request: ActionRequest, state: Mapping[str, object]) -> Vote:
        del state
        evidence = request.payload.get("security_evidence")
        if not isinstance(evidence, Mapping):
            return Vote(self.name, Outcome.DENY, "security_evidence is missing or malformed")

        expected = {proof.value for proof in REQUIRED_PROOFS}
        supplied = {key for key in evidence if isinstance(key, str)}
        unexpected = sorted(supplied - expected)
        failed = sorted(
            proof.value for proof in REQUIRED_PROOFS if evidence.get(proof.value) is not True
        )
        if unexpected:
            failed.extend(f"unexpected:{name}" for name in unexpected)
        if failed:
            return Vote(self.name, Outcome.DENY, f"security proof failed: {', '.join(failed)}")
        return Vote(self.name, Outcome.ALLOW)
