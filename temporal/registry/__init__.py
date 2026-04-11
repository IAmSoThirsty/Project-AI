"""
Distributed Agent Registry with Service Discovery

Provides service discovery, health checking, capability announcement,
load balancing, and failure detection for 1000+ agents across regions.
"""

from .agent_registry import AgentRegistry, AgentInfo, AgentCapabilities, AgentMetrics, AgentStatus
from .service_discovery import ServiceDiscovery, EtcdServiceDiscovery, ConsulServiceDiscovery
from .health_checker import HealthChecker, HealthStatus, HealthCheckResult
from .load_balancer import LoadBalancer, LoadBalancingStrategy, LoadBalancingRequest
from .failure_detector import FailureDetector, FailureEvent, FailureType

__all__ = [
    'AgentRegistry',
    'AgentInfo',
    'AgentCapabilities',
    'AgentMetrics',
    'AgentStatus',
    'ServiceDiscovery',
    'EtcdServiceDiscovery',
    'ConsulServiceDiscovery',
    'HealthChecker',
    'HealthStatus',
    'HealthCheckResult',
    'LoadBalancer',
    'LoadBalancingStrategy',
    'LoadBalancingRequest',
    'FailureDetector',
    'FailureEvent',
    'FailureType',
]
