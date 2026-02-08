# Command Pattern (CQRS) in Project-AI

## Overview

Project-AI implements Command Query Responsibility Segregation (CQRS) to separate write operations (commands) from read operations (queries). Commands modify state and emit events; queries read denormalized views.

## CQRS Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    CQRS Flow                               │
└────────────────────────────────────────────────────────────┘

Client Request
      │
      ├──► Command?
      │         │
      │         ▼
      │    ┌─────────────┐
      │    │Command Bus  │
      │    └──────┬──────┘
      │           │
      │           ▼
      │    ┌─────────────────┐
      │    │Command Handler  │
      │    │                 │
      │    │ 1. Validate     │
      │    │ 2. Load Agg     │
      │    │ 3. Execute      │
      │    │ 4. Save Agg     │
      │    │ 5. Emit Events  │
      │    └────────┬────────┘
      │             │
      │             ▼
      │        [Write DB]
      │             │
      │             ▼
      │        [Event Bus] ──► Event Handlers ──► Update Read Models
      │                                                    │
      │                                                    ▼
      └──► Query?                                    [Read DB]
                │                                          ▲
                ▼                                          │
         ┌─────────────┐                                  │
         │Query Handler│──────────────────────────────────┘
         └─────────────┘
```

## Command Base Classes

```python
# application/commands/base.py
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4
import logging

logger = logging.getLogger(__name__)

@dataclass
class Command(ABC):
    """Base command for CQRS write operations."""
    
    command_id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_id: Optional[UUID] = None
    correlation_id: Optional[UUID] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        logger.debug(f"Created command {self.__class__.__name__} with ID {self.command_id}")
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate command (override in subclasses)."""
        return True, None

@dataclass
class CommandResult:
    """Result of command execution."""
    success: bool
    aggregate_id: Optional[UUID] = None
    error: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    events_emitted: int = 0
```

---

## Command Catalog

### User Management Commands

```python
# application/commands/user_commands.py
from dataclasses import dataclass
from typing import Optional
from uuid import UUID
import re
from application.commands.base import Command

@dataclass
class RegisterUserCommand(Command):
    """Command: Register new user."""
    username: str = ""
    email: str = ""
    password: str = ""
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate registration data."""
        # Username validation
        if not 3 <= len(self.username) <= 50:
            return False, "Username must be 3-50 characters"
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', self.username):
            return False, "Username can only contain alphanumeric, underscore, hyphen"
        
        # Email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, self.email):
            return False, "Invalid email format"
        
        # Password validation
        if len(self.password) < 8:
            return False, "Password must be at least 8 characters"
        
        if not any(c.isupper() for c in self.password):
            return False, "Password must contain uppercase letter"
        
        if not any(c.isdigit() for c in self.password):
            return False, "Password must contain digit"
        
        return True, None

@dataclass
class LoginUserCommand(Command):
    """Command: Authenticate user and create session."""
    username: str = ""
    password: str = ""
    ip_address: str = ""
    session_duration_hours: int = 24
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate login data."""
        if not self.username:
            return False, "Username required"
        if not self.password:
            return False, "Password required"
        if not self.ip_address:
            return False, "IP address required"
        return True, None

@dataclass
class ChangePasswordCommand(Command):
    """Command: Change user password."""
    user_id: UUID = None
    old_password: str = ""
    new_password: str = ""
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate password change."""
        if not self.user_id:
            return False, "User ID required"
        if len(self.new_password) < 8:
            return False, "New password must be at least 8 characters"
        return True, None

