"""Project-AI tarl public interface."""

from tarl.core import TARL, TARL_VERSION, make_tarl
from tarl.diagnostics import (
    Diagnostic,
    DiagnosticBatch,
    Location,
    Severity,
    make_diagnostic,
)
from tarl.policy import (
    PolicyProtocol,
    PolicyRule,
    TarlPolicy,
    allow_policy,
    deny_policy,
)
from tarl.spec import (
    ALLOWED_VERDICTS,
    TarlDecision,
    TarlError,
    TarlVerdict,
    make_decision,
)

__version__ = "0.0.0.dev0"

__all__ = [
    "ALLOWED_VERDICTS",
    "TARL",
    "TARL_VERSION",
    "Diagnostic",
    "DiagnosticBatch",
    "Location",
    "PolicyProtocol",
    "PolicyRule",
    "Severity",
    "TarlDecision",
    "TarlError",
    "TarlPolicy",
    "TarlVerdict",
    "allow_policy",
    "deny_policy",
    "make_decision",
    "make_diagnostic",
    "make_tarl",
]
