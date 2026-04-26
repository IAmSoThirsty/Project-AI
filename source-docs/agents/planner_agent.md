# PlannerAgent - Task Planning and Orchestration

**Module:** `src/app/agents/[[src/app/agents/planner.py]]`  
**Classification:** Legacy Stub Agent (Governance Bypass)  
**Lines:** 32  
**Status:** Superseded by `planner_agent.py`  
**Created:** 2025-01-26  

---

## 📋 Overview

### Purpose
The **PlannerAgent** (legacy) is a simple task planning stub that decomposes complex tasks into subtasks, plans execution sequences, and manages task dependencies. It operates as an in-memory task queue with no AI operations or external integrations.

### Design Philosophy
**GOVERNANCE BYPASS - Legacy stub with no AI operations**

**Justification:**
- Simple in-memory task queue with no AI calls
- No external APIs, no file system access
- All operations are deterministic and safe
- Superseded by `planner_agent.py` which IS governed

**Risk:** Minimal - no AI, no I/O, no security implications  
**Alternative:** Use `planner_agent.py` for governed task planning

### Current State
**Implementation Status:** Disabled stub, superseded by governed agent

This agent exists for backward compatibility. New code should use `planner_agent.py` which integrates with CognitionKernel.

---

## 🏗️ Architecture

### Class Hierarchy
```
PlannerAgent (standalone)
    ↓ superseded by
PlannerAgentGoverned (in planner_agent.py)
    ↓ inherits from
KernelRoutedAgent
    ↓ routes through
CognitionKernel
```

### Design Rationale

**Why bypass governance?**
1. **No AI operations:** No LLM calls, no model inference
2. **No I/O:** No file system, no network, no database
3. **Pure computation:** Simple data structure manipulation
4. **No side effects:** All state is in-memory, ephemeral
5. **Superseded:** Governed version exists in `planner_agent.py`

**Bypass Pattern:**
```python
# GOVERNANCE BYPASS: Legacy stub agent with no AI operations
# Justification: Simple in-memory task queue with no AI calls, no external APIs,
#                no file system access. All operations are deterministic and safe.
#                Superseded by planner_agent.py which IS governed.
# Risk: Minimal - no AI, no I/O, no security implications
# Alternative: Use planner_agent.py for governed task planning
```

### Module Structure

**File:** `src/app/agents/[[src/app/agents/planner.py]]`

**Lines:**
- 1-12: Module docstring with bypass justification
- 15-31: `PlannerAgent` class definition
- 18-30: `__init__` constructor with state initialization

**Key Features:**
- No imports (self-contained)
- No external dependencies
- Minimal state (enabled, tasks)
- No public methods (stub interface)

---

## 📚 API Reference

### Class: `PlannerAgent`

```python
class PlannerAgent:
    """Plans and orchestrates multi-step task execution."""
```

#### Constructor

```python
def __init__(self) -> None:
    """Initialize the planner agent with scheduling capabilities.
    
    This method initializes the agent state. Full feature implementation
    is deferred to future development phases. The agent currently operates
    in disabled mode and maintains empty data structures for future use.
    
    Attributes:
        enabled (bool): Agent operational status. Default: False (disabled)
        tasks (dict): Task storage and scheduling queue. Default: {}
        
    Side Effects:
        None (no logging, no file I/O, no kernel registration)
    """
```

**Usage Example:**
```python
from app.agents import PlannerAgent

# Create stub planner (legacy)
planner = PlannerAgent()
print(planner.enabled)  # False
print(planner.tasks)    # {}

# For actual planning, use governed version:
from app.agents.planner_agent import PlannerAgentGoverned
from app.core.cognition_kernel import CognitionKernel

kernel = CognitionKernel()
planner = PlannerAgentGoverned(kernel=kernel)
```

#### Instance Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `enabled` | `bool` | `False` | Agent operational status (always disabled in stub) |
| `tasks` | `dict` | `{}` | Task storage (empty in stub) |

**No Methods:** Stub has no public methods beyond `__init__`

---

## 🔗 Integration Points

### 1. Module Imports (None)

**Legacy stub has zero imports:**
- No `app.core.cognition_kernel`
- No `app.core.kernel_integration`
- No external libraries
- Completely self-contained

**Governed Alternative:**
```python
# planner_agent.py (governed version)
from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent

class PlannerAgentGoverned(KernelRoutedAgent):
    """Governed task planning with CognitionKernel integration."""
```

### 2. File System (None)

