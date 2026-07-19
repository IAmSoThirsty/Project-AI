"""Project-AI execution public interface."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

from execution.gate import ExecutionGate, ExecutionResult, Executor, submit_action
from execution.risk import (
    LexicalRiskClassifier,
    RiskAssessment,
    RiskClass,
    RiskClassifier,
    SafeAllowCalibration,
    request_fingerprint,
)

try:
    __version__ = _pkg_version("project-ai-execution")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0.dev0"

__all__ = [
    "ExecutionGate",
    "ExecutionResult",
    "Executor",
    "LexicalRiskClassifier",
    "RiskAssessment",
    "RiskClass",
    "RiskClassifier",
    "SafeAllowCalibration",
    "request_fingerprint",
    "submit_action",
]
