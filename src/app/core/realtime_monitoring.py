#!/usr/bin/env python3
"""
Real-Time Monitoring Module - Streaming Data Architecture
Global Scenario Engine Real-Time Capabilities

Implements:
- Incremental data updates
- Real-time alert system
- Webhook notifications
- Monitoring dashboard hooks
"""

import json
import logging
import threading
import time
from collections import deque
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


class IncrementalUpdateManager:
    """
    Manages incremental updates to scenario engine data.

    Allows updating specific countries/domains without full reload.
    """

    def __init__(self, engine):
        """
        Initialize incremental update manager.

        Args:
            engine: GlobalScenarioEngine instance
        """
        self.engine = engine
        self.update_log = deque(maxlen=1000)  # Keep last 1000 updates
        self.lock = threading.Lock()

    def update_country_data(
        self, country: str, domain: str, year: int, value: float
    ) -> bool:
        """
        Update data for a specific country/domain/year.

        Args:
            country: ISO3 country code
            domain: Risk domain
            year: Year
            value: New value

        Returns:
            bool: Success status
        """
        from app.core.simulation_contingency_root import RiskDomain

        try:
            with self.lock:
                domain_enum = RiskDomain(domain)

                if domain_enum not in self.engine.historical_data:
                    self.engine.historical_data[domain_enum] = {}

                if country not in self.engine.historical_data[domain_enum]:
                    self.engine.historical_data[domain_enum][country] = {}

                old_value = self.engine.historical_data[domain_enum][country].get(year)
                self.engine.historical_data[domain_enum][country][year] = value

                # Log update
                self.update_log.append(
                    {
                        "timestamp": datetime.now(UTC).isoformat(),
                        "country": country,
                        "domain": domain,
                        "year": year,
                        "old_value": old_value,
                        "new_value": value,
                    }
                )

                logger.info(
                    "Updated %s/%s/%s: %s -> %s",
                    country,
                    domain,
                    year,
                    old_value,
                    value,
                )
                return True

        except Exception as e:
            logger.error("Failed to update country data: %s", e)
            return False

    def get_update_history(self, limit: int = 100) -> list[dict[str, Any]]:
        """
        Get recent update history.

        Args:
            limit: Maximum number of updates to return

        Returns:
            List of update records
        """
        return list(self.update_log)[-limit:]


