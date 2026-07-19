"""Project-AI Shadow-Thirst (6th tier) convergence harness public interface."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

from convergence.shadow_thirst import (
    ConvergenceError,
    ConvergenceReport,
    TierWitness,
    run_convergence,
)

try:
    __version__ = _pkg_version("project-ai-convergence")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0.dev0"

__all__ = [
    "ConvergenceError",
    "ConvergenceReport",
    "TierWitness",
    "run_convergence",
]
