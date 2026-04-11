#!/usr/bin/env python3
"""
Workflow Metrics Exporter

Exports Temporal workflow metrics for monitoring.
"""

from prometheus_client import start_http_server, Counter, Histogram, Gauge
import time
import random
import os

# Workflow metrics
WORKFLOW_COMPLETED = Counter(
    'temporal_workflow_completed_total',
    'Total completed workflows',
    ['workflow_type']
)
WORKFLOW_FAILED = Counter(
    'temporal_workflow_failed_total',
    'Total failed workflows',
    ['workflow_type']
)
WORKFLOW_RUNNING = Gauge(
    'temporal_workflow_running',
    'Currently running workflows',
    ['workflow_type']
)
WORKFLOW_DURATION = Histogram(
    'temporal_workflow_execution_duration_seconds',
    'Workflow execution duration',
    ['workflow_type'],
    buckets=(1, 5, 10, 30, 60, 120, 300, 600, 1800, 3600)
)
WORKFLOW_RETRY = Counter(
    'temporal_workflow_retry_total',
    'Workflow retries',
    ['workflow_type']
)

# Activity metrics
ACTIVITY_COMPLETED = Counter(
    'temporal_activity_completed_total',
    'Total completed activities',
    ['activity_type']
)
ACTIVITY_FAILED = Counter(
    'temporal_activity_failed_total',
    'Total failed activities',
    ['activity_type']
)
ACTIVITY_TIMEOUT = Counter(
    'temporal_activity_timeout_total',
    'Activity timeouts',
    ['activity_type']
)

# Task queue metrics
TASK_QUEUE_DEPTH = Gauge(
    'temporal_task_queue_depth',
    'Tasks waiting in queue',
    ['task_queue']
)
TASK_QUEUE_CONSUMERS = Gauge(
    'temporal_task_queue_consumers',
    'Number of queue consumers',
    ['task_queue']
)

# Worker metrics
WORKER_SLOTS_TOTAL = Gauge(
    'temporal_worker_task_slots_total',
    'Total worker task slots',
    ['worker_pool']
)
WORKER_SLOTS_AVAILABLE = Gauge(
    'temporal_worker_task_slots_available',
    'Available worker task slots',
    ['worker_pool']
)
WORKER_TASK_LATENCY = Histogram(
    'temporal_worker_task_latency_seconds',
    'Time from task scheduled to started',
    ['worker_id'],
    buckets=(0.1, 0.5, 1, 2, 5, 10, 30)
)


class WorkflowMetricsExporter:
    """Exports workflow and activity metrics."""
    
    def __init__(self):
        self.workflow_types = [
            'agent_sync',
            'data_processing',
            'notification',
            'scheduled_task',
            'batch_job'
        ]
        self.activity_types = [
            'database_query',
            'api_call',
            'file_processing',
            'notification_send'
        ]
        self.task_queues = ['default', 'high-priority', 'batch']
        
    def update_metrics(self):
        """Simulate workflow metrics updates."""
        # Workflow execution
        for workflow_type in self.workflow_types:
            # Running workflows
            running = random.randint(10, 100)
            WORKFLOW_RUNNING.labels(workflow_type=workflow_type).set(running)
            
            # Completions
            if random.random() > 0.02:  # 98% success rate
                WORKFLOW_COMPLETED.labels(workflow_type=workflow_type).inc()
                duration = random.expovariate(1/60)  # Average 1 minute
                WORKFLOW_DURATION.labels(workflow_type=workflow_type).observe(duration)
            else:
                WORKFLOW_FAILED.labels(workflow_type=workflow_type).inc()
                if random.random() > 0.5:
                    WORKFLOW_RETRY.labels(workflow_type=workflow_type).inc()
        
        # Activity execution
        for activity_type in self.activity_types:
            if random.random() > 0.05:  # 95% success rate
                ACTIVITY_COMPLETED.labels(activity_type=activity_type).inc()
            else:
                ACTIVITY_FAILED.labels(activity_type=activity_type).inc()
                if random.random() > 0.7:
                    ACTIVITY_TIMEOUT.labels(activity_type=activity_type).inc()
        
        # Task queues
        for task_queue in self.task_queues:
            depth = random.randint(0, 1000)
            consumers = random.randint(5, 20)
            TASK_QUEUE_DEPTH.labels(task_queue=task_queue).set(depth)
            TASK_QUEUE_CONSUMERS.labels(task_queue=task_queue).set(consumers)
        
        # Worker pools
        for i in range(3):
            pool = f'worker-pool-{i}'
            total_slots = 100
            available = random.randint(20, 80)
            WORKER_SLOTS_TOTAL.labels(worker_pool=pool).set(total_slots)
            WORKER_SLOTS_AVAILABLE.labels(worker_pool=pool).set(available)
            
            # Worker latency
            worker_id = f'worker-{i}'
            latency = random.uniform(0.1, 5)
            WORKER_TASK_LATENCY.labels(worker_id=worker_id).observe(latency)


def main():
    """Main exporter loop."""
    port = int(os.getenv('METRICS_PORT', '9091'))
    
    # Start Prometheus HTTP server
    start_http_server(port)
    print(f"Workflow metrics exporter started on port {port}")
    
    exporter = WorkflowMetricsExporter()
    
    # Update metrics every 15 seconds
    while True:
        exporter.update_metrics()
        time.sleep(15)


if __name__ == '__main__':
    main()
