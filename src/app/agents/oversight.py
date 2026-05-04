"""System oversight agent for monitoring and compliance.

Monitors system health, tracks activities, and ensures compliance with
policy constraints and security requirements.

All operations route through CognitionKernel for governance tracking.
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent

logger = logging.getLogger(__name__)

_DENY_RATE_THRESHOLD = 0.20
_DEFAULT_WINDOW_SECONDS = 300  # 5-minute sliding window
_ALERTS_DIR = "data/governance_drift_alerts"


class OversightAgent(KernelRoutedAgent):
    """Monitors constitutional compliance across all agents.

    Reads AuditLog events and alerts when any agent's deny rate
    spikes above the threshold within a sliding window.
    """

    def __init__(self, kernel: CognitionKernel | None = None) -> None:
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="medium",
        )
        self.enabled: bool = True
        self.monitors: dict = {}
        self._lock = threading.Lock()
        os.makedirs(_ALERTS_DIR, exist_ok=True)

    # ------------------------------------------------------------------ public

    def monitor_compliance(
        self,
        window_seconds: int = _DEFAULT_WINDOW_SECONDS,
        audit_log_path: str | None = None,
    ) -> dict[str, Any]:
        """Scan the audit log for compliance issues in the given window.

        Returns a report dict with per-agent metrics and any fired alerts.
        """
        return self._execute_through_kernel(
            self._do_monitor_compliance,
            action_name="OversightAgent.monitor_compliance",
            action_args=(window_seconds, audit_log_path),
        )

    def get_deny_rates(
        self,
        window_seconds: int = _DEFAULT_WINDOW_SECONDS,
        audit_log_path: str | None = None,
    ) -> dict[str, float]:
        """Return per-actor deny rates over the sliding window."""
        events = self._load_recent_events(window_seconds, audit_log_path)
        return self._calculate_deny_rates(events)

    # --------------------------------------------------------------- private

    def _do_monitor_compliance(
        self,
        window_seconds: int,
        audit_log_path: str | None,
    ) -> dict[str, Any]:
        events = self._load_recent_events(window_seconds, audit_log_path)
        deny_rates = self._calculate_deny_rates(events)
        alerts_fired: list[dict] = []

        for actor, rate in deny_rates.items():
            if rate > _DENY_RATE_THRESHOLD:
                alert = self._fire_alert(actor, rate, window_seconds)
                alerts_fired.append(alert)
                logger.warning(
                    "OversightAgent: deny-rate spike for actor=%s rate=%.2f%%",
                    actor,
                    rate * 100,
                )

        with self._lock:
            self.monitors = {
                "last_run_utc": datetime.now(timezone.utc).isoformat(),
                "window_seconds": window_seconds,
                "actors_checked": len(deny_rates),
                "alerts_fired": len(alerts_fired),
                "deny_rates": deny_rates,
            }

        return {
            "deny_rates": deny_rates,
            "alerts_fired": alerts_fired,
            "event_count": len(events),
        }

    def _load_recent_events(
        self,
        window_seconds: int,
        audit_log_path: str | None,
    ) -> list[dict]:
        """Parse YAML audit log and return events within the time window."""
        if audit_log_path is None:
            # Default: governance/audit_log.yaml relative to project root
            audit_log_path = str(
                Path(__file__).parent.parent.parent.parent
                / "governance"
                / "audit_log.yaml"
            )

        log_file = Path(audit_log_path)
        if not log_file.exists():
            return []

        cutoff = datetime.now(timezone.utc).timestamp() - window_seconds
        events: list[dict] = []

        try:
            content = log_file.read_text(encoding="utf-8")
            for entry in yaml.safe_load_all(content):
                if not isinstance(entry, dict):
                    continue
                ts_raw = entry.get("timestamp", "")
                try:
                    ts = datetime.fromisoformat(ts_raw).timestamp()
                except Exception:
                    continue
                if ts >= cutoff:
                    events.append(entry)
        except Exception as exc:
            logger.warning("OversightAgent: failed to read audit log: %s", exc)

        return events

    def _calculate_deny_rates(self, events: list[dict]) -> dict[str, float]:
        """Return deny-rate per actor from a list of audit events."""
        totals: dict[str, int] = defaultdict(int)
        denies: dict[str, int] = defaultdict(int)

        for event in events:
            actor = event.get("actor", "unknown")
            totals[actor] += 1
            event_type = event.get("event_type", "")
            data = event.get("data", {}) or {}
            verdict = str(data.get("verdict", "")).upper()
            if "DENY" in event_type.upper() or "DENY" in verdict or "BLOCK" in verdict:
                denies[actor] += 1

        return {
            actor: denies[actor] / totals[actor]
            for actor in totals
            if totals[actor] > 0
        }

    def _fire_alert(self, actor: str, rate: float, window_seconds: int) -> dict:
        alert = {
            "alert_type": "deny_rate_spike",
            "severity": "high" if rate > 0.5 else "medium",
            "actor": actor,
            "deny_rate": rate,
            "window_seconds": window_seconds,
            "threshold": _DENY_RATE_THRESHOLD,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        ts_slug = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        fname = os.path.join(_ALERTS_DIR, f"oversight_{actor}_{ts_slug}.json")
        try:
            with open(fname, "w", encoding="utf-8") as fh:
                json.dump(alert, fh, indent=2)
        except Exception as exc:
            logger.warning("OversightAgent: failed to write alert file: %s", exc)
        return alert