@dataclass
class GrantPermissionCommand(Command):
    """Command: Grant permission to user."""
    user_id: UUID = None
    resource: str = ""
    action: str = ""
    granted_by: str = ""
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate permission grant."""
        if not self.user_id:
            return False, "User ID required"
        if not self.resource:
            return False, "Resource required"
        if self.action not in ["read", "write", "delete", "execute", "*"]:
            return False, "Invalid action"
        return True, None
```

### AI Governance Commands

```python
# application/commands/governance_commands.py
from dataclasses import dataclass
from typing import Dict, Optional
from uuid import UUID
from application.commands.base import Command

@dataclass
class EvaluateActionCommand(Command):
    """Command: Evaluate action against governance laws."""
    action: str = ""
    context: Dict = field(default_factory=dict)
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate evaluation request."""
        if not self.action or not self.action.strip():
            return False, "Action cannot be empty"
        if not isinstance(self.context, dict):
            return False, "Context must be dictionary"
        return True, None

@dataclass
class ActivateOverrideCommand(Command):
    """Command: Activate emergency override."""
    override_type: str = ""
    justification: str = ""
    activated_by: str = ""
    duration_minutes: int = 60
    master_password: str = ""
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate override activation."""
        if not self.override_type:
            return False, "Override type required"
        if len(self.justification) < 20:
            return False, "Justification must be at least 20 characters"
        if not self.master_password:
            return False, "Master password required"
        if self.duration_minutes <= 0 or self.duration_minutes > 1440:
            return False, "Duration must be 1-1440 minutes"
        return True, None

@dataclass
class AddToBlackVaultCommand(Command):
    """Command: Add forbidden content to Black Vault."""
    content: str = ""
    reason: str = ""
    added_by: str = ""
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate Black Vault addition."""
        if not self.content:
            return False, "Content required"
        if not self.reason:
            return False, "Reason required"
        return True, None
```

### Memory Management Commands

```python
# application/commands/memory_commands.py
from dataclasses import dataclass
from typing import Dict, Optional
from uuid import UUID
from application.commands.base import Command

@dataclass
class StartConversationCommand(Command):
    """Command: Start new conversation."""
    user_id: UUID = None
    initial_message: str = ""
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate conversation start."""
        if not self.user_id:
            return False, "User ID required"
        if not self.initial_message:
            return False, "Initial message required"
        return True, None

@dataclass
class AddMemoryEntryCommand(Command):
    """Command: Add conversation turn to memory."""
    user_id: UUID = None
    user_message: str = ""
    ai_response: str = ""
    metadata: Dict = field(default_factory=dict)
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate memory entry."""
        if not self.user_id:
            return False, "User ID required"
        if not self.user_message:
            return False, "User message required"
        if not self.ai_response:
            return False, "AI response required"
        return True, None

@dataclass
class ConsolidateKnowledgeCommand(Command):
    """Command: Extract knowledge from conversation entry."""
    user_id: UUID = None
    entry_id: UUID = None
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate knowledge consolidation."""
        if not self.user_id:
            return False, "User ID required"
        if not self.entry_id:
            return False, "Entry ID required"
        return True, None

@dataclass
class PurgeOldMemoriesCommand(Command):
    """Command: Remove old memories per retention policy."""
    user_id: UUID = None
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate purge command."""
        if not self.user_id:
            return False, "User ID required"
        return True, None
```

### Agent Execution Commands

```python
# application/commands/agent_commands.py
from dataclasses import dataclass
from typing import Dict, List, Optional
from uuid import UUID
from application.commands.base import Command

@dataclass
class CreateAgentCommand(Command):
    """Command: Create new agent."""
    agent_name: str = ""
    agent_type: str = ""
    capabilities: List[str] = field(default_factory=list)
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate agent creation."""
        if not self.agent_name:
            return False, "Agent name required"
        if self.agent_type not in ["oversight", "planner", "validator", "explainer", "executor"]:
            return False, "Invalid agent type"
        return True, None

@dataclass
class AssignTaskCommand(Command):
    """Command: Assign task to agent."""
    agent_id: UUID = None
    task_description: str = ""
    task_params: Dict = field(default_factory=dict)
    priority: str = "normal"
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate task assignment."""
        if not self.agent_id:
            return False, "Agent ID required"
        if not self.task_description:
            return False, "Task description required"
        if self.priority not in ["low", "normal", "high", "critical"]:
            return False, "Invalid priority"
        return True, None

