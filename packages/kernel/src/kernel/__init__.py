"""Project-AI kernel public interface."""

from kernel.deterministic_replay import ReplayResult, replay, verify_event_chain
from kernel.event_spine import Event, EventSpine
from kernel.evidence_bundle import EvidenceBundle, build_evidence_bundle
from kernel.invariant_engine import Invariant, InvariantEngine, InvariantViolation
from kernel.invariant_severity import InvariantSeverity
from kernel.state_register import RevisionConflictError, StateRegister, StateSnapshot
from kernel.tarl_bridge import (
    EscalationHandler,
    TarlEnforcementError,
    TarlGate,
    TarlVerdictValue,
    TarlVerdictView,
)
from kernel.threat_detection import (
    AttackPatternLibrary,
    BehaviorAnalyzer,
    BehaviorPattern,
    HeuristicPredictor,
    RecommendedAction,
    ThreatAssessment,
    ThreatCategory,
    ThreatDetectionEngine,
)
from kernel.time_trust import TimeRollbackError, TrustedClock
from kernel.types import ActionRequest, Decision, JsonScalar, JsonValue, Outcome

__version__ = "0.0.0.dev0"

__all__ = [
    "ActionRequest",
    "AttackPatternLibrary",
    "BehaviorAnalyzer",
    "BehaviorPattern",
    "Decision",
    "EscalationHandler",
    "Event",
    "EventSpine",
    "EvidenceBundle",
    "HeuristicPredictor",
    "Invariant",
    "InvariantEngine",
    "InvariantSeverity",
    "InvariantViolation",
    "JsonScalar",
    "JsonValue",
    "Outcome",
    "RecommendedAction",
    "ReplayResult",
    "RevisionConflictError",
    "StateRegister",
    "StateSnapshot",
    "TarlEnforcementError",
    "TarlGate",
    "TarlVerdictValue",
    "TarlVerdictView",
    "ThreatAssessment",
    "ThreatCategory",
    "ThreatDetectionEngine",
    "TimeRollbackError",
    "TrustedClock",
    "build_evidence_bundle",
    "replay",
    "verify_event_chain",
]
