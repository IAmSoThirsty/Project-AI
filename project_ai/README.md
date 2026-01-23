# PACE Architecture Package - README

## Overview

The PACE (Policy-Agent-Cognition-Engine) Architecture Package provides a comprehensive framework for building intelligent, ethical, and extensible AI systems within Project-AI. This package implements a modular architecture that coordinates policies, agents, cognitive processes, and execution workflows.

## Package Structure

```
project_ai/
├── __init__.py                          # Package root
├── main.py                              # Runnable demo entrypoint
└── engine/                              # Core PACE engine
    ├── __init__.py                      # PACEEngine class
    ├── identity/
    │   ├── __init__.py
    │   └── identity_manager.py          # Identity and bonding management
    ├── policy/
    │   ├── __init__.py
    │   └── policy_engine.py             # Policy enforcement
    ├── cognition/
    │   ├── __init__.py
    │   └── deliberation_engine.py       # Reasoning and planning
    ├── workflow/
    │   ├── __init__.py
    │   └── workflow_engine.py           # Workflow orchestration
    ├── capabilities/
    │   ├── __init__.py
    │   └── capability_invoker.py        # Capability execution
    ├── agents/
    │   ├── __init__.py
    │   └── agent_coordinator.py         # Agent coordination
    ├── state/
    │   ├── __init__.py
    │   └── state_manager.py             # State persistence
    └── io/
        ├── __init__.py
        └── io_router.py                 # I/O routing
```

## Documentation Files

The architecture is fully documented in the repository root:

1. **[ENGINE_SPEC.md](../ENGINE_SPEC.md)** - Engine specification and runtime loop
1. **[PACE_ARCHITECTURE.md](../PACE_ARCHITECTURE.md)** - Overall architecture design
1. **[MODULE_CONTRACTS.md](../MODULE_CONTRACTS.md)** - Module interface contracts
1. **[IDENTITY_ENGINE.md](../IDENTITY_ENGINE.md)** - Identity management specification
1. **[CAPABILITY_MODEL.md](../CAPABILITY_MODEL.md)** - Capability system design
1. **[AGENT_MODEL.md](../AGENT_MODEL.md)** - Agent coordination model
1. **[WORKFLOW_ENGINE.md](../WORKFLOW_ENGINE.md)** - Workflow execution engine
1. **[STATE_MODEL.md](../STATE_MODEL.md)** - State management model
1. **[INTEGRATION_LAYER.md](../INTEGRATION_LAYER.md)** - Integration interfaces

## Quick Start

### Installation

The PACE package is part of Project-AI and requires no separate installation if you have the Project-AI repository:

```bash
git clone https://github.com/IAmSoThirsty/Project-AI.git
cd Project-AI
```

### Running the Demo

Run the included demo to see the PACE engine in action:

```bash
python3 -m project_ai.main
```

This will demonstrate:

1. Engine initialization
1. Bonding protocol execution
1. Handling a diagnostic request

### Basic Usage

```python
from project_ai.engine import PACEEngine

# Initialize engine
engine = PACEEngine()

# Run bonding protocol
bonding_profile = {
    "name": "Project-AI (User Bonded)",
    "values": {"safety": "high", "clarity": "high"},
    "temperament": {"direct": True, "verbose": False},
    "relationship": {"operator": "User"},
    "constraints": {"respect_operator": True},
}
identity = engine.run_bonding_protocol(bonding_profile)

# Handle input
payload = {
    "type": "diagnostic",
    "message": "Check system status",
}
response = engine.handle_input("cli", payload)

print(f"Identity Phase: {response['identity_phase']}")
print(f"Explanation: {response['explanation']}")
```

## Core Concepts

### Identity Phases

The PACE engine operates in two identity phases:

1. **Unbonded** - Bootstrap mode with conservative policies
1. **Bonded** - Full identity active with bonding relationship

### Main Runtime Loop

Every input goes through this flow:

1. **Input** → I/O Router
1. **Authentication** → Identity Manager
1. **Policy Validation** → Policy Engine
1. **Cognitive Planning** → Deliberation Engine
1. **Workflow Construction** → Workflow Engine
1. **Agent Assignment** → Agent Coordinator
1. **Execution** → Capability Invoker
1. **State Recording** → State Manager
1. **Output** → I/O Router

### Built-in Capabilities

The system includes these built-in capabilities:

- `analyze_goal` - Analyze goal complexity
- `summarize_context` - Summarize contextual information
- `evaluate_risk` - Evaluate action risk
- `policy_check` - Validate against policy
- `memory_read` - Read from state
- `memory_write` - Write to state
- `handle_goal_step` - Execute goal step

## Configuration

Configure the engine with a config dictionary:

```python
config = {
    "identity": {
        # Identity configuration
    },
    "state": {
        # State management configuration
    },
    "capabilities": {
        "custom_capabilities": {
            # Add custom capabilities here
        }
    }
}

engine = PACEEngine(config)
```

## Integration with Project-AI

The PACE engine integrates with existing Project-AI systems:

