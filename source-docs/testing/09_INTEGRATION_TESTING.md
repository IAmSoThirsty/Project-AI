# Integration Testing

**Purpose:** Testing interactions between multiple system components  
**Modules:** 30+ integration test files  
**Coverage:** Full system integration, agent pipelines, orchestration, council hub  

---

## Overview

Integration tests validate:

1. **Component Interactions** - How systems work together
2. **Data Flow** - Information passing between components
3. **Agent Pipelines** - Multi-agent workflows
4. **Orchestration** - TARL coordination of system components
5. **API Integration** - External service integration

---

## Full System Integration

### test_complete_system.py

**Purpose:** Validate all core systems working together

#### End-to-End User Flow
```python
def test_complete_user_workflow(tmp_path):
    """Test complete user workflow from login to AI interaction."""
    # Setup systems
    user_manager = UserManager(users_file=str(tmp_path / "users.json"))
    persona = AIPersona(data_dir=str(tmp_path / "persona"))
    memory = MemoryExpansionSystem(data_dir=str(tmp_path / "memory"))
    learning = LearningRequestManager(data_dir=str(tmp_path / "learning"))
    
    # Step 1: User Registration
    user_manager.create_user("alice", "secure_password")
    assert "alice" in user_manager.users
    
    # Step 2: Authentication
    success, msg = user_manager.authenticate("alice", "secure_password")
    assert success is True
    
    # Step 3: Persona Interaction
    persona.set_user_name("Alice")
    persona.adjust_trait("friendliness", 0.1)
    assert persona.user_name == "Alice"
    
    # Step 4: Conversation Logging
    conv_id = memory.log_conversation("Hello AI", "Hello Alice!")
    assert len(conv_id) > 0
    
    # Step 5: Knowledge Storage
    memory.add_knowledge("user_prefs", "greeting_style", "friendly")
    pref = memory.get_knowledge("user_prefs", "greeting_style")
    assert pref == "friendly"
    
    # Step 6: Learning Request
    req_id = learning.create_request("Python", "Learn async programming")
    request = learning.get_request(req_id)
    assert request["status"] == "pending"
    
    # Step 7: Four Laws Validation
    is_allowed, reason = FourLaws.validate_action(
        "learn_programming",
        context={"is_user_order": True}
    )
    assert is_allowed is True
```

### test_full_integration.py

**Coverage:**
- Multi-system coordination
- State synchronization
- Error propagation
- Transaction-like operations

#### Cross-System State Management
```python
def test_cross_system_state_consistency(tmp_path):
    """Verify state consistency across systems."""
    data_dir = str(tmp_path)
    
    # Initialize systems
    persona = AIPersona(data_dir=data_dir)
    memory = MemoryExpansionSystem(data_dir=data_dir)
    
    # Persona change triggers memory update
    persona.set_user_name("Bob")
    persona.adjust_trait("curiosity", 0.2)
    
    # Memory should be aware of persona state
    memory.add_knowledge("persona", "user_name", persona.user_name)
    memory.add_knowledge("persona", "curiosity", 
                        str(persona.personality["curiosity"]))
    
    # Reload systems from disk
    persona2 = AIPersona(data_dir=data_dir)
    memory2 = MemoryExpansionSystem(data_dir=data_dir)
    
    # Verify state consistency
    assert persona2.user_name == "Bob"
    stored_name = memory2.get_knowledge("persona", "user_name")
    assert stored_name == "Bob"
```

---

## Agent Pipeline Testing

### test_agents_pipeline.py

**Purpose:** Test multi-agent workflows (Oversight → Planner → Validator → Explainability)

