"""
SubstrateManager — deployment topology and failure handling for Cerberus SASE.
"""

from __future__ import annotations

import time
from enum import Enum


class DeploymentTopology(Enum):
    SINGLE_NODE = "single-node"
    HA_CLUSTER = "ha-cluster"
    GEO_DISTRIBUTED = "geo-distributed"
    EDGE = "edge"


class FailureMode(Enum):
    CLOCK_SKEW = "clock_skew"
    REGIONAL_OUTAGE = "regional_outage"
    NODE_FAILURE = "node_failure"
    NETWORK_PARTITION = "network_partition"


class SubstrateManager:
    def __init__(self, topology: DeploymentTopology = DeploymentTopology.SINGLE_NODE) -> None:
        self._topology = topology
        self._recent_failures = 0
        self._metrics: dict = {}

    def get_health_status(self) -> dict:
        return {
            "topology": self._topology.value,
            "healthy": True,
            "metrics": dict(self._metrics),
            "recent_failures": self._recent_failures,
            "monotonic_time": time.monotonic(),
        }

    def validate_deployment(self) -> dict:
        return {
            "valid": True,
            "topology": self._topology.value,
        }

    def handle_failure(self, failure_mode: FailureMode, context: dict) -> dict:
        self._recent_failures += 1
        if failure_mode == FailureMode.CLOCK_SKEW:
            return {"success": True, "action": "monotonic_enforcement"}
        if failure_mode == FailureMode.REGIONAL_OUTAGE:
            backup = context.get("backup_region", "default")
            return {"success": True, "action": "failover", "backup_region": backup}
        return {"success": True, "action": "recovery"}
