"""
Security Metrics Collection and Monitoring System

Implements operational monitoring for security agents:
- Security metrics (attack success rate, time to detect/respond, false positive rate)
- Reliability metrics (latency p95/p99, CI failure rate)
- Quality metrics (patch acceptance rate, regression rate)

Author: Security Agents Team
Date: 2026-01-21
"""

import json
import statistics
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


class SecurityMetricsCollector:
    """Collects and aggregates security-related metrics."""

    def __init__(self, data_dir: str = "data/metrics"):
        """
        Initialize metrics collector.

        Args:
            data_dir: Directory to store metrics data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # In-memory metrics storage
        self.attack_results: list[dict[str, Any]] = []
        self.detection_events: list[dict[str, Any]] = []
        self.response_events: list[dict[str, Any]] = []
        self.safety_detections: list[dict[str, Any]] = []
        self.latency_measurements: dict[str, list[float]] = defaultdict(list)
        self.ci_runs: list[dict[str, Any]] = []
        self.patch_proposals: list[dict[str, Any]] = []
        self.pattern_updates: list[dict[str, Any]] = []

        # Load existing metrics
        self._load_metrics()

    def record_attack_result(
        self,
        persona: str,
        guardrail: str,
        success: bool,
        turns: int,
        timestamp: str | None = None,
    ):
        """Record result of an adversarial attack."""
        event = {
            "persona": persona,
            "guardrail": guardrail,
            "success": success,
            "turns": turns,
            "timestamp": timestamp or datetime.now().isoformat(),
        }
        self.attack_results.append(event)
        self._save_metrics()

    def record_detection_event(
        self,
        attack_type: str,
        detected: bool,
        detection_time_ms: float,
        timestamp: str | None = None,
    ):
        """Record security event detection."""
        event = {
            "attack_type": attack_type,
            "detected": detected,
            "detection_time_ms": detection_time_ms,
            "timestamp": timestamp or datetime.now().isoformat(),
        }
        self.detection_events.append(event)
        self._save_metrics()

    def record_response_event(
        self,
        incident_id: str,
        response_time_seconds: float,
        mitigated: bool,
        timestamp: str | None = None,
    ):
        """Record incident response event."""
        event = {
            "incident_id": incident_id,
            "response_time_seconds": response_time_seconds,
            "mitigated": mitigated,
            "timestamp": timestamp or datetime.now().isoformat(),
        }
        self.response_events.append(event)
        self._save_metrics()

    def record_safety_detection(
        self,
        detection_type: str,
        is_true_positive: bool,
        confidence: float,
        timestamp: str | None = None,
    ):
        """Record safety guard detection."""
        event = {
            "detection_type": detection_type,
            "is_true_positive": is_true_positive,
            "confidence": confidence,
            "timestamp": timestamp or datetime.now().isoformat(),
        }
        self.safety_detections.append(event)
        self._save_metrics()

    def record_latency(
        self, agent_name: str, latency_ms: float, timestamp: str | None = None
    ):
        """Record agent operation latency."""
        self.latency_measurements[agent_name].append(latency_ms)

        # Keep only recent measurements (last 1000)
        if len(self.latency_measurements[agent_name]) > 1000:
            self.latency_measurements[agent_name] = self.latency_measurements[
                agent_name
            ][-1000:]

        self._save_metrics()

    def record_ci_run(
        self,
        run_id: str,
        test_type: str,
        success: bool,
        duration_seconds: float,
        timestamp: str | None = None,
    ):
        """Record CI adversarial test run."""
        run = {
            "run_id": run_id,
            "test_type": test_type,
            "success": success,
            "duration_seconds": duration_seconds,
            "timestamp": timestamp or datetime.now().isoformat(),
        }
        self.ci_runs.append(run)
        self._save_metrics()

    def record_patch_proposal(
        self,
        patch_id: str,
        accepted: bool,
        auto_generated: bool,
        review_time_hours: float,
        timestamp: str | None = None,
    ):
        """Record code patch proposal outcome."""
        proposal = {
            "patch_id": patch_id,
            "accepted": accepted,
            "auto_generated": auto_generated,
            "review_time_hours": review_time_hours,
            "timestamp": timestamp or datetime.now().isoformat(),
        }
        self.patch_proposals.append(proposal)
        self._save_metrics()

    def record_pattern_update(
        self,
        pattern_type: str,
        patterns_added: int,
        caused_regression: bool,
        timestamp: str | None = None,
    ):
        """Record detection pattern update."""
        update = {
            "pattern_type": pattern_type,
            "patterns_added": patterns_added,
            "caused_regression": caused_regression,
            "timestamp": timestamp or datetime.now().isoformat(),
        }
        self.pattern_updates.append(update)
        self._save_metrics()

    # Metric calculation methods

    def get_attack_success_rate(
        self, persona: str | None = None, guardrail: str | None = None, hours: int = 24
    ) -> dict[str, float]:
        """Calculate attack success rate."""
        cutoff = datetime.now() - timedelta(hours=hours)

        filtered = [
            r
            for r in self.attack_results
            if datetime.fromisoformat(r["timestamp"]) > cutoff
        ]

        if persona:
            filtered = [r for r in filtered if r["persona"] == persona]
        if guardrail:
            filtered = [r for r in filtered if r["guardrail"] == guardrail]

        if not filtered:
            return {"success_rate": 0.0, "total_attacks": 0}

        successes = sum(1 for r in filtered if r["success"])
        rate = successes / len(filtered)

        return {
            "success_rate": rate,
            "total_attacks": len(filtered),
            "successful_attacks": successes,
        }

    def get_time_to_detect(self, hours: int = 24) -> dict[str, float]:
        """Calculate time to detect incidents."""
        cutoff = datetime.now() - timedelta(hours=hours)

        filtered = [
            e
            for e in self.detection_events
            if datetime.fromisoformat(e["timestamp"]) > cutoff and e["detected"]
        ]

        if not filtered:
            return {"mean_ms": 0.0, "median_ms": 0.0, "p95_ms": 0.0}

        times = [e["detection_time_ms"] for e in filtered]

        return {
            "mean_ms": statistics.mean(times),
            "median_ms": statistics.median(times),
            "p95_ms": self._percentile(times, 95),
        }

    def get_time_to_respond(self, hours: int = 24) -> dict[str, float]:
        """Calculate time to respond to incidents."""
        cutoff = datetime.now() - timedelta(hours=hours)

        filtered = [
            e
            for e in self.response_events
            if datetime.fromisoformat(e["timestamp"]) > cutoff
        ]

        if not filtered:
            return {"mean_seconds": 0.0, "median_seconds": 0.0, "p95_seconds": 0.0}

        times = [e["response_time_seconds"] for e in filtered]

        return {
            "mean_seconds": statistics.mean(times),
            "median_seconds": statistics.median(times),
            "p95_seconds": self._percentile(times, 95),
        }

    def get_false_positive_rate(self, hours: int = 24) -> dict[str, float]:
        """Calculate false positive rate for safety detections."""
        cutoff = datetime.now() - timedelta(hours=hours)

        filtered = [
            d
            for d in self.safety_detections
            if datetime.fromisoformat(d["timestamp"]) > cutoff
        ]

        if not filtered:
            return {"false_positive_rate": 0.0, "total_detections": 0}

        false_positives = sum(1 for d in filtered if not d["is_true_positive"])
        rate = false_positives / len(filtered)

        return {
            "false_positive_rate": rate,
            "total_detections": len(filtered),
            "false_positives": false_positives,
        }

    def get_agent_latency(self, agent_name: str) -> dict[str, float]:
        """Calculate latency percentiles for an agent."""
        measurements = self.latency_measurements.get(agent_name, [])

        if not measurements:
            return {"p50_ms": 0.0, "p95_ms": 0.0, "p99_ms": 0.0}

        return {
            "p50_ms": self._percentile(measurements, 50),
            "p95_ms": self._percentile(measurements, 95),
            "p99_ms": self._percentile(measurements, 99),
            "mean_ms": statistics.mean(measurements),
        }

    def get_ci_failure_rate(self, hours: int = 24) -> dict[str, float]:
        """Calculate CI run failure rate."""
        cutoff = datetime.now() - timedelta(hours=hours)

        filtered = [
            r for r in self.ci_runs if datetime.fromisoformat(r["timestamp"]) > cutoff
        ]

        if not filtered:
            return {"failure_rate": 0.0, "total_runs": 0}

        failures = sum(1 for r in filtered if not r["success"])
        rate = failures / len(filtered)

        return {"failure_rate": rate, "total_runs": len(filtered), "failures": failures}

    def get_patch_acceptance_rate(self, hours: int = 168) -> dict[str, float]:
        """Calculate patch acceptance rate (default 7 days)."""
        cutoff = datetime.now() - timedelta(hours=hours)

        filtered = [
            p
            for p in self.patch_proposals
            if datetime.fromisoformat(p["timestamp"]) > cutoff
        ]

        if not filtered:
            return {"acceptance_rate": 0.0, "total_proposals": 0}

        accepted = sum(1 for p in filtered if p["accepted"])
        rate = accepted / len(filtered)

        return {
            "acceptance_rate": rate,
            "total_proposals": len(filtered),
            "accepted": accepted,
        }

    def get_regression_rate(self, hours: int = 168) -> dict[str, float]:
        """Calculate regression rate from pattern updates (default 7 days)."""
        cutoff = datetime.now() - timedelta(hours=hours)

        filtered = [
            u
            for u in self.pattern_updates
            if datetime.fromisoformat(u["timestamp"]) > cutoff
        ]

        if not filtered:
            return {"regression_rate": 0.0, "total_updates": 0}

        regressions = sum(1 for u in filtered if u["caused_regression"])
        rate = regressions / len(filtered)

        return {
            "regression_rate": rate,
            "total_updates": len(filtered),
            "regressions": regressions,
        }

    def get_all_metrics(self) -> dict[str, Any]:
        """Get all metrics in a single summary."""
        return {
            "security": {
                "attack_success_rate": self.get_attack_success_rate(),
                "time_to_detect": self.get_time_to_detect(),
                "time_to_respond": self.get_time_to_respond(),
                "false_positive_rate": self.get_false_positive_rate(),
            },
            "reliability": {
                "long_context_latency": self.get_agent_latency("long_context"),
                "safety_guard_latency": self.get_agent_latency("safety_guard"),
                "ci_failure_rate": self.get_ci_failure_rate(),
            },
            "quality": {
                "patch_acceptance_rate": self.get_patch_acceptance_rate(),
                "regression_rate": self.get_regression_rate(),
            },
            "timestamp": datetime.now().isoformat(),
        }

    # Utility methods

    def _percentile(self, data: list[float], percentile: int) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int((percentile / 100.0) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]

    def _load_metrics(self):
        """Load metrics from disk."""
        metrics_file = self.data_dir / "security_metrics.json"

        if metrics_file.exists():
            try:
                with open(metrics_file) as f:
                    data = json.load(f)

                self.attack_results = data.get("attack_results", [])
                self.detection_events = data.get("detection_events", [])
                self.response_events = data.get("response_events", [])
                self.safety_detections = data.get("safety_detections", [])
                self.latency_measurements = defaultdict(
                    list, data.get("latency_measurements", {})
                )
                self.ci_runs = data.get("ci_runs", [])
                self.patch_proposals = data.get("patch_proposals", [])
                self.pattern_updates = data.get("pattern_updates", [])
            except Exception as e:
                print(f"Warning: Could not load metrics: {e}")

    def _save_metrics(self):
        """Save metrics to disk."""
        metrics_file = self.data_dir / "security_metrics.json"

        data = {
            "attack_results": self.attack_results[-1000:],  # Keep last 1000
            "detection_events": self.detection_events[-1000:],
            "response_events": self.response_events[-1000:],
            "safety_detections": self.safety_detections[-1000:],
            "latency_measurements": dict(self.latency_measurements),
            "ci_runs": self.ci_runs[-1000:],
            "patch_proposals": self.patch_proposals[-500:],
            "pattern_updates": self.pattern_updates[-500:],
        }

        try:
            with open(metrics_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save metrics: {e}")

    def export_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus format."""
        metrics = self.get_all_metrics()
        lines = []

        # Security metrics
        lines.append("# HELP security_attack_success_rate Attack success rate")
        lines.append("# TYPE security_attack_success_rate gauge")
        lines.append(
            f"security_attack_success_rate {metrics['security']['attack_success_rate']['success_rate']}"
        )

        lines.append("# HELP security_time_to_detect_ms Time to detect incidents (ms)")
        lines.append("# TYPE security_time_to_detect_ms gauge")
        lines.append(
            f"security_time_to_detect_ms {{quantile=\"0.95\"}} {metrics['security']['time_to_detect']['p95_ms']}"
        )

        lines.append("# HELP security_false_positive_rate False positive rate")
        lines.append("# TYPE security_false_positive_rate gauge")
        lines.append(
            f"security_false_positive_rate {metrics['security']['false_positive_rate']['false_positive_rate']}"
        )

        # Reliability metrics
        for agent in ["long_context", "safety_guard"]:
            latency = metrics["reliability"].get(f"{agent}_latency", {})
            if latency:
                lines.append(f"# HELP {agent}_latency_ms Agent latency (ms)")
                lines.append(f"# TYPE {agent}_latency_ms gauge")
                lines.append(
                    f"{agent}_latency_ms {{quantile=\"0.95\"}} {latency.get('p95_ms', 0)}"
                )
                lines.append(
                    f"{agent}_latency_ms {{quantile=\"0.99\"}} {latency.get('p99_ms', 0)}"
                )

        return "\n".join(lines)
