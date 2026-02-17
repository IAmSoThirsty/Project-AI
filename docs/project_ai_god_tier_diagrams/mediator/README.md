# Mediator Pattern in Project-AI

## Overview

Mediator Pattern centralizes complex communications and control logic between objects. Project-AI's CouncilHub acts as a mediator for agent collaboration.

## CouncilHub Mediator

```python

# domain/mediators/council_hub.py

import logging
from typing import Dict, List
from uuid import UUID

logger = logging.getLogger(__name__)

class CouncilHub:
    """Mediator for agent council collaboration."""

    def __init__(self):
        self.agents: Dict[UUID, Any] = {}
        self.active_councils: Dict[str, Dict] = {}
        logger.info("Initialized CouncilHub mediator")

    def register_agent(self, agent_id: UUID, agent: Any) -> None:
        """Register agent with hub."""
        self.agents[agent_id] = agent
        logger.info(f"Registered agent {agent_id} with CouncilHub")

    def convene_council(
        self,
        council_name: str,
        agent_ids: List[UUID],
        topic: str
    ) -> str:
        """Convene council and coordinate discussion."""
        council_id = f"{council_name}_{len(self.active_councils)}"

        self.active_councils[council_id] = {
            "name": council_name,
            "agents": agent_ids,
            "topic": topic,
            "votes": {}
        }

        logger.info(f"Convened council {council_id} with {len(agent_ids)} agents")
        return council_id

    def coordinate_vote(self, council_id: str) -> Dict:
        """Coordinate voting among council members."""
        council = self.active_councils.get(council_id)
        if not council:
            raise ValueError(f"Council {council_id} not found")

        # Collect votes from agents

        for agent_id in council["agents"]:
            agent = self.agents.get(agent_id)
            if agent:
                vote = agent.cast_vote(council["topic"])
                council["votes"][str(agent_id)] = vote

        logger.info(f"Coordinated vote for council {council_id}")
        return council["votes"]
```

## Related Documentation

- **[Agent Execution](../../workflow/temporal_workflows.md)** - Agent orchestration
- **[Factory Pattern](../factory/README.md)** - Agent creation