@dataclass
class StartWorkflowCommand(Command):
    """Command: Start Temporal workflow."""
    workflow_type: str = ""
    input_params: Dict = field(default_factory=dict)
    workflow_id: Optional[str] = None
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate workflow start."""
        if not self.workflow_type:
            return False, "Workflow type required"
        return True, None

@dataclass
class ConveneCouncilCommand(Command):
    """Command: Convene agent council for decision."""
    council_name: str = ""
    agent_ids: List[UUID] = field(default_factory=list)
    decision_topic: str = ""
    voting_threshold: float = 0.67
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate council convening."""
        if not self.council_name:
            return False, "Council name required"
        if len(self.agent_ids) < 3:
            return False, "Council needs at least 3 agents"
        if not self.decision_topic:
            return False, "Decision topic required"
        if not 0.5 <= self.voting_threshold <= 1.0:
            return False, "Threshold must be 0.5-1.0"
        return True, None
```

---

## Command Bus

```python
# application/command_bus.py
from typing import Callable, Dict, Type
import logging
from application.commands.base import Command, CommandResult

logger = logging.getLogger(__name__)

class CommandBus:
    """Command bus for routing commands to handlers."""
    
    def __init__(self):
        self._handlers: Dict[Type[Command], Callable] = {}
        logger.info("Initialized command bus")
    
    def register(self, command_type: Type[Command], handler: Callable[[Command], CommandResult]) -> None:
        """Register command handler."""
        self._handlers[command_type] = handler
        logger.info(f"Registered handler for {command_type.__name__}")
    
    def dispatch(self, command: Command) -> CommandResult:
        """Dispatch command to registered handler."""
        try:
            # Validate command
            is_valid, error = command.validate()
            if not is_valid:
                logger.warning(f"Command validation failed: {error}")
                return CommandResult(success=False, error=error)
            
            # Find handler
            handler = self._handlers.get(type(command))
            if not handler:
                error = f"No handler registered for {type(command).__name__}"
                logger.error(error)
                return CommandResult(success=False, error=error)
            
            # Execute handler
            logger.info(f"Dispatching {type(command).__name__} (ID: {command.command_id})")
            result = handler(command)
            
            if result.success:
                logger.info(
                    f"Command {type(command).__name__} succeeded "
                    f"(emitted {result.events_emitted} events)"
                )
            else:
                logger.error(f"Command {type(command).__name__} failed: {result.error}")
            
            return result
            
        except Exception as e:
            logger.error(f"Command dispatch failed: {e}", exc_info=True)
            return CommandResult(success=False, error=str(e))
```

---

## Command Handlers (Examples)

See **[Command Handlers](command_handlers.md)** for detailed implementations.

---

## Command Validation

```python
# application/commands/validation.py
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class CommandValidator:
    """Centralized command validation with business rules."""
    
    @staticmethod
    def validate_user_registration(username: str, email: str, password: str) -> tuple[bool, Optional[str]]:
        """Validate user registration data."""
        # Username rules
        if not 3 <= len(username) <= 50:
            return False, "Username must be 3-50 characters"
        
        # Check for profanity (simple example)
        profanity_list = ["badword1", "badword2"]  # Production: use library
        if any(word in username.lower() for word in profanity_list):
            return False, "Username contains inappropriate content"
        
        # Email rules
        if "@" not in email or "." not in email.split("@")[-1]:
            return False, "Invalid email format"
        
        # Password strength
        if len(password) < 12:
            return False, "Password must be at least 12 characters (recommended)"
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        if not (has_upper and has_lower and has_digit and has_special):
            return False, "Password must contain uppercase, lowercase, digit, and special character"
        
        return True, None
    
    @staticmethod
    def validate_governance_action(action: str, context: Dict) -> tuple[bool, Optional[str]]:
        """Validate governance action evaluation."""
        required_context = ["is_user_order", "endangers_humans", "endangers_self"]
        
        for key in required_context:
            if key not in context:
                return False, f"Missing required context: {key}"
        
        # Check for obviously dangerous actions
        dangerous_keywords = ["rm -rf", "drop table", "delete *", "format c:"]
        if any(keyword in action.lower() for keyword in dangerous_keywords):
            logger.warning(f"Dangerous action detected: {action}")
            # Still allow if properly flagged in context
        
        return True, None
