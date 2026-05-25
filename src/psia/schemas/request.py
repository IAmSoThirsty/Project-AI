"""PSIA request envelope schemas."""
from __future__ import annotations

import hashlib
import json
from typing import Any

from pydantic import BaseModel, ConfigDict

from psia.schemas.identity import Signature


class Intent(BaseModel):
    action: str
    resource: str
    parameters: dict[str, Any] = {}


class RequestContext(BaseModel):
    trace_id: str = ""
    session_id: str = ""
    metadata: dict[str, Any] = {}


class RequestTimestamps(BaseModel):
    created_at: str
    expires_at: str | None = None


class RequestEnvelope(BaseModel):
    model_config = ConfigDict(extra="allow")

    request_id: str
    actor: str
    subject: str
    capability_token_id: str
    intent: Any = None
    context: RequestContext = RequestContext()
    timestamps: Any = None
    signature: Signature

    def compute_hash(self) -> str:
        d = self.model_dump()
        d.pop("signature", None)
        return hashlib.sha256(
            json.dumps(d, sort_keys=True, default=str).encode()
        ).hexdigest()
