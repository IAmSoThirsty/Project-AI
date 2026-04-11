"""
Control Plane Operator

Main operator for managing agent and workflow lifecycle.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .crd import AgentCRD, WorkflowCRD
from .controller import AgentController, WorkflowController

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ControlPlaneOperator:
    """
    Kubernetes operator for control plane resources
    
    Manages the lifecycle of Agent and Workflow custom resources.
    """
    
    def __init__(self, namespace: str = "default"):
        self.namespace = namespace
        self.agent_controller = AgentController(namespace)
        self.workflow_controller = WorkflowController(namespace)
        self.running = False
        self.watch_tasks = []
        
    async def start(self):
        """Start the operator"""
        logger.info("Starting Control Plane Operator")
        
        # Install CRDs
        await self._install_crds()
        
        # Start watching resources
        self.running = True
        self.watch_tasks = [
            asyncio.create_task(self._watch_agents()),
            asyncio.create_task(self._watch_workflows()),
        ]
        
        logger.info("Control Plane Operator started")
        
    async def stop(self):
        """Stop the operator"""
        logger.info("Stopping Control Plane Operator")
        
        self.running = False
        
        # Cancel watch tasks
        for task in self.watch_tasks:
            task.cancel()
        
        await asyncio.gather(*self.watch_tasks, return_exceptions=True)
        
        logger.info("Control Plane Operator stopped")
        
    async def _install_crds(self):
        """Install custom resource definitions"""
        logger.info("Installing CRDs")
        
        agent_crd = AgentCRD.get_definition()
        workflow_crd = WorkflowCRD.get_definition()
        
        # In real implementation, apply CRDs to Kubernetes
        logger.info(f"Installed CRD: {agent_crd['metadata']['name']}")
        logger.info(f"Installed CRD: {workflow_crd['metadata']['name']}")
        
    async def _watch_agents(self):
        """Watch Agent resources"""
        logger.info("Starting Agent watch loop")
        
        try:
            while self.running:
                # In real implementation, watch Kubernetes API for Agent resources
                # This is a simplified version
                await asyncio.sleep(5)
                
        except asyncio.CancelledError:
            logger.info("Agent watch loop cancelled")
            
    async def _watch_workflows(self):
        """Watch Workflow resources"""
        logger.info("Starting Workflow watch loop")
        
        try:
            while self.running:
                # In real implementation, watch Kubernetes API for Workflow resources
                await asyncio.sleep(5)
                
        except asyncio.CancelledError:
            logger.info("Workflow watch loop cancelled")
            
    async def handle_agent_event(self, event_type: str, agent: Dict[str, Any]):
        """
        Handle Agent resource events
        
        Args:
            event_type: Event type (ADDED, MODIFIED, DELETED)
            agent: Agent resource
        """
        name = agent.get("metadata", {}).get("name")
        
        logger.info(f"Agent event: {event_type} - {name}")
        
        if event_type == "DELETED":
            await self._delete_agent_resources(agent)
        else:
            result = self.agent_controller.reconcile(agent)
            await self._apply_agent_resources(agent, result)
            
    async def handle_workflow_event(self, event_type: str, workflow: Dict[str, Any]):
        """
        Handle Workflow resource events
        
        Args:
            event_type: Event type (ADDED, MODIFIED, DELETED)
            workflow: Workflow resource
        """
        name = workflow.get("metadata", {}).get("name")
        
        logger.info(f"Workflow event: {event_type} - {name}")
        
        if event_type == "DELETED":
            await self._delete_workflow_resources(workflow)
        else:
            result = self.workflow_controller.reconcile(workflow)
            await self._apply_workflow_resources(workflow, result)
            
    async def _apply_agent_resources(self, agent: Dict[str, Any], result: Dict[str, Any]):
        """Apply agent resources to Kubernetes"""
        # In real implementation, apply resources using Kubernetes API
        name = agent.get("metadata", {}).get("name")
        logger.info(f"Applied resources for agent: {name}")
        
    async def _delete_agent_resources(self, agent: Dict[str, Any]):
        """Delete agent resources from Kubernetes"""
        name = agent.get("metadata", {}).get("name")
        logger.info(f"Deleted resources for agent: {name}")
        
    async def _apply_workflow_resources(self, workflow: Dict[str, Any], result: Dict[str, Any]):
        """Apply workflow resources to Kubernetes"""
        name = workflow.get("metadata", {}).get("name")
        logger.info(f"Applied resources for workflow: {name}")
        
    async def _delete_workflow_resources(self, workflow: Dict[str, Any]):
        """Delete workflow resources from Kubernetes"""
        name = workflow.get("metadata", {}).get("name")
        logger.info(f"Deleted resources for workflow: {name}")
        
    def get_metrics(self) -> Dict[str, Any]:
        """Get operator metrics"""
        return {
            "agent_count": len(self.agent_controller.agents),
            "workflow_count": len(self.workflow_controller.workflows),
            "uptime": "N/A",
            "last_reconciliation": datetime.utcnow().isoformat(),
        }


async def main():
    """Main entry point for operator"""
    operator = ControlPlaneOperator()
    
    try:
        await operator.start()
        
        # Keep running until interrupted
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await operator.stop()


if __name__ == "__main__":
    asyncio.run(main())
