# Agent Interaction Diagram - Core AI Agents

**Document:** Agent Collaboration Architecture  
**Agents:** OversightAgent, PlannerAgent, ValidatorAgent, ExplainabilityAgent  
**Created:** 2025-01-26  

---

## 🔄 Agent Interaction Flow

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        TIER 1: GOVERNANCE                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              CognitionKernel (Hub)                         │ │
│  │  - All executions route through kernel                     │ │
│  │  - Enforces FourLaws, Triumvirate, Black Vault            │ │
│  │  - Manages ExecutionContext and results                   │ │
│  └─────────────┬───────────────┬────────────┬─────────────────┘ │
└────────────────┼───────────────┼────────────┼───────────────────┘
                 │               │            │
                 ▼               ▼            ▼
┌────────────────────────────────────────────────────────────────┐
│                     TIER 2: CAPABILITY LAYER                    │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Oversight   │  │  Validator   │  │Explainability│         │
│  │    Agent     │  │    Agent     │  │    Agent     │         │
│  │              │  │              │  │              │         │
│  │ - Monitor    │  │ - Validate   │  │ - Explain    │         │
│  │ - Compliance │  │ - Enforce    │  │ - Report     │         │
│  │ - Observe    │  │ - Block      │  │ - Clarify    │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                 │
│         └──────────────────┼──────────────────┘                 │
│                            │                                    │
│                  ┌─────────▼─────────┐                         │
│                  │   Planner Agent   │                         │
│                  │  (Legacy Stub)    │                         │
│                  │                   │                         │
│                  │ - No operations   │                         │
│                  │ - Bypassed        │                         │
│                  └───────────────────┘                         │
└────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────┐
│                     TIER 3: EXECUTION LAYER                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Tools, Plugins, External APIs                          │  │
│  │  - Execute validated actions                            │  │
│  │  - Report results back to Tier 2                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

---

## 🔀 Collaboration Patterns

### Pattern 1: Validation → Execution → Explanation

**Scenario:** User action requires validation, execution, and transparency

```
User Action Request
    ↓
1. ValidatorAgent validates input
    ├─ Type checking
    ├─ Security validation (SQL injection, XSS)
    ├─ Black Vault check
    └─ Identity mutation validation
    ↓
2. CognitionKernel routes validated action
    ├─ Triumvirate review
    ├─ FourLaws validation
    └─ Execution approval
    ↓
3. Action executes (Tier 3)
    ↓
4. OversightAgent monitors execution
    ├─ Health checks
    ├─ Compliance verification
    └─ Anomaly detection
    ↓
5. ExplainabilityAgent generates explanation
    ├─ Decision reasoning
    ├─ Governance context
    └─ User-friendly report
    ↓
User receives validated, monitored, explained result
```

**Code Example:**
```python
from app.agents import ValidatorAgent, OversightAgent, ExplainabilityAgent
from app.core.cognition_kernel import CognitionKernel

kernel = CognitionKernel()
validator = ValidatorAgent(kernel=kernel)
oversight = OversightAgent(kernel=kernel)
explainer = ExplainabilityAgent(kernel=kernel)

# Step 1: Validate
validation_result = validator.validate_input(user_data, schema)
if not validation_result["valid"]:
    return {"error": "Validation failed", "details": validation_result}

# Step 2: Execute through kernel (automatic routing)
execution_result = kernel.process(
    action=execute_action,
    action_args=(user_data,),
    execution_type=ExecutionType.SYSTEM_OPERATION,
)

# Step 3: Monitor (future implementation)
# oversight.monitor_execution(execution_result["execution_id"])

# Step 4: Explain
explanation = explainer.explain_decision(execution_result)

# Return comprehensive result
return {
    "validation": validation_result,
    "execution": execution_result,
    "explanation": explanation,
}
```

---

### Pattern 2: Oversight-Triggered Validation

**Scenario:** Monitoring detects anomaly, triggers validation

```
OversightAgent detects anomaly
    ↓
Escalates to ValidatorAgent
    ├─ Validate current state
    ├─ Check for violations
    └─ Identify root cause
    ↓
If violation detected:
    ├─ Block further execution (ValidatorAgent authority)
    ├─ Escalate to Triumvirate
    └─ Generate incident report (ExplainabilityAgent)
    ↓
Resolution and explanation
```

