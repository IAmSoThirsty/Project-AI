"""
Lifecycle Management API

Start, stop, restart, and update agent lifecycle.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import uuid


class AgentState(str, Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    RESTARTING = "restarting"
    UPDATING = "updating"
    FAILED = "failed"


class LifecycleOperation(str, Enum):
    START = "start"
    STOP = "stop"
    RESTART = "restart"
    UPDATE = "update"
    PAUSE = "pause"
    RESUME = "resume"


class Agent:
    """Agent resource representation"""
    
    def __init__(
        self,
        name: str,
        agent_type: str,
        version: str,
        config: Optional[Dict[str, Any]] = None,
    ):
        self.id = str(uuid.uuid4())
        self.name = name
        self.agent_type = agent_type
        self.version = version
        self.config = config or {}
        self.state = AgentState.STOPPED
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.last_state_change = datetime.utcnow()
        self.restarts = 0
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.agent_type,
            "version": self.version,
            "config": self.config,
            "state": self.state,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_state_change": self.last_state_change.isoformat(),
            "restarts": self.restarts,
        }


class LifecycleAPI:
    """API for agent lifecycle management"""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.operation_history: List[Dict[str, Any]] = []
        
    def create_agent(
        self,
        name: str,
        agent_type: str,
        version: str = "1.0.0",
        config: Optional[Dict[str, Any]] = None,
        auto_start: bool = False,
    ) -> Dict[str, Any]:
        """
        Create a new agent
        
        Args:
            name: Agent name
            agent_type: Agent type
            version: Agent version
            config: Agent configuration
            auto_start: Start agent immediately
            
        Returns:
            Agent details
        """
        agent = Agent(
            name=name,
            agent_type=agent_type,
            version=version,
            config=config,
        )
        
        self.agents[agent.id] = agent
        
        if auto_start:
            self.start_agent(agent.id)
        
        return agent.to_dict()
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent by ID"""
        agent = self.agents.get(agent_id)
        return agent.to_dict() if agent else None
    
    def list_agents(
        self,
        agent_type: Optional[str] = None,
        state: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List agents with optional filters
        
        Args:
            agent_type: Filter by type
            state: Filter by state
            
        Returns:
            List of agents
        """
        agents = list(self.agents.values())
        
        if agent_type:
            agents = [a for a in agents if a.agent_type == agent_type]
        
        if state:
            agents = [a for a in agents if a.state == state]
        
        return [a.to_dict() for a in agents]
    
    def start_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Start an agent
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Operation result
        """
        agent = self.agents.get(agent_id)
        if not agent:
            return None
        
        if agent.state == AgentState.RUNNING:
            return {"error": "Agent already running"}
        
        agent.state = AgentState.STARTING
        agent.last_state_change = datetime.utcnow()
        
        # Simulate startup
        agent.state = AgentState.RUNNING
        agent.updated_at = datetime.utcnow()
        
        operation = self._record_operation(agent_id, LifecycleOperation.START)
        
        return {
            "agent": agent.to_dict(),
            "operation": operation,
        }
    
    def stop_agent(self, agent_id: str, graceful: bool = True) -> Optional[Dict[str, Any]]:
        """
        Stop an agent
        
        Args:
            agent_id: Agent ID
            graceful: Graceful shutdown
            
        Returns:
            Operation result
        """
        agent = self.agents.get(agent_id)
        if not agent:
            return None
        
        if agent.state == AgentState.STOPPED:
            return {"error": "Agent already stopped"}
        
        agent.state = AgentState.STOPPING
        agent.last_state_change = datetime.utcnow()
        
        # Simulate shutdown
        agent.state = AgentState.STOPPED
        agent.updated_at = datetime.utcnow()
        
        operation = self._record_operation(agent_id, LifecycleOperation.STOP, {"graceful": graceful})
        
        return {
            "agent": agent.to_dict(),
            "operation": operation,
        }
    
    def restart_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Restart an agent
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Operation result
        """
        agent = self.agents.get(agent_id)
        if not agent:
            return None
        
        agent.state = AgentState.RESTARTING
        agent.last_state_change = datetime.utcnow()
        agent.restarts += 1
        
        # Simulate restart
        agent.state = AgentState.RUNNING
        agent.updated_at = datetime.utcnow()
        
        operation = self._record_operation(agent_id, LifecycleOperation.RESTART)
        
        return {
            "agent": agent.to_dict(),
            "operation": operation,
        }
    
    def update_agent(
        self,
        agent_id: str,
        version: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        restart: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Update agent configuration
        
        Args:
            agent_id: Agent ID
            version: New version
            config: Updated configuration
            restart: Restart after update
            
        Returns:
            Operation result
        """
        agent = self.agents.get(agent_id)
        if not agent:
            return None
        
        agent.state = AgentState.UPDATING
        agent.last_state_change = datetime.utcnow()
        
        if version:
            agent.version = version
        
        if config:
            agent.config.update(config)
        
        agent.updated_at = datetime.utcnow()
        
        if restart and agent.state == AgentState.RUNNING:
            agent.state = AgentState.RUNNING
            agent.restarts += 1
        else:
            agent.state = AgentState.STOPPED
        
        operation = self._record_operation(
            agent_id,
            LifecycleOperation.UPDATE,
            {"version": version, "restart": restart}
        )
        
        return {
            "agent": agent.to_dict(),
            "operation": operation,
        }
    
    def pause_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Pause agent execution"""
        agent = self.agents.get(agent_id)
        if not agent:
            return None
        
        # Custom state for paused agents
        agent.config["paused"] = True
        agent.updated_at = datetime.utcnow()
        
        operation = self._record_operation(agent_id, LifecycleOperation.PAUSE)
        
        return {
            "agent": agent.to_dict(),
            "operation": operation,
        }
    
    def resume_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Resume agent execution"""
        agent = self.agents.get(agent_id)
        if not agent:
            return None
        
        agent.config["paused"] = False
        agent.updated_at = datetime.utcnow()
        
        operation = self._record_operation(agent_id, LifecycleOperation.RESUME)
        
        return {
            "agent": agent.to_dict(),
            "operation": operation,
        }
    
    def delete_agent(self, agent_id: str, force: bool = False) -> Optional[Dict[str, Any]]:
        """
        Delete an agent
        
        Args:
            agent_id: Agent ID
            force: Force deletion even if running
            
        Returns:
            Deletion result
        """
        agent = self.agents.get(agent_id)
        if not agent:
            return None
        
        if agent.state == AgentState.RUNNING and not force:
            return {"error": "Cannot delete running agent without force flag"}
        
        del self.agents[agent_id]
        
        return {"success": True, "agent_id": agent_id}
    
    def get_operation_history(
        self,
        agent_id: Optional[str] = None,
        operation: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get operation history
        
        Args:
            agent_id: Filter by agent
            operation: Filter by operation type
            limit: Maximum results
            
        Returns:
            List of operations
        """
        history = self.operation_history
        
        if agent_id:
            history = [h for h in history if h["agent_id"] == agent_id]
        
        if operation:
            history = [h for h in history if h["operation"] == operation]
        
        return history[-limit:]
    
    def _record_operation(
        self,
        agent_id: str,
        operation: LifecycleOperation,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Record lifecycle operation"""
        op_record = {
            "id": str(uuid.uuid4()),
            "agent_id": agent_id,
            "operation": operation,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {},
            "status": "completed",
        }
        
        self.operation_history.append(op_record)
        return op_record
