"""
Alert Manager for Security Agents

Implements alert rules, notification channels, and incident management
for security agent monitoring.

Author: Security Agents Team
Date: 2026-01-21
"""

import json
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertChannel(Enum):
    """Alert notification channels."""
    PAGER = "pager"
    EMAIL = "email"
    SLACK = "slack"
    TICKET = "ticket"
    LOG = "log"


class AlertRule:
    """Defines an alert rule with conditions and actions."""

    def __init__(
        self,
        name: str,
        severity: AlertSeverity,
        channels: List[AlertChannel],
        condition: Callable[[Dict[str, Any]], bool],
        message_template: str,
        cooldown_minutes: int = 60
    ):
        """
        Initialize alert rule.

        Args:
            name: Alert rule name
            severity: Alert severity level
            channels: Notification channels
            condition: Function that evaluates metrics and returns True if alert should fire
            message_template: Alert message template
            cooldown_minutes: Minimum time between identical alerts
        """
        self.name = name
        self.severity = severity
        self.channels = channels
        self.condition = condition
        self.message_template = message_template
        self.cooldown_minutes = cooldown_minutes
        self.last_fired = None

    def should_fire(self, metrics: Dict[str, Any]) -> bool:
        """Check if alert should fire based on metrics."""
        return self.condition(metrics)

    def format_message(self, metrics: Dict[str, Any]) -> str:
        """Format alert message with metrics."""
        return self.message_template.format(**metrics)