#### Four-Agent Pipeline
```python
def test_full_agent_pipeline():
    """Test complete agent pipeline execution."""
    from app.agents.oversight import OversightAgent
    from app.agents.planner import PlannerAgent
    from app.agents.validator import ValidatorAgent
    from app.agents.explainability import ExplainabilityAgent
    
    # Initialize agents
    oversight = OversightAgent()
    planner = PlannerAgent()
    validator = ValidatorAgent()
    explainer = ExplainabilityAgent()
    
    # User request
    user_request = "Analyze dataset and create visualization"
    
    # Step 1: Oversight checks request safety
    safety_check = oversight.validate_request(user_request)
    assert safety_check["safe"] is True
    
    # Step 2: Planner decomposes into tasks
    plan = planner.create_plan(user_request)
    assert len(plan["tasks"]) > 0
    assert "analyze" in str(plan["tasks"]).lower()
    assert "visualize" in str(plan["tasks"]).lower()
    
    # Step 3: Validator validates each task
    validation_results = []
    for task in plan["tasks"]:
        validation = validator.validate_task(task)
        validation_results.append(validation)
    assert all(v["valid"] for v in validation_results)
    
    # Step 4: Explainer generates explanation
    explanation = explainer.explain_plan(plan)
    assert len(explanation["steps"]) == len(plan["tasks"])
    assert all("rationale" in step for step in explanation["steps"])
```

#### Pipeline Error Handling
```python
def test_agent_pipeline_error_propagation():
    """Test error handling in agent pipeline."""
    oversight = OversightAgent()
    planner = PlannerAgent()
    
    # Unsafe request
    dangerous_request = "Delete all system files"
    
    # Oversight blocks request
    safety_check = oversight.validate_request(dangerous_request)
    assert safety_check["safe"] is False
    
    # Planner should not execute unsafe requests
    with pytest.raises(SecurityError, match="unsafe|blocked"):
        plan = planner.create_plan(dangerous_request)
```

---

## TARL Orchestration Testing

### test_tarl_orchestration.py

**Purpose:** Test TARL (Trust, Autonomy, Responsibility, Law) orchestration

#### Basic Orchestration
```python
def test_tarl_basic_orchestration():
    """Test basic TARL orchestration flow."""
    tarl = TARLOrchestrator()
    
    # Submit action for orchestration
    result = tarl.orchestrate_action(
        action="process_data",
        context={"data_type": "user_profile", "operation": "read"}
    )
    
    # Verify orchestration steps executed
    assert "trust_score" in result
    assert "autonomy_level" in result
    assert "responsibility_assigned" in result
    assert "law_validation" in result
    
    # Verify Law validation
    assert result["law_validation"]["passed"] is True
    
    # Verify responsibility assignment
    assert result["responsibility_assigned"] is not None
```

#### Multi-Step Orchestration
```python
def test_tarl_multi_step_orchestration():
    """Test complex multi-step orchestration."""
    tarl = TARLOrchestrator()
    
    steps = [
        {"action": "validate_input", "context": {"input": "user_data"}},
        {"action": "process_data", "context": {"data": "validated_input"}},
        {"action": "store_result", "context": {"result": "processed_data"}},
    ]
    
    results = []
    for step in steps:
        result = tarl.orchestrate_action(step["action"], step["context"])
        results.append(result)
    
    # Verify all steps succeeded
    assert all(r["law_validation"]["passed"] for r in results)
    
    # Verify trust scores maintained/improved
    trust_scores = [r["trust_score"] for r in results]
    assert all(score >= 0.7 for score in trust_scores)
```

### test_tarl_orchestration_extended.py

**Extended Coverage:**
- Parallel task execution
- Task dependencies
- Rollback on failure
- Audit trail generation

#### Task Dependencies
```python
def test_tarl_task_dependencies():
    """Test orchestration with task dependencies."""
    tarl = TARLOrchestrator()
    
    # Define tasks with dependencies
    tasks = [
        {"id": "task1", "action": "load_data", "depends_on": []},
        {"id": "task2", "action": "validate_data", "depends_on": ["task1"]},
        {"id": "task3", "action": "process_data", "depends_on": ["task2"]},
        {"id": "task4", "action": "save_data", "depends_on": ["task3"]},
    ]
    
    # Execute with dependency resolution
    results = tarl.execute_with_dependencies(tasks)
    
    # Verify execution order
    execution_order = [r["task_id"] for r in results]
    assert execution_order == ["task1", "task2", "task3", "task4"]
```

