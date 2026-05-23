from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import numpy as np

__all__ = ["EntropyState", "EntropySnapshot", "EntropySlopeMonitor"]

# ── completion convergence ────────────────────────────────────────────────────
_COMPLETION_MIN_YEARS: float = 10.0
_COMPLETION_SLOPE_PER_YEAR: float = 0.005   # max annual drift to call "complete"
_COMPLETION_RESIDUAL_STD: float = 0.05       # max residual σ; above → "Poor fit"

# ── creep detection ───────────────────────────────────────────────────────────
_CREEP_WINDOW_DAYS: int = 90                 # look-back window for recency
_CREEP_MIN_SPAN_DAYS: float = 7.0            # minimum span to assess a trend
_CREEP_MIN_POINTS: int = 5                   # minimum recent points
_CREEP_SLOPE_PER_DAY: float = 0.001          # threshold: below → "below creep threshold"
_CREEP_SLOPE_EPSILON: float = 1e-10          # treat slopes ≤ this as zero

# ── collapse / converging ─────────────────────────────────────────────────────
_COLLAPSE_FRACTION: float = 0.5             # current < fraction*baseline → collapsed
_CONVERGING_SLOPE_PER_YEAR: float = 0.05    # stable but not yet complete


class EntropyState(Enum):
    COLLAPSED = "COLLAPSED"
    COMPLETE = "COMPLETE"
    CREEPING = "CREEPING"
    CONVERGING = "CONVERGING"
    NORMAL = "NORMAL"


@dataclass
class EntropySnapshot:
    timestamp: float
    entropy_value: float
    source: str
    ledger_hash: str

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "entropy_value": self.entropy_value,
            "source": self.source,
            "ledger_hash": self.ledger_hash,
        }


