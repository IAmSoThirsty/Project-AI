"""Project-AI security surfaces."""

from security.bridge import (
    AppendOnlyAuditRelay,
    receive_canary_hit,
    receive_verdict,
    report_governance_denial,
    start_audit_relay,
)
from security.chimera import CanaryHit, ChimeraSecurity, Detection, classify

# Proof-obligation extraction is imported lazily so a missing
# thirsty-lang dep does not crash the rest of the security package
# at import time. The module is fail-closed on its own; this is an
# additional layer of defense for callers that never use the
# proof-obligation surface.
try:
    from security.proof_obligations import (
        ContractAnnotation,
        ProofObligationError,
        ProofObligationReport,
        extract_obligations,
    )
except ImportError:  # pragma: no cover - fail-closed
    ContractAnnotation = None  # type: ignore[assignment,misc]
    ProofObligationError = None  # type: ignore[assignment,misc]
    ProofObligationReport = None  # type: ignore[assignment,misc]
    extract_obligations = None  # type: ignore[assignment]

__all__ = [
    "AppendOnlyAuditRelay",
    "CanaryHit",
    "ChimeraSecurity",
    "ContractAnnotation",
    "Detection",
    "ProofObligationError",
    "ProofObligationReport",
    "classify",
    "extract_obligations",
    "receive_canary_hit",
    "receive_verdict",
    "report_governance_denial",
    "start_audit_relay",
]
