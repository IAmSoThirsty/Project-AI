"""
sovereign_vault.tamper

Policy-driven, not event-driven: a tamper event does not have an
intrinsic response baked into the detector. It is looked up in an
explicit TamperPolicy table that you configure, and the audit event for
"tamper detected" is always written BEFORE the response is applied — so
even if the response itself fails partway, there is a durable record
that the event happened and what response was selected.

Five response tiers, ordered least to most destructive. REGENERATE_COMPONENT
is the ARDA-derived tier: rebuild one compromised component from a signed
blueprint under attestation, rather than jumping straight to sealing the
whole vault or wiping. See regeneration.py for that flow.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum

from .errors import TamperDetectedError
from .interfaces import AuditChainProvider


class TamperEvent(Enum):
    TOKEN_REMOVED = "token_removed"
    ENCLOSURE_OPENED = "enclosure_opened"  # chassis intrusion switch
    ATTESTATION_FAILED = "attestation_failed"
    ATTESTATION_DRIFT = "attestation_drift"  # PCR/measurement changed mid-session
    BINARY_MODIFIED = "binary_modified"  # IMA / dm-verity / code-signing violation
    DEBUGGER_ATTACHED = "debugger_attached"  # ptrace detection
    AUTH_FAILURE_THRESHOLD = "auth_failure_threshold"
    AUDIT_UNAVAILABLE = "audit_unavailable"
    CLOCK_ANOMALY = "clock_anomaly"


class TamperResponse(Enum):
    REATTEST = "reattest"  # least destructive: demand fresh attestation, resume if it passes
    REGENERATE_COMPONENT = (
        "regenerate_component"  # rebuild one component from signed blueprint (see regeneration.py)
    )
    SEAL = "seal"  # stop accepting new object-release requests; existing session ends
    REVOKE = "revoke"  # invalidate current tokens/bindings; require re-enrollment
    FORCE_RECOVERY = "force_recovery"  # most destructive: only quorum recovery can restore access


# Default policy. NOT hardcoded into the detector — pass your own
# TamperPolicy(table=...) to override per deployment. Nothing here wipes
# data; FORCE_RECOVERY requires quorum (recovery.py) which is itself
# non-destructive to the sealed objects, only to the current key epoch's
# access.
DEFAULT_POLICY: dict[TamperEvent, TamperResponse] = {
    TamperEvent.TOKEN_REMOVED: TamperResponse.SEAL,
    TamperEvent.ENCLOSURE_OPENED: TamperResponse.FORCE_RECOVERY,
    TamperEvent.ATTESTATION_FAILED: TamperResponse.SEAL,
    TamperEvent.ATTESTATION_DRIFT: TamperResponse.REGENERATE_COMPONENT,
    TamperEvent.BINARY_MODIFIED: TamperResponse.FORCE_RECOVERY,
    TamperEvent.DEBUGGER_ATTACHED: TamperResponse.SEAL,
    TamperEvent.AUTH_FAILURE_THRESHOLD: TamperResponse.REVOKE,
    TamperEvent.AUDIT_UNAVAILABLE: TamperResponse.SEAL,
    TamperEvent.CLOCK_ANOMALY: TamperResponse.REATTEST,
}


@dataclass
class TamperPolicy:
    table: dict[TamperEvent, TamperResponse] = field(default_factory=lambda: dict(DEFAULT_POLICY))

    def response_for(self, event: TamperEvent) -> TamperResponse:
        if event not in self.table:
            # An event with no configured response is itself a policy gap —
            # fail to the second-most destructive tier (REVOKE), not to
            # REATTEST. An unconfigured event must never resolve to the
            # least destructive response by default.
            return TamperResponse.REVOKE
        return self.table[event]


@dataclass
class TamperHandler:
    policy: TamperPolicy
    audit: AuditChainProvider
    on_seal: Callable[[TamperEvent], None] | None = None
    on_revoke: Callable[[TamperEvent], None] | None = None
    on_regenerate: Callable[[TamperEvent], None] | None = None
    on_force_recovery: Callable[[TamperEvent], None] | None = None
    on_reattest: Callable[[TamperEvent], None] | None = None

    def handle(self, event: TamperEvent, detail: dict[str, object]) -> TamperResponse:
        response = self.policy.response_for(event)

        # Audit write happens before the response is applied, and is not
        # optional: if the audit chain has no capacity, escalate to SEAL
        # regardless of what the policy table said, because an unaudited
        # tamper response is itself a governance failure. The escalation
        # must still take effect even though the audit write for THIS
        # event will also fail — audit unavailability is the reason to
        # seal, not a reason the seal can be skipped.
        audit_unavailable = not self.audit.has_capacity()
        if audit_unavailable:
            response = TamperResponse.SEAL
            detail = {**detail, "escalated_reason": "audit_unavailable_during_tamper_response"}

        try:
            self.audit.append(
                "TAMPER_DETECTED",
                {"event": event.value, "response": response.value, "detail": detail},
            )
        except Exception:
            # Could not record the event. Proceed with the response anyway —
            # a silently-dropped tamper response would be worse than an
            # unaudited one. The gap itself is recorded structurally by the
            # fact that this event's response is forced to SEAL.
            if not audit_unavailable:
                raise  # an audit failure that ISN'T capacity-related is unexpected; don't swallow it
            response = TamperResponse.SEAL

        handler_map = {
            TamperResponse.REATTEST: self.on_reattest,
            TamperResponse.REGENERATE_COMPONENT: self.on_regenerate,
            TamperResponse.SEAL: self.on_seal,
            TamperResponse.REVOKE: self.on_revoke,
            TamperResponse.FORCE_RECOVERY: self.on_force_recovery,
        }
        callback = handler_map.get(response)
        if callback is not None:
            callback(event)

        if response in (TamperResponse.SEAL, TamperResponse.REVOKE, TamperResponse.FORCE_RECOVERY):
            raise TamperDetectedError(
                f"tamper event {event.value} -> {response.value}: session terminated"
            )

        return response
