# T.A.R.L. Deterministic Orchestration Integration

## Overview

This document describes the complete deterministic AI orchestration layer integrated into Project-AI's T.A.R.L. system.

## Architecture

The implementation consists of six core subsystems:

### 1. Deterministic VM (`DeterministicVM`)

**Purpose**: Executes workflows with deterministic, reproducible behavior.

**Key Features**:
- **Logical Clock**: Uses monotonic counter (`self._counter`) instead of `time.time()`
- **Event Logging**: All workflow events tracked with sequence numbers
- **Deterministic Snapshots**: Identified by `hash(state + sequence)`, not wall-clock time
- **State Persistence**: Full VM state can be saved and restored

**Determinism Guarantees**:
- Event IDs: `(workflow_id, sequence_number)`
- Snapshot IDs: SHA-256 hash of `workflow_id:counter:state_json`
- Error IDs: SHA-256 hash of `workflow_id:error_message`
- No use of `time.time()`, `random.random()`, or other non-deterministic sources

### 2. Structured Capabilities (`Capability`, `Policy`, `CapabilityEngine`)

**Purpose**: Declarative capability system with compile-time/runtime checks.

**Key Features**:
- **Structured Capabilities**: `Capability(name, resource, constraints)`
- **Declarative Policies**: `Policy(name, capability_name, constraints, enforcement_level)`
- **Workflow Manifests**: Workflows declare `required_caps` upfront
- **Verification**: `verify_workflow()` checks manifest against registry and policies

**Example**:
```python
# Define capability
cap = Capability(
    name="Net.Connect",
    resource="network",
    constraints={"protocol": "https", "ca": "TrustedCA"}
)

# Define policy
policy = Policy(
    name="RequireHTTPS",
    capability_name="Net.Connect",
    constraints={"protocol": "https"},
    enforcement_level="required"
)

# Workflow declares required capabilities
workflow = Workflow(
    workflow_id="api_workflow",
    entrypoint=my_function,
    required_caps={"Net.Connect"}  # Checked at registration
)
```

### 3. Agent Orchestration (`AgentOrchestrator`)

**Purpose**: High-level patterns for multi-agent coordination.

**Patterns**:

1. **Sequential**: Pipeline pattern where output of agent[i] feeds agent[i+1]
   ```python
   result = orchestrator.sequential("wf_id", ["planner", "executor", "validator"], initial_input)
   ```

2. **Concurrent**: Fan-out pattern where all agents run in parallel
   ```python
   results = orchestrator.concurrent("wf_id", ["agent1", "agent2"], [input1, input2])
   ```

3. **Chat**: Multi-agent conversation with turn-taking
   ```python
   conversation = orchestrator.chat("wf_id", ["agent1", "agent2"], "Hello", max_turns=10)
   ```

4. **Graph**: DAG-based execution with arbitrary dependencies
   ```python
   graph = {"planner": ["executor"], "executor": ["validator"], "validator": []}
   result = orchestrator.graph("wf_id", graph, "planner", input_data)
   ```

### 4. Record & Replay (`EventRecorder`)

**Purpose**: Complete deterministic replay of workflow executions.

**Key Features**:
- **Event Recording**: Captures tool/LLM outputs, timer fires, API responses, agent decisions
- **Replay Mode**: On replay, pulls outputs from recorded event list instead of calling real tools
- **Partial Replay**: `replay_workflow(workflow_id, until_event=N)` replays up to event N
- **Persistence**: Recordings saved to JSON for audit and debugging

**Example**:
```python
# During execution
recorder.record_external_call(
    workflow_id="analysis",
    call_type="llm",
    call_args={"prompt": "Analyze data"},
    call_result={"response": "Analysis complete"}
)
recorder.save_recording("analysis", "recording_v1")

# Later, replay
result = recorder.replay_workflow("recording_v1", until_event=42)
```

### 5. Provenance & SBOM (`ProvenanceManager`)

**Purpose**: Track artifact relationships and generate Software Bill of Materials.

**Key Features**:
- **Artifact Registry**: Tracks workflows, modules, binaries, configs, snapshots
- **Relationships**: Dependency graph with typed edges (uses, depends_on, produces, requires)
- **Attestations**: Records policy checks, test results, signatures
- **SBOM Generation**: Full dependency graph with attestations for compliance

**Artifact Kinds**:

- `workflow`: Executable workflow
- `module`: Code module/library
- `binary`: Compiled artifact
- `config`: Configuration file
- `snapshot`: VM snapshot

**Example**:
```python
# Register artifacts
workflow_artifact = Artifact(
    artifact_id="data_analysis",
    kind="workflow",
    version="1.0.0",
    content_hash=hashlib.sha256(b"code").hexdigest()
)
provenance.register_artifact(workflow_artifact)

config_artifact = Artifact(
    artifact_id="config.toml",
    kind="config",
    version="1.0.0",
    content_hash=hashlib.sha256(b"config").hexdigest()
)
provenance.register_artifact(config_artifact)

# Add relationship
provenance.add_relationship(
    ArtifactRelationship(
        from_artifact="data_analysis",
        to_artifact="config.toml",
        relationship_type="uses"
    )
)

# Attest
provenance.attest("tests_passed", "data_analysis", {"test_count": 50})

# Generate SBOM
sbom = provenance.generate_sbom("data_analysis")
provenance.save_sbom("data_analysis")
```

