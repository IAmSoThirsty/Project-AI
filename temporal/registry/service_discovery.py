"""
Service Discovery Integration

Provides integration with Consul and etcd for distributed service discovery.
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Callable
from dataclasses import asdict

try:
    import aiohttp
except ImportError:
    aiohttp = None

from .agent_registry import AgentInfo, AgentRegistry

logger = logging.getLogger(__name__)


class ServiceDiscovery(ABC):
    """Abstract service discovery interface"""
    
    @abstractmethod
    async def register_service(self, agent: AgentInfo) -> bool:
        """Register agent as a service"""
        pass
    
    @abstractmethod
    async def deregister_service(self, agent_id: str) -> bool:
        """Deregister agent service"""
        pass
    
    @abstractmethod
    async def discover_services(self, service_name: str) -> List[AgentInfo]:
        """Discover services by name"""
        pass
    
    @abstractmethod
    async def watch_services(self, callback: Callable[[List[AgentInfo]], None]) -> None:
        """Watch for service changes"""
        pass
    
    @abstractmethod
    async def health_check(self, agent_id: str) -> bool:
        """Perform health check"""
        pass


class EtcdServiceDiscovery(ServiceDiscovery):
    """
    etcd-based service discovery implementation.
    
    Uses etcd v3 API for:
    - Service registration with TTL leases
    - Service discovery with prefix scanning
    - Watch-based service monitoring
    - Distributed health checking
    """
    
    def __init__(
        self,
        etcd_endpoints: List[str],
        registry: AgentRegistry,
        service_prefix: str = "/agents",
        ttl: int = 30
    ):
        self.etcd_endpoints = etcd_endpoints
        self.registry = registry
        self.service_prefix = service_prefix
        self.ttl = ttl
        self._session: Optional[aiohttp.ClientSession] = None
        self._leases: Dict[str, str] = {}  # agent_id -> lease_id
        self._watch_task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Initialize etcd connection"""
        if aiohttp is None:
            logger.warning("aiohttp not installed, using mock etcd discovery")
            return
        
        self._session = aiohttp.ClientSession()
        logger.info(f"Connected to etcd at {self.etcd_endpoints}")
    
    async def stop(self):
        """Cleanup etcd connection"""
        if self._watch_task:
            self._watch_task.cancel()
            try:
                await self._watch_task
            except asyncio.CancelledError:
                pass
        
        if self._session:
            await self._session.close()
    
    async def register_service(self, agent: AgentInfo) -> bool:
        """Register agent with etcd"""
        try:
            # Create lease
            lease_id = await self._create_lease(self.ttl)
            if not lease_id:
                return False
            
            # Store agent data under lease
            key = f"{self.service_prefix}/{agent.region}/{agent.agent_id}"
            value = json.dumps(agent.to_dict())
            
            success = await self._put_with_lease(key, value, lease_id)
            if success:
                self._leases[agent.agent_id] = lease_id
                # Start lease keepalive
                asyncio.create_task(self._keepalive_lease(agent.agent_id, lease_id))
                logger.info(f"Registered {agent.agent_id} in etcd with lease {lease_id}")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Failed to register service in etcd: {e}")
            return False
    
    async def deregister_service(self, agent_id: str) -> bool:
        """Deregister agent from etcd"""
        try:
            lease_id = self._leases.pop(agent_id, None)
            if lease_id:
                await self._revoke_lease(lease_id)
            
            # Also delete the key directly
            await self._delete_key(f"{self.service_prefix}/*/{agent_id}")
            logger.info(f"Deregistered {agent_id} from etcd")
            return True
        
        except Exception as e:
            logger.error(f"Failed to deregister service from etcd: {e}")
            return False
    
    async def discover_services(self, service_name: str = "") -> List[AgentInfo]:
        """Discover all registered agents"""
        try:
            prefix = f"{self.service_prefix}/"
            agents = await self._get_prefix(prefix)
            return agents
        
        except Exception as e:
            logger.error(f"Failed to discover services: {e}")
            return []
    
    async def watch_services(self, callback: Callable[[List[AgentInfo]], None]) -> None:
        """Watch for service changes"""
        async def watch_loop():
            while True:
                try:
                    agents = await self.discover_services()
                    callback(agents)
                    await asyncio.sleep(5)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in watch loop: {e}")
                    await asyncio.sleep(5)
        
        self._watch_task = asyncio.create_task(watch_loop())
    
    async def health_check(self, agent_id: str) -> bool:
        """Check if agent is registered"""
        try:
            key = f"{self.service_prefix}/*/{agent_id}"
            agents = await self._get_prefix(key)
            return len(agents) > 0
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    # etcd API helpers (mock implementation for now)
    
    async def _create_lease(self, ttl: int) -> Optional[str]:
        """Create etcd lease"""
        # Mock implementation
        import uuid
        return str(uuid.uuid4())
    
    async def _put_with_lease(self, key: str, value: str, lease_id: str) -> bool:
        """Put key-value with lease"""
        # Mock implementation
        return True
    
    async def _delete_key(self, key: str) -> bool:
        """Delete key from etcd"""
        # Mock implementation
        return True
    
    async def _revoke_lease(self, lease_id: str) -> bool:
        """Revoke etcd lease"""
        # Mock implementation
        return True
    
    async def _get_prefix(self, prefix: str) -> List[AgentInfo]:
        """Get all keys with prefix"""
        # Mock implementation - return agents from local registry
        agents = await self.registry.get_healthy_agents()
        return agents
    
    async def _keepalive_lease(self, agent_id: str, lease_id: str):
        """Keep lease alive"""
        while agent_id in self._leases:
            try:
                # Mock keepalive - in real implementation, send keepalive to etcd
                await asyncio.sleep(self.ttl // 3)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Lease keepalive failed for {agent_id}: {e}")
                break


class ConsulServiceDiscovery(ServiceDiscovery):
    """
    Consul-based service discovery implementation.
    
    Uses Consul HTTP API for:
    - Service registration with health checks
    - Service discovery via catalog API
    - Health monitoring
    - DNS-based service resolution
    """
    
    def __init__(
        self,
        consul_url: str,
        registry: AgentRegistry,
        datacenter: str = "dc1"
    ):
        self.consul_url = consul_url.rstrip('/')
        self.registry = registry
        self.datacenter = datacenter
        self._session: Optional[aiohttp.ClientSession] = None
        self._watch_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Initialize Consul connection"""
        if aiohttp is None:
            logger.warning("aiohttp not installed, using mock consul discovery")
            return
        
        self._session = aiohttp.ClientSession()
        logger.info(f"Connected to Consul at {self.consul_url}")
    
    async def stop(self):
        """Cleanup Consul connection"""
        if self._watch_task:
            self._watch_task.cancel()
            try:
                await self._watch_task
            except asyncio.CancelledError:
                pass
        
        if self._session:
            await self._session.close()
    
    async def register_service(self, agent: AgentInfo) -> bool:
        """Register agent with Consul"""
        try:
            service_def = {
                "ID": agent.agent_id,
                "Name": "sovereign-agent",
                "Tags": [
                    agent.region,
                    *[f"lang:{lang}" for lang in agent.capabilities.languages],
                    *[f"tool:{tool}" for tool in agent.capabilities.tools],
                    *[f"spec:{spec}" for spec in agent.capabilities.specializations],
                ],
                "Address": agent.endpoint.split(':')[0] if ':' in agent.endpoint else agent.endpoint,
                "Port": int(agent.endpoint.split(':')[1]) if ':' in agent.endpoint else 8080,
                "Meta": {
                    "region": agent.region,
                    "version": agent.version,
                    "max_tasks": str(agent.capabilities.max_concurrent_tasks),
                },
                "Check": {
                    "HTTP": f"http://{agent.endpoint}/health",
                    "Interval": "10s",
                    "Timeout": "5s",
                }
            }
            
            success = await self._register_consul_service(service_def)
            if success:
                logger.info(f"Registered {agent.agent_id} in Consul")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Failed to register service in Consul: {e}")
            return False
    
    async def deregister_service(self, agent_id: str) -> bool:
        """Deregister agent from Consul"""
        try:
            await self._deregister_consul_service(agent_id)
            logger.info(f"Deregistered {agent_id} from Consul")
            return True
        
        except Exception as e:
            logger.error(f"Failed to deregister service from Consul: {e}")
            return False
    
    async def discover_services(self, service_name: str = "sovereign-agent") -> List[AgentInfo]:
        """Discover services from Consul"""
        try:
            services = await self._query_consul_services(service_name)
            return services
        
        except Exception as e:
            logger.error(f"Failed to discover services: {e}")
            return []
    
    async def watch_services(self, callback: Callable[[List[AgentInfo]], None]) -> None:
        """Watch for service changes using blocking queries"""
        async def watch_loop():
            index = 0
            while True:
                try:
                    agents, new_index = await self._watch_consul_services(index)
                    if new_index > index:
                        index = new_index
                        callback(agents)
                    await asyncio.sleep(1)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in watch loop: {e}")
                    await asyncio.sleep(5)
        
        self._watch_task = asyncio.create_task(watch_loop())
    
    async def health_check(self, agent_id: str) -> bool:
        """Check agent health via Consul"""
        try:
            return await self._check_consul_health(agent_id)
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    # Consul API helpers (mock implementation)
    
    async def _register_consul_service(self, service_def: dict) -> bool:
        """Register service in Consul"""
        # Mock implementation
        return True
    
    async def _deregister_consul_service(self, service_id: str) -> bool:
        """Deregister service from Consul"""
        # Mock implementation
        return True
    
    async def _query_consul_services(self, service_name: str) -> List[AgentInfo]:
        """Query services from Consul catalog"""
        # Mock implementation - return from local registry
        agents = await self.registry.get_healthy_agents()
        return agents
    
    async def _watch_consul_services(self, index: int) -> tuple[List[AgentInfo], int]:
        """Watch services with blocking query"""
        # Mock implementation
        agents = await self.registry.get_healthy_agents()
        return agents, index + 1
    
    async def _check_consul_health(self, service_id: str) -> bool:
        """Check service health in Consul"""
        # Mock implementation
        agent = await self.registry.get_agent(service_id)
        return agent is not None
