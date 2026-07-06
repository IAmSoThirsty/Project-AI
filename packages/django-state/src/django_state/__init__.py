"""Project-AI Django State Engine (J2 scenario engine port).

Human Misunderstanding Extinction Engine - models irreversible
state evolution, human misunderstanding cascades, and system
extinction dynamics.
"""

from __future__ import annotations

from django_state.engine import DjangoStateEngine
from django_state.evaluation import DARPAEvaluator, validators
from django_state.kernel import (
    CausalEvent,
    CollapseScheduler,
    IrreversibilityLaws,
    RealityClock,
    StateVector,
)
from django_state.modules import (
    HumanForcesModule,
    InstitutionalPressureModule,
    MetricsModule,
    OutcomesModule,
    PerceptionWarfareModule,
    RedTeamModule,
    TimelineModule,
)
from django_state.schemas import (
    BetrayalEvent,
    CooperationEvent,
    EngineConfig,
    Event,
    EventType,
    InstitutionalFailureEvent,
    IrreversibilityConfig,
    ManipulationEvent,
    OutcomeThresholds,
    RedTeamEvent,
    StateDimension,
)

__version__ = "0.0.0.dev0"

__all__ = [
    "BetrayalEvent",
    "CausalEvent",
    "CollapseScheduler",
    "CooperationEvent",
    "DARPAEvaluator",
    "DjangoStateEngine",
    "EngineConfig",
    "Event",
    "EventType",
    "HumanForcesModule",
    "InstitutionalFailureEvent",
    "InstitutionalPressureModule",
    "IrreversibilityConfig",
    "IrreversibilityLaws",
    "ManipulationEvent",
    "MetricsModule",
    "OutcomeThresholds",
    "OutcomesModule",
    "PerceptionWarfareModule",
    "RealityClock",
    "RedTeamEvent",
    "RedTeamModule",
    "StateDimension",
    "StateVector",
    "TimelineModule",
    "validators",
]