class EntropySlopeMonitor:
    """Ledger-backed entropy monitor. Fully stateless beyond init-time constants."""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        genesis_path = self.data_dir / "genesis_seal.bin"
        if not genesis_path.exists():
            genesis_path.write_bytes(os.urandom(32))

        genesis_bytes = genesis_path.read_bytes()
        self.oracle_seed = hashlib.sha256(genesis_bytes + b"ORACLE_SEED").hexdigest()

        # Full 256-bit hash: an exact-zero baseline is cryptographically negligible,
        # not realistically reachable (not a hard guarantee).
        baseline_raw = hashlib.sha256(genesis_bytes + b"BASELINE").hexdigest()
        self.baseline_entropy = int(baseline_raw, 16) / (2**256 - 1)

        self.entropy_ledger_path = self.data_dir / "entropy_ledger.jsonl"

    # ── ledger I/O ────────────────────────────────────────────────────────────

    def record_entropy_snapshot(
        self, entropy_value: float, source: str, ledger_state: dict
    ) -> None:
        record: dict = {
            "timestamp": time.time(),
            "entropy_value": entropy_value,
            "source": source,
            "ledger_state": ledger_state,
        }
        ledger_hash = hashlib.sha256(
            json.dumps(record, sort_keys=True).encode("utf-8")
        ).hexdigest()
        record["ledger_hash"] = ledger_hash

        with open(self.entropy_ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def load_entropy_snapshots(
        self,
        start_time: float | None = None,
        end_time: float | None = None,
    ) -> list[EntropySnapshot]:
        if not self.entropy_ledger_path.exists():
            return []

        snapshots: list[EntropySnapshot] = []
        with open(self.entropy_ledger_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    # Skip corrupted lines (e.g. from a crash mid-write)
                    continue
                ts = float(data["timestamp"])
                if start_time is not None and ts < start_time:
                    continue
                if end_time is not None and ts > end_time:
                    continue
                snapshots.append(
                    EntropySnapshot(
                        timestamp=ts,
                        entropy_value=float(data["entropy_value"]),
                        source=str(data["source"]),
                        ledger_hash=str(data.get("ledger_hash", "")),
                    )
                )
        return snapshots

    # ── slope regression ──────────────────────────────────────────────────────

    def compute_entropy_slope(
        self, snapshots: list[EntropySnapshot]
    ) -> tuple[float, float]:
        if len(snapshots) < 2:
            return 0.0, 0.0

        # Sort by timestamp so x is always monotonically increasing from 0.
        ordered = sorted(snapshots, key=lambda s: s.timestamp)
        timestamps = np.array([s.timestamp for s in ordered])
        values = np.array([s.entropy_value for s in ordered])

        x = (timestamps - timestamps[0]) / 86400.0
        coeffs = np.polyfit(x, values, 1)
        slope = float(coeffs[0])

        y_pred = np.polyval(coeffs, x)
        ss_res = float(np.sum((values - y_pred) ** 2))
        ss_tot = float(np.sum((values - float(np.mean(values))) ** 2))

        if ss_tot == 0.0:
            r_squared = 1.0 if ss_res == 0.0 else 0.0
        else:
            r_squared = max(0.0, 1.0 - ss_res / ss_tot)

        return slope, r_squared

    # ── detector: completion convergence ──────────────────────────────────────

    def detect_completion_convergence(
        self, snapshots: list[EntropySnapshot]
    ) -> tuple[bool, dict]:
        if not snapshots:
            return False, {"reason": "No snapshots", "duration_years": 0.0}

        min_ts = min(s.timestamp for s in snapshots)
        max_ts = max(s.timestamp for s in snapshots)
        duration_years = (max_ts - min_ts) / 86400.0 / 365.25

        if duration_years < _COMPLETION_MIN_YEARS:
            return False, {
                "reason": "Insufficient duration",
                "duration_years": duration_years,
            }

        ordered = sorted(snapshots, key=lambda s: s.timestamp)
        timestamps = np.array([s.timestamp for s in ordered])
        values = np.array([s.entropy_value for s in ordered])
        x = (timestamps - timestamps[0]) / 86400.0
        coeffs = np.polyfit(x, values, 1)
        slope = float(coeffs[0])
        y_pred = np.polyval(coeffs, x)
        residuals = values - y_pred
        residual_std = float(np.std(residuals))

        if residual_std > _COMPLETION_RESIDUAL_STD:
            return False, {
                "reason": "Poor fit",
                "duration_years": duration_years,
                "residual_std": residual_std,
            }

        slope_per_year = abs(slope) * 365.25
        if slope_per_year > _COMPLETION_SLOPE_PER_YEAR:
            return False, {
                "reason": "Slope too high",
                "duration_years": duration_years,
                "slope_per_year": slope_per_year,
            }

        ss_res = float(np.sum(residuals**2))
        ss_tot = float(np.sum((values - float(np.mean(values))) ** 2))
        r_squared = max(0.0, 1.0 - ss_res / ss_tot) if ss_tot > 0.0 else 1.0

        return True, {
            "duration_years": duration_years,
            "slope": slope,
            "r_squared": r_squared,
        }

    # ── detector: entropy creep ───────────────────────────────────────────────

    def detect_entropy_creep(
        self, snapshots: list[EntropySnapshot]
    ) -> tuple[bool, dict]:
        now = time.time()
        cutoff = now - _CREEP_WINDOW_DAYS * 86400.0
        recent = [s for s in snapshots if s.timestamp >= cutoff]

        recent_span_days = (
            (max(s.timestamp for s in recent) - min(s.timestamp for s in recent))
            / 86400.0
            if recent
            else 0.0
        )
        if len(recent) < _CREEP_MIN_POINTS or recent_span_days < _CREEP_MIN_SPAN_DAYS:
            return False, {"reason": "Insufficient recent data"}

        raw_slope, _ = self.compute_entropy_slope(recent)
        # Clamp floating-point noise to zero so metadata is honest.
        slope = 0.0 if abs(raw_slope) <= _CREEP_SLOPE_EPSILON else raw_slope

        if slope <= 0.0:
            return False, {"reason": "Entropy not increasing", "slope": slope}

        if slope < _CREEP_SLOPE_PER_DAY:
            return False, {"reason": "Slope below creep threshold", "slope": slope}

        return True, {"slope": slope, "is_creeping": True}

    # ── detector: entropy collapse ────────────────────────────────────────────

    def detect_entropy_collapse(
        self, snapshots: list[EntropySnapshot]
    ) -> tuple[bool, dict]:
        if not snapshots:
            return False, {"reason": "No snapshots"}

        latest = max(snapshots, key=lambda s: s.timestamp)
        current_entropy = latest.entropy_value
        threshold = self.baseline_entropy * _COLLAPSE_FRACTION

        if current_entropy < threshold:
            return True, {"current_entropy": current_entropy}

        return False, {
            "reason": "Entropy above collapse threshold",
            "current_entropy": current_entropy,
        }

    # ── state classification ──────────────────────────────────────────────────

    def get_entropy_state(
        self, snapshots: list[EntropySnapshot] | None = None
    ) -> tuple[EntropyState, dict]:
        if snapshots is None:
            snapshots = self.load_entropy_snapshots()

        if not snapshots:
            return EntropyState.NORMAL, {"reason": "No snapshots"}

        is_collapsed, collapse_meta = self.detect_entropy_collapse(snapshots)
        if is_collapsed:
            return EntropyState.COLLAPSED, collapse_meta

        is_complete, completion_meta = self.detect_completion_convergence(snapshots)
        if is_complete:
            return EntropyState.COMPLETE, completion_meta

        is_creeping, creep_meta = self.detect_entropy_creep(snapshots)
        if is_creeping:
            return EntropyState.CREEPING, creep_meta

        if len(snapshots) >= _CREEP_MIN_POINTS:
            slope, _ = self.compute_entropy_slope(snapshots)
            if abs(slope) * 365.25 < _CONVERGING_SLOPE_PER_YEAR:
                return EntropyState.CONVERGING, {"slope": slope}

        return EntropyState.NORMAL, {}

    # ── composite metrics ─────────────────────────────────────────────────────

    def compute_dual_baseline_metrics(
        self, snapshots: list[EntropySnapshot]
    ) -> dict:
        if not snapshots:
            return {
                "error": "No snapshots",
                "oracle_seed": self.oracle_seed,
                "baseline_entropy": self.baseline_entropy,
            }

        is_complete, completion_meta = self.detect_completion_convergence(snapshots)
        completion_meta["is_complete"] = is_complete

        is_creeping, creep_meta = self.detect_entropy_creep(snapshots)
        creep_meta["is_creeping"] = is_creeping

        is_collapsed, collapse_meta = self.detect_entropy_collapse(snapshots)
        collapse_meta["is_collapsed"] = is_collapsed

        # Derive state from already-computed booleans to avoid re-running every
        # detector a second time through get_entropy_state.
        if is_collapsed:
            state = EntropyState.COLLAPSED
        elif is_complete:
            state = EntropyState.COMPLETE
        elif is_creeping:
            state = EntropyState.CREEPING
        elif len(snapshots) >= _CREEP_MIN_POINTS:
            slope, _ = self.compute_entropy_slope(snapshots)
            state = (
                EntropyState.CONVERGING
                if abs(slope) * 365.25 < _CONVERGING_SLOPE_PER_YEAR
                else EntropyState.NORMAL
            )
        else:
            state = EntropyState.NORMAL

        return {
            "oracle_seed": self.oracle_seed,
            "baseline_entropy": self.baseline_entropy,
            "current_state": state.value,
            "completion": completion_meta,
            "creep": creep_meta,
            "collapse": collapse_meta,
        }
