"""
Thirsty's Kernel - Telemetry & Metrics System

Production-grade metrics collection and exposition with:
- RED metrics (Rate, Errors, Duration)
- System resource metrics (CPU, memory, I/O)
- Custom kernel metrics
- Prometheus exposition
- OpenTelemetry integration
- Metric aggregation and downsampling
- Alert threshold monitoring
- Historical trend analysis

Thirst of Gods Level Architecture
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Callable, Any
from collections import defaultdict, deque
import threading

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Metric types"""
    COUNTER = "counter"        # Monotonically increasing
    GAUGE = "gauge"            # Can go up or down
    HISTOGRAM = "histogram"    # Distribution of values
    SUMMARY = "summary"        # Quantiles over sliding window


@dataclass
class MetricValue:
    """Single metric measurement"""
    timestamp: float
    value: float
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class Metric:
    """Metric definition and storage"""
    name: str
    metric_type: MetricType
    description: str
    unit: str
    labels: List[str] = field(default_factory=list)
    values: deque = field(default_factory=lambda: deque(maxlen=10000))  # Ring buffer
    
    # For histograms
    buckets: List[float] = field(default_factory=list)
    
    # For summaries
    quantiles: List[float] = field(default_factory=lambda: [0.5, 0.9, 0.95, 0.99])


@dataclass
class Alert:
    """Alert threshold"""
    metric_name: str
    condition: str  # e.g., ">", "<", "=="
    threshold: float
    callback: Callable[[float, float], None]  # callback(current_value, threshold)
    description: str = ""