### test_tarl_orchestration_governance.py

**Governance Testing:**
- Policy enforcement
- Compliance checking
- Audit log verification
- Governance override prevention

---

## Council Hub Integration

### test_council_hub.py

**Purpose:** Test Council Hub (multi-agent decision making)

#### Council Decision Making
```python
def test_council_decision_making():
    """Test Council Hub multi-agent decision."""
    council = CouncilHub()
    
    # Add council members (different agent types)
    council.add_member("security_agent", SecurityAgent())
    council.add_member("ethics_agent", EthicsAgent())
    council.add_member("efficiency_agent", EfficiencyAgent())
    
    # Request council decision
    proposal = {
        "action": "deploy_update",
        "description": "Deploy system update with new features",
        "impact": "medium",
    }
    
    decision = council.decide(proposal)
    
    # Verify all members voted
    assert len(decision["votes"]) == 3
    
    # Verify decision reached
    assert decision["outcome"] in ["approved", "rejected", "defer"]
    
    # Verify reasoning provided
    assert "reasoning" in decision
    assert len(decision["reasoning"]) > 0
```

#### Council Conflict Resolution
```python
def test_council_conflict_resolution():
    """Test Council Hub conflict resolution."""
    council = CouncilHub()
    council.add_member("agent1", Agent(priority="security"))
    council.add_member("agent2", Agent(priority="speed"))
    
    # Proposal creates conflict (security vs speed)
    proposal = {
        "action": "skip_security_check",
        "reason": "urgent deployment",
    }
    
    decision = council.decide(proposal)
    
    # Security should win (higher priority)
    assert decision["outcome"] == "rejected"
    assert "security" in decision["reasoning"].lower()
```

### test_council_hub_integration.py

**Extended Coverage:**
- Dynamic member addition/removal
- Voting weight adjustment
- Quorum requirements
- Tie-breaking mechanisms

---

## Integration Flow Testing

### test_integration_flow.py

**Purpose:** Test specific integration flows

#### User Learning Flow
```python
def test_user_learning_integration_flow(tmp_path):
    """Test complete user learning request flow."""
    # Initialize systems
    learning = LearningRequestManager(data_dir=str(tmp_path / "learning"))
    memory = MemoryExpansionSystem(data_dir=str(tmp_path / "memory"))
    oversight = OversightAgent()
    
    # Step 1: User creates learning request
    req_id = learning.create_request(
        topic="Machine Learning",
        description="Learn neural networks"
    )
    
    # Step 2: Oversight validates request
    request = learning.get_request(req_id)
    safety = oversight.validate_request(request["description"])
    assert safety["safe"] is True
    
    # Step 3: Approve request
    learning.approve_request(req_id)
    
    # Step 4: Store learned knowledge in memory
    memory.add_knowledge("skills", "neural_networks", "basic understanding")
    
    # Step 5: Verify knowledge stored
    skill = memory.get_knowledge("skills", "neural_networks")
    assert skill == "basic understanding"
```

### test_integration_user_learning.py

Dedicated user learning integration tests.

---

## Pipeline Blocking Tests

### test_integration_pipeline_blocking.py

**Purpose:** Test pipeline blocking under error conditions

#### Cascading Failure Prevention
```python
def test_pipeline_cascading_failure_prevention():
    """Verify one component failure doesn't cascade."""
    pipeline = IntegrationPipeline()
    
    # Configure pipeline: A → B → C
    pipeline.add_stage("stage_a", StageA())
    pipeline.add_stage("stage_b", StageB())  # Will fail
    pipeline.add_stage("stage_c", StageC())
    
    # Inject failure in stage B
    pipeline.inject_failure("stage_b")
    
    # Execute pipeline
    result = pipeline.execute(input_data)
    
    # Verify graceful degradation
    assert result["stage_a"]["status"] == "success"
    assert result["stage_b"]["status"] == "failed"
    assert result["stage_c"]["status"] == "skipped"  # Not executed
    
    # Verify error isolation
    assert "error" in result["stage_b"]
    assert result["overall_status"] == "partial_failure"
```