class AlertManager:
    """Manages alert rules and notifications."""

    def __init__(self, data_dir: str = "data/alerts"):
        """
        Initialize alert manager.

        Args:
            data_dir: Directory to store alert data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.rules: List[AlertRule] = []
        self.alert_history: List[Dict[str, Any]] = []
        self.incident_log: List[Dict[str, Any]] = []
        
        # Initialize default alert rules
        self._setup_default_rules()
        
        # Load alert history
        self._load_alert_history()

    def _setup_default_rules(self):
        """Set up default alert rules."""
        
        # High-severity attack success
        self.rules.append(AlertRule(
            name="high_severity_attack_success",
            severity=AlertSeverity.CRITICAL,
            channels=[AlertChannel.PAGER, AlertChannel.SLACK, AlertChannel.TICKET],
            condition=lambda m: m.get("security", {}).get("attack_success_rate", {}).get("success_rate", 0) > 0.1,
            message_template="CRITICAL: Attack success rate {security[attack_success_rate][success_rate]:.1%} exceeds threshold",
            cooldown_minutes=30
        ))
        
        # Rising false positive trend
        self.rules.append(AlertRule(
            name="rising_false_positive_rate",
            severity=AlertSeverity.HIGH,
            channels=[AlertChannel.EMAIL, AlertChannel.TICKET],
            condition=lambda m: m.get("security", {}).get("false_positive_rate", {}).get("false_positive_rate", 0) > 0.2,
            message_template="HIGH: False positive rate {security[false_positive_rate][false_positive_rate]:.1%} exceeds threshold - safety review required",
            cooldown_minutes=120
        ))
        
        # CI red-team regressions
        self.rules.append(AlertRule(
            name="ci_redteam_regression",
            severity=AlertSeverity.MEDIUM,
            channels=[AlertChannel.SLACK, AlertChannel.TICKET],
            condition=lambda m: m.get("reliability", {}).get("ci_failure_rate", {}).get("failure_rate", 0) > 0.3,
            message_template="MEDIUM: CI failure rate {reliability[ci_failure_rate][failure_rate]:.1%} - block merges to main",
            cooldown_minutes=60
        ))
        
        # High latency
        self.rules.append(AlertRule(
            name="high_agent_latency",
            severity=AlertSeverity.MEDIUM,
            channels=[AlertChannel.SLACK, AlertChannel.EMAIL],
            condition=lambda m: (
                m.get("reliability", {}).get("long_context_latency", {}).get("p95_ms", 0) > 5000 or
                m.get("reliability", {}).get("safety_guard_latency", {}).get("p95_ms", 0) > 500
            ),
            message_template="MEDIUM: Agent latency exceeds threshold - performance investigation required",
            cooldown_minutes=60
        ))
        
        # Low patch acceptance rate
        self.rules.append(AlertRule(
            name="low_patch_acceptance",
            severity=AlertSeverity.LOW,
            channels=[AlertChannel.EMAIL],
            condition=lambda m: m.get("quality", {}).get("patch_acceptance_rate", {}).get("acceptance_rate", 1.0) < 0.3,
            message_template="LOW: Patch acceptance rate {quality[patch_acceptance_rate][acceptance_rate]:.1%} - review patch quality",
            cooldown_minutes=240
        ))
        
        # Detection pattern regression
        self.rules.append(AlertRule(
            name="pattern_regression",
            severity=AlertSeverity.MEDIUM,
            channels=[AlertChannel.SLACK, AlertChannel.TICKET],
            condition=lambda m: m.get("quality", {}).get("regression_rate", {}).get("regression_rate", 0) > 0.1,
            message_template="MEDIUM: Pattern update regression rate {quality[regression_rate][regression_rate]:.1%} - rollback required",
            cooldown_minutes=60
        ))

    def evaluate_metrics(self, metrics: Dict[str, Any]):
        """Evaluate all alert rules against current metrics."""
        for rule in self.rules:
            try:
                if rule.should_fire(metrics):
                    self._fire_alert(rule, metrics)
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.name}: {e}")

    def _fire_alert(self, rule: AlertRule, metrics: Dict[str, Any]):
        """Fire an alert."""
        # Check cooldown
        if rule.last_fired:
            minutes_since_last = (datetime.now() - rule.last_fired).total_seconds() / 60
            if minutes_since_last < rule.cooldown_minutes:
                return  # Still in cooldown
        
        # Format message
        try:
            message = rule.format_message(metrics)
        except Exception as e:
            logger.error(f"Error formatting alert message for {rule.name}: {e}")
            message = f"Alert: {rule.name} (message formatting failed)"
        
        # Create alert
        alert = {
            "rule_name": rule.name,
            "severity": rule.severity.value,
            "channels": [c.value for c in rule.channels],
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "metrics_snapshot": metrics
        }
        
        # Log alert
        self.alert_history.append(alert)
        logger.warning(f"[{rule.severity.value.upper()}] {message}")
        
        # Send notifications
        for channel in rule.channels:
            self._send_notification(channel, alert)
        
        # Create incident for high/critical severity
        if rule.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
            self._create_incident(rule, alert, metrics)
        
        # Update last fired time
        rule.last_fired = datetime.now()
        
        # Save alert history
        self._save_alert_history()

    def _send_notification(self, channel: AlertChannel, alert: Dict[str, Any]):
        """Send alert notification to specified channel."""
        if channel == AlertChannel.PAGER:
            logger.critical(f"PAGER ALERT: {alert['message']}")
            # In production: integrate with PagerDuty/Opsgenie
        
        elif channel == AlertChannel.EMAIL:
            logger.info(f"EMAIL ALERT: {alert['message']}")
            # In production: send email via SMTP
        
        elif channel == AlertChannel.SLACK:
            logger.info(f"SLACK ALERT: {alert['message']}")
            # In production: send to Slack webhook
        
        elif channel == AlertChannel.TICKET:
            logger.info(f"TICKET CREATED: {alert['message']}")
            # In production: create Jira/GitHub issue
        
        elif channel == AlertChannel.LOG:
            logger.warning(f"LOG ALERT: {alert['message']}")

    def _create_incident(
        self,
        rule: AlertRule,
        alert: Dict[str, Any],
        metrics: Dict[str, Any]
    ):
        """Create incident for high-severity alerts."""
        incident = {
            "incident_id": f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "rule_name": rule.name,
            "severity": rule.severity.value,
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "alert": alert,
            "metrics": metrics,
            "actions_taken": [],
            "resolved_at": None
        }
        
        self.incident_log.append(incident)
        logger.critical(f"Incident created: {incident['incident_id']} - {alert['message']}")
        
        # In production: trigger incident workflow
        self._trigger_incident_workflow(incident)
        
        # Save incident log
        self._save_incident_log()

    def _trigger_incident_workflow(self, incident: Dict[str, Any]):
        """Trigger automated incident response workflow."""
        logger.info(f"Triggering incident workflow for {incident['incident_id']}")
        
        # In production: integrate with Temporal workflow
        # Example actions:
        # - Block deployment if CI failure
        # - Rollback pattern update if regression
        # - Scale up resources if latency
        # - Notify on-call team

    def get_open_incidents(self) -> List[Dict[str, Any]]:
        """Get list of open incidents."""
        return [i for i in self.incident_log if i["status"] == "open"]

    def resolve_incident(self, incident_id: str, resolution_notes: str):
        """Resolve an incident."""
        for incident in self.incident_log:
            if incident["incident_id"] == incident_id:
                incident["status"] = "resolved"
                incident["resolved_at"] = datetime.now().isoformat()
                incident["resolution_notes"] = resolution_notes
                logger.info(f"Incident resolved: {incident_id}")
                self._save_incident_log()
                return
        
        logger.warning(f"Incident not found: {incident_id}")

    def get_alert_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary of alerts in the last N hours."""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(hours=hours)
        
        recent_alerts = [
            a for a in self.alert_history
            if datetime.fromisoformat(a["timestamp"]) > cutoff
        ]
        
        by_severity = {}
        for alert in recent_alerts:
            severity = alert["severity"]
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        return {
            "total_alerts": len(recent_alerts),
            "by_severity": by_severity,
            "open_incidents": len(self.get_open_incidents()),
            "time_window_hours": hours
        }

    def _load_alert_history(self):
        """Load alert history from disk."""
        history_file = self.data_dir / "alert_history.json"
        incident_file = self.data_dir / "incident_log.json"
        
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    self.alert_history = json.load(f)
            except Exception as e:
                logger.error(f"Could not load alert history: {e}")
        
        if incident_file.exists():
            try:
                with open(incident_file, 'r') as f:
                    self.incident_log = json.load(f)
            except Exception as e:
                logger.error(f"Could not load incident log: {e}")

    def _save_alert_history(self):
        """Save alert history to disk."""
        history_file = self.data_dir / "alert_history.json"
        
        try:
            # Keep last 10,000 alerts
            with open(history_file, 'w') as f:
                json.dump(self.alert_history[-10000:], f, indent=2)
        except Exception as e:
            logger.error(f"Could not save alert history: {e}")

    def _save_incident_log(self):
        """Save incident log to disk."""
        incident_file = self.data_dir / "incident_log.json"
        
        try:
            with open(incident_file, 'w') as f:
                json.dump(self.incident_log, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save incident log: {e}")
