"""Project-AI kernel public interface."""

from kernel.deterministic_replay import ReplayResult, replay, verify_event_chain
from kernel.event_spine import Event, EventSpine
from kernel.evidence_bundle import EvidenceBundle, build_evidence_bundle
from kernel.invariant_engine import Invariant, InvariantEngine, InvariantViolation
from kernel.invariant_severity import InvariantSeverity
from kernel.state_register import RevisionConflictError, StateRegister, StateSnapshot
from kernel.time_trust import TimeRollbackError, TrustedClock
from kernel.types import ActionRequest, Decision, JsonScalar, JsonValue, Outcome

__version__ = "0.0.0.dev0"

__all__ = [
    "ActionRequest",
    "Decision",
    "Event",
    "EventSpine",
    "EvidenceBundle",
    "Invariant",
    "InvariantEngine",
    "InvariantSeverity",
    "InvariantViolation",
    "JsonScalar",
    "JsonValue",
    "Outcome",
    "ReplayResult",
    "RevisionConflictError",
    "StateRegister",
    "StateSnapshot",
    "TimeRollbackError",
    "TrustedClock",
    "build_evidence_bundle",
    "replay",
    "verify_event_chain",
]
