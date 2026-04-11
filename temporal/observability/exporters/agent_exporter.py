#!/usr/bin/env python3
"""
Agent Metrics Exporter

Exports custom metrics for agent monitoring.
Implements Prometheus exposition format.
"""

from prometheus_client import start_http_server, Gauge, Counter, Histogram, Summary
import time
import random
import os

# Metrics definitions
AGENT_UP = Gauge('up', 'Agent availability', ['agent_id', 'region', 'zone'])
AGENT_TASKS_TOTAL = Counter('agent_tasks_total', 'Total tasks processed', ['agent_id', 'status'])
AGENT_TASK_DURATION = Histogram(
    'agent_task_duration_seconds',
    'Task execution duration',
    ['agent_id', 'task_type'],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0)
)
AGENT_ERRORS = Counter('agent_errors_total', 'Total errors', ['agent_id', 'error_type'])
AGENT_QUEUE_DEPTH = Gauge('agent_task_queue_depth', 'Tasks in queue', ['agent_id'])
AGENT_CPU = Gauge('agent_cpu_usage_percent', 'CPU usage percentage', ['agent_id'])
AGENT_MEMORY = Gauge('agent_memory_usage_bytes', 'Memory usage in bytes', ['agent_id'])
AGENT_MEMORY_LIMIT = Gauge('agent_memory_limit_bytes', 'Memory limit in bytes', ['agent_id'])
AGENT_NETWORK_LATENCY = Histogram(
    'agent_network_latency_seconds',
    'Network latency to other regions',
    ['agent_id', 'source_region', 'target_region'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)
)


class AgentMetricsExporter:
    """Exports metrics for a single agent."""
    
    def __init__(self, agent_id: str, region: str, zone: str):
        self.agent_id = agent_id
        self.region = region
        self.zone = zone
        
    def update_metrics(self):
        """Simulate agent metrics updates."""
        # Agent is up
        AGENT_UP.labels(agent_id=self.agent_id, region=self.region, zone=self.zone).set(1)
        
        # Simulate task processing
        if random.random() > 0.1:  # 90% success rate
            AGENT_TASKS_TOTAL.labels(agent_id=self.agent_id, status='success').inc()
            duration = random.expovariate(1/5)  # Average 5 seconds
            AGENT_TASK_DURATION.labels(agent_id=self.agent_id, task_type='standard').observe(duration)
        else:
            AGENT_TASKS_TOTAL.labels(agent_id=self.agent_id, status='failed').inc()
            AGENT_ERRORS.labels(agent_id=self.agent_id, error_type='execution_error').inc()
        
        # Queue depth
        queue_depth = random.randint(0, 100)
        AGENT_QUEUE_DEPTH.labels(agent_id=self.agent_id).set(queue_depth)
        
        # Resource usage
        cpu_usage = random.uniform(20, 80)
        AGENT_CPU.labels(agent_id=self.agent_id).set(cpu_usage)
        
        memory_usage = random.uniform(1e9, 4e9)  # 1-4 GB
        memory_limit = 8e9  # 8 GB
        AGENT_MEMORY.labels(agent_id=self.agent_id).set(memory_usage)
        AGENT_MEMORY_LIMIT.labels(agent_id=self.agent_id).set(memory_limit)
        
        # Network latency to other regions
        regions = ['us-east-1', 'us-west-1', 'eu-central-1', 'ap-southeast-1']
        for target_region in regions:
            if target_region != self.region:
                latency = random.uniform(0.01, 0.5)
                AGENT_NETWORK_LATENCY.labels(
                    agent_id=self.agent_id,
                    source_region=self.region,
                    target_region=target_region
                ).observe(latency)


def main():
    """Main exporter loop."""
    port = int(os.getenv('METRICS_PORT', '8080'))
    agent_id = os.getenv('AGENT_ID', 'agent-001')
    region = os.getenv('REGION', 'us-east-1')
    zone = os.getenv('ZONE', 'us-east-1a')
    
    # Start Prometheus HTTP server
    start_http_server(port)
    print(f"Agent metrics exporter started on port {port}")
    print(f"Agent: {agent_id}, Region: {region}, Zone: {zone}")
    
    exporter = AgentMetricsExporter(agent_id, region, zone)
    
    # Update metrics every 10 seconds
    while True:
        exporter.update_metrics()
        time.sleep(10)


if __name__ == '__main__':
    main()
