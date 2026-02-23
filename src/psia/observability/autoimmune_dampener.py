"""
Autoimmune Dampener — False Positive Suppression.

Prevents the immune system (PSIA) from over-reacting to benign
anomalies by tracking false positive rates and dynamically adjusting
sensitivity thresholds.

This solves the "autoimmune disease" problem: an overly aggressive
security system that blocks legitimate operations.

Mechanisms:
    - Per-rule tracking of deny decisions vs manual overrides
    - Dynamic threshold adjustment based on false positive rates
    - Cooldown periods after sensitivity changes
    - Sensitivity bounds (never drops below minimum or exceeds maximum)

Security invariants:
    - Dampening is bounded: sensitivity can never drop below minimum
    - All threshold changes are audited
    - Manual overrides always take precedence
    - Dampening can be globally disabled

Production notes:
    - In production, false positive data would be fed back from
      user complaints, support tickets, or admin overrides
    - Machine learning could replace the heuristic dampener
    - A/B testing would validate threshold changes
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable

logger = logging.getLogger(__name__)


@dataclass
class SensitivityAdjustment:
    """Record of a sensitivity change."""
    rule_id: str
    old_sensitivity: float
    new_sensitivity: float
    reason: str
    timestamp: str


@dataclass
class DampenerStats:
    """Statistics for a single rule."""
    rule_id: str
    total_decisions: int
    false_positives: int
    false_positive_rate: float
    current_sensitivity: float
    adjustments: int


class AutoimmuneDampener:
    """Dynamically adjusts PSIA sensitivity to suppress false positives.

    For each security rule, tracks:
    - Total deny decisions
    - False positive reports (overrides)
    - Current sensitivity multiplier

    When the false positive rate exceeds the target, sensitivity
    is reduced (dampened). When it drops below, sensitivity is
    restored toward the baseline.

    Args:
        target_fp_rate: Target false positive rate (default 0.05 = 5%)
        min_sensitivity: Minimum sensitivity multiplier (never go below)
        max_sensitivity: Maximum sensitivity multiplier (starting point)
        adjustment_step: How much to adjust per cycle
        cooldown_decisions: Decisions between adjustments
        enabled: Whether dampening is active
        on_adjustment: Callback for sensitivity changes
    """

    def __init__(
        self,
        *,
        target_fp_rate: float = 0.05,
        min_sensitivity: float = 0.3,
        max_sensitivity: float = 1.0,
        adjustment_step: float = 0.05,
        cooldown_decisions: int = 10,
        enabled: bool = True,
        on_adjustment: Callable[[SensitivityAdjustment], None] | None = None,
    ) -> None:
        self.target_fp_rate = target_fp_rate
        self.min_sensitivity = min_sensitivity
        self.max_sensitivity = max_sensitivity
        self.adjustment_step = adjustment_step
        self.cooldown_decisions = cooldown_decisions
        self.enabled = enabled
        self.on_adjustment = on_adjustment

        # Per-rule state
        self._total: dict[str, int] = {}
        self._false_positives: dict[str, int] = {}
        self._sensitivity: dict[str, float] = {}
        self._decisions_since_adjust: dict[str, int] = {}
        self._adjustments: list[SensitivityAdjustment] = []

    def record_decision(self, rule_id: str, *, denied: bool = True) -> None:
        """Record that a rule produced a deny decision.

        Args:
            rule_id: Identifier of the security rule
            denied: Whether the rule denied the request
        """
        if not denied:
            return
        self._ensure_rule(rule_id)
        self._total[rule_id] += 1
        self._decisions_since_adjust[rule_id] += 1
        self._maybe_adjust(rule_id)

    def record_false_positive(self, rule_id: str) -> None:
        """Record that a deny decision was a false positive (overridden).

        Args:
            rule_id: Identifier of the security rule
        """
        self._ensure_rule(rule_id)
        self._false_positives[rule_id] += 1
        self._decisions_since_adjust[rule_id] += 1
        self._maybe_adjust(rule_id)

    def get_sensitivity(self, rule_id: str) -> float:
        """Get the current sensitivity multiplier for a rule.

        Returns max_sensitivity for unknown rules (conservative default).
        """
        if not self.enabled:
            return self.max_sensitivity
        return self._sensitivity.get(rule_id, self.max_sensitivity)

    def should_apply_rule(self, rule_id: str, base_score: float) -> bool:
        """Check if a rule should fire given its dampened sensitivity.

        Args:
            rule_id: The security rule
            base_score: The raw anomaly score (0.0–1.0)

        Returns:
            True if the dampened score exceeds the threshold
        """
        sensitivity = self.get_sensitivity(rule_id)
        dampened_score = base_score * sensitivity
        return dampened_score >= 0.5  # Fixed threshold

    def get_stats(self, rule_id: str) -> DampenerStats:
        """Get statistics for a specific rule."""
        self._ensure_rule(rule_id)
        total = self._total[rule_id]
        fp = self._false_positives[rule_id]
        return DampenerStats(
            rule_id=rule_id,
            total_decisions=total,
            false_positives=fp,
            false_positive_rate=fp / total if total > 0 else 0.0,
            current_sensitivity=self._sensitivity[rule_id],
            adjustments=sum(1 for a in self._adjustments if a.rule_id == rule_id),
        )

    def get_all_stats(self) -> dict[str, DampenerStats]:
        """Get statistics for all tracked rules."""
        return {r: self.get_stats(r) for r in self._sensitivity}

    @property
    def adjustment_log(self) -> list[SensitivityAdjustment]:
        return list(self._adjustments)

    @property
    def tracked_rules(self) -> list[str]:
        return list(self._sensitivity.keys())

    def reset_rule(self, rule_id: str) -> None:
        """Reset tracking for a specific rule (admin action)."""
        self._total.pop(rule_id, None)
        self._false_positives.pop(rule_id, None)
        self._sensitivity.pop(rule_id, None)
        self._decisions_since_adjust.pop(rule_id, None)

    def _ensure_rule(self, rule_id: str) -> None:
        if rule_id not in self._sensitivity:
            self._total[rule_id] = 0
            self._false_positives[rule_id] = 0
            self._sensitivity[rule_id] = self.max_sensitivity
            self._decisions_since_adjust[rule_id] = 0

    def _maybe_adjust(self, rule_id: str) -> None:
        """Check if enough decisions have passed to adjust sensitivity."""
        if not self.enabled:
            return
        if self._decisions_since_adjust[rule_id] < self.cooldown_decisions:
            return

        self._decisions_since_adjust[rule_id] = 0
        total = self._total[rule_id]
        if total == 0:
            return

        fp_rate = self._false_positives[rule_id] / total
        old_sensitivity = self._sensitivity[rule_id]

        if fp_rate > self.target_fp_rate:
            # Too many false positives — reduce sensitivity
            new_sensitivity = max(
                self.min_sensitivity,
                old_sensitivity - self.adjustment_step,
            )
        elif fp_rate < self.target_fp_rate * 0.5:
            # Very few false positives — can increase sensitivity
            new_sensitivity = min(
                self.max_sensitivity,
                old_sensitivity + self.adjustment_step,
            )
        else:
            return  # In acceptable range

        if new_sensitivity == old_sensitivity:
            return

        self._sensitivity[rule_id] = new_sensitivity

        adjustment = SensitivityAdjustment(
            rule_id=rule_id,
            old_sensitivity=old_sensitivity,
            new_sensitivity=new_sensitivity,
            reason=f"FP rate {fp_rate:.3f} vs target {self.target_fp_rate:.3f}",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self._adjustments.append(adjustment)

        logger.info(
            "Sensitivity adjusted for %s: %.2f → %.2f (FP rate: %.3f)",
            rule_id, old_sensitivity, new_sensitivity, fp_rate,
        )

        if self.on_adjustment:
            self.on_adjustment(adjustment)


__all__ = [
    "AutoimmuneDampener",
    "SensitivityAdjustment",
    "DampenerStats",
]