### Triumvirate Integration

```python
# Consult ethics, security, and logic agents
from src.cognition.galahad.engine import GalahadEngine
from src.cognition.cerberus.engine import CerberusEngine
from src.cognition.codex.engine import CodexEngine

# Ethics check
ethics_assessment = galahad.assess_ethics(action)

# Security check  
security_assessment = cerberus.assess_security(action)

# Logic validation
logic_assessment = codex.validate_logic(reasoning)
```

### Temporal Workflows

The PACE engine can integrate with Temporal.io for durable workflows:

```python
# Execute PACE workflow via Temporal
from temporalio.client import Client

client = await Client.connect("localhost:7233")
result = await client.execute_workflow(
    "pace_workflow",
    workflow_params
)
```

### Existing Core Systems

PACE complements existing Project-AI core systems in `src/app/core/`:

- **ai_systems.py** - Six core AI systems (FourLaws, AIPersona, etc.)
- **user_manager.py** - User authentication
- **intelligence_engine.py** - OpenAI integration
- **And more...**

PACE provides a unified orchestration layer on top of these systems.

## Extending PACE

### Adding Custom Capabilities

```python
def my_custom_capability(inputs: dict) -> dict:
    # Your implementation
    return {"result": "success"}

custom_capabilities = {
    "my_capability": {
        "name": "my_capability",
        "risk_level": 2,
        "requires_external": False,
        "fn": my_custom_capability,
    }
}

config = {
    "capabilities": {
        "custom_capabilities": custom_capabilities
    }
}

engine = PACEEngine(config)
```

### Adding Custom Policies

Extend the `PolicyEngine` class:

```python
class CustomPolicyEngine(PolicyEngine):
    def __init__(self, identity_manager):
        super().__init__(identity_manager)
        self.policies["custom"] = {
            # Custom policy rules
        }
```

### Adding Custom Agents

Implement agents that work with the `AgentCoordinator`:

```python
class CustomAgent:
    def execute(self, task):
        # Agent implementation
        return result
```

## Testing

Test the PACE engine:

```python
# Basic import test
from project_ai.engine import PACEEngine
engine = PACEEngine()
assert engine.get_identity_phase() == "unbonded"

# Bonding test
bonding_profile = {"name": "Test", "values": {}}
identity = engine.run_bonding_protocol(bonding_profile)
assert engine.get_identity_phase() == "bonded"

# Workflow execution test
payload = {"type": "test", "message": "Test message"}
response = engine.handle_input("cli", payload)
assert "result" in response
assert "explanation" in response
```

## Architecture Principles

The PACE architecture follows these key principles:

1. **Separation of Concerns** - Each module has a single responsibility
1. **Composability** - Components can be combined and configured
1. **Extensibility** - New capabilities, policies, and agents can be added
1. **Observability** - All operations are logged and traceable
1. **Safety by Design** - Multiple validation and policy enforcement layers

## Performance Targets

- **Startup Time**: < 1 second
- **Request Latency**: < 100ms for simple workflows
- **Throughput**: > 1000 requests/second
- **Memory**: < 500MB baseline

## Security

The PACE engine implements multiple security layers:

1. **Identity Authentication** - All requests authenticated
1. **Policy Authorization** - All actions authorized
1. **Input Validation** - All inputs validated
1. **Sandboxing** - Capabilities execute in isolation
1. **Audit Logging** - All operations logged

## Troubleshooting

### Import Errors

If you encounter import errors:

```bash
# Ensure you're running from the project root
cd /path/to/Project-AI
python3 -m project_ai.main
```

### Identity Phase Issues

If bonding doesn't work:

```python
# Check current phase
print(engine.get_identity_phase())

# Check identity
print(engine.identity_manager.load_identity())
```

### Capability Errors

If capabilities fail:

```python
# Check policy context
print(engine.policy_engine.get_policy_context())

# Check capability registry
print(list(engine.capability_invoker.registry.keys()))
```

## Contributing

When contributing to the PACE architecture:

1. Follow the existing code structure
1. Add docstrings to all public methods
1. Update documentation if changing interfaces
1. Test all changes before submitting

## License

The PACE architecture package is part of Project-AI and is licensed under the MIT License.

## Support

For questions or issues:

- Check the documentation files in the repository root
- Review existing Project-AI documentation in `docs/`
- Open an issue on GitHub

## Version History

- **1.0.0** (2026-01-23) - Initial PACE architecture implementation
  - Core engine with all modules
  - Identity and bonding system
  - Built-in capabilities
  - Documentation suite
  - Demo application

## Future Roadmap

Planned enhancements:

- [ ] Advanced workflow patterns (parallel, conditional, loops)
- [ ] Additional built-in capabilities
- [ ] Enhanced agent coordination (multi-agent workflows)
- [ ] Persistent state backends (PostgreSQL, MongoDB)
- [ ] REST API server
- [ ] Web UI dashboard
- [ ] Performance optimizations
- [ ] Comprehensive test suite
- [ ] Integration examples with all Project-AI systems
