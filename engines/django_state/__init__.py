"""Django State Engine - Human Misunderstanding Extinction Engine.

Production-grade simulation engine for modeling irreversible state evolution,
human misunderstanding cascades, and system extinction dynamics.

Complete implementation with:
- Irreversibility laws (trust decay, kindness singularity, betrayal probability, etc.)
- Event sourcing and causal timeline
- Black vault SHA-256 fingerprinting
- Entropy delta calculation
- Complete module integration
- DARPA-grade evaluation
"""

from .engine import DjangoStateEngine
from .schemas import (
    StateVector,
    StateDimension,
    Event,
    EventType,
    BetrayalEvent,
    CooperationEvent,
    InstitutionalFailureEvent,
    ManipulationEvent,
    RedTeamEvent,
    EngineConfig,
    IrreversibilityConfig,
    OutcomeThresholds,
)
from .kernel import (
    RealityClock,
    CausalEvent,
    IrreversibilityLaws,
    CollapseScheduler,
)
from .modules import (
    HumanForcesModule,
    InstitutionalPressureModule,
    PerceptionWarfareModule,
    RedTeamModule,
    MetricsModule,
    TimelineModule,
    OutcomesModule,
)

__version__ = "1.0.0"
__author__ = "Django State Engine Team"

__all__ = [
    # Main engine
    "DjangoStateEngine",
    
    # Schemas
    "StateVector",
    "StateDimension",
    "Event",
    "EventType",
    "BetrayalEvent",
    "CooperationEvent",
    "InstitutionalFailureEvent",
    "ManipulationEvent",
    "RedTeamEvent",
    "EngineConfig",
    "IrreversibilityConfig",
    "OutcomeThresholds",
    
    # Kernel
    "RealityClock",
    "CausalEvent",
    "IrreversibilityLaws",
    "CollapseScheduler",
    
    # Modules
    "HumanForcesModule",
    "InstitutionalPressureModule",
    "PerceptionWarfareModule",
    "RedTeamModule",
    "MetricsModule",
    "TimelineModule",
    "OutcomesModule",
]