**Code Example:**
```python
# Future implementation
class OversightAgent(KernelRoutedAgent):
    def monitor_system_health(self) -> dict:
        """Monitor and trigger validation if anomaly detected."""
        health_metrics = self._collect_metrics()
        
        if self._detect_anomaly(health_metrics):
            # Escalate to validator
            validator = ValidatorAgent(kernel=self.kernel)
            validation = validator.validate_system_state(health_metrics)
            
            if not validation["valid"]:
                # Generate incident report
                explainer = ExplainabilityAgent(kernel=self.kernel)
                incident_report = explainer.explain_incident(
                    anomaly=health_metrics,
                    validation=validation,
                )
                
                # Escalate to governance
                self.kernel.escalate_to_triumvirate(incident_report)
                
                return {
                    "status": "critical",
                    "incident_report": incident_report,
                }
        
        return {"status": "healthy"}
```

---

### Pattern 3: Explanation-Driven Validation

**Scenario:** User requests explanation, triggers validation of explanation integrity

```
User requests explanation
    ↓
ExplainabilityAgent generates explanation
    ↓
ValidatorAgent validates explanation
    ├─ Sanitize sensitive data
    ├─ Verify factual accuracy
    └─ Check for information leaks
    ↓
OversightAgent audits explanation delivery
    ├─ Log access (who, when, what)
    ├─ Track explanation usage
    └─ Detect explanation abuse
    ↓
Validated, sanitized explanation delivered
```

**Code Example:**
```python
def explain_with_validation(
    explainer: ExplainabilityAgent,
    validator: ValidatorAgent,
    oversight: OversightAgent,
    decision: dict,
    user_id: str,
) -> dict:
    """Generate validated, monitored explanation."""
    # Step 1: Generate raw explanation
    raw_explanation = explainer.explain_decision(decision)
    
    # Step 2: Validate and sanitize
    validated_explanation = validator.validate_explanation(raw_explanation)
    
    if not validated_explanation["valid"]:
        return {
            "error": "Explanation failed validation",
            "reason": validated_explanation["reason"],
        }
    
    # Step 3: Monitor access
    oversight.log_explanation_access(
        user_id=user_id,
        decision_id=decision["id"],
        explanation_id=raw_explanation["id"],
    )
    
    # Return sanitized explanation
    return validated_explanation["sanitized_explanation"]
```

---

### Pattern 4: Orchestrated Agent Pipeline

**Scenario:** Complex workflow requiring all agents in sequence

```
Complex User Request
    ↓
┌─────────────────────────────────────────┐
│  PHASE 1: PRE-PROCESSING               │
│  ┌───────────────┐  ┌───────────────┐  │
│  │ ValidatorAgent│→ │OversightAgent │  │
│  │ - Input check │  │ - Pre-flight  │  │
│  └───────────────┘  └───────────────┘  │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  PHASE 2: EXECUTION (CognitionKernel)  │
│  - Triumvirate review                   │
│  - FourLaws validation                  │
│  - Action execution                     │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  PHASE 3: POST-PROCESSING              │
│  ┌───────────────┐  ┌───────────────┐  │
│  │OversightAgent │→ │Explainability │  │
│  │ - Monitor     │  │ - Explain     │  │
│  └───────────────┘  └───────────────┘  │
└─────────────────────────────────────────┘
    ↓
Comprehensive Result
```

**Code Example:**
```python
class AgentPipeline:
    """Orchestrated agent pipeline for complex workflows."""
    
    def __init__(self, kernel: CognitionKernel):
        self.validator = ValidatorAgent(kernel=kernel)
        self.oversight = OversightAgent(kernel=kernel)
        self.explainer = ExplainabilityAgent(kernel=kernel)
        self.kernel = kernel
    
    def execute_workflow(
        self,
        user_input: dict,
        workflow_type: str,
    ) -> dict:
        """Execute orchestrated workflow."""
        # PHASE 1: PRE-PROCESSING
        validation = self.validator.validate_input(
            user_input,
            schema=self._get_schema(workflow_type),
        )
        
        if not validation["valid"]:
            return {
                "phase": "validation",
                "success": False,
                "details": validation,
            }
        
        pre_flight = self.oversight.pre_flight_check(user_input)
        if not pre_flight["ready"]:
            return {
                "phase": "pre_flight",
                "success": False,
                "details": pre_flight,
            }
        
        # PHASE 2: EXECUTION
        execution_result = self.kernel.process(
            action=self._get_workflow_action(workflow_type),
            action_args=(user_input,),
            execution_type=ExecutionType.SYSTEM_OPERATION,
        )
        
        if not execution_result.success:
            # Generate failure explanation
            failure_explanation = self.explainer.explain_failure(
                execution_result
            )
            return {
                "phase": "execution",
                "success": False,
                "explanation": failure_explanation,
            }
        
        # PHASE 3: POST-PROCESSING
        post_monitoring = self.oversight.post_execution_check(
            execution_result
        )
        
        explanation = self.explainer.explain_decision({
            "execution": execution_result,
            "validation": validation,
            "monitoring": post_monitoring,
        })
        
        return {
            "phase": "complete",
            "success": True,
            "result": execution_result.result,
            "explanation": explanation,
            "monitoring": post_monitoring,
        }
```