```

---

## Integration with Event Sourcing

```python
# application/commands/event_sourced_handler.py
import logging
from typing import Generic, TypeVar
from uuid import UUID
from application.commands.base import Command, CommandResult
from domain.base.aggregate import AggregateRoot
from infrastructure.event_store.event_store import EventStore

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=AggregateRoot)

class EventSourcedCommandHandler(Generic[T]):
    """Base handler for event-sourced commands."""
    
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
    
    def handle(self, command: Command, aggregate_id: UUID) -> CommandResult:
        """Handle command with event sourcing."""
        try:
            # Load aggregate from event history
            events = self.event_store.load_events(aggregate_id)
            aggregate = self._create_aggregate(aggregate_id)
            aggregate.load_from_history(events)
            
            # Execute command on aggregate
            self._execute_command(command, aggregate)
            
            # Get uncommitted events
            new_events = aggregate.get_uncommitted_events()
            
            # Persist events
            for event in new_events:
                self.event_store.append_event(event)
            
            logger.info(
                f"Persisted {len(new_events)} events for aggregate {aggregate_id}"
            )
            
            return CommandResult(
                success=True,
                aggregate_id=aggregate_id,
                events_emitted=len(new_events)
            )
            
        except Exception as e:
            logger.error(f"Event-sourced command failed: {e}")
            return CommandResult(success=False, error=str(e))
    
    def _create_aggregate(self, aggregate_id: UUID) -> T:
        """Create new aggregate instance (override in subclasses)."""
        raise NotImplementedError
    
    def _execute_command(self, command: Command, aggregate: T) -> None:
        """Execute command on aggregate (override in subclasses)."""
        raise NotImplementedError
```

---

## Testing

```python
# tests/application/test_commands.py
import pytest
from uuid import uuid4
from application.commands.user_commands import RegisterUserCommand, LoginUserCommand
from application.commands.governance_commands import EvaluateActionCommand
from application.command_bus import CommandBus

class TestCommands:
    """Test command validation and execution."""
    
    def test_command_validation_success(self):
        """Verify valid command passes validation."""
        cmd = RegisterUserCommand(
            username="validuser",
            email="valid@example.com",
            password="SecurePass123!"
        )
        
        is_valid, error = cmd.validate()
        assert is_valid
        assert error is None
    
    def test_command_validation_failure(self):
        """Verify invalid command fails validation."""
        cmd = RegisterUserCommand(
            username="ab",  # Too short
            email="invalid-email",
            password="weak"
        )
        
        is_valid, error = cmd.validate()
        assert not is_valid
        assert error is not None
    
    def test_command_bus_dispatch(self):
        """Verify command bus routing."""
        bus = CommandBus()
        handled = []
        
        def handler(cmd):
            handled.append(cmd)
            return CommandResult(success=True)
        
        bus.register(EvaluateActionCommand, handler)
        
        cmd = EvaluateActionCommand(
            action="test_action",
            context={"is_user_order": True}
        )
        
        result = bus.dispatch(cmd)
        
        assert result.success
        assert len(handled) == 1
```

## Related Documentation

- **[Command Handlers](command_handlers.md)** - Handler implementations
- **[Command Validation](command_validation.md)** - Validation rules
- **[Domain Events](../domain/domain_events.md)** - Event emission from commands
- **[Query Pattern](../query/README.md)** - CQRS query side
