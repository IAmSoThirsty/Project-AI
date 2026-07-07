from __future__ import annotations

from dataclasses import dataclass

from identity.records import IdentityRecord, IdentityRegistry

from canonical._internal.capability_tokens import (
    CapabilityRegistry,
    CapabilityToken,
)
from canonical._internal.governance_policy import StaticGovernancePolicy


@dataclass
class CanonicalState:
    identities: IdentityRegistry
    capabilities: CapabilityRegistry
    policy: StaticGovernancePolicy

    @classmethod
    def empty(cls) -> CanonicalState:
        return cls(
            identities=IdentityRegistry(),
            capabilities=CapabilityRegistry(),
            policy=StaticGovernancePolicy(),
        )

    def to_record(self) -> dict[str, object]:
        return {
            "identities": [identity.to_record() for identity in self.identities.records()],
            "capabilities": [capability.to_record() for capability in self.capabilities.tokens()],
            "policy": self.policy.to_record(),
        }

    @classmethod
    def from_record(cls, record: dict[str, object]) -> CanonicalState:
        identities = [
            IdentityRecord.from_record(identity) for identity in record.get("identities", [])
        ]
        capabilities = [
            CapabilityToken.from_record(capability) for capability in record.get("capabilities", [])
        ]
        policy_record = record.get("policy", {})
        if not isinstance(policy_record, dict):
            raise ValueError("canonical policy record must be an object")
        return cls(
            identities=IdentityRegistry(identities),
            capabilities=CapabilityRegistry(capabilities),
            policy=StaticGovernancePolicy.from_record(policy_record),
        )