---

## 🔗 Agent Dependencies

### Direct Dependencies

```
CognitionKernel
    ↓ provides routing to
    ├─ OversightAgent
    ├─ ValidatorAgent
    ├─ ExplainabilityAgent
    └─ PlannerAgent (legacy stub)
```

### Indirect Dependencies (via Kernel)

```
All 4 Agents
    ↓ access via kernel
    ├─ Triumvirate (governance decisions)
    ├─ FourLaws (safety validation)
    ├─ Black Vault (forbidden content)
    ├─ Identity System (mutation validation)
    ├─ Memory System (history, logging)
    └─ Reflection System (insights, analysis)
```

### Cross-Agent Dependencies

```
OversightAgent
    ↓ can trigger
    ValidatorAgent
        ↓ blocks invalid actions
        ExplainabilityAgent
            ↓ explains blocks
            OversightAgent (logs explanation access)
```

---

## 📊 Authority Hierarchy

### Authority Levels (from Platform Tiers)

```
TIER 1 (GOVERNANCE)
    AuthorityLevel.SOVEREIGN
    ├─ CognitionKernel
    ├─ Triumvirate
    └─ FourLaws

TIER 2 (CAPABILITY)
    AuthorityLevel.ENFORCEMENT
    ├─ ValidatorAgent (can block)
    
    AuthorityLevel.ADVISORY
    ├─ OversightAgent (can observe)
    ├─ ExplainabilityAgent (can explain)
    
    AuthorityLevel.NONE
    └─ PlannerAgent (stub, no authority)

TIER 3 (EXECUTION)
    AuthorityLevel.EXECUTION
    ├─ Tools
    ├─ Plugins
    └─ External APIs
```

### Authority Flow

```
┌────────────────────────────────────┐
│  Authority flows DOWNWARD          │
│  (control, permissions, blocking)  │
│                                    │
│  Tier 1 (Sovereign)                │
│      ↓                             │
│  Tier 2 (Enforcement/Advisory)     │
│      ↓                             │
│  Tier 3 (Execution)                │
└────────────────────────────────────┘

┌────────────────────────────────────┐
│  Capability flows UPWARD           │
│  (reporting, monitoring, insights) │
│                                    │
│  Tier 3 (Execution)                │
│      ↑                             │
│  Tier 2 (Capability)               │
│      ↑                             │
│  Tier 1 (Governance)               │
└────────────────────────────────────┘
```

---

## 🎯 Use Case Matrix

| Use Case | Validator | Oversight | Explainer | Planner | Kernel |
|----------|-----------|-----------|-----------|---------|--------|
| **User input validation** | ✅ Primary | ⚠️ Audit | ❌ | ❌ | ✅ Routes |
| **Security threat detection** | ✅ Detect | ✅ Monitor | ✅ Explain | ❌ | ✅ Routes |
| **Governance decision** | ⚠️ Validate | ⚠️ Monitor | ✅ Explain | ❌ | ✅ Primary |
| **System health monitoring** | ⚠️ Validate | ✅ Primary | ⚠️ Report | ❌ | ✅ Routes |
| **Decision transparency** | ❌ | ⚠️ Audit | ✅ Primary | ❌ | ⚠️ Source |
| **Identity mutation** | ✅ Validate | ✅ Monitor | ✅ Explain | ❌ | ✅ Enforce |
| **Black Vault check** | ✅ Check | ⚠️ Log | ✅ Explain | ❌ | ✅ Routes |
| **Task planning** | ❌ | ❌ | ❌ | ⚠️ Stub | ✅ (use planner_agent.py) |

**Legend:**
- ✅ Primary responsibility
- ⚠️ Supporting role
- ❌ Not involved

---

## 🔄 Message Flow Example

### Complete Flow: User Action → Validated → Executed → Monitored → Explained