class TelemetrySystem:
    """
    Production-grade telemetry and metrics system
    
    Features:
    - Multiple metric types
    - Label-based dimensionality
    - Prometheus exposition
    - OpenTelemetry integration
    - Alert thresholds
    - Historical analysis
    """
    
    def __init__(self):
        # Metric registry
        self.metrics: Dict[str, Metric] = {}
        
        # Alert registry
        self.alerts: List[Alert] = []
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Aggregation caches
        self.rate_cache: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.last_values: Dict[str, float] = {}
        
        # Initialize standard kernel metrics
        self._init_standard_metrics()
        
        logger.info("Telemetry system initialized")
    
    def _init_standard_metrics(self):
        """Initialize standard kernel metrics"""
        # Process metrics
        self.register_metric(
            "kernel_processes_total",
            MetricType.GAUGE,
            "Total number of processes",
            "processes"
        )
        
        self.register_metric(
            "kernel_processes_created_total",
            MetricType.COUNTER,
            "Total processes created",
            "processes"
        )
        
        self.register_metric(
            "kernel_context_switches_total",
            MetricType.COUNTER,
            "Total context switches",
            "switches"
        )
        
        # Memory metrics
        self.register_metric(
            "kernel_memory_used_bytes",
            MetricType.GAUGE,
            "Memory currently used",
            "bytes"
        )
        
        self.register_metric(
            "kernel_memory_free_bytes",
            MetricType.GAUGE,
            "Memory currently free",
            "bytes"
        )
        
        self.register_metric(
            "kernel_page_faults_total",
            MetricType.COUNTER,
            "Total page faults",
            "faults"
        )
        
        # CPU metrics
        self.register_metric(
            "kernel_cpu_usage_percent",
            MetricType.GAUGE,
            "CPU usage percentage",
            "percent",
            labels=["cpu"]
        )
        
        # Syscall metrics
        self.register_metric(
            "kernel_syscalls_total",
            MetricType.COUNTER,
            "Total syscalls",
            "calls",
            labels=["syscall"]
        )
        
        self.register_metric(
            "kernel_syscalls_denied_total",
            MetricType.COUNTER,
            "Total syscalls denied",
            "calls",
            labels=["syscall", "reason"]
        )
        
        # Latency metrics (histogram)
        self.register_metric(
            "kernel_syscall_duration_seconds",
            MetricType.HISTOGRAM,
            "Syscall duration distribution",
            "seconds",
            labels=["syscall"]
        )
        
        # Set histogram buckets for latency
        self.metrics["kernel_syscall_duration_seconds"].buckets = [
            0.00001,  # 10μs
            0.0001,   # 100μs
            0.001,    # 1ms
            0.01,     # 10ms
            0.1,      # 100ms
            1.0,      # 1s
            10.0,     # 10s
        ]
    
    def register_metric(
        self,
        name: str,
        metric_type: MetricType,
        description: str,
        unit: str,
        labels: Optional[List[str]] = None
    ):
        """Register a new metric"""
        with self.lock:
            if name in self.metrics:
                logger.warning(f"Metric {name} already registered")
                return
            
            metric = Metric(
                name=name,
                metric_type=metric_type,
                description=description,
                unit=unit,
                labels=labels or []
            )
            
            self.metrics[name] = metric
            logger.debug(f"Registered metric: {name} ({metric_type.value})")
    
    def record(
        self,
        metric_name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        timestamp: Optional[float] = None
    ):
        """Record a metric value"""
        with self.lock:
            if metric_name not in self.metrics:
                logger.warning(f"Unknown metric: {metric_name}")
                return
            
            metric = self.metrics[metric_name]
            
            metric_value = MetricValue(
                timestamp=timestamp or time.time(),
                value=value,
                labels=labels or {}
            )
            
            metric.values.append(metric_value)
            
            # Check alerts
            self._check_alerts(metric_name, value)
    
    def increment(self, metric_name: str, amount: float = 1.0, labels: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        with self.lock:
            if metric_name not in self.metrics:
                logger.warning(f"Unknown metric: {metric_name}")
                return
            
            metric = self.metrics[metric_name]
            
            if metric.metric_type != MetricType.COUNTER:
                logger.error(f"Cannot increment non-counter metric: {metric_name}")
                return
            
            # Get last value
            label_key = str(sorted((labels or {}).items()))
            last = self.last_values.get(f"{metric_name}:{label_key}", 0.0)
            new_value = last + amount
            
            self.record(metric_name, new_value, labels)
            self.last_values[f"{metric_name}:{label_key}"] = new_value
    
    def set_gauge(self, metric_name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Set a gauge metric value"""
        with self.lock:
            if metric_name not in self.metrics:
                logger.warning(f"Unknown metric: {metric_name}")
                return
            
            metric = self.metrics[metric_name]
            
            if metric.metric_type != MetricType.GAUGE:
                logger.error(f"Cannot set non-gauge metric: {metric_name}")
                return
            
            self.record(metric_name, value, labels)
    
    def observe_histogram(self, metric_name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Observe a value for histogram metric"""
        with self.lock:
            if metric_name not in self.metrics:
                logger.warning(f"Unknown metric: {metric_name}")
                return
            
            metric = self.metrics[metric_name]
            
            if metric.metric_type != MetricType.HISTOGRAM:
                logger.error(f"Cannot observe non-histogram metric: {metric_name}")
                return
            
            self.record(metric_name, value, labels)
    
    def get_metric_value(self, metric_name: str, labels: Optional[Dict[str, str]] = None) -> Optional[float]:
        """Get latest value for metric"""
        with self.lock:
            if metric_name not in self.metrics:
                return None
            
            metric = self.metrics[metric_name]
            
            if not metric.values:
                return None
            
            # Filter by labels if provided
            if labels:
                for mv in reversed(metric.values):
                    if all(mv.labels.get(k) == v for k, v in labels.items()):
                        return mv.value
                return None
            else:
                return metric.values[-1].value
    
    def calculate_rate(
        self,
        metric_name: str,
        window_seconds: float = 60.0,
        labels: Optional[Dict[str, str]] = None
    ) -> float:
        """
        Calculate rate of change (per second) over time window
        
        Useful for converting counters to rates
        """
        with self.lock:
            if metric_name not in self.metrics:
                return 0.0
            
            metric = self.metrics[metric_name]
            now = time.time()
            cutoff = now - window_seconds
            
            # Filter values in time window
            recent_values = [
                mv for mv in metric.values
                if mv.timestamp >= cutoff
                and (not labels or all(mv.labels.get(k) == v for k, v in labels.items()))
            ]
            
            if len(recent_values) < 2:
                return 0.0
            
            # Calculate rate: (value_delta) / (time_delta)
            first = recent_values[0]
            last = recent_values[-1]
            
            value_delta = last.value - first.value
            time_delta = last.timestamp - first.timestamp
            
            if time_delta == 0:
                return 0.0
            
            return value_delta / time_delta
    
    def calculate_percentile(
        self,
        metric_name: str,
        percentile: float,
        window_seconds: float = 60.0,
        labels: Optional[Dict[str, str]] = None
    ) -> Optional[float]:
        """
        Calculate percentile value over time window
        
        Args:
            percentile: 0.0 to 1.0 (e.g., 0.99 for 99th percentile)
        """
        with self.lock:
            if metric_name not in self.metrics:
                return None
            
            metric = self.metrics[metric_name]
            now = time.time()
            cutoff = now - window_seconds
            
            # Filter values in time window
            recent_values = [
                mv.value for mv in metric.values
                if mv.timestamp >= cutoff
                and (not labels or all(mv.labels.get(k) == v for k, v in labels.items()))
            ]
            
            if not recent_values:
                return None
            
            # Calculate percentile
            sorted_values = sorted(recent_values)
            index = int(len(sorted_values) * percentile)
            return sorted_values[min(index, len(sorted_values) - 1)]
    
    def add_alert(
        self,
        metric_name: str,
        condition: str,
        threshold: float,
        callback: Callable[[float, float], None],
        description: str = ""
    ):
        """Add an alert threshold"""
        with self.lock:
            alert = Alert(
                metric_name=metric_name,
                condition=condition,
                threshold=threshold,
                callback=callback,
                description=description
            )
            
            self.alerts.append(alert)
            logger.debug(f"Added alert: {metric_name} {condition} {threshold}")
    
    def _check_alerts(self, metric_name: str, value: float):
        """Check if any alerts are triggered"""
        for alert in self.alerts:
            if alert.metric_name != metric_name:
                continue
            
            triggered = False
            
            if alert.condition == ">":
                triggered = value > alert.threshold
            elif alert.condition == ">=":
                triggered = value >= alert.threshold
            elif alert.condition == "<":
                triggered = value < alert.threshold
            elif alert.condition == "<=":
                triggered = value <= alert.threshold
            elif alert.condition == "==":
                triggered = abs(value - alert.threshold) < 0.0001
            
            if triggered:
                try:
                    alert.callback(value, alert.threshold)
                except Exception as e:
                    logger.error(f"Alert callback failed: {e}")
    
    def export_prometheus(self) -> str:
        """
        Export metrics in Prometheus text format
        
        Format:
        # HELP metric_name Description
        # TYPE metric_name type
        metric_name{label="value"} 123.45 timestamp
        """
        with self.lock:
            lines = []
            
            for metric in self.metrics.values():
                # HELP line
                lines.append(f"# HELP {metric.name} {metric.description}")
                
                # TYPE line
                type_map = {
                    MetricType.COUNTER: "counter",
                    MetricType.GAUGE: "gauge",
                    MetricType.HISTOGRAM: "histogram",
                    MetricType.SUMMARY: "summary",
                }
                lines.append(f"# TYPE {metric.name} {type_map[metric.metric_type]}")
                
                # Values
                if metric.metric_type == MetricType.HISTOGRAM:
                    # Histogram buckets
                    label_key_values = self._get_histogram_export(metric)
                    lines.extend(label_key_values)
                else:
                    # Regular metric
                    if metric.values:
                        mv = metric.values[-1]
                        label_str = self._format_labels(mv.labels)
                        timestamp_ms = int(mv.timestamp * 1000)
                        lines.append(f"{metric.name}{label_str} {mv.value} {timestamp_ms}")
                
                lines.append("")  # Blank line between metrics
            
            return "\n".join(lines)
    
    def _format_labels(self, labels: Dict[str, str]) -> str:
        """Format labels for Prometheus format"""
        if not labels:
            return ""
        
        pairs = [f'{k}="{v}"' for k, v in sorted(labels.items())]
        return "{" + ",".join(pairs) + "}"
    
    def _get_histogram_export(self, metric: Metric) -> List[str]:
        """Export histogram metric in Prometheus format"""
        lines = []
        
        # Group values by label set
        label_groups = defaultdict(list)
        for mv in metric.values:
            label_key = str(sorted(mv.labels.items()))
            label_groups[label_key].append(mv.value)
        
        # For each label set, calculate bucket counts
        for label_key, values in label_groups.items():
            # Reconstruct labels dict
            labels = dict(eval(label_key)) if label_key != "[]" else {}
            
            # Count values in each bucket
            for bucket in metric.buckets:
                count = sum(1 for v in values if v <= bucket)
                bucket_labels = {**labels, "le": str(bucket)}
                label_str = self._format_labels(bucket_labels)
                lines.append(f"{metric.name}_bucket{label_str} {count}")
            
            # +Inf bucket
            inf_labels = {**labels, "le": "+Inf"}
            label_str = self._format_labels(inf_labels)
            lines.append(f"{metric.name}_bucket{label_str} {len(values)}")
            
            # Sum and count
            label_str = self._format_labels(labels)
            lines.append(f"{metric.name}_sum{label_str} {sum(values)}")
            lines.append(f"{metric.name}_count{label_str} {len(values)}")
        
        return lines
    
    def get_stats(self) -> Dict[str, Any]:
        """Get telemetry system statistics"""
        with self.lock:
            return {
                "total_metrics": len(self.metrics),
                "total_alerts": len(self.alerts),
                "metrics_by_type": {
                    mt.value: sum(1 for m in self.metrics.values() if m.metric_type == mt)
                    for mt in MetricType
                },
                "total_measurements": sum(len(m.values) for m in self.metrics.values()),
            }


# Public API
__all__ = [
    "TelemetrySystem",
    "Metric",
    "MetricType",
    "MetricValue",
    "Alert",
]
