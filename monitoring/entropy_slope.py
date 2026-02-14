"""
Entropy Slope Monitor - Ledger-Driven Entropy Analysis

This module implements slope-based entropy monitoring for detecting completion
and creep patterns. All metrics are derived from the constitutional ledger with
ORACLE_SEED providing cryptographic anchoring.

Key Features:
- Slope calculation from ledger-derived entropy snapshots
- Dual-baseline detection (completion vs. creep)
- ORACLE_SEED derived from genesis seal (immutable)
- Zero internal state - all values computed from ledger
- Completion convergence detection (10-year criteria)
- Creep detection (slow entropy increase indicating drift)

No internal counters or accumulators - pure function evaluation from ledger state.
"""

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


class EntropyState(StrEnum):
    """Entropy monitoring states"""

    NORMAL = "normal"  # Within expected bounds
    CONVERGING = "converging"  # Approaching completion
    COMPLETE = "complete"  # Completion criteria met
    CREEPING = "creeping"  # Slow entropy increase (drift)
    COLLAPSED = "collapsed"  # Entropy collapse detected


@dataclass
class EntropySnapshot:
    """Single entropy measurement snapshot"""

    timestamp: float
    entropy_value: float
    source: str  # Source of entropy measurement
    ledger_hash: str  # Hash of ledger state at this measurement

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "timestamp": self.timestamp,
            "entropy_value": self.entropy_value,
            "source": self.source,
            "ledger_hash": self.ledger_hash,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EntropySnapshot":
        """Create from dictionary"""
        return cls(
            timestamp=data["timestamp"],
            entropy_value=data["entropy_value"],
            source=data["source"],
            ledger_hash=data["ledger_hash"],
        )


