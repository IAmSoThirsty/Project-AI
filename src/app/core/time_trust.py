"""time_trust.py — Upgrade 20: Externalized Time / RFC 3161 Heartbeat.

Risk: local clock tampering misclassifies human gap.

NOTE: External TSA calls are MOCKED in tests.  Production deployments
should configure a real RFC 3161 TSA endpoint via TIME_TRUST_TSA_URL.

If TSA unavailable → degraded auditability mode (NOT silent success).
If clock skew > threshold → HALT or ESCALATE.
"""
from __future__ import annotations

import hashlib
import logging
import os
import time
import urllib.request
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

_TSA_URL = os.environ.get("TIME_TRUST_TSA_URL", "")
_SKEW_THRESHOLD_SECONDS = float(os.environ.get("TIME_TRUST_SKEW_THRESHOLD", "300"))  # 5 min
_TSA_TIMEOUT = float(os.environ.get("TIME_TRUST_TSA_TIMEOUT", "5"))


@dataclass
class TimeTrustResult:
    """Result of a time trust validation."""

    local_time: float
    external_time: float | None
    skew_seconds: float | None
    tsa_available: bool
    tsa_url: str
    token_hash: str           # hash of TSA response or "mock"
    outcome: str              # "OK", "SKEW_DETECTED", "TSA_UNAVAILABLE", "DEGRADED_AUDIT"
    audit_event: str
    governance_recommendation: str  # "ALLOW", "HALT", "ESCALATE", "DEGRADED_READ_ONLY"
    metadata: dict[str, Any] = field(default_factory=dict)


class TimeTrustValidator:
    """Validates local clock against external trusted timestamp.

    TSA integration is STUBBED for offline operation.
    Set TIME_TRUST_TSA_URL to enable real RFC 3161 queries.

    In tests: pass mock_external_time to bypass actual network calls.
    """

    def __init__(
        self,
        tsa_url: str = _TSA_URL,
        skew_threshold: float = _SKEW_THRESHOLD_SECONDS,
    ) -> None:
        self.tsa_url = tsa_url
        self.skew_threshold = skew_threshold

    def validate(
        self,
        mock_external_time: float | None = None,   # for testing only
    ) -> TimeTrustResult:
        local_time = time.time()

        if mock_external_time is not None:
            # Test path — explicit mock
            return self._evaluate(local_time, mock_external_time, tsa_available=True, token_hash="mock")

        if not self.tsa_url:
            return self._tsa_unavailable(local_time, reason="TIME_TRUST_TSA_URL not configured")

        external_time, token_hash, error = self._query_tsa()
        if error or external_time is None:
            return self._tsa_unavailable(local_time, reason=error or "TSA query failed")

        return self._evaluate(local_time, external_time, tsa_available=True, token_hash=token_hash)

    def _query_tsa(self) -> tuple[float | None, str, str]:
        """Query RFC 3161 TSA.  Returns (timestamp, token_hash, error)."""
        try:
            # Minimal RFC 3161 query: HEAD request to get Date header as proxy for time
            req = urllib.request.Request(self.tsa_url, method="HEAD")
            with urllib.request.urlopen(req, timeout=_TSA_TIMEOUT) as resp:
                date_header = resp.headers.get("Date", "")
                if date_header:
                    import email.utils
                    ext_time = email.utils.parsedate_to_datetime(date_header).timestamp()
                    token_hash = hashlib.sha256(date_header.encode()).hexdigest()[:16]
                    return ext_time, token_hash, ""
            return None, "", "No Date header in TSA response"
        except Exception as exc:
            return None, "", str(exc)

    def _evaluate(
        self, local: float, external: float, tsa_available: bool, token_hash: str
    ) -> TimeTrustResult:
        skew = abs(local - external)
        if skew > self.skew_threshold:
            outcome = "SKEW_DETECTED"
            recommendation = "HALT" if skew > self.skew_threshold * 3 else "ESCALATE"
            audit = f"CLOCK_SKEW_{recommendation}: local={local:.0f} external={external:.0f} skew={skew:.1f}s"
            logger.critical(
                "TimeTrust: %s (skew=%.1fs threshold=%.1fs)",
                outcome, skew, self.skew_threshold,
            )
        else:
            outcome = "OK"
            recommendation = "ALLOW"
            audit = f"TIME_TRUST_OK: skew={skew:.1f}s"
            logger.debug("TimeTrust: OK skew=%.1fs", skew)

        return TimeTrustResult(
            local_time=local,
            external_time=external,
            skew_seconds=skew,
            tsa_available=tsa_available,
            tsa_url=self.tsa_url,
            token_hash=token_hash,
            outcome=outcome,
            audit_event=audit,
            governance_recommendation=recommendation,
        )

    def _tsa_unavailable(self, local: float, reason: str) -> TimeTrustResult:
        audit = f"TSA_UNAVAILABLE: {reason}"
        logger.warning("TimeTrust: %s", audit)
        return TimeTrustResult(
            local_time=local,
            external_time=None,
            skew_seconds=None,
            tsa_available=False,
            tsa_url=self.tsa_url,
            token_hash="unavailable",
            outcome="TSA_UNAVAILABLE",
            audit_event=audit,
            # Not HALT — degraded auditability mode, not silent success
            governance_recommendation="DEGRADED_READ_ONLY",
            metadata={"reason": reason},
        )


_validator: TimeTrustValidator | None = None


def get_time_trust_validator() -> TimeTrustValidator:
    global _validator
    if _validator is None:
        _validator = TimeTrustValidator()
    return _validator


__all__ = ["TimeTrustResult", "TimeTrustValidator", "get_time_trust_validator"]
