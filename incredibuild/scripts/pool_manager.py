#!/usr/bin/env python3
"""
Cloud Pool Manager - Manages distributed build nodes
"""

import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger("PoolManager")


@dataclass
class BuildNode:
    """Represents a build node in the cloud pool"""
    node_id: str
    instance_id: str
    ip_address: str
    status: str  # initializing, ready, busy, terminating
    cpu_cores: int
    memory_gb: int
    instance_type: str
    availability_zone: str
    cost_per_hour: float
    launched_at: float
    last_heartbeat: float


class CloudPoolManager:
    """Manages cloud-based build node pool"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cloud_config = config.get('cloud', {})
        self.provider = self.cloud_config.get('provider', 'aws')
        
        self.nodes: Dict[str, BuildNode] = {}
        self.available_nodes: List[str] = []
        self.busy_nodes: List[str] = []
        
        self.min_nodes = self.cloud_config.get(self.provider, {}).get('min_nodes', 2)
        self.max_nodes = self.cloud_config.get(self.provider, {}).get('max_nodes', 20)
        
        self._initialized = False
    
    def initialize(self) -> bool:
        """Initialize the cloud pool"""
        logger.info(f"Initializing cloud pool on {self.provider}")
        
        try:
            # In production, this would create actual cloud instances
            # For demo, create mock nodes
            logger.info(f"Creating {self.min_nodes} initial nodes...")
            
            for i in range(self.min_nodes):
                node = self._create_node(f"node-{i+1:03d}")
                self.nodes[node.node_id] = node
                self.available_nodes.append(node.node_id)
                logger.info(f"Created {node.node_id} ({node.instance_type})")
            
            self._initialized = True
            logger.info(f"✅ Pool initialized with {len(self.nodes)} nodes")
            return True
            
        except Exception as e:
            logger.error(f"Pool initialization failed: {e}")
            return False
    
    def _create_node(self, node_id: str) -> BuildNode:
        """Create a new build node"""
        # In production, this would launch actual EC2/GCP/Azure instances
        # For demo, create mock node
        
        instance_type = self.cloud_config.get(self.provider, {}).get('instance_type', 'c5.2xlarge')
        
        # Simulate instance details
        if 'c5.2xlarge' in instance_type:
            cpu_cores = 8
            memory_gb = 16
            cost_per_hour = 0.085 if self.cloud_config.get(self.provider, {}).get('spot_instances') else 0.34
        else:
            cpu_cores = 4
            memory_gb = 8
            cost_per_hour = 0.05
        
        node = BuildNode(
            node_id=node_id,
            instance_id=f"i-{hash(node_id) % 1000000:016x}",
            ip_address=f"10.0.1.{hash(node_id) % 254 + 1}",
            status="ready",
            cpu_cores=cpu_cores,
            memory_gb=memory_gb,
            instance_type=instance_type,
            availability_zone=f"{self.cloud_config.get(self.provider, {}).get('region', 'us-east-1')}a",
            cost_per_hour=cost_per_hour,
            launched_at=time.time(),
            last_heartbeat=time.time(),
        )
        
        return node
    
    def allocate_node(self) -> Optional[BuildNode]:
        """Allocate a node from the pool"""
        if not self._initialized:
            logger.error("Pool not initialized")
            return None
        
        # Check if we have available nodes
        if not self.available_nodes:
            # Try to scale up if under max
            if len(self.nodes) < self.max_nodes:
                logger.info("No available nodes, scaling up...")
                new_node = self._create_node(f"node-{len(self.nodes)+1:03d}")
                self.nodes[new_node.node_id] = new_node
                self.available_nodes.append(new_node.node_id)
                logger.info(f"Created {new_node.node_id}")
            else:
                logger.warning("Pool at max capacity, waiting for available node...")
                # In production, wait or queue the request
                time.sleep(1)
                return self.allocate_node()
        
        # Allocate from available pool
        node_id = self.available_nodes.pop(0)
        self.busy_nodes.append(node_id)
        
        node = self.nodes[node_id]
        node.status = "busy"
        
        logger.debug(f"Allocated {node_id}")
        return node
    
    def release_node(self, node: BuildNode) -> None:
        """Release a node back to the available pool"""
        if node.node_id in self.busy_nodes:
            self.busy_nodes.remove(node.node_id)
            self.available_nodes.append(node.node_id)
            
            node.status = "ready"
            node.last_heartbeat = time.time()
            
            logger.debug(f"Released {node.node_id}")
    
    def scale_up(self, count: int) -> int:
        """Scale up the pool by count nodes"""
        added = 0
        
        for i in range(count):
            if len(self.nodes) >= self.max_nodes:
                logger.warning(f"Cannot scale up, at max capacity ({self.max_nodes})")
                break
            
            node = self._create_node(f"node-{len(self.nodes)+1:03d}")
            self.nodes[node.node_id] = node
            self.available_nodes.append(node.node_id)
            added += 1
            logger.info(f"Scaled up: created {node.node_id}")
        
        return added
    
    def scale_down(self, count: int) -> int:
        """Scale down the pool by count nodes"""
        removed = 0
        
        for i in range(count):
            if len(self.nodes) <= self.min_nodes:
                logger.warning(f"Cannot scale down, at min capacity ({self.min_nodes})")
                break
            
            # Remove from available nodes first
            if self.available_nodes:
                node_id = self.available_nodes.pop()
                node = self.nodes.pop(node_id)
                logger.info(f"Scaled down: terminated {node_id}")
                removed += 1
        
        return removed
    
    def get_pool_status(self) -> Dict[str, Any]:
        """Get current pool status"""
        total_nodes = len(self.nodes)
        available = len(self.available_nodes)
        busy = len(self.busy_nodes)
        
        total_cost = sum(node.cost_per_hour for node in self.nodes.values())
        
        return {
            'total_nodes': total_nodes,
            'available_nodes': available,
            'busy_nodes': busy,
            'utilization': busy / total_nodes if total_nodes > 0 else 0,
            'cost_per_hour': total_cost,
            'provider': self.provider,
            'nodes': [
                {
                    'node_id': node.node_id,
                    'status': node.status,
                    'cpu_cores': node.cpu_cores,
                    'memory_gb': node.memory_gb,
                    'uptime_hours': (time.time() - node.launched_at) / 3600,
                }
                for node in self.nodes.values()
            ]
        }
    
    def cleanup(self) -> None:
        """Cleanup all nodes"""
        logger.info("Terminating all build nodes...")
        
        for node_id, node in list(self.nodes.items()):
            logger.info(f"Terminating {node_id}")
            # In production: terminate cloud instance
            
        self.nodes.clear()
        self.available_nodes.clear()
        self.busy_nodes.clear()
        
        logger.info("✅ All nodes terminated")