class RealTimeAlertSystem:
    """
    Real-time alert generation and notification system.

    Monitors for threshold exceedances and generates immediate alerts.
    """

    def __init__(self, engine, alert_threshold: float = 0.7):
        """
        Initialize real-time alert system.

        Args:
            engine: GlobalScenarioEngine instance
            alert_threshold: Minimum likelihood for alerts
        """
        self.engine = engine
        self.alert_threshold = alert_threshold
        self.alert_queue = deque(maxlen=100)
        self.subscribers: list[Callable] = []
        self.monitoring = False
        self.monitor_thread = None

    def subscribe(self, callback: Callable) -> None:
        """
        Subscribe to real-time alerts.

        Args:
            callback: Function to call when alert is generated
                     Signature: callback(alert: CrisisAlert) -> None
        """
        self.subscribers.append(callback)
        logger.info("Added alert subscriber: %s", callback.__name__)

    def unsubscribe(self, callback: Callable) -> None:
        """
        Unsubscribe from real-time alerts.

        Args:
            callback: Function to remove
        """
        if callback in self.subscribers:
            self.subscribers.remove(callback)
            logger.info("Removed alert subscriber: %s", callback.__name__)

    def emit_alert(self, alert) -> None:
        """
        Emit alert to all subscribers.

        Args:
            alert: CrisisAlert instance
        """
        self.alert_queue.append(
            {"timestamp": datetime.now(UTC).isoformat(), "alert": alert}
        )

        for subscriber in self.subscribers:
            try:
                subscriber(alert)
            except Exception as e:
                logger.error("Error in alert subscriber %s: %s", subscriber.__name__, e)

    def check_for_alerts(self) -> None:
        """Check for new alerts based on current data."""
        try:
            # Re-run scenario simulation
            scenarios = self.engine.simulate_scenarios(
                projection_years=5, num_simulations=500
            )

            # Generate alerts
            alerts = self.engine.generate_alerts(
                scenarios, threshold=self.alert_threshold
            )

            # Emit new alerts
            for alert in alerts:
                self.emit_alert(alert)

        except Exception as e:
            logger.error("Error checking for alerts: %s", e)

    def start_monitoring(self, interval: int = 3600) -> None:
        """
        Start continuous monitoring.

        Args:
            interval: Check interval in seconds (default: 1 hour)
        """
        if self.monitoring:
            logger.warning("Monitoring already started")
            return

        self.monitoring = True

        def monitor_loop():
            while self.monitoring:
                self.check_for_alerts()
                time.sleep(interval)

        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Started real-time monitoring (interval: %ss)", interval)

    def stop_monitoring(self) -> None:
        """Stop continuous monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Stopped real-time monitoring")


class WebhookNotifier:
    """
    Webhook notification system for alerts.

    Sends HTTP POST requests to configured webhooks when alerts are generated.
    """

    def __init__(self, webhook_urls: list[str] | None = None):
        """
        Initialize webhook notifier.

        Args:
            webhook_urls: List of webhook URLs to notify
        """
        import requests

        self.webhook_urls = webhook_urls or []
        self.session = requests.Session()
        self.notification_log = deque(maxlen=100)

    def add_webhook(self, url: str) -> None:
        """
        Add webhook URL.

        Args:
            url: Webhook URL
        """
        if url not in self.webhook_urls:
            self.webhook_urls.append(url)
            logger.info("Added webhook: %s", url)

    def remove_webhook(self, url: str) -> None:
        """
        Remove webhook URL.

        Args:
            url: Webhook URL
        """
        if url in self.webhook_urls:
            self.webhook_urls.remove(url)
            logger.info("Removed webhook: %s", url)

    def notify(self, alert) -> None:
        """
        Send alert to all webhooks.

        Args:
            alert: CrisisAlert instance
        """

        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "alert": {
                "alert_id": alert.alert_id,
                "risk_score": alert.risk_score,
                "scenario_title": alert.scenario.title,
                "likelihood": alert.scenario.likelihood,
                "severity": alert.scenario.severity.value,
                "year": alert.scenario.year,
                "summary": alert.explainability[:500],  # First 500 chars
            },
        }

        for url in self.webhook_urls:
            try:
                response = self.session.post(
                    url,
                    json=payload,
                    timeout=10,
                    headers={"Content-Type": "application/json"},
                )
                response.raise_for_status()

                self.notification_log.append(
                    {
                        "timestamp": datetime.now(UTC).isoformat(),
                        "url": url,
                        "alert_id": alert.alert_id,
                        "status": "success",
                        "status_code": response.status_code,
                    }
                )

                logger.info(
                    "Webhook notification sent to %s: %s", url, response.status_code
                )

            except Exception as e:
                self.notification_log.append(
                    {
                        "timestamp": datetime.now(UTC).isoformat(),
                        "url": url,
                        "alert_id": alert.alert_id,
                        "status": "failed",
                        "error": str(e),
                    }
                )
                logger.error("Failed to send webhook to %s: %s", url, e)


class MonitoringDashboard:
    """
    Monitoring dashboard data provider.

    Provides real-time metrics for visualization dashboards.
    """

    def __init__(self, engine):
        """
        Initialize monitoring dashboard.

        Args:
            engine: GlobalScenarioEngine instance
        """
        self.engine = engine
        self.metrics_history = deque(maxlen=1000)
        self.lock = threading.Lock()

    def get_current_metrics(self) -> dict[str, Any]:
        """
        Get current system metrics.

        Returns:
            Dictionary with current metrics
        """
        with self.lock:
            metrics = {
                "timestamp": datetime.now(UTC).isoformat(),
                "data_points": sum(
                    sum(len(years) for years in data.values())
                    for data in self.engine.historical_data.values()
                ),
                "countries": len(
                    set().union(
                        *[
                            set(data.keys())
                            for data in self.engine.historical_data.values()
                        ]
                    )
                ),
                "domains": len(self.engine.historical_data),
                "threshold_events": len(self.engine.threshold_events),
                "scenarios": len(self.engine.scenarios),
                "alerts": len(self.engine.alerts),
                "top_risks": self._get_top_risks(),
            }

            self.metrics_history.append(metrics)
            return metrics

    def _get_top_risks(self, limit: int = 5) -> list[dict[str, Any]]:
        """
        Get top risk scenarios.

        Args:
            limit: Number of top risks to return

        Returns:
            List of top risk scenarios
        """
        if not self.engine.scenarios:
            return []

        top_scenarios = sorted(
            self.engine.scenarios, key=lambda s: s.likelihood, reverse=True
        )[:limit]

        return [
            {
                "title": s.title,
                "likelihood": s.likelihood,
                "year": s.year,
                "severity": s.severity.value,
            }
            for s in top_scenarios
        ]

    def get_metrics_history(self, minutes: int = 60) -> list[dict[str, Any]]:
        """
        Get metrics history.

        Args:
            minutes: Number of minutes of history to return

        Returns:
            List of historical metrics
        """
        cutoff = datetime.now(UTC).timestamp() - (minutes * 60)

        return [
            m
            for m in self.metrics_history
            if datetime.fromisoformat(m["timestamp"]).timestamp() > cutoff
        ]

    def export_dashboard_state(self, filepath: str) -> bool:
        """
        Export dashboard state to file.

        Args:
            filepath: Output file path

        Returns:
            bool: Success status
        """
        try:
            state = {
                "current_metrics": self.get_current_metrics(),
                "metrics_history": list(self.metrics_history),
                "alerts": [
                    {
                        "alert_id": a.alert_id,
                        "risk_score": a.risk_score,
                        "scenario_title": a.scenario.title,
                    }
                    for a in self.engine.alerts[-10:]  # Last 10 alerts
                ],
            }

            with open(filepath, "w") as f:
                json.dump(state, f, indent=2, default=str)

            logger.info("Dashboard state exported to %s", filepath)
            return True

        except Exception as e:
            logger.error("Failed to export dashboard state: %s", e)
            return False


# Factory function to setup real-time capabilities
def setup_real_time_monitoring(
    engine,
    enable_alerts: bool = True,
    enable_webhooks: bool = False,
    webhook_urls: list[str] | None = None,
    alert_threshold: float = 0.7,
    monitor_interval: int = 3600,
) -> dict[str, Any]:
    """
    Setup real-time monitoring capabilities for the engine.

    Args:
        engine: GlobalScenarioEngine instance
        enable_alerts: Enable real-time alert system
        enable_webhooks: Enable webhook notifications
        webhook_urls: List of webhook URLs
        alert_threshold: Alert likelihood threshold
        monitor_interval: Monitoring interval in seconds

    Returns:
        Dictionary with monitoring components
    """
    components = {
        "update_manager": IncrementalUpdateManager(engine),
        "dashboard": MonitoringDashboard(engine),
    }

    if enable_alerts:
        alert_system = RealTimeAlertSystem(engine, alert_threshold)
        components["alert_system"] = alert_system

        if enable_webhooks and webhook_urls:
            webhook_notifier = WebhookNotifier(webhook_urls)
            alert_system.subscribe(webhook_notifier.notify)
            components["webhook_notifier"] = webhook_notifier

        # Start monitoring
        alert_system.start_monitoring(interval=monitor_interval)

    logger.info("Real-time monitoring setup completed")
    return components
