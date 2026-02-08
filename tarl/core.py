"""
TARL Core - Trust and Authorization Runtime Layer (Policy/Governance System)

This is the POLICY/GOVERNANCE subsystem version 2.0.
For the LANGUAGE RUNTIME VM, see tarl/system.py (version 1.0.0).

The policy TARL provides authorization and trust management.
The language TARL provides a complete programming language implementation.
"""

import hashlib
import json
from dataclasses import dataclass

TARL_VERSION = "2.0"  # Policy/Governance TARL version


@dataclass(frozen=True)
class TARL:
    intent: str
    scope: str
    authority: str
    constraints: tuple[str, ...]
    version: str = TARL_VERSION

    def canonical(self) -> dict:
        return {
            "version": self.version,
            "intent": self.intent,
            "scope": self.scope,
            "authority": self.authority,
            "constraints": list(self.constraints),
        }

    def hash(self) -> str:
        blob = json.dumps(self.canonical(), sort_keys=True).encode()
        return hashlib.sha256(blob).hexdigest()