---

## API Integration Testing

### test_api.py

**Purpose:** Test API integration points

#### External API Mocking
```python
@patch('requests.get')
def test_github_api_integration(mock_get):
    """Test GitHub API integration."""
    # Mock API response
    mock_get.return_value.json.return_value = {
        "name": "test-repo",
        "stars": 100,
        "forks": 20,
    }
    mock_get.return_value.status_code = 200
    
    # Call integration function
    from app.core.security_resources import fetch_github_repos
    repos = fetch_github_repos("security")
    
    # Verify integration
    assert len(repos) > 0
    assert mock_get.called
    assert "github.com" in mock_get.call_args[0][0]
```

---

## Wired Systems Testing

### test_wired_systems.py

**Purpose:** Test system wiring and dependency injection

#### System Wiring Validation
```python
def test_system_wiring():
    """Verify all systems properly wired."""
    from app.core import wiring
    
    # Get wired container
    container = wiring.get_container()
    
    # Verify core systems available
    assert container.get("user_manager") is not None
    assert container.get("persona") is not None
    assert container.get("memory") is not None
    assert container.get("learning") is not None
    
    # Verify dependency resolution
    persona = container.get("persona")
    memory = container.get("memory")
    
    # Systems should share data_dir configuration
    assert persona.data_dir == memory.data_dir
```

---

## Best Practices

### ✅ DO
- Test component interactions explicitly
- Use mocks for external dependencies
- Test error propagation between components
- Verify state consistency across systems
- Test rollback mechanisms
- Use integration fixtures for setup

### ❌ DON'T
- Test implementation details
- Skip error path testing
- Assume component isolation
- Share state between tests
- Ignore cascade failures
- Skip cleanup in integration tests

---

## Integration Test Patterns

### Pattern 1: Multi-System Setup
```python
@pytest.fixture
def integrated_systems(tmp_path):
    """Setup multiple integrated systems."""
    systems = {
        "user_manager": UserManager(users_file=str(tmp_path / "users.json")),
        "persona": AIPersona(data_dir=str(tmp_path / "persona")),
        "memory": MemoryExpansionSystem(data_dir=str(tmp_path / "memory")),
    }
    yield systems
    # Cleanup automatic via tmp_path
```

### Pattern 2: Pipeline Testing
```python
def test_pipeline(integrated_systems):
    """Test data flow through systems."""
    input_data = {...}
    
    # Stage 1
    result1 = integrated_systems["system1"].process(input_data)
    
    # Stage 2 uses result1
    result2 = integrated_systems["system2"].process(result1)
    
    # Verify final output
    assert result2["status"] == "success"
```

### Pattern 3: Error Injection
```python
def test_error_handling(integrated_systems, mocker):
    """Test error handling in integration."""
    # Inject error in component
    mocker.patch.object(
        integrated_systems["system1"],
        "process",
        side_effect=RuntimeError("Simulated failure")
    )
    
    # Verify graceful handling
    with pytest.raises(IntegrationError):
        integrated_systems["orchestrator"].execute()
```

---

## Next Steps

1. Read `10_E2E_TESTING.md` for end-to-end test patterns
2. See `11_GUI_TESTING.md` for GUI integration tests
3. Check `12_TEST_MAINTENANCE.md` for test maintenance strategies

---

**See Also:**
- `tests/test_complete_system.py` - Full system integration
- `tests/test_agents_pipeline.py` - Agent pipeline tests
- `tests/test_tarl_orchestration.py` - TARL orchestration
- `tests/test_council_hub_integration.py` - Council Hub integration
