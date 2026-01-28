from dataclasses import dataclass
from typing import Tuple
import hashlib, json

TARL_VERSION = "2.0"

@dataclass(frozen=True)
class TARL:
    intent: str
    scope: str
    authority: str
    constraints: Tuple[str, ...]
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