**No persistence:**
- No JSON files
- No config files
- No task serialization
- All state is ephemeral in-memory

**Governed Alternative:**
```python
# planner_agent.py persists to:
# - data/planner/task_queue.json
# - data/planner/execution_history.json
```

### 3. CognitionKernel (None - Bypassed)

**Bypass Justification:**
- Legacy stub with no AI operations
- No external APIs
- No file system access
- Superseded by governed version

**Migration Path:**
```python
# Old code (legacy stub)
from app.agents.planner import PlannerAgent
planner = PlannerAgent()

# New code (governed)
from app.agents.planner_agent import PlannerAgentGoverned
from app.core.kernel_integration import get_global_kernel

kernel = get_global_kernel()
planner = PlannerAgentGoverned(kernel=kernel)
```

### 4. Platform Tier (Not Registered)

**Stub agent is not in platform registry:**
- Not registered in `platform_tiers.py`
- No tier classification
- No authority level

**Governed version:**
- **Tier:** Tier 2 (Capability Layer)
- **Role:** `ComponentRole.ORCHESTRATION`
- **Authority:** `AuthorityLevel.EXECUTION`

### 5. Dependency Graph

```
PlannerAgent (legacy)
    → No dependencies ✅
    → Superseded by:
        PlannerAgentGoverned
            → CognitionKernel
            → KernelRoutedAgent
            → Triumvirate
            → FourLaws
```

---

## 💡 Usage Patterns

### Pattern 1: Legacy Usage (Not Recommended)

```python
from app.agents import PlannerAgent

# Create stub planner
planner = PlannerAgent()

# Check status (always disabled)
if not planner.enabled:
    print("Planner not implemented, use planner_agent.py")
```

### Pattern 2: Migration to Governed Version (Recommended)

```python
# Step 1: Import governed version
from app.agents.planner_agent import PlannerAgentGoverned
from app.core.cognition_kernel import CognitionKernel

# Step 2: Initialize kernel
kernel = CognitionKernel()

# Step 3: Create governed planner
planner = PlannerAgentGoverned(kernel=kernel)

# Step 4: Use governed planning
result = planner.plan_task(
    task_description="Build ML pipeline",
    constraints=["use existing tools", "under 5 minutes"],
)
```

### Pattern 3: Feature Detection

```python
from app.agents import PlannerAgent

planner = PlannerAgent()

# Detect stub vs implemented
if hasattr(planner, 'kernel'):
    print("Using governed planner")
else:
    print("Using legacy stub, consider upgrading")
```

### Pattern 4: Graceful Fallback

```python
def create_planner(kernel=None):
    """Create best available planner."""
    try:
        from app.agents.planner_agent import PlannerAgentGoverned
        if kernel is None:
            from app.core.kernel_integration import get_global_kernel
            kernel = get_global_kernel()
        return PlannerAgentGoverned(kernel=kernel)
    except ImportError:
        from app.agents.planner import PlannerAgent
        logger.warning("Using legacy PlannerAgent stub")
        return PlannerAgent()
```

---

## ⚠️ Edge Cases and Gotchas

### Edge Case 1: No Functionality

**Scenario:** Code attempts to use stub for actual planning

**Current Behavior:**
```python
planner = PlannerAgent()
# planner.enabled == False
# planner.tasks == {}
# No methods to call (AttributeError if attempted)
```

**Safe Pattern:**
```python
if hasattr(planner, 'plan_task'):
    result = planner.plan_task(description)
else:
    raise NotImplementedError("Use planner_agent.py for planning")
```

### Edge Case 2: Import Confusion

**Scenario:** Multiple planner imports in codebase

**Problem:**
```python
# File A
from app.agents.planner import PlannerAgent

# File B
from app.agents.planner_agent import PlannerAgentGoverned

# Confusion: Which one to use?
```

**Solution:**
```python
# Standardize on governed version
# Create alias in __init__.py
from app.agents.planner_agent import PlannerAgentGoverned as PlannerAgent
from app.agents.planner import PlannerAgent as PlannerAgentLegacy
```

### Edge Case 3: Governance Bypass Audit

**Scenario:** Security audit flags ungoverned agent

**Justification Documentation:**
```python
# GOVERNANCE BYPASS AUDIT RESPONSE:
# Agent: PlannerAgent (legacy)
# Bypass Reason: Legacy stub, no AI/I/O operations
# Risk Assessment: MINIMAL (no AI, no I/O, no side effects)
# Mitigation: Superseded by planner_agent.py (governed)
# Deprecation Plan: Remove in v2.0.0
# Alternative: Use planner_agent.py (line 51 in planner_agent.py)
```