### 6. TarlStackBox (Integration Layer)

**Purpose**: Unified interface to all subsystems.

**Key Features**:
- **Config-Driven**: All paths and options configurable
- **Production-Ready**: Full error handling, logging, persistence
- **Provenance-First**: `execute_with_provenance()` tracks everything
- **Status Monitoring**: `get_full_status()` reports all subsystem health

## Usage Example

```python
from project_ai.tarl.integrations import TarlStackBox, Workflow, Capability, Policy

# Initialize system
stack = TarlStackBox(config={
    "vm_data_dir": "data/tarl_vm",
    "recording_dir": "data/recordings",
    "provenance_dir": "data/provenance"
})

# Register capabilities and policies
cap = Capability(
    name="Net.Connect",
    resource="network",
    constraints={"protocol": "https"}
)
stack.capabilities.register_capability(cap)

policy = Policy(
    name="RequireHTTPS",
    capability_name="Net.Connect",
    constraints={"protocol": "https"}
)
stack.capabilities.register_policy(policy)

# Define workflow
def my_workflow(vm, context):
    # Check capability
    allowed, reason = stack.capabilities.check_capability(
        "Net.Connect", {"protocol": "https"}
    )
    if not allowed:
        raise PermissionError(reason)
    
    # Record external call
    stack.recorder.record_external_call(
        workflow_id="my_workflow",
        call_type="api",
        call_args={"endpoint": "api.example.com"},
        call_result={"data": [1, 2, 3]}
    )
    
    # Take snapshot
    snapshot_hash = vm.snapshot("my_workflow")
    
    return {"result": "success", "snapshot": snapshot_hash}

# Create and execute
stack.create_workflow(
    workflow_id="my_workflow",
    entrypoint=my_workflow,
    required_caps={"Net.Connect"},
    metadata={"version": "1.0.0"}
)

result = stack.execute_with_provenance("my_workflow")

# Save recording for replay
stack.recorder.save_recording("my_workflow", "recording_v1")

# Generate SBOM
sbom = stack.provenance.generate_sbom("my_workflow")
stack.provenance.save_sbom("my_workflow")
```

## Testing

Comprehensive test suite with 35 tests covering:

- Logical clock determinism
- Workflow execution and error handling
- State persistence and restoration
- Structured capabilities and policies
- Agent orchestration patterns (sequential, concurrent, chat, graph)
- Event recording and replay
- Provenance tracking and SBOM generation
- End-to-end integration

Run tests:
```bash
python -m pytest tests/test_tarl_orchestration.py -v
```

## Demo Harness

Interactive demo showing all features:
```bash
python -m project_ai.tarl.integrations.orchestration
```

Output includes:
- Deterministic workflow execution
- Agent orchestration patterns
- Recording persistence
- SBOM generation and verification
- System status reporting

## Key Design Principles

1. **Determinism First**: All non-determinism externalized to event log
2. **Structured Over Ad-Hoc**: Capabilities and policies are structured data, not lambdas
3. **Compile-Time Checks**: Workflow manifests enable early verification
4. **Complete Replay**: Full execution can be reproduced from event log
5. **Provenance by Default**: All artifacts and relationships tracked
6. **Production-Grade**: Full error handling, logging, persistence

## Integration with Project-AI

The T.A.R.L. orchestration layer integrates with Project-AI's existing systems:

- **Workflow Engine**: Can be used as deterministic backend for existing workflows
- **Agent System**: Provides orchestration patterns for multi-agent scenarios
- **Security**: Capability system enforces least-privilege at workflow level
- **Compliance**: SBOM generation supports audit and compliance requirements

## File Structure

```
project_ai/tarl/
├── __init__.py
└── integrations/
    ├── __init__.py
    └── orchestration.py  (1400+ lines, production-ready)

tests/
└── test_tarl_orchestration.py  (800+ lines, 35 tests)
```

## Performance Characteristics

- **Event Logging**: O(1) append per event
- **Snapshot Creation**: O(n) where n is state size
- **Capability Check**: O(p) where p is number of policies
- **SBOM Generation**: O(a + r) where a is artifacts, r is relationships
- **Replay**: O(e) where e is number of events to replay

## Future Enhancements

Potential extensions:
1. **Parallel VM Execution**: Multiple workflow instances
2. **Time-Travel Debugging**: Step through event log with state viewer
3. **Policy DSL**: Custom language for capability constraints
4. **Distributed Replay**: Replay across multiple machines
5. **SBOM Signing**: Cryptographic attestations
6. **IR Integration**: Compile-time capability checks in T.A.R.L. IR

## References

- Design inspired by Temporal.io and durable execution patterns
- Capability system based on object-capability security model
- SBOM format aligned with CycloneDX and SPDX standards
- Deterministic replay based on event sourcing patterns
