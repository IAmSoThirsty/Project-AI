# Builder Pattern in Project-AI

## Overview

Builder Pattern constructs complex objects step-by-step. Project-AI uses builders for execution contexts, governance decisions, and configuration objects.

## Execution Context Builder

```python

# domain/builders/execution_context_builder.py

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)

@dataclass
class ExecutionContext:
    """Context for agent execution."""
    context_id: UUID
    agent_id: UUID
    task_id: UUID
    environment: Dict[str, Any]
    permissions: List[str]
    resource_limits: Dict[str, int]
    timeout_seconds: int
    created_at: datetime

class ExecutionContextBuilder:
    """Builder for execution contexts."""

    def __init__(self):
        self._context_id = uuid4()
        self._agent_id: Optional[UUID] = None
        self._task_id: Optional[UUID] = None
        self._environment: Dict = {}
        self._permissions: List[str] = []
        self._resource_limits: Dict = {}
        self._timeout_seconds: int = 300
        logger.debug(f"Initialized ExecutionContextBuilder {self._context_id}")

    def for_agent(self, agent_id: UUID) -> 'ExecutionContextBuilder':
        """Set agent ID."""
        self._agent_id = agent_id
        return self

    def for_task(self, task_id: UUID) -> 'ExecutionContextBuilder':
        """Set task ID."""
        self._task_id = task_id
        return self

    def with_environment(self, key: str, value: Any) -> 'ExecutionContextBuilder':
        """Add environment variable."""
        self._environment[key] = value
        return self

    def with_permission(self, permission: str) -> 'ExecutionContextBuilder':
        """Grant permission."""
        self._permissions.append(permission)
        return self

    def with_resource_limit(self, resource: str, limit: int) -> 'ExecutionContextBuilder':
        """Set resource limit."""
        self._resource_limits[resource] = limit
        return self

    def with_timeout(self, seconds: int) -> 'ExecutionContextBuilder':
        """Set execution timeout."""
        self._timeout_seconds = seconds
        return self

    def build(self) -> ExecutionContext:
        """Build execution context."""
        if not self._agent_id:
            raise ValueError("Agent ID required")
        if not self._task_id:
            raise ValueError("Task ID required")

        context = ExecutionContext(
            context_id=self._context_id,
            agent_id=self._agent_id,
            task_id=self._task_id,
            environment=self._environment,
            permissions=self._permissions,
            resource_limits=self._resource_limits,
            timeout_seconds=self._timeout_seconds,
            created_at=datetime.utcnow()
        )

        logger.info(f"Built execution context {context.context_id}")
        return context
```

## Usage Example

```python

# Example: Building execution context

from domain.builders.execution_context_builder import ExecutionContextBuilder

context = (
    ExecutionContextBuilder()
    .for_agent(agent_id)
    .for_task(task_id)
    .with_environment("API_KEY", "secret")
    .with_permission("file_read")
    .with_permission("network_access")
    .with_resource_limit("max_memory_mb", 512)
    .with_timeout(600)
    .build()
)
```

## Related Documentation

- **[Factory Pattern](../factory/README.md)** - Object creation
- **[Domain Models](../domain/domain_models.md)** - Entities and value objects
