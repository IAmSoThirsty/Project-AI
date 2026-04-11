#!/usr/bin/env python3
"""
Metrics Collector - Collects build performance metrics
"""

import time
import logging
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger("MetricsCollector")


@dataclass
class BuildMetric:
    """Represents a single metric data point"""
    timestamp: float
    metric_name: str
    value: float
    tags: Dict[str, str]


class MetricsCollector:
    """Collects and exports build metrics"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.monitoring_config = config.get('monitoring', {})
        
        self.metrics: List[BuildMetric] = []
        self._running = False
    
    def start(self) -> None:
        """Start metrics collection"""
        logger.info("Starting metrics collection...")
        self._running = True
        logger.info("✅ Metrics collection started")
    
    def stop(self) -> None:
        """Stop metrics collection"""
        logger.info("Stopping metrics collection...")
        self._running = False
        logger.info("✅ Metrics collection stopped")
    
    def record(self, metric_name: str, value: float, tags: Dict[str, str] = None) -> None:
        """Record a metric"""
        if not self._running:
            return
        
        metric = BuildMetric(
            timestamp=time.time(),
            metric_name=metric_name,
            value=value,
            tags=tags or {},
        )
        
        self.metrics.append(metric)
        logger.debug(f"Recorded metric: {metric_name}={value}")
    
    def get_metrics(self, since: float = None) -> List[BuildMetric]:
        """Get metrics since timestamp"""
        if since is None:
            return self.metrics
        
        return [m for m in self.metrics if m.timestamp >= since]
    
    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        # In production: format metrics for Prometheus scraping
        output = []
        
        for metric in self.metrics:
            tags_str = ','.join(f'{k}="{v}"' for k, v in metric.tags.items())
            output.append(f"{metric.metric_name}{{{tags_str}}} {metric.value} {int(metric.timestamp * 1000)}")
        
        return '\n'.join(output)
