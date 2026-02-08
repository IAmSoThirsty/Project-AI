"""Metrics module.

Real-time state tracking and metrics calculation.
"""

import logging
from typing import Any

from ..schemas.state_schema import StateVector

logger = logging.getLogger(__name__)


class MetricsModule:
    """Real-time metrics tracking and analysis.
    
    Calculates and tracks key performance indicators, trends, and anomalies.
    """

    def __init__(self):
        """Initialize metrics module."""
        self.metrics_history: list[dict[str, Any]] = []

        # Trend tracking
        self.trust_trend: list[float] = []
        self.legitimacy_trend: list[float] = []
        self.kindness_trend: list[float] = []
        self.moral_injury_trend: list[float] = []
        self.epistemic_trend: list[float] = []

        # Anomaly detection
        self.anomalies_detected: list[dict[str, Any]] = []

        logger.info("Metrics module initialized")

    def calculate_current_metrics(self, state: StateVector) -> dict[str, Any]:
        """Calculate all current metrics from state.
        
        Args:
            state: Current state vector
            
        Returns:
            Dictionary of metrics
        """
        metrics = {
            "timestamp": state.timestamp,
            "tick": state.tick_count,

            # Primary dimensions
            "trust": state.trust.value,
            "legitimacy": state.legitimacy.value,
            "kindness": state.kindness.value,
            "moral_injury": state.moral_injury.value,
            "epistemic_confidence": state.epistemic_confidence.value,

            # Ceilings and floors (irreversibility indicators)
            "trust_ceiling": state.trust.ceiling,
            "legitimacy_ceiling": state.legitimacy.ceiling,
            "moral_injury_floor": state.moral_injury.floor,

            # Derived metrics
            "social_cohesion": state.social_cohesion,
            "governance_capacity": state.governance_capacity,
            "reality_consensus": state.reality_consensus,

            # Counters
            "betrayal_count": state.betrayal_count,
            "cooperation_count": state.cooperation_count,
            "broken_promises": state.broken_promises,
            "institutional_failures": state.institutional_failures,
            "manipulation_events": state.manipulation_events,

            # Collapse indicators
            "in_collapse": state.in_collapse,
            "collapse_triggered_at": state.collapse_triggered_at,

            # Composite health score (0 to 100)
            "system_health": self._calculate_system_health(state),

            # Risk score (0 to 100)
            "collapse_risk": self._calculate_collapse_risk(state),
        }

        # Record history
        self.metrics_history.append(metrics)

        # Update trends
        self.trust_trend.append(state.trust.value)
        self.legitimacy_trend.append(state.legitimacy.value)
        self.kindness_trend.append(state.kindness.value)
        self.moral_injury_trend.append(state.moral_injury.value)
        self.epistemic_trend.append(state.epistemic_confidence.value)

        # Check for anomalies
        self._detect_anomalies(state, metrics)

        return metrics

    def _calculate_system_health(self, state: StateVector) -> float:
        """Calculate overall system health score.
        
        Args:
            state: Current state vector
            
        Returns:
            Health score (0 to 100)
        """
        # Weighted average of positive indicators
        health = (
            state.trust.value * 25 +
            state.legitimacy.value * 20 +
            state.kindness.value * 20 +
            (1.0 - state.moral_injury.value) * 15 +
            state.epistemic_confidence.value * 20
        )

        # Penalize if in collapse
        if state.in_collapse:
            health *= 0.5

        return health

    def _calculate_collapse_risk(self, state: StateVector) -> float:
        """Calculate risk of imminent collapse.
        
        Args:
            state: Current state vector
            
        Returns:
            Risk score (0 to 100)
        """
        risk = 0.0

        # Distance from collapse thresholds
        if state.kindness.value < 0.3:
            risk += (0.3 - state.kindness.value) * 50

        if state.trust.value < 0.25:
            risk += (0.25 - state.trust.value) * 40

        if state.legitimacy.value < 0.2:
            risk += (0.2 - state.legitimacy.value) * 50

        if state.moral_injury.value > 0.7:
            risk += (state.moral_injury.value - 0.7) * 30

        if state.epistemic_confidence.value < 0.3:
            risk += (0.3 - state.epistemic_confidence.value) * 35

        # Already in collapse = maximum risk
        if state.in_collapse:
            risk = 100.0

        return min(risk, 100.0)

    def _detect_anomalies(self, state: StateVector, metrics: dict[str, Any]) -> None:
        """Detect anomalous state changes.
        
        Args:
            state: Current state vector
            metrics: Current metrics
        """
        if len(self.metrics_history) < 5:
            return  # Need history for anomaly detection

        # Check for sudden drops
        recent = self.metrics_history[-5:]

        # Trust sudden drop
        if len(self.trust_trend) >= 2:
            trust_change = self.trust_trend[-1] - self.trust_trend[-2]
            if trust_change < -0.15:
                self.anomalies_detected.append({
                    "timestamp": state.timestamp,
                    "type": "sudden_trust_drop",
                    "magnitude": trust_change,
                })
                logger.warning("ANOMALY: Sudden trust drop %s", trust_change)

        # Legitimacy sudden drop
        if len(self.legitimacy_trend) >= 2:
            legitimacy_change = self.legitimacy_trend[-1] - self.legitimacy_trend[-2]
            if legitimacy_change < -0.12:
                self.anomalies_detected.append({
                    "timestamp": state.timestamp,
                    "type": "sudden_legitimacy_drop",
                    "magnitude": legitimacy_change,
                })
                logger.warning("ANOMALY: Sudden legitimacy drop %s", legitimacy_change)

        # Moral injury spike
        if len(self.moral_injury_trend) >= 2:
            moral_change = self.moral_injury_trend[-1] - self.moral_injury_trend[-2]
            if moral_change > 0.1:
                self.anomalies_detected.append({
                    "timestamp": state.timestamp,
                    "type": "moral_injury_spike",
                    "magnitude": moral_change,
                })
                logger.warning("ANOMALY: Moral injury spike %s", moral_change)

    def get_trend_analysis(self, window: int = 20) -> dict[str, str]:
        """Analyze trends over recent window.
        
        Args:
            window: Number of recent ticks to analyze
            
        Returns:
            Dictionary of trend directions
        """
        def analyze_trend(data: list[float]) -> str:
            if len(data) < window:
                return "insufficient_data"

            recent = data[-window:]
            first_half = sum(recent[:window//2]) / (window//2)
            second_half = sum(recent[window//2:]) / (window - window//2)

            diff = second_half - first_half

            if diff > 0.05:
                return "improving"
            elif diff < -0.05:
                return "degrading"
            else:
                return "stable"

        return {
            "trust": analyze_trend(self.trust_trend),
            "legitimacy": analyze_trend(self.legitimacy_trend),
            "kindness": analyze_trend(self.kindness_trend),
            "moral_injury": analyze_trend(self.moral_injury_trend),
            "epistemic_confidence": analyze_trend(self.epistemic_trend),
        }

    def get_summary(self) -> dict[str, Any]:
        """Get module summary.
        
        Returns:
            Dictionary with module state
        """
        if not self.metrics_history:
            return {"metrics_recorded": 0}

        current = self.metrics_history[-1]
        trends = self.get_trend_analysis()

        return {
            "metrics_recorded": len(self.metrics_history),
            "current_system_health": current.get("system_health", 0),
            "current_collapse_risk": current.get("collapse_risk", 0),
            "anomalies_detected": len(self.anomalies_detected),
            "trends": trends,
        }

    def export_metrics(self) -> list[dict[str, Any]]:
        """Export all metrics history.
        
        Returns:
            List of metrics dictionaries
        """
        return self.metrics_history.copy()

    def reset(self) -> None:
        """Reset module to initial state."""
        self.__init__()
        logger.info("Metrics module reset")