class EntropySlopeMonitor:
    """
    Entropy slope monitoring system with dual-baseline detection.

    This monitor tracks entropy over time using slope analysis to detect
    both completion (entropy stabilizing) and creep (entropy increasing).
    All state is derived from the ledger - no internal accumulators.
    """

    # Completion criteria: 10 years of stable entropy
    COMPLETION_CONVERGENCE_YEARS = 10
    COMPLETION_SLOPE_THRESHOLD = 0.01  # Max slope for completion
    COMPLETION_R_SQUARED_THRESHOLD = 0.8  # Min R-squared for good fit
    COMPLETION_BASELINE_DELTA_THRESHOLD = 0.1  # Max delta from baseline

    # Creep detection: gradual entropy increase
    CREEP_SLOPE_THRESHOLD = 0.1  # Min slope for creep detection
    CREEP_WINDOW_DAYS = 30  # Window for creep analysis
    CREEP_R_SQUARED_THRESHOLD = 0.6  # Min R-squared for sustained trend

    # Collapse detection: rapid entropy decrease
    COLLAPSE_THRESHOLD = 0.5  # Max ratio of current/baseline for collapse

    # Converging detection
    CONVERGING_WINDOW_SIZE = 100  # Number of recent snapshots for converging check

    def __init__(
        self,
        data_dir: Path | str = "governance/sovereign_data",
        oracle_seed: str | None = None,
    ):
        """
        Initialize Entropy Slope Monitor.

        Args:
            data_dir: Directory for entropy ledger
            oracle_seed: ORACLE_SEED from genesis seal (immutable)
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.entropy_ledger_path = self.data_dir / "entropy_snapshots.jsonl"

        # Derive or load ORACLE_SEED
        if oracle_seed is None:
            oracle_seed = self._load_oracle_seed()
        self.oracle_seed = oracle_seed

        # Compute baseline entropy from ORACLE_SEED
        self.baseline_entropy = self._compute_baseline_entropy()

        logger.info(
            "EntropySlopeMonitor initialized with ORACLE_SEED: %s..., baseline: %.4f",
            self.oracle_seed[:16],
            self.baseline_entropy,
        )

    def _load_oracle_seed(self) -> str:
        """Load ORACLE_SEED from genesis seal"""
        genesis_path = self.data_dir / "genesis_seal.bin"
        if genesis_path.exists():
            with open(genesis_path, "rb") as f:
                genesis_seal = f.read()
            # Derive ORACLE_SEED same way as SingularityOverride
            oracle_data = genesis_seal + b"ORACLE_SEED"
            return hashlib.sha256(oracle_data).hexdigest()
        else:
            # Create new genesis seal
            genesis_data = {
                "created_at": datetime.now().isoformat(),
                "version": "1.0.0",
                "system": "Project-AI Entropy Monitor",
            }
            genesis_seal = hashlib.sha256(
                json.dumps(genesis_data, sort_keys=True).encode()
            ).digest()

            with open(genesis_path, "wb") as f:
                f.write(genesis_seal)

            oracle_data = genesis_seal + b"ORACLE_SEED"
            return hashlib.sha256(oracle_data).hexdigest()

    def _compute_baseline_entropy(self) -> float:
        """
        Compute baseline entropy from ORACLE_SEED (immutable).

        The baseline is the expected entropy at genesis. All measurements
        are compared against this cryptographically-anchored baseline.

        Returns:
            Baseline entropy value
        """
        # Hash ORACLE_SEED with "BASELINE" tag
        baseline_data = (self.oracle_seed + "BASELINE").encode()
        baseline_hash = hashlib.sha256(baseline_data).digest()

        # Convert hash to entropy value (0.0 to 1.0 range)
        # Use first 8 bytes as uint64, normalize to [0, 1]
        entropy_int = int.from_bytes(baseline_hash[:8], byteorder="big")
        baseline = entropy_int / (2**64 - 1)

        return baseline

    def record_entropy_snapshot(
        self, entropy_value: float, source: str, ledger_state: dict[str, Any]
    ):
        """
        Record entropy snapshot to ledger.

        Args:
            entropy_value: Measured entropy value
            source: Source of measurement (e.g., "system", "user_actions", "model")
            ledger_state: Current constitutional ledger state
        """
        # Compute ledger state hash
        ledger_hash = hashlib.sha256(
            json.dumps(ledger_state, sort_keys=True).encode()
        ).hexdigest()

        snapshot = EntropySnapshot(
            timestamp=datetime.now().timestamp(),
            entropy_value=entropy_value,
            source=source,
            ledger_hash=ledger_hash,
        )

        with open(self.entropy_ledger_path, "a") as f:
            f.write(json.dumps(snapshot.to_dict()) + "\n")

        logger.debug(
            "Entropy snapshot recorded: value=%.4f, source=%s", entropy_value, source
        )

    def load_entropy_snapshots(
        self, start_time: float | None = None, end_time: float | None = None
    ) -> list[EntropySnapshot]:
        """
        Load entropy snapshots from ledger (stateless).

        Args:
            start_time: Optional start timestamp for filtering
            end_time: Optional end timestamp for filtering

        Returns:
            List of entropy snapshots in time range
        """
        if not self.entropy_ledger_path.exists():
            return []

        snapshots = []
        try:
            with open(self.entropy_ledger_path) as f:
                for line in f:
                    if line.strip():
                        snapshot_dict = json.loads(line)
                        snapshot = EntropySnapshot.from_dict(snapshot_dict)

                        # Apply time filtering
                        if start_time and snapshot.timestamp < start_time:
                            continue
                        if end_time and snapshot.timestamp > end_time:
                            continue

                        snapshots.append(snapshot)
        except Exception as e:
            logger.error("Failed to load entropy snapshots: %s", e)

        return snapshots

    def compute_entropy_slope(
        self, snapshots: list[EntropySnapshot]
    ) -> tuple[float, float]:
        """
        Compute entropy slope from snapshots using linear regression.

        Args:
            snapshots: List of entropy snapshots (time-ordered)

        Returns:
            Tuple of (slope, r_squared) where:
                - slope: Rate of entropy change per second
                - r_squared: Goodness of fit (0.0 to 1.0)
        """
        if len(snapshots) < 2:
            return 0.0, 0.0

        # Extract timestamps and values
        times = np.array([s.timestamp for s in snapshots])
        values = np.array([s.entropy_value for s in snapshots])

        # Normalize times to start at 0 for numerical stability
        times = times - times[0]

        # Linear regression: entropy = slope * time + intercept
        slope, intercept = np.polyfit(times, values, 1)

        # Compute R-squared
        predictions = slope * times + intercept
        ss_res = np.sum((values - predictions) ** 2)
        ss_tot = np.sum((values - np.mean(values)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

        return float(slope), float(r_squared)

    def detect_completion_convergence(
        self, snapshots: list[EntropySnapshot]
    ) -> tuple[bool, dict[str, Any]]:
        """
        Detect completion convergence (10-year stable entropy).

        Completion is detected when:
        1. Entropy has been stable (low slope) for 10 years
        2. R-squared indicates good fit (low noise)
        3. Entropy is near baseline

        Args:
            snapshots: List of entropy snapshots

        Returns:
            Tuple of (is_complete, metadata)
        """
        if len(snapshots) < 2:
            return False, {"reason": "Insufficient snapshots"}

        # Check if we have 10 years of data
        first_timestamp = snapshots[0].timestamp
        last_timestamp = snapshots[-1].timestamp
        duration_years = (last_timestamp - first_timestamp) / (
            365.25 * 24 * 3600
        )  # Convert seconds to years

        if duration_years < self.COMPLETION_CONVERGENCE_YEARS:
            return False, {
                "reason": "Insufficient duration",
                "duration_years": duration_years,
                "required_years": self.COMPLETION_CONVERGENCE_YEARS,
            }

        # Compute slope over full period
        slope, r_squared = self.compute_entropy_slope(snapshots)

        # Check slope threshold (near-zero slope = stable)
        if abs(slope) > self.COMPLETION_SLOPE_THRESHOLD:
            return False, {
                "reason": "Slope too high",
                "slope": slope,
                "threshold": self.COMPLETION_SLOPE_THRESHOLD,
            }

        # Check R-squared (good fit = low noise)
        if r_squared < self.COMPLETION_R_SQUARED_THRESHOLD:
            return False, {
                "reason": "Poor fit (high noise)",
                "r_squared": r_squared,
            }

        # Check proximity to baseline
        current_entropy = snapshots[-1].entropy_value
        baseline_delta = abs(current_entropy - self.baseline_entropy)

        if baseline_delta > self.COMPLETION_BASELINE_DELTA_THRESHOLD:
            return False, {
                "reason": "Not converged to baseline",
                "current_entropy": current_entropy,
                "baseline_entropy": self.baseline_entropy,
                "delta": baseline_delta,
            }

        # All criteria met - completion detected
        logger.info(
            "Completion convergence detected: duration=%.1f years, slope=%.6f, r²=%.3f",
            duration_years,
            slope,
            r_squared,
        )

        return True, {
            "duration_years": duration_years,
            "slope": slope,
            "r_squared": r_squared,
            "current_entropy": current_entropy,
            "baseline_entropy": self.baseline_entropy,
            "baseline_delta": baseline_delta,
        }

    def detect_entropy_creep(
        self, snapshots: list[EntropySnapshot]
    ) -> tuple[bool, dict[str, Any]]:
        """
        Detect entropy creep (slow increase indicating drift).

        Creep is detected when:
        1. Entropy is increasing (positive slope)
        2. Slope exceeds creep threshold
        3. Trend is sustained over window period

        Args:
            snapshots: List of entropy snapshots

        Returns:
            Tuple of (is_creeping, metadata)
        """
        if len(snapshots) < 2:
            return False, {"reason": "Insufficient snapshots"}

        # Filter to recent window
        window_start = datetime.now().timestamp() - (
            self.CREEP_WINDOW_DAYS * 24 * 3600
        )
        recent_snapshots = [s for s in snapshots if s.timestamp >= window_start]

        if len(recent_snapshots) < 2:
            return False, {"reason": "Insufficient recent snapshots"}

        # Compute slope over window
        slope, r_squared = self.compute_entropy_slope(recent_snapshots)

        # Check for positive slope (increasing entropy)
        if slope <= 0:
            return False, {
                "reason": "Entropy not increasing",
                "slope": slope,
            }

        # Check if slope exceeds creep threshold
        if slope < self.CREEP_SLOPE_THRESHOLD:
            return False, {
                "reason": "Slope below creep threshold",
                "slope": slope,
                "threshold": self.CREEP_SLOPE_THRESHOLD,
            }

        # Check for sustained trend (good fit)
        if r_squared < self.CREEP_R_SQUARED_THRESHOLD:
            return False, {
                "reason": "Trend not sustained (low R²)",
                "r_squared": r_squared,
            }

        # Creep detected
        logger.warning(
            "Entropy creep detected: slope=%.6f, r²=%.3f over %d days",
            slope,
            r_squared,
            self.CREEP_WINDOW_DAYS,
        )

        return True, {
            "slope": slope,
            "r_squared": r_squared,
            "window_days": self.CREEP_WINDOW_DAYS,
            "snapshot_count": len(recent_snapshots),
        }

    def detect_entropy_collapse(
        self, snapshots: list[EntropySnapshot]
    ) -> tuple[bool, dict[str, Any]]:
        """
        Detect entropy collapse (rapid decrease).

        Collapse is detected when current entropy falls below threshold
        percentage of baseline entropy.

        Args:
            snapshots: List of entropy snapshots

        Returns:
            Tuple of (is_collapsed, metadata)
        """
        if not snapshots:
            return False, {"reason": "No snapshots"}

        current_entropy = snapshots[-1].entropy_value

        # Check if current entropy is below collapse threshold
        if current_entropy >= (self.baseline_entropy * self.COLLAPSE_THRESHOLD):
            return False, {
                "reason": "Entropy above collapse threshold",
                "current_entropy": current_entropy,
                "baseline_entropy": self.baseline_entropy,
                "ratio": current_entropy / self.baseline_entropy,
            }

        # Collapse detected
        logger.critical(
            "Entropy collapse detected: current=%.4f, baseline=%.4f, ratio=%.2f%%",
            current_entropy,
            self.baseline_entropy,
            (current_entropy / self.baseline_entropy) * 100,
        )

        return True, {
            "current_entropy": current_entropy,
            "baseline_entropy": self.baseline_entropy,
            "ratio": current_entropy / self.baseline_entropy,
            "threshold": self.COLLAPSE_THRESHOLD,
        }

    def get_entropy_state(
        self, snapshots: list[EntropySnapshot] | None = None
    ) -> tuple[EntropyState, dict[str, Any]]:
        """
        Get current entropy state (ledger-derived, stateless).

        Args:
            snapshots: Optional list of snapshots (loads from ledger if None)

        Returns:
            Tuple of (state, metadata)
        """
        if snapshots is None:
            snapshots = self.load_entropy_snapshots()

        if not snapshots:
            return EntropyState.NORMAL, {"reason": "No snapshots"}

        # Check for collapse (highest priority)
        is_collapsed, collapse_meta = self.detect_entropy_collapse(snapshots)
        if is_collapsed:
            return EntropyState.COLLAPSED, collapse_meta

        # Check for completion convergence
        is_complete, complete_meta = self.detect_completion_convergence(snapshots)
        if is_complete:
            return EntropyState.COMPLETE, complete_meta

        # Check for creep
        is_creeping, creep_meta = self.detect_entropy_creep(snapshots)
        if is_creeping:
            return EntropyState.CREEPING, creep_meta

        # Check if converging (approaching completion)
        # This is a weaker version of completion check
        if len(snapshots) >= 2:
            slope, r_squared = self.compute_entropy_slope(
                snapshots[-self.CONVERGING_WINDOW_SIZE :]
            )  # Last N snapshots
            if abs(slope) < self.COMPLETION_SLOPE_THRESHOLD * 2 and r_squared > 0.5:
                return EntropyState.CONVERGING, {
                    "slope": slope,
                    "r_squared": r_squared,
                    "reason": "Entropy stabilizing",
                }

        # Default to normal
        return EntropyState.NORMAL, {
            "current_entropy": snapshots[-1].entropy_value,
            "baseline_entropy": self.baseline_entropy,
            "snapshot_count": len(snapshots),
        }

    def compute_dual_baseline_metrics(
        self, snapshots: list[EntropySnapshot] | None = None
    ) -> dict[str, Any]:
        """
        Compute dual-baseline metrics (completion vs. creep).

        This provides a comprehensive view of entropy trends using both
        completion (long-term stability) and creep (short-term drift) baselines.

        Args:
            snapshots: Optional list of snapshots (loads from ledger if None)

        Returns:
            Dictionary with dual-baseline metrics
        """
        if snapshots is None:
            snapshots = self.load_entropy_snapshots()

        if not snapshots:
            return {"error": "No snapshots available"}

        # Completion baseline (full history)
        is_complete, complete_meta = self.detect_completion_convergence(snapshots)

        # Creep baseline (recent window)
        is_creeping, creep_meta = self.detect_entropy_creep(snapshots)

        # Collapse check
        is_collapsed, collapse_meta = self.detect_entropy_collapse(snapshots)

        # Current state
        current_state, state_meta = self.get_entropy_state(snapshots)

        return {
            "oracle_seed": self.oracle_seed[:16] + "...",
            "baseline_entropy": self.baseline_entropy,
            "current_state": current_state.value,
            "state_metadata": state_meta,
            "completion": {
                "is_complete": is_complete,
                "metadata": complete_meta,
            },
            "creep": {
                "is_creeping": is_creeping,
                "metadata": creep_meta,
            },
            "collapse": {
                "is_collapsed": is_collapsed,
                "metadata": collapse_meta,
            },
            "snapshot_count": len(snapshots),
            "time_range": {
                "start": datetime.fromtimestamp(snapshots[0].timestamp).isoformat()
                if snapshots
                else None,
                "end": datetime.fromtimestamp(snapshots[-1].timestamp).isoformat()
                if snapshots
                else None,
            },
        }


__all__ = ["EntropySlopeMonitor", "EntropyState", "EntropySnapshot"]
