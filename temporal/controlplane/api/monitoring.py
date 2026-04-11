"""
Monitoring API

Query metrics, logs, and traces.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import random


class MetricType(str, Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MonitoringAPI:
    """API for monitoring and observability"""
    
    def __init__(self):
        self.metrics: Dict[str, List[Dict[str, Any]]] = {}
        self.logs: List[Dict[str, Any]] = []
        self.traces: List[Dict[str, Any]] = []
        
    def query_metrics(
        self,
        metric_name: str,
        deployment_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        aggregation: str = "avg",
    ) -> Dict[str, Any]:
        """
        Query metrics with optional filters
        
        Args:
            metric_name: Metric name (e.g., cpu_usage, memory_usage)
            deployment_id: Filter by deployment
            start_time: Start time
            end_time: End time
            aggregation: Aggregation method (avg, sum, min, max)
            
        Returns:
            Metric data points
        """
        if not start_time:
            start_time = datetime.utcnow() - timedelta(hours=1)
        if not end_time:
            end_time = datetime.utcnow()
        
        # Generate sample metric data
        data_points = self._generate_metric_data(
            metric_name,
            start_time,
            end_time,
            deployment_id,
        )
        
        return {
            "metric": metric_name,
            "deployment_id": deployment_id,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "aggregation": aggregation,
            "data_points": data_points,
            "summary": {
                "avg": sum(d["value"] for d in data_points) / len(data_points) if data_points else 0,
                "min": min(d["value"] for d in data_points) if data_points else 0,
                "max": max(d["value"] for d in data_points) if data_points else 0,
            }
        }
    
    def get_available_metrics(self, deployment_id: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Get list of available metrics
        
        Args:
            deployment_id: Filter by deployment
            
        Returns:
            List of available metrics
        """
        return [
            {"name": "cpu_usage", "type": "gauge", "unit": "percent"},
            {"name": "memory_usage", "type": "gauge", "unit": "bytes"},
            {"name": "request_count", "type": "counter", "unit": "count"},
            {"name": "request_duration", "type": "histogram", "unit": "milliseconds"},
            {"name": "error_rate", "type": "gauge", "unit": "percent"},
            {"name": "active_connections", "type": "gauge", "unit": "count"},
            {"name": "queue_depth", "type": "gauge", "unit": "count"},
            {"name": "throughput", "type": "gauge", "unit": "requests/sec"},
        ]
    
    def query_logs(
        self,
        deployment_id: Optional[str] = None,
        level: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        search: Optional[str] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Query logs with filters
        
        Args:
            deployment_id: Filter by deployment
            level: Filter by log level
            start_time: Start time
            end_time: End time
            search: Search term
            limit: Maximum results
            
        Returns:
            Log entries
        """
        if not start_time:
            start_time = datetime.utcnow() - timedelta(hours=1)
        if not end_time:
            end_time = datetime.utcnow()
        
        # Generate sample log data
        logs = self._generate_log_data(
            deployment_id,
            start_time,
            end_time,
            level,
            search,
        )
        
        return {
            "total": len(logs),
            "logs": logs[:limit],
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        }
    
    def query_traces(
        self,
        deployment_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        min_duration: Optional[float] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Query distributed traces
        
        Args:
            deployment_id: Filter by deployment
            trace_id: Specific trace ID
            start_time: Start time
            end_time: End time
            min_duration: Minimum duration in ms
            limit: Maximum results
            
        Returns:
            Trace data
        """
        if not start_time:
            start_time = datetime.utcnow() - timedelta(hours=1)
        if not end_time:
            end_time = datetime.utcnow()
        
        # Generate sample trace data
        traces = self._generate_trace_data(
            deployment_id,
            trace_id,
            start_time,
            end_time,
            min_duration,
        )
        
        return {
            "total": len(traces),
            "traces": traces[:limit],
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        }
    
    def get_health_status(self, deployment_id: str) -> Dict[str, Any]:
        """
        Get health status of a deployment
        
        Args:
            deployment_id: Deployment ID
            
        Returns:
            Health status details
        """
        return {
            "deployment_id": deployment_id,
            "status": "healthy",
            "checks": {
                "liveness": "passing",
                "readiness": "passing",
                "startup": "passing",
            },
            "metrics": {
                "cpu_usage": random.uniform(20, 60),
                "memory_usage": random.uniform(30, 70),
                "error_rate": random.uniform(0, 2),
                "response_time": random.uniform(50, 200),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def get_dashboard_data(self, deployment_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get dashboard overview data
        
        Args:
            deployment_id: Filter by deployment
            
        Returns:
            Dashboard data
        """
        return {
            "summary": {
                "total_deployments": 10,
                "healthy_deployments": 9,
                "warning_deployments": 1,
                "failed_deployments": 0,
            },
            "metrics": {
                "avg_cpu_usage": random.uniform(30, 50),
                "avg_memory_usage": random.uniform(40, 60),
                "total_requests": random.randint(10000, 50000),
                "avg_response_time": random.uniform(100, 300),
                "error_rate": random.uniform(0.1, 2.0),
            },
            "alerts": [
                {
                    "id": "alert-1",
                    "severity": "warning",
                    "message": "High memory usage detected",
                    "deployment_id": "deploy-123",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ],
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def _generate_metric_data(
        self,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        deployment_id: Optional[str],
    ) -> List[Dict[str, Any]]:
        """Generate sample metric data"""
        data_points = []
        current = start_time
        interval = timedelta(minutes=5)
        
        while current <= end_time:
            value = random.uniform(20, 80)
            data_points.append({
                "timestamp": current.isoformat(),
                "value": value,
                "deployment_id": deployment_id,
            })
            current += interval
        
        return data_points
    
    def _generate_log_data(
        self,
        deployment_id: Optional[str],
        start_time: datetime,
        end_time: datetime,
        level: Optional[str],
        search: Optional[str],
    ) -> List[Dict[str, Any]]:
        """Generate sample log data"""
        logs = []
        messages = [
            "Request processed successfully",
            "Database connection established",
            "Cache miss for key: user_123",
            "Processing workflow task",
            "Agent started successfully",
        ]
        
        for i in range(20):
            timestamp = start_time + timedelta(
                seconds=random.randint(0, int((end_time - start_time).total_seconds()))
            )
            log_level = level or random.choice(["info", "warning", "error"])
            
            logs.append({
                "timestamp": timestamp.isoformat(),
                "level": log_level,
                "message": random.choice(messages),
                "deployment_id": deployment_id or f"deploy-{random.randint(1, 10)}",
                "source": "agent",
            })
        
        logs.sort(key=lambda x: x["timestamp"], reverse=True)
        return logs
    
    def _generate_trace_data(
        self,
        deployment_id: Optional[str],
        trace_id: Optional[str],
        start_time: datetime,
        end_time: datetime,
        min_duration: Optional[float],
    ) -> List[Dict[str, Any]]:
        """Generate sample trace data"""
        traces = []
        
        for i in range(10):
            trace = {
                "trace_id": trace_id or f"trace-{i}",
                "start_time": (start_time + timedelta(minutes=i)).isoformat(),
                "duration_ms": random.uniform(50, 500),
                "spans": [
                    {
                        "span_id": f"span-{j}",
                        "operation": f"operation-{j}",
                        "duration_ms": random.uniform(10, 100),
                        "tags": {"deployment_id": deployment_id or f"deploy-{random.randint(1, 10)}"},
                    }
                    for j in range(random.randint(2, 5))
                ],
            }
            
            if min_duration is None or trace["duration_ms"] >= min_duration:
                traces.append(trace)
        
        return traces
