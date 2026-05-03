"""NIRL — Nested Intention-Response Loop.

Four-component reactive state machine cascade implementing the biological
immune-system analogy from the NIRL specification paper.

Components (in dependency order):
  Heart     — global tick engine; spawns probe skeletons, monitors heartbeats
  MiniBrain — per-section controller; spawns Antibodies, validates templates
  Antibody  — single-lifecycle escort unit; seals and routes payloads to Forge
  Forge     — purification + destruction engine; atomic verification and sign-off
"""

from .antibody import Antibody, AntibodyState
from .forge import Forge, ForgeState
from .heart import Heart, HeartState
from .mini_brain import MiniBrain, MiniBrainState

__all__ = [
    "Antibody",
    "AntibodyState",
    "Forge",
    "ForgeState",
    "Heart",
    "HeartState",
    "MiniBrain",
    "MiniBrainState",
]
