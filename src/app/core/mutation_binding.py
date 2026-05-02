"""Cryptographic binding between a governance decision and the mutation it authorises."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class MutationGovernanceBinding:
    decision_id: str
    actor: str
    action: str
    context: Dict[str, Any]
    approved: bool
    output_hash: str
    binding_hash: str

    @staticmethod
    def create(decision_record: Any) -> "MutationGovernanceBinding":
        serialized = json.dumps(
            {
                "decision_id": decision_record.decision_id,
                "actor": decision_record.actor,
                "action": decision_record.action,
                "context": decision_record.context,
                "approved": decision_record.approved,
                "output_hash": decision_record.output_hash,
            },
            sort_keys=True,
        )
        binding_hash = hashlib.sha256(serialized.encode()).hexdigest()
        return MutationGovernanceBinding(
            decision_id=decision_record.decision_id,
            actor=decision_record.actor,
            action=decision_record.action,
            context=decision_record.context,
            approved=decision_record.approved,
            output_hash=decision_record.output_hash,
            binding_hash=binding_hash,
        )

    def verify(self) -> bool:
        serialized = json.dumps(
            {
                "decision_id": self.decision_id,
                "actor": self.actor,
                "action": self.action,
                "context": self.context,
                "approved": self.approved,
                "output_hash": self.output_hash,
            },
            sort_keys=True,
        )
        expected = hashlib.sha256(serialized.encode()).hexdigest()
        return expected == self.binding_hash


__all__ = ["MutationGovernanceBinding"]