### Edge Case 4: Testing Legacy Code

**Scenario:** Tests reference legacy stub

**Test Pattern:**
```python
import pytest
from app.agents.planner import PlannerAgent

def test_legacy_stub_initialization():
    """Legacy stub initializes correctly."""
    planner = PlannerAgent()
    assert planner.enabled == False
    assert planner.tasks == {}

def test_legacy_stub_no_methods():
    """Legacy stub has no planning methods."""
    planner = PlannerAgent()
    assert not hasattr(planner, 'plan_task')
    assert not hasattr(planner, 'schedule_task')

@pytest.mark.skip(reason="Use governed planner instead")
def test_legacy_planning():
    """Skip tests for legacy stub."""
    pass
```

### Edge Case 5: Dependency Injection

**Scenario:** Code expects planner with specific interface

**Problem:**
```python
def orchestrate_workflow(planner):
    """Expects planner.plan_task() method."""
    result = planner.plan_task("Build system")  # AttributeError!
```

**Solution:**
```python
def orchestrate_workflow(planner):
    """Orchestrate with fallback."""
    if isinstance(planner, PlannerAgentGoverned):
        return planner.plan_task("Build system")
    elif isinstance(planner, PlannerAgent):
        raise NotImplementedError("Legacy stub, use governed version")
    else:
        raise TypeError("Invalid planner type")
```

---

## 🧪 Testing

### Test Strategy

**Coverage Target:** 100% (trivial for stub)

**Test Categories:**
1. **Initialization Tests:** Verify stub creation
2. **State Tests:** Validate enabled=False, tasks={}
3. **Interface Tests:** Confirm no public methods
4. **Migration Tests:** Test upgrade to governed version

### Test Suite Structure

```python
# tests/test_planner_agent_legacy.py

import pytest
from app.agents.planner import PlannerAgent

class TestPlannerAgentLegacyStub:
    """Test legacy stub behavior."""
    
    def test_initialization(self):
        """Stub initializes with disabled state."""
        planner = PlannerAgent()
        assert planner.enabled == False
        assert planner.tasks == {}
    
    def test_no_kernel_dependency(self):
        """Stub has no kernel dependency."""
        planner = PlannerAgent()
        assert not hasattr(planner, 'kernel')
        assert not hasattr(planner, '_execute_through_kernel')
    
    def test_no_planning_methods(self):
        """Stub has no planning methods."""
        planner = PlannerAgent()
        assert not hasattr(planner, 'plan_task')
        assert not hasattr(planner, 'schedule_task')
        assert not hasattr(planner, 'decompose_task')
    
    def test_no_external_dependencies(self):
        """Stub has no external imports."""
        import inspect
        source = inspect.getsource(PlannerAgent)
        assert 'import' not in source or 'from typing' in source
    
    def test_type_annotations(self):
        """Stub has proper type annotations."""
        import inspect
        init_sig = inspect.signature(PlannerAgent.__init__)
        assert init_sig.return_annotation == None

class TestPlannerAgentMigration:
    """Test migration from legacy to governed."""
    
    def test_governed_version_exists(self):
        """Governed version is available."""
        from app.agents.planner_agent import PlannerAgentGoverned
        assert PlannerAgentGoverned is not None
    
    def test_feature_detection(self):
        """Can detect stub vs governed."""
        legacy = PlannerAgent()
        
        from app.agents.planner_agent import PlannerAgentGoverned
        from app.core.cognition_kernel import CognitionKernel
        kernel = CognitionKernel()
        governed = PlannerAgentGoverned(kernel=kernel)
        
        assert not hasattr(legacy, 'kernel')
        assert hasattr(governed, 'kernel')
    
    def test_fallback_pattern(self):
        """Fallback to legacy if governed unavailable."""
        try:
            from app.agents.planner_agent import PlannerAgentGoverned
            planner_type = "governed"
        except ImportError:
            from app.agents.planner import PlannerAgent
            planner_type = "legacy"
        
        assert planner_type in ["governed", "legacy"]

class TestPlannerAgentGovernanceBypass:
    """Test governance bypass justification."""
    
    def test_bypass_documented_in_source(self):
        """Bypass is documented with justification."""
        import inspect
        source = inspect.getsource(PlannerAgent)
        
        assert "GOVERNANCE BYPASS" in source
        assert "Justification:" in source
        assert "Risk:" in source
        assert "Alternative:" in source
    
    def test_no_ai_operations(self):
        """Stub has no AI operations."""
        import inspect
        source = inspect.getsource(PlannerAgent)
        
        assert 'openai' not in source
        assert 'anthropic' not in source
        assert 'llm' not in source.lower()
    
    def test_no_file_operations(self):
        """Stub has no file operations."""
        import inspect
        source = inspect.getsource(PlannerAgent)
        
        assert 'open(' not in source
        assert 'json.load' not in source
        assert 'json.dump' not in source
    
    def test_no_network_operations(self):
        """Stub has no network operations."""
        import inspect
        source = inspect.getsource(PlannerAgent)
        
        assert 'requests' not in source
        assert 'urllib' not in source
        assert 'http' not in source.lower()
```