```
1. User submits action
   {
     "action": "delete_user",
     "user_id": "user_123",
     "reason": "Account closure request"
   }
   
2. ValidatorAgent.validate_input()
   ↓ Routes through kernel
   ↓ Validates:
   ├─ Type: user_id is string ✅
   ├─ Security: No SQL injection ✅
   ├─ Black Vault: No forbidden patterns ✅
   └─ Result: {"valid": true}
   
3. CognitionKernel.process()
   ↓ Triumvirate review
   ├─ FourLaws: No human harm ✅
   ├─ Black Vault: No violations ✅
   ├─ Identity Guard: Valid mutation ✅
   └─ Consensus: APPROVED
   
4. Execute action (Tier 3)
   ├─ Delete user from database
   ├─ Archive user data
   └─ Result: {"success": true}
   
5. OversightAgent.monitor_execution()
   ↓ Post-execution check
   ├─ Verify deletion complete ✅
   ├─ Check data integrity ✅
   ├─ Log compliance record ✅
   └─ Result: {"compliant": true}
   
6. ExplainabilityAgent.explain_decision()
   ↓ Generate explanation
   └─ Result:
      {
        "explanation": "Action: Delete user 'user_123'
                        Result: Success
                        Reason: Account closure request approved
                        Validation: Passed security and policy checks
                        Governance: Approved by Triumvirate consensus
                        Monitoring: Deletion verified, data archived"
      }
      
7. Return to user
   {
     "success": true,
     "action": "delete_user",
     "user_id": "user_123",
     "explanation": "Your account has been deleted...",
     "compliance": "Action logged and monitored"
   }
```

---

## 📈 Performance Considerations

### Latency Budget

| Agent | Avg Latency | Max Latency | Notes |
|-------|-------------|-------------|-------|
| **ValidatorAgent** | 10-50ms | 200ms | Fast validation checks |
| **CognitionKernel** | 50-200ms | 1000ms | Governance overhead |
| **OversightAgent** | 20-100ms | 500ms | Monitoring checks |
| **ExplainabilityAgent** | 50-300ms | 2000ms | Explanation generation |
| **Total Pipeline** | 130-650ms | 3700ms | Sequential execution |

### Optimization Strategies

1. **Parallel Validation**
   ```python
   # Run independent validations in parallel
   import asyncio
   
   async def validate_parallel(data):
       tasks = [
           validator.validate_types(data),
           validator.validate_security(data),
           validator.validate_black_vault(data),
       ]
       results = await asyncio.gather(*tasks)
       return all(r["valid"] for r in results)
   ```

2. **Cached Explanations**
   ```python
   # Cache common explanations
   @lru_cache(maxsize=1000)
   def explain_common_decision(decision_hash: str) -> dict:
       return explainer.explain_decision(...)
   ```

3. **Lazy Monitoring**
   ```python
   # Monitor asynchronously, don't block execution
   oversight.monitor_async(execution_id, callback=log_results)
   ```

---

## 🔐 Security Considerations

### Agent Isolation

- Each agent operates in isolated context
- No direct agent-to-agent calls (all through kernel)
- Agent state is protected by kernel routing

### Authority Enforcement

- ValidatorAgent can **block** but not **execute**
- OversightAgent can **observe** but not **modify**
- ExplainabilityAgent can **explain** but not **decide**
- PlannerAgent has **no authority** (stub)

### Audit Trail

All agent interactions logged:
```python
{
    "timestamp": "2025-01-26T10:30:00Z",
    "kernel_execution_id": "exec_123",
    "agent_sequence": [
        {"agent": "ValidatorAgent", "action": "validate_input", "result": "approved"},
        {"agent": "CognitionKernel", "action": "process", "result": "approved"},
        {"agent": "OversightAgent", "action": "monitor", "result": "compliant"},
        {"agent": "ExplainabilityAgent", "action": "explain", "result": "generated"},
    ],
    "user_id": "user_456",
}
```

---

**Documentation maintained by:** AI Systems Documentation Team  
**Last updated:** 2025-01-26  
**Diagram version:** 1.0.0  
**Related:** [oversight_agent.md](oversight_agent.md), [validator_agent.md](validator_agent.md), [explainability_agent.md](explainability_agent.md), [planner_agent.md](planner_agent.md)

---

## 📁 Source Code References

This documentation references the following source files:

- [[src/app/agents/explainability.py]]
- [[src/app/agents/oversight.py]]
- [[src/app/agents/planner_agent.py]]
- [[src/app/agents/validator.py]]

---

---

## 🔗 Relationship Maps

This component is documented in the following relationship maps:
- [[relationships/agents/AGENT_ORCHESTRATION.md|Agent Orchestration]]
- [[relationships/agents/PLANNING_HIERARCHIES.md|Planning Hierarchies]]
- [[relationships/agents/VALIDATION_CHAINS.md|Validation Chains]]

---

---

## 📚 Referenced In Relationship Maps

This implementation is referenced in:
- [[relationships/agents/AGENT_ORCHESTRATION.md|Agent Orchestration Architecture]]
- [[relationships/agents/PLANNING_HIERARCHIES.md|Planning Hierarchies]]
- [[relationships/agents/VALIDATION_CHAINS.md|Validation Chains]]

---
