"""
Governance Drift Monitor - Detect when governance approvals trend looser over time.

Background job that analyzes governance decisions to detect drift in approval patterns.
This is critical for alignment safety - if governance becomes more permissive over time,
it could indicate a gradual erosion of safety constraints.

Uses the five-channel memory data to track governance trends.
"""

import json
import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class GovernanceDriftAlert:
    """An alert about detected governance drift."""

    def __init__(
        self,
        alert_type: str,
        severity: str,
        message: str,
        evidence: dict[str, Any],
    ):
        self.alert_type = alert_type
        self.severity = severity
        self.message = message
        self.evidence = evidence
        self.timestamp = datetime.now(UTC)

    def __repr__(self) -> str:
        return f"GovernanceDriftAlert({self.severity}: {self.message})"


class GovernanceDriftMonitor:
    """
    Monitor governance decisions for drift patterns.

    Detects:
    1. Increasing approval rates over time
    2. Decreasing consensus requirements
    3. Faster approval times (less deliberation)
    4. Approval of previously blocked action types
    5. Weakening of core value protections

    This is alignment-critical - governance drift can indicate:
    - Gradual erosion of safety constraints
    - Value drift
    - Optimization pressure overriding safety
    """

    def __init__(
        self,
        data_dir: str = "data",
        window_days: int = 30,
        alert_threshold: float = 0.15,
    ):
        """
        Initialize drift monitor.

        Args:
            data_dir: Directory where execution logs are stored
            window_days: Number of days for rolling window analysis
            alert_threshold: Percentage change to trigger alert (e.g., 0.15 = 15%)
        """
        self.data_dir = Path(data_dir)
        self.replay_dir = self.data_dir / "kernel_replays"
        self.window_days = window_days
        self.alert_threshold = alert_threshold

        self.alerts_dir = self.data_dir / "governance_drift_alerts"
        self.alerts_dir.mkdir(parents=True, exist_ok=True)

    def analyze_drift(self) -> dict[str, Any]:
        """
        Analyze governance decisions for drift patterns.

        Returns:
            Drift analysis with alerts if any
        """
        # Load all executions with governance decisions
        executions = self._load_governance_decisions()

        if not executions:
            return {
                "status": "no_data",
                "message": "No governance decisions found",
            }

        # Sort by timestamp
        executions.sort(key=lambda e: datetime.fromisoformat(e["timestamp"]))

        # Split into time windows
        now = datetime.now(UTC)
        cutoff = now - timedelta(days=self.window_days)

        recent = [
            e for e in executions if datetime.fromisoformat(e["timestamp"]) >= cutoff
        ]
        historical = [
            e for e in executions if datetime.fromisoformat(e["timestamp"]) < cutoff
        ]

        if not historical or not recent:
            return {
                "status": "insufficient_data",
                "message": "Need data from both recent and historical windows",
            }

        # Analyze different drift patterns
        alerts = []

        # 1. Approval rate drift
        approval_alert = self._detect_approval_rate_drift(historical, recent)
        if approval_alert:
            alerts.append(approval_alert)

        # 2. Consensus drift
        consensus_alert = self._detect_consensus_drift(historical, recent)
        if consensus_alert:
            alerts.append(consensus_alert)

        # 3. Risk level drift
        risk_alert = self._detect_risk_level_drift(historical, recent)
        if risk_alert:
            alerts.append(risk_alert)

        # 4. Core value protection drift
        core_value_alert = self._detect_core_value_drift(historical, recent)
        if core_value_alert:
            alerts.append(core_value_alert)

        # Save alerts
        if alerts:
            self._save_alerts(alerts)

        return {
            "status": "analyzed",
            "analysis_window_days": self.window_days,
            "historical_count": len(historical),
            "recent_count": len(recent),
            "alerts": [
                {
                    "type": a.alert_type,
                    "severity": a.severity,
                    "message": a.message,
                    "evidence": a.evidence,
                    "timestamp": a.timestamp.isoformat(),
                }
                for a in alerts
            ],
            "drift_detected": len(alerts) > 0,
        }

    def _load_governance_decisions(self) -> list[dict[str, Any]]:
        """Load all executions with governance decisions."""
        executions = []

        if not self.replay_dir.exists():
            return executions

        for filepath in self.replay_dir.glob("*.json"):
            try:
                with filepath.open() as f:
                    execution = json.load(f)

                # Only include if has governance decision
                if execution.get("governance_decision"):
                    executions.append(execution)

            except Exception as e:
                logger.warning("Failed to load %s: %s", filepath, e)

        return executions

    def _detect_approval_rate_drift(
        self, historical: list[dict[str, Any]], recent: list[dict[str, Any]]
    ) -> GovernanceDriftAlert | None:
        """Detect if approval rate is increasing."""
        hist_approvals = sum(
            1 for e in historical if e["governance_decision"]["approved"]
        )
        hist_rate = hist_approvals / len(historical) if historical else 0

        recent_approvals = sum(
            1 for e in recent if e["governance_decision"]["approved"]
        )
        recent_rate = recent_approvals / len(recent) if recent else 0

        drift = recent_rate - hist_rate

        if drift > self.alert_threshold:
            return GovernanceDriftAlert(
                alert_type="approval_rate_drift",
                severity="high",
                message=f"Approval rate increased by {drift * 100:.1f}% "
                f"(historical: {hist_rate * 100:.1f}%, recent: {recent_rate * 100:.1f}%)",
                evidence={
                    "historical_rate": hist_rate,
                    "recent_rate": recent_rate,
                    "drift_percentage": drift * 100,
                    "historical_sample_size": len(historical),
                    "recent_sample_size": len(recent),
                },
            )

        return None

    def _detect_consensus_drift(
        self, historical: list[dict[str, Any]], recent: list[dict[str, Any]]
    ) -> GovernanceDriftAlert | None:
        """Detect if consensus requirements are weakening."""
        hist_consensus_rate = (
            sum(
                1
                for e in historical
                if e["governance_decision"].get("consensus_achieved")
            )
            / len(historical)
            if historical
            else 0
        )

        recent_consensus_rate = (
            sum(1 for e in recent if e["governance_decision"].get("consensus_achieved"))
            / len(recent)
            if recent
            else 0
        )

        drift = hist_consensus_rate - recent_consensus_rate  # Note: inverted

        if drift > self.alert_threshold:
            return GovernanceDriftAlert(
                alert_type="consensus_drift",
                severity="critical",
                message=f"Consensus achievement decreased by {drift * 100:.1f}% "
                f"(historical: {hist_consensus_rate * 100:.1f}%, recent: {recent_consensus_rate * 100:.1f}%)",
                evidence={
                    "historical_consensus_rate": hist_consensus_rate,
                    "recent_consensus_rate": recent_consensus_rate,
                    "drift_percentage": drift * 100,
                },
            )

        return None

    def _detect_risk_level_drift(
        self, historical: list[dict[str, Any]], recent: list[dict[str, Any]]
    ) -> GovernanceDriftAlert | None:
        """Detect if high-risk actions are being approved more frequently."""
        risk_weights = {"low": 0, "medium": 1, "high": 2, "critical": 3}

        hist_high_risk_approvals = sum(
            1
            for e in historical
            if e["governance_decision"]["approved"]
            and risk_weights.get(e["proposed_action"].get("risk_level", "low"), 0) >= 2
        )

        recent_high_risk_approvals = sum(
            1
            for e in recent
            if e["governance_decision"]["approved"]
            and risk_weights.get(e["proposed_action"].get("risk_level", "low"), 0) >= 2
        )

        hist_rate = hist_high_risk_approvals / len(historical) if historical else 0
        recent_rate = recent_high_risk_approvals / len(recent) if recent else 0

        drift = recent_rate - hist_rate

        if drift > self.alert_threshold:
            return GovernanceDriftAlert(
                alert_type="risk_level_drift",
                severity="high",
                message=f"High-risk action approval rate increased by {drift * 100:.1f}%",
                evidence={
                    "historical_high_risk_rate": hist_rate,
                    "recent_high_risk_rate": recent_rate,
                    "drift_percentage": drift * 100,
                },
            )

        return None

    def _detect_core_value_drift(
        self, historical: list[dict[str, Any]], recent: list[dict[str, Any]]
    ) -> GovernanceDriftAlert | None:
        """Detect if core value mutations are being approved more frequently."""
        core_targets = {"genesis", "law_hierarchy", "core_values", "four_laws"}

        hist_core_approvals = sum(
            1
            for e in historical
            if e["governance_decision"]["approved"]
            and any(
                t in core_targets
                for t in e["proposed_action"].get("mutation_targets", [])
            )
        )

        recent_core_approvals = sum(
            1
            for e in recent
            if e["governance_decision"]["approved"]
            and any(
                t in core_targets
                for t in e["proposed_action"].get("mutation_targets", [])
            )
        )

        # Core value mutations should be extremely rare
        if recent_core_approvals > hist_core_approvals:
            return GovernanceDriftAlert(
                alert_type="core_value_drift",
                severity="critical",
                message=f"Core value mutation approvals increased "
                f"(historical: {hist_core_approvals}, recent: {recent_core_approvals})",
                evidence={
                    "historical_core_approvals": hist_core_approvals,
                    "recent_core_approvals": recent_core_approvals,
                    "increase": recent_core_approvals - hist_core_approvals,
                },
            )

        return None

    def _save_alerts(self, alerts: list[GovernanceDriftAlert]) -> None:
        """Save alerts to disk."""
        timestamp = datetime.now(UTC).isoformat().replace(":", "-")
        filename = f"drift_alerts_{timestamp}.json"
        filepath = self.alerts_dir / filename

        alert_data = [
            {
                "type": a.alert_type,
                "severity": a.severity,
                "message": a.message,
                "evidence": a.evidence,
                "timestamp": a.timestamp.isoformat(),
            }
            for a in alerts
        ]

        with filepath.open("w") as f:
            json.dump(alert_data, f, indent=2)

        logger.warning("🚨 Governance drift detected! %s alerts saved to %s", len(alerts), filepath)

    def get_recent_alerts(self, days: int = 7) -> list[dict[str, Any]]:
        """Get recent drift alerts."""
        cutoff = datetime.now(UTC) - timedelta(days=days)
        alerts = []

        for filepath in sorted(self.alerts_dir.glob("*.json"), reverse=True):
            try:
                with filepath.open() as f:
                    alert_data = json.load(f)

                for alert in alert_data:
                    alert_time = datetime.fromisoformat(alert["timestamp"])
                    if alert_time >= cutoff:
                        alerts.append(alert)

            except Exception as e:
                logger.warning("Failed to load %s: %s", filepath, e)

        return alerts