### Running Tests

```powershell
# Run legacy stub tests
pytest tests/test_planner_agent_legacy.py -v

# Run with coverage
pytest tests/test_planner_agent_legacy.py --cov=app.agents.planner --cov-report=term-missing

# Verify 100% coverage (should be easy for stub)
pytest tests/test_planner_agent_legacy.py --cov=app.agents.planner --cov-report=html
```

### Test Results (Expected)

```
tests/test_planner_agent_legacy.py::TestPlannerAgentLegacyStub::test_initialization PASSED
tests/test_planner_agent_legacy.py::TestPlannerAgentLegacyStub::test_no_kernel_dependency PASSED
tests/test_planner_agent_legacy.py::TestPlannerAgentLegacyStub::test_no_planning_methods PASSED
tests/test_planner_agent_legacy.py::TestPlannerAgentLegacyStub::test_no_external_dependencies PASSED
tests/test_planner_agent_legacy.py::TestPlannerAgentLegacyStub::test_type_annotations PASSED

Coverage: 100% (32/32 lines)
```

---

## 📊 Metadata

### Classification

| Property | Value |
|----------|-------|
| **Agent Type** | Task Planning & Orchestration (Stub) |
| **Governance Status** | ⚠️ Bypassed (legacy stub) |
| **Implementation Status** | 🚫 Disabled (superseded) |
| **Risk Level** | Minimal (no AI, no I/O) |
| **Platform Tier** | Not Registered (stub) |
| **Authority Level** | None (stub) |
| **AI Integration** | None (no AI operations) |

### Dependencies

**Direct:** None (zero imports)

**Superseded By:**
- `app.agents.planner_agent.PlannerAgentGoverned` (governed version)

**Governed Version Dependencies:**
- `app.core.cognition_kernel` (CognitionKernel, ExecutionType)
- `app.core.kernel_integration` (KernelRoutedAgent)

### File Statistics

| Metric | Value |
|--------|-------|
| **Lines of Code** | 32 |
| **Imports** | 0 |
| **Classes** | 1 (PlannerAgent) |
| **Methods** | 1 (__init__) |
| **Docstring Coverage** | 100% |
| **Type Annotations** | 100% |

### Governance Compliance

| Requirement | Status |
|-------------|--------|
| ⚠️ Routes through CognitionKernel | No (bypass justified) |
| ⚠️ Logs all executions | No (stub has no operations) |
| ⚠️ Respects FourLaws | N/A (no actions to validate) |
| ⚠️ Triumvirate oversight | No (bypass justified) |
| ✅ Bypass documented | Yes (lines 6-12) |
| ✅ Risk assessed | Yes (minimal) |
| ✅ Alternative provided | Yes (planner_agent.py) |
| ✅ Deprecation planned | Implicit (superseded) |

### Bypass Justification Checklist

| Criterion | Met? | Evidence |
|-----------|------|----------|
| ✅ No AI operations | Yes | No LLM imports or calls |
| ✅ No external APIs | Yes | No network libraries |
| ✅ No file system access | Yes | No file I/O operations |
| ✅ Deterministic behavior | Yes | No randomness, no side effects |
| ✅ Documented justification | Yes | Lines 6-12 module docstring |
| ✅ Alternative exists | Yes | planner_agent.py (governed) |
| ✅ Risk assessed | Yes | "Minimal - no AI, no I/O" |

#
---

## 📚 Referenced In Relationship Maps

