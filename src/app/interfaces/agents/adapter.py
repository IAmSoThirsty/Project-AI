"""
Agent interface adapter: Routes AI agent operations through governance pipeline.

Old behavior: Agents → Direct AI calls
New behavior: Agents → Agent Adapter → Router → Governance → AI Orchestrator
"""

from __future__ import annotations

import logging
from typing import Any

from app.core.runtime.router import route_request

logger = logging.getLogger(__name__)


class AgentAdapter:
    """
    Adapter that routes agent operations through governance pipeline.
    
    Usage in agent code:
        adapter = AgentAdapter(agent_id="oversight-agent")
        result = adapter.execute_ai("chat", {"prompt": "Analyze action safety"})
    """

    def __init__(self, agent_id: str, agent_type: str = "generic"):
        """
        Initialize agent adapter.
        
        Args:
            agent_id: Unique agent identifier
            agent_type: Agent type (oversight/planner/validator/explainability)
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        logger.info(f"Agent adapter initialized: {agent_id} ({agent_type})")

    def execute_ai(self, task_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Execute AI operation through orchestrator.
        
        Args:
            task_type: AI task type (chat/image/embedding/analysis)
            payload: Task parameters
            
        Returns:
            Response dict with status, result, metadata
        """
        # Add agent context
        payload["action"] = f"ai.{task_type}"
        payload["task_type"] = task_type
        payload["agent"] = {
            "id": self.agent_id,
            "type": self.agent_type,
        }

        # Route through governance pipeline
        response = route_request(source="agent", payload=payload)
        
        logger.info(
            f"Agent {self.agent_id} AI request: {response['status']}"
        )
        
        return response

    def analyze_action_safety(self, action: str, context: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze action safety (for oversight agents).
        
        Args:
            action: Action to analyze
            context: Execution context
            
        Returns:
            Safety analysis result
        """
        response = self.execute_ai(
            "analysis",
            {
                "prompt": f"Analyze safety of action: {action}",
                "context": context,
            },
        )

        return response

    def plan_task(self, goal: str, constraints: dict[str, Any]) -> dict[str, Any]:
        """
        Plan task execution (for planner agents).
        
        Args:
            goal: Goal to achieve
            constraints: Execution constraints
            
        Returns:
            Task plan
        """
        response = self.execute_ai(
            "chat",
            {
                "prompt": f"Create plan for goal: {goal}",
                "context": constraints,
            },
        )

        return response

    def validate_output(self, output: Any, expected_schema: dict[str, Any]) -> dict[str, Any]:
        """
        Validate output (for validator agents).
        
        Args:
            output: Output to validate
            expected_schema: Expected schema
            
        Returns:
            Validation result
        """
        response = self.execute_ai(
            "analysis",
            {
                "prompt": f"Validate output against schema",
                "output": output,
                "schema": expected_schema,
            },
        )

        return response

    def explain_decision(self, decision: str, context: dict[str, Any]) -> str:
        """
        Explain decision (for explainability agents).
        
        Args:
            decision: Decision to explain
            context: Decision context
            
        Returns:
            Explanation text
        """
        response = self.execute_ai(
            "chat",
            {
                "prompt": f"Explain why this decision was made: {decision}",
                "context": context,
            },
        )

        if response["status"] == "success":
            return response["result"]
        else:
            return f"Explanation failed: {response.get('error', 'Unknown error')}"
