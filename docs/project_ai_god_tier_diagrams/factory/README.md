# Factory Pattern in Project-AI

## Overview

Factory Pattern provides an interface for creating objects without specifying their exact classes. Project-AI uses factories for agent creation, workflow instantiation, and complex object building.

## Agent Factory

```python

# domain/factories/agent_factory.py

import logging
from enum import Enum
from typing import Dict, List
from uuid import UUID, uuid4
from domain.agent.entities import Agent, AgentType

logger = logging.getLogger(__name__)

class AgentFactory:
    """Factory for creating specialized agents."""

    # Agent capability mappings

    AGENT_CAPABILITIES = {
        AgentType.OVERSIGHT: [
            "action_validation",
            "law_enforcement",
            "risk_assessment"
        ],
        AgentType.PLANNER: [
            "task_decomposition",
            "dependency_analysis",
            "resource_allocation"
        ],
        AgentType.VALIDATOR: [
            "input_validation",
            "output_verification",
            "constraint_checking"
        ],
        AgentType.EXPLAINER: [
            "decision_explanation",
            "rationale_generation",
            "transparency_reporting"
        ],
        AgentType.EXECUTOR: [
            "task_execution",
            "command_running",
            "result_reporting"
        ]
    }

    @classmethod
    def create_agent(
        cls,
        agent_type: AgentType,
        name: str,
        custom_capabilities: List[str] = None
    ) -> Agent:
        """Create agent with type-specific capabilities."""
        try:
            capabilities = cls.AGENT_CAPABILITIES.get(agent_type, [])

            if custom_capabilities:
                capabilities.extend(custom_capabilities)

            agent = Agent(
                agent_id=uuid4(),
                name=name,
                agent_type=agent_type,
                capabilities=capabilities
            )

            logger.info(
                f"Created {agent_type.value} agent '{name}' "
                f"with {len(capabilities)} capabilities"
            )

            return agent

        except Exception as e:
            logger.error(f"Agent creation failed: {e}")
            raise

    @classmethod
    def create_agent_pool(
        cls,
        pool_config: Dict[AgentType, int]
    ) -> List[Agent]:
        """Create pool of agents by type."""
        agents = []

        for agent_type, count in pool_config.items():
            for i in range(count):
                name = f"{agent_type.value}_{i+1}"
                agent = cls.create_agent(agent_type, name)
                agents.append(agent)

        logger.info(f"Created agent pool with {len(agents)} agents")
        return agents
```

## Workflow Factory

```python

# domain/factories/workflow_factory.py

import logging
from typing import Dict, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)

class WorkflowFactory:
    """Factory for Temporal workflow creation."""

    @classmethod
    def create_workflow(
        cls,
        workflow_type: str,
        input_params: Dict,
        workflow_id: Optional[str] = None
    ) -> Dict:
        """Create workflow configuration."""
        try:
            if not workflow_id:
                workflow_id = f"{workflow_type}_{uuid4()}"

            config = {
                "workflow_id": workflow_id,
                "workflow_type": workflow_type,
                "input_params": input_params,
                "task_queue": cls._get_task_queue(workflow_type),
                "execution_timeout": cls._get_timeout(workflow_type)
            }

            logger.info(f"Created workflow config: {workflow_type}")
            return config

        except Exception as e:
            logger.error(f"Workflow creation failed: {e}")
            raise

    @classmethod
    def _get_task_queue(cls, workflow_type: str) -> str:
        """Get task queue for workflow type."""
        queue_mapping = {
            "oversight": "oversight-queue",
            "planning": "planning-queue",
            "execution": "execution-queue"
        }
        return queue_mapping.get(workflow_type, "default-queue")

    @classmethod
    def _get_timeout(cls, workflow_type: str) -> int:
        """Get execution timeout for workflow type."""
        timeout_mapping = {
            "oversight": 300,      # 5 minutes
            "planning": 600,       # 10 minutes
            "execution": 3600      # 1 hour
        }
        return timeout_mapping.get(workflow_type, 600)
```

## Testing

```python

# tests/domain/test_factories.py

import pytest
from domain.factories.agent_factory import AgentFactory
from domain.agent.entities import AgentType

class TestAgentFactory:
    """Test agent factory."""

    def test_create_agent(self):
        """Verify agent creation."""
        agent = AgentFactory.create_agent(
            AgentType.OVERSIGHT,
            "test_oversight"
        )

        assert agent.name == "test_oversight"
        assert agent.agent_type == AgentType.OVERSIGHT
        assert "action_validation" in agent.capabilities

    def test_create_agent_pool(self):
        """Verify agent pool creation."""
        pool = AgentFactory.create_agent_pool({
            AgentType.OVERSIGHT: 2,
            AgentType.PLANNER: 1
        })

        assert len(pool) == 3
        assert sum(1 for a in pool if a.agent_type == AgentType.OVERSIGHT) == 2
```

## Related Documentation

- **[Builder Pattern](../builder/README.md)** - Complex object construction
- **[Agent Entities](../domain/domain_models.md)** - Agent domain models