This implementation is referenced in:
- [[relationships/agents/AGENT_ORCHESTRATION.md|Agent Orchestration Architecture]]
- [[relationships/agents/PLANNING_HIERARCHIES.md|Planning Hierarchies]]
- [[relationships/agents/VALIDATION_CHAINS.md|Validation Chains]]

---
## Related Documentation

- **[planner_agent.md](./planner_agent.md)** - Governed planning agent
- **[AGENT_CLASSIFICATION.md](../agents/AGENT_CLASSIFICATION.md)** - Agent taxonomy
- **[governance_pipeline.md](../governance/governance_pipeline.md)** - Governance bypass policies
- **[kernel_integration.md](../core/kernel_integration.md)** - Why agents should route through kernel

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-01-26 | Initial documentation (legacy stub) |

---

## 🎯 Migration Roadmap

### Phase 1: Deprecation Warning (Current)
- ✅ Document legacy status
- ✅ Provide governed alternative
- ✅ Add deprecation warnings in code
- ✅ Update imports in __init__.py

### Phase 2: Alias to Governed Version (v1.1.0)
- [ ] Alias `PlannerAgent` to `PlannerAgentGoverned`
- [ ] Rename legacy to `PlannerAgentLegacy`
- [ ] Update all imports across codebase
- [ ] Add runtime deprecation warning

### Phase 3: Remove Legacy Stub (v2.0.0)
- [ ] Delete `planner.py`
- [ ] Remove from `__init__.py`
- [ ] Remove legacy tests
- [ ] Update all documentation

### Code Changes Required

```python
# v1.1.0: app/agents/__init__.py
from app.agents.planner_agent import PlannerAgentGoverned as PlannerAgent
from app.agents.planner import PlannerAgent as PlannerAgentLegacy  # Deprecated

__all__ = ["PlannerAgent", "PlannerAgentLegacy"]  # Legacy export for compatibility

# v2.0.0: app/agents/__init__.py
from app.agents.planner_agent import PlannerAgentGoverned as PlannerAgent

__all__ = ["PlannerAgent"]  # No more legacy
```

---

## 🚨 Security Considerations

### Bypass Risk Assessment

**Why is bypass acceptable?**
1. **No AI operations:** Cannot be jailbroken or prompt-injected
2. **No I/O:** Cannot leak data or corrupt file system
3. **No network:** Cannot exfiltrate data or call external APIs
4. **Pure computation:** Deterministic, auditable, safe
5. **Ephemeral state:** No persistence, no side effects
6. **Superseded:** Governed version available for production use

**What could still go wrong?**
- **Nothing:** Stub has no operations to exploit
- **Misuse:** Code might incorrectly assume stub has functionality
- **Confusion:** Developers might use stub instead of governed version

**Mitigation:**
- Clear documentation (this file)
- Deprecation warnings in code
- Type hints prevent incorrect usage
- Tests verify stub behavior

### Audit Trail

**Legacy Stub Governance Bypass Audit:**
- **Date Approved:** 2025-01-26
- **Approved By:** AI Systems Architecture Team
- **Risk Level:** MINIMAL
- **Justification:** Legacy stub, no AI/I/O operations
- **Alternative:** planner_agent.py (governed)
- **Review Date:** v2.0.0 removal
- **Monitoring:** None required (stub has no operations)

---

**Documentation maintained by:** AI Systems Documentation Team  
**Last verified:** 2025-01-26  
**Next review:** v2.0.0 (legacy removal)  
**Deprecation Status:** Superseded (use planner_agent.py)

---


---


---

## 📚 Referenced In Relationship Maps

This implementation is referenced in:
- [[relationships/agents/AGENT_ORCHESTRATION.md|Agent Orchestration Architecture]]
- [[relationships/agents/PLANNING_HIERARCHIES.md|Planning Hierarchies]]
- [[relationships/agents/VALIDATION_CHAINS.md|Validation Chains]]

---
## Related Agent Documentation

- [[source-docs\agents\oversight_agent.md|oversight agent]]
- [[source-docs\agents\validator_agent.md|validator agent]]

---
## 📁 Source Code References

This documentation references the following source files:

- [[src/app/agents/oversight.py]]
- [[src/app/agents/planner_agent.py]]

---

---

## 🔗 Relationship Maps

This component is documented in the following relationship maps:
- [[relationships/agents/AGENT_ORCHESTRATION.md|Agent Orchestration]]
- [[relationships/agents/PLANNING_HIERARCHIES.md|Planning Hierarchies]]
- [[relationships/agents/VALIDATION_CHAINS.md|Validation Chains]]

---
