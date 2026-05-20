"""
Asymmetric Security — multi-dimensional entropy-based access enforcement.

Components:
- SecurityContext: per-request descriptor with dimensional entropy payload
- OperationalState: system health enum
- RFICalculator: Reuse Friction Index from dimensional entropy sums
- AdversarialProber: LRU failure registry with friction multiplier tiers
- DimensionEntropyGuard: per-dimension minimum entropy validator
- SecurityEnforcementGateway: unified enforcement facade
"""

from __future__ import annotations

import time
from collections import OrderedDict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SecurityViolationError(Exception):
    pass


@dataclass
class SecurityContext:
    user_id: str
    action: str
    tenant_id: str = "default"
    auth_proof: Any = None
    dimensions: dict[str, float] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


class OperationalState(Enum):
    NORMAL = "normal"
    DEGRADED = "degraded"
    LOCKED = "locked"
    HALTED = "halted"


class RFICalculator:
    """Reuse Friction Index: 1 − 2^(−Σ positive entropy dimensions)."""

    def calculate(self, ctx: SecurityContext) -> float:
        total = sum(v for v in ctx.dimensions.values() if v > 0)
        if total == 0:
            return 0.0
        return 1.0 - 2.0 ** (-total)


class AdversarialProber:
    """Tracks per-source failure counts with LRU eviction and time-based cleanup."""

    _CLEANUP_INTERVAL = 3600.0
    _FRICTION_MEDIUM_THRESHOLD = 4
    _FRICTION_HIGH_THRESHOLD = 12

    def __init__(self, max_registry_size: int = 10_000) -> None:
        self.max_registry_size = max_registry_size
        self.probe_registry: OrderedDict[str, int] = OrderedDict()
        self.last_cleanup: float = time.monotonic()

    def record_attempt(self, source: str, success: bool) -> None:
        self._maybe_cleanup()
        if success:
            if source in self.probe_registry:
                self.probe_registry[source] -= 1
                if self.probe_registry[source] <= 0:
                    del self.probe_registry[source]
        else:
            if source in self.probe_registry:
                self.probe_registry[source] += 1
            else:
                if len(self.probe_registry) >= self.max_registry_size:
                    self.probe_registry.popitem(last=False)
                self.probe_registry[source] = 1

    def get_friction_multiplier(self, source: str) -> float:
        count = self.probe_registry.get(source, 0)
        if count >= self._FRICTION_HIGH_THRESHOLD:
            return 2.0
        if count >= self._FRICTION_MEDIUM_THRESHOLD:
            return 1.25
        return 1.0

    def _maybe_cleanup(self) -> None:
        now = time.monotonic()
        if now - self.last_cleanup < self._CLEANUP_INTERVAL:
            return
        stale = [k for k, v in self.probe_registry.items() if v <= 0]
        for k in stale:
            del self.probe_registry[k]
        self.last_cleanup = now


class DimensionEntropyGuard:
    """Rejects contexts where any dimension falls below the minimum entropy floor."""

    MIN_ENTROPY_PER_DIMENSION = 3.0

    def validate(self, ctx: SecurityContext) -> None:
        for dim_name, value in ctx.dimensions.items():
            if value < self.MIN_ENTROPY_PER_DIMENSION:
                raise SecurityViolationError(
                    f"Dimension '{dim_name}' does not meet entropy requirement: "
                    f"{value:.2f} < {self.MIN_ENTROPY_PER_DIMENSION}"
                )


class SecurityEnforcementGateway:
    """Orchestrates entropy validation, RFI checks, and adversarial friction."""

    _DEFAULT_DIMENSIONS: dict[str, float] = {
        "identity": 5.0,
        "spatial": 5.0,
        "temporal": 5.0,
    }

    def __init__(self, data_dir: str | None = None) -> None:
        self.data_dir = data_dir
        self.rfi_calculator = RFICalculator()
        self.prober = AdversarialProber()
        self._entropy_guard = DimensionEntropyGuard()
        self.rfi_thresholds: dict[str, float] = {
            "default": 0.80,
            "delete_user_data": 0.95,
            "admin": 0.90,
        }

    def _populate_dimensions(self, ctx: SecurityContext) -> None:
        if not ctx.dimensions:
            ctx.dimensions.update(self._DEFAULT_DIMENSIONS)

    def validate_and_enforce(self, ctx: SecurityContext) -> tuple[bool, str]:
        self._populate_dimensions(ctx)

        try:
            self._entropy_guard.validate(ctx)
        except SecurityViolationError as exc:
            self.prober.record_attempt(ctx.user_id, success=False)
            return False, str(exc)

        rfi = self.rfi_calculator.calculate(ctx)
        threshold = self.rfi_thresholds.get(ctx.action, self.rfi_thresholds["default"])
        friction = self.prober.get_friction_multiplier(ctx.user_id)
        required = min(threshold * friction, 0.9999)

        if rfi < required:
            self.prober.record_attempt(ctx.user_id, success=False)
            return False, f"Insufficient RFI: {rfi:.4f} < {required:.4f}"

        self.prober.record_attempt(ctx.user_id, success=True)
        return True, "SUCCESS"
