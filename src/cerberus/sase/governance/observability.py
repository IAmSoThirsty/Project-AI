"""
S ASE - Sovereign Adversarial Signal Engine
L11: Observability & Metrics Fabric

Prometheus/Grafana integration for SASE metrics.

METRICS:
- False positive rate
- Mean time to detect
- Model drift delta
- ASN entropy index
- Beacon activation density
"""

import logging
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

logger = logging.getLogger("SASE.L11.Observability")


@dataclass
class Metric:
    """SASE system metric"""

    name: str
    value: float
    timestamp: float
    labels: Dict[str, str] = None

    def __post_init__(self):
        if self.labels is None:
            self.labels = {}


class MetricsExporter:
    """
    Prometheus-compatible metrics exporter

    Exports SASE metrics in Prometheus format
    """

    def __init__(self):
        self.metrics: Dict[str, List[Metric]] = {}

    def record(self, name: str, value: float, labels: Dict = None):
        """Record metric"""
        metric = Metric(
            name=name, value=value, timestamp=time.time(), labels=labels or {}
        )

        if name not in self.metrics:
            self.metrics[name] = []

        self.metrics[name].append(metric)

        # Keep last 1000 samples per metric
        if len(self.metrics[name]) > 1000:
            self.metrics[name] = self.metrics[name][-1000:]

    def export_prometheus(self) -> str:
        """Export in Prometheus format"""
        lines = []

        for metric_name, samples in self.metrics.items():
            # Use most recent sample
            if samples:
                latest = samples[-1]

                # Format labels
                label_str = ""
                if latest.labels:
                    label_pairs = [f'{k}="{v}"' for k, v in latest.labels.items()]
                    label_str = "{" + ",".join(label_pairs) + "}"

                # Prometheus format
                lines.append(
                    f"{metric_name}{label_str} {latest.value} {int(latest.timestamp * 1000)}"
                )

        return "\n".join(lines)


class ObservabilityFabric:
    """
    L11: Observability & Metrics Fabric

    Tracks key SASE performance and security metrics
    """

    # Metric names
    METRIC_FALSE_POSITIVE_RATE = "sase_false_positive_rate"
    METRIC_MEAN_TIME_TO_DETECT = "sase_mean_time_to_detect_seconds"
    METRIC_MODEL_DRIFT = "sase_model_drift_delta"
    METRIC_ASN_ENTROPY = "sase_asn_entropy_index"
    METRIC_BEACON_DENSITY = "sase_beacon_activation_density"
    METRIC_EVENTS_INGESTED = "sase_events_ingested_total"
    METRIC_CONTAINMENT_ACTIONS = "sase_containment_actions_total"

    def __init__(self):
        self.exporter = MetricsExporter()

        # Tracking state
        self.event_count = 0
        self.false_positives = 0
        self.detection_times: List[float] = []

        logger.info("L11 Observability Fabric initialized")

    def record_event_ingested(self, artifact_type: str):
        """Record event ingestion"""
        self.event_count += 1
        self.exporter.record(
            self.METRIC_EVENTS_INGESTED,
            self.event_count,
            {"artifact_type": artifact_type},
        )

    def record_false_positive(self):
        """Record false positive"""
        self.false_positives += 1

        # Calculate rate
        rate = self.false_positives / max(1, self.event_count)
        self.exporter.record(self.METRIC_FALSE_POSITIVE_RATE, rate)

    def record_detection(self, detection_time_seconds: float):
        """Record time to detection"""
        self.detection_times.append(detection_time_seconds)

        # Calculate mean
        mean_time = sum(self.detection_times) / len(self.detection_times)
        self.exporter.record(self.METRIC_MEAN_TIME_TO_DETECT, mean_time)

    def record_model_drift(self, drift_delta: float):
        """Record model drift"""
        self.exporter.record(self.METRIC_MODEL_DRIFT, drift_delta)

    def record_asn_entropy(self, entropy: float):
        """Record ASN entropy index"""
        self.exporter.record(self.METRIC_ASN_ENTROPY, entropy)

    def record_containment_action(self, action_type: str):
        """Record containment action"""
        self.exporter.record(
            self.METRIC_CONTAINMENT_ACTIONS, 1.0, {"action": action_type}
        )

    def export_metrics(self) -> str:
        """Export all metrics in Prometheus format"""
        return self.exporter.export_prometheus()


__all__ = ["Metric", "MetricsExporter", "ObservabilityFabric"]
