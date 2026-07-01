"""Project-AI Shadow-Thirst (6th tier) convergence harness public interface."""

from convergence.shadow_thirst import (
    ConvergenceError,
    ConvergenceReport,
    TierWitness,
    run_convergence,
)

__version__ = "0.0.0.dev0"

__all__ = [
    "ConvergenceError",
    "ConvergenceReport",
    "TierWitness",
    "run_convergence",
]
