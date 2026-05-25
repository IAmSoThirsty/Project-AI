"""PSIA autoimmune dampener — sensitivity adjustment, false positive tracking."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class DampenerStats:
    rule_id: str
    total_decisions: int = 0
    false_positives: int = 0
    current_sensitivity: float = 1.0
    events_since_last_adjust: int = field(default=0, repr=False)

    @property
    def false_positive_rate(self) -> float:
        if self.total_decisions == 0:
            return 0.0
        return self.false_positives / self.total_decisions


class AutoimmuneDampener:
    def __init__(
        self,
        target_fp_rate: float = 0.05,
        min_sensitivity: float = 0.1,
        max_sensitivity: float = 1.0,
        cooldown_decisions: int = 10,
        adjustment_step: float = 0.1,
        enabled: bool = True,
        on_adjustment: Callable[[Any], None] | None = None,
    ) -> None:
        self._target_fp_rate = target_fp_rate
        self._min_sensitivity = min_sensitivity
        self._max_sensitivity = max_sensitivity
        self._cooldown = cooldown_decisions
        self._adjustment_step = adjustment_step
        self._enabled = enabled
        self._on_adjustment = on_adjustment
        self._rules: dict[str, DampenerStats] = {}

    def _ensure(self, rule_id: str) -> DampenerStats:
        if rule_id not in self._rules:
            self._rules[rule_id] = DampenerStats(
                rule_id=rule_id,
                current_sensitivity=self._max_sensitivity,
            )
        return self._rules[rule_id]

    def _maybe_adjust(self, rule_id: str) -> None:
        if not self._enabled:
            return
        stats = self._rules[rule_id]
        if stats.events_since_last_adjust < self._cooldown:
            return
        stats.events_since_last_adjust = 0
        fp_rate = stats.false_positive_rate
        if fp_rate > self._target_fp_rate:
            new_sensitivity = max(self._min_sensitivity, stats.current_sensitivity - self._adjustment_step)
        else:
            new_sensitivity = min(self._max_sensitivity, stats.current_sensitivity + self._adjustment_step)
        if new_sensitivity != stats.current_sensitivity:
            old_sensitivity = stats.current_sensitivity
            stats.current_sensitivity = new_sensitivity
            if self._on_adjustment is not None:
                self._on_adjustment({
                    "rule_id": rule_id,
                    "old_sensitivity": old_sensitivity,
                    "new_sensitivity": new_sensitivity,
                    "fp_rate": fp_rate,
                })

    def record_decision(self, rule_id: str, denied: bool = True) -> None:
        if not denied:
            return
        stats = self._ensure(rule_id)
        stats.total_decisions += 1
        stats.events_since_last_adjust += 1
        self._maybe_adjust(rule_id)

    def record_false_positive(self, rule_id: str) -> None:
        if rule_id not in self._rules:
            return
        stats = self._rules[rule_id]
        stats.false_positives += 1
        stats.events_since_last_adjust += 1
        self._maybe_adjust(rule_id)

    def should_apply_rule(self, rule_id: str, score: float) -> bool:
        return score * self.get_sensitivity(rule_id) >= 0.5

    def get_sensitivity(self, rule_id: str) -> float:
        if not self._enabled:
            return self._max_sensitivity
        if rule_id not in self._rules:
            return self._max_sensitivity
        return self._rules[rule_id].current_sensitivity

    def get_stats(self, rule_id: str) -> DampenerStats:
        if rule_id not in self._rules:
            return DampenerStats(rule_id=rule_id, current_sensitivity=self._max_sensitivity)
        return self._rules[rule_id]

    def get_all_stats(self) -> dict[str, DampenerStats]:
        return dict(self._rules)

    @property
    def tracked_rules(self) -> list[str]:
        return list(self._rules.keys())

    def reset_rule(self, rule_id: str) -> None:
        self._rules.pop(rule_id, None)
