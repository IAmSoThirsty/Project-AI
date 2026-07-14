"""
sovereign_vault.deny

The formal uncertainty-denial gate. This is the module that makes "the
vault should not try its best" enforceable rather than aspirational.

RuntimeConditions has no default of True for anything. Every field starts
as None (UNKNOWN). A gated operation calls `require_all()`, which raises
UncertainStateError on ANY field that is still None, and SafeHaltError on
any field that is explicitly False. There is no code path from "some
condition wasn't checked" to "operation proceeds anyway."
"""

from __future__ import annotations

import time
from dataclasses import dataclass, fields

from .errors import SafeHaltError, UncertainStateError


@dataclass
class RuntimeConditions:
    device_identity_verified: bool | None = None
    clock_trusted: bool | None = None
    policy_state_fresh: bool | None = None
    audit_available: bool | None = None
    attestation_consistent: bool | None = None
    token_present: bool | None = None

    def require_all(self) -> None:
        for f in fields(self):
            value = getattr(self, f.name)
            if value is None:
                raise UncertainStateError(
                    f"RuntimeConditions.{f.name} was never explicitly checked "
                    f"(still UNKNOWN). Refusing to proceed on an unproven "
                    f"invariant — SAFE_HALT."
                )
            if value is False:
                raise SafeHaltError(f"RuntimeConditions.{f.name} == False. SAFE_HALT.")

    def is_fully_proven(self) -> bool:
        try:
            self.require_all()
            return True
        except SafeHaltError:
            return False


class TrustedClock:
    """
    Clock-trust check. Real deployment: NTP with certificate pinning
    against a fixed set of trusted time sources, cross-checked against the
    monotonic sequence number's own timestamp trend (state.Checkpoint) so
    that a large forward *or backward* jump versus the last checkpoint's
    timestamp is itself treated as clock distrust, not just NTP failure.

    This module implements the *check*, not the NTP client — the NTP
    stack itself is a deploy-time seam (see deploy/ for the pinned-cert
    config this expects).
    """

    def __init__(self, max_drift_seconds: float = 5.0, max_backward_seconds: float = 1.0):
        self.max_drift_seconds = max_drift_seconds
        self.max_backward_seconds = max_backward_seconds
        self._last_observed_ns: int | None = None

    def check(self, ntp_reference_ns: int | None) -> bool:
        """
        Returns True only if:
          - an NTP reference was actually supplied (None = untrusted, not
            'skip the check'), AND
          - local monotonic time agrees with it within max_drift_seconds, AND
          - local time has not moved backward past max_backward_seconds
            relative to the last time this check ran (catches a rolled-back
            system clock even if NTP itself is spoofed).
        """
        if ntp_reference_ns is None:
            return False
        local_ns = time.time_ns()
        drift = abs(local_ns - ntp_reference_ns) / 1e9
        if drift > self.max_drift_seconds:
            return False
        if self._last_observed_ns is not None:
            backward = (self._last_observed_ns - local_ns) / 1e9
            if backward > self.max_backward_seconds:
                return False
        self._last_observed_ns = local_ns
        return True
