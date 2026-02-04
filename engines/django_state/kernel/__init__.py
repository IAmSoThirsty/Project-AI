"""Django State Engine Kernel.

Core physics engine implementing irreversibility laws and state evolution.
"""

from .state_vector import StateVector
from .reality_clock import RealityClock, CausalEvent
from .irreversibility_laws import IrreversibilityLaws
from .collapse_scheduler import CollapseScheduler

__all__ = [
    "StateVector",
    "RealityClock",
    "CausalEvent",
    "IrreversibilityLaws",
    "CollapseScheduler",
]
