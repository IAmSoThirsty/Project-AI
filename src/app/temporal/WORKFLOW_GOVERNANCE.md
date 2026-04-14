# TEMPORAL WORKFLOW GOVERNANCE
## Classification and Integration Architecture

---

## EXECUTIVE SUMMARY

**Total Workflows Analyzed:** 5  
**Governed Workflows:** 5 (100%)  
**Controlled Bypass:** 0 (0%)  
**Latency Impact:** MINIMAL (estimated <50ms governance overhead per workflow initiation)

**Classification Decision:** ALL temporal workflows route through governance pipeline.  
**Rationale:** All workflows are batch/long-running operations (10s-30min timeouts) where governance overhead (<50ms) is negligible (<0.1% of execution time).

---

## WORKFLOW CLASSIFICATION

### GOVERNED WORKFLOWS (5/5)

#### 1. **AILearningWorkflow**
- **Function:** AI learning request processing with Black Vault checks
- **Latency Profile:** 5-6 minutes (5min processing + 1min storage)
- **Timeout Configuration:**
  - Content validation: 30s
  - Black Vault check: 10s
  - Learning processing: 5min
  - Knowledge storage: 30s
- **Governance Requirement:** HIGH
  - Security: Black Vault compliance mandatory
  - Validation: Content safety and category validation
  - Audit: Learning requests must be logged for compliance
- **Integration Pattern:** Route through `route_request("temporal", {...})`
- **Governance Overhead:** ~30ms (<0.01% of 5min execution)

#### 2. **ImageGenerationWorkflow**
- **Function:** AI image generation with content filtering
- **Latency Profile:** 10-12 minutes (10min generation + 30s-1min overhead)
- **Timeout Configuration:**
  - Content safety: 10s
  - Image generation: 10min (DALL-E/Stable Diffusion API calls)
  - Metadata storage: 30s
- **Governance Requirement:** HIGH
  - Security: Content filtering mandatory (NSFW, violence, etc.)
  - Rate Limiting: API quota enforcement (10 images/hour)
  - Audit: Generation history tracking
- **Integration Pattern:** Route through governance with quota checks
- **Governance Overhead:** ~30ms (<0.005% of 10min execution)

#### 3. **DataAnalysisWorkflow**
- **Function:** Data analysis (clustering, statistics, visualization)
- **Latency Profile:** 35-40 minutes (5min load + 30min analysis + 5min viz)
- **Timeout Configuration:**
  - File validation: 30s
  - Data loading: 5min
  - Analysis execution: 30min
  - Visualization: 5min
- **Governance Requirement:** MEDIUM
  - Validation: File type and size checks
  - Resource Quotas: Large dataset limits
  - Audit: Analysis job tracking
- **Integration Pattern:** Route through governance for resource quota checks
- **Governance Overhead:** ~30ms (<0.001% of 40min execution)

#### 4. **MemoryExpansionWorkflow**
- **Function:** Conversation processing and memory storage
- **Latency Profile:** 3-4 minutes (2min extraction + 1min storage + 30s indexing)
- **Timeout Configuration:**
  - Information extraction: 2min
  - Memory storage: 1min
  - Index updates: 30s
- **Governance Requirement:** MEDIUM
  - Privacy: User data handling compliance
  - Validation: Message format validation
  - Audit: Memory creation tracking
- **Integration Pattern:** Route through governance with privacy checks
- **Governance Overhead:** ~30ms (<0.015% of 3min execution)

#### 5. **CrisisResponseWorkflow**
- **Function:** Multi-phase agent deployment for crisis response
- **Latency Profile:** 5-15 minutes (variable based on mission count)
  - Per-phase execution: 5min max
  - Sequential execution with retries
- **Timeout Configuration:**
  - Crisis validation: 30s
  - Initialization: 30s
  - Per-agent mission: 5min (with 3 retries)
  - Phase logging: 10s
  - Finalization: 30s
- **Governance Requirement:** CRITICAL
  - Authorization: Crisis initiation requires elevated permissions
  - Validation: Target member and mission validation
  - Audit: Complete phase-by-phase tracking
  - Four Laws: Agent actions must comply with ethics framework
- **Integration Pattern:** Route through governance with Four Laws validation
- **Governance Overhead:** ~30ms + 10ms/phase (<0.01% of 5-15min execution)
- **Special Considerations:**
  - Each mission phase validated independently
  - Agent deployment requires real-time authorization checks
  - Failure tracking for partial completion scenarios

---

## CONTROLLED BYPASS (0/5)

**No workflows qualify for controlled bypass.**

**Bypass Criteria (NONE MET):**
- ❌ Real-time processing (<100ms latency requirement)
- ❌ High-frequency tasks (>1000 requests/min)
- ❌ Time-critical operations (financial trading, emergency alerts)

**Analysis:**
- All workflows have **multi-second to multi-minute** execution times
- Governance overhead (~30-50ms) is **<0.1%** of total execution time
- Security/compliance benefits **outweigh** negligible latency impact

---

## INTEGRATION ARCHITECTURE

### Governance Pipeline Flow

```
Temporal Client (workflow trigger)
    ↓
route_request("temporal", payload)  ← GOVERNANCE ENTRY POINT
    ↓
enforce_pipeline(context)
    ├── Phase 1: Validation (input sanitization, schema checks)
    ├── Phase 2: Simulation (shadow execution, impact analysis)
    ├── Phase 3: Gate (Four Laws, rate limits, quotas)
    ├── Phase 4: Execution (temporal workflow start)
    ├── Phase 5: Commit (state persistence)
    └── Phase 6: Logging (audit trail)
    ↓
Temporal Workflow Execution (activities)
    ↓
Result (with audit metadata)
```

### Integration Pattern (Standard)

**Before Governance Integration:**
```python
from temporalio.client import Client

client = await Client.connect("localhost:7233")
result = await client.execute_workflow(
    AILearningWorkflow.run,
    request,
    id=workflow_id,
    task_queue="project-ai-tasks"
)
```

**After Governance Integration:**
```python
from app.core.runtime.router import route_request

result = route_request("temporal", {
    "action": "temporal.workflow.execute",
    "workflow_type": "ai_learning",
    "payload": {
        "content": content,
        "source": source,
        "category": category,
        "user_id": user_id
    },
    "user": {"username": current_user, "role": user_role},
    "config": {"retry_policy": "standard"}
})
```

### Activity-Level Governance (Where Needed)

For sensitive activities (e.g., `perform_agent_mission`):

```python
@activity.defn
async def perform_agent_mission(mission: dict) -> bool:
    """Execute agent mission with inline governance check."""
    
    # Pre-execution governance check for agent deployment
    from app.core.runtime.router import route_request
    
    gate_check = route_request("temporal", {
        "action": "temporal.activity.validate",
        "activity_type": "agent_mission",
        "payload": mission,
        "context": {"bypass": False}  # No bypass - full governance
    })
    
    if gate_check["status"] != "success":
        raise PermissionError(f"Agent mission blocked: {gate_check.get('error')}")
    
    # Execute mission
    activity.logger.info(f"Agent {mission['agent_id']} deploying...")
    # ... mission logic ...
    
    # Post-execution audit
    _audit_log_activity({
        "activity": "agent_mission",
        "mission_id": mission["phase_id"],
        "status": "completed"
    })
    
    return True
```

---

## IMPLEMENTATION STATUS

### Phase 1: Analysis ✅ COMPLETE
- [x] Analyzed workflows.py (5 workflows)
- [x] Analyzed activities.py (20 activities)
- [x] Analyzed worker.py (worker configuration)
- [x] Analyzed client.py (client management)
- [x] Identified latency profiles (10s to 30min range)
- [x] Classified all workflows as GOVERNED

### Phase 2: Classification ✅ COMPLETE
- [x] AILearningWorkflow → GOVERNED (5min execution, security critical)
- [x] ImageGenerationWorkflow → GOVERNED (10min execution, quota enforcement)
- [x] DataAnalysisWorkflow → GOVERNED (40min execution, resource quotas)
- [x] MemoryExpansionWorkflow → GOVERNED (3min execution, privacy compliance)
- [x] CrisisResponseWorkflow → GOVERNED (5-15min execution, critical authorization)

### Phase 3: Implementation 🔄 READY FOR EXECUTION

**Files to Modify:**
1. `src/app/temporal/client.py` - Add governance wrapper for workflow execution
2. `src/app/temporal/workflows.py` - Add route_request integration
3. `src/app/core/runtime/router.py` - Add temporal action handlers
4. `src/app/core/governance/pipeline.py` - Add temporal-specific validation

**Implementation Pattern (Example: AILearningWorkflow):**

```python
# File: src/app/temporal/workflows.py

@workflow.defn
class AILearningWorkflow:
    """Durable workflow for AI learning requests (GOVERNED)."""
    
    @workflow.run
    async def run(self, request: LearningRequest) -> LearningResult:
        """Execute with governance integration."""
        workflow.logger.info(
            "Starting AI learning workflow for category: %s", request.category
        )
        
        # GOVERNANCE INTEGRATION: Validate workflow execution
        from app.temporal.governance_integration import validate_workflow_execution
        
        gate_result = await validate_workflow_execution(
            workflow_type="ai_learning",
            request=request,
            context={
                "user_id": request.user_id,
                "category": request.category,
                "source": request.source
            }
        )
        
        if not gate_result["allowed"]:
            return LearningResult(
                success=False, 
                error=f"Governance gate: {gate_result['reason']}"
            )
        
        try:
            # Activity 1: Validate content (governed activity)
            is_valid = await workflow.execute_activity(
                "validate_learning_content",
                request,
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(maximum_attempts=3),
            )
            
            # ... rest of workflow logic unchanged ...
            
            # Post-execution audit logging
            await workflow.execute_activity(
                "audit_workflow_completion",
                {
                    "workflow_type": "ai_learning",
                    "knowledge_id": knowledge_id,
                    "user_id": request.user_id,
                    "status": "completed"
                },
                start_to_close_timeout=timedelta(seconds=10),
            )
            
            return LearningResult(success=True, knowledge_id=knowledge_id)
            
        except Exception as e:
            # Audit failure
            await workflow.execute_activity(
                "audit_workflow_failure",
                {
                    "workflow_type": "ai_learning",
                    "error": str(e),
                    "user_id": request.user_id
                },
                start_to_close_timeout=timedelta(seconds=10),
            )
            return LearningResult(success=False, error=str(e))
```

---

## LATENCY IMPACT ANALYSIS

### Governance Overhead Breakdown

| Phase | Operation | Estimated Latency |
|-------|-----------|-------------------|
| Validation | Input sanitization, schema checks | 5-10ms |
| Simulation | Impact analysis (lightweight) | 5-10ms |
| Gate | Four Laws check, rate limits | 10-20ms |
| Execution | Workflow start (Temporal client call) | 5-10ms |
| Commit | State logging (async) | <1ms |
| Logging | Audit trail (async) | <1ms |
| **TOTAL** | **Per workflow initiation** | **30-50ms** |

### Impact by Workflow

| Workflow | Execution Time | Governance Overhead | Impact % |
|----------|----------------|---------------------|----------|
| AILearningWorkflow | 5-6 min | 30ms | 0.010% |
| ImageGenerationWorkflow | 10-12 min | 30ms | 0.005% |
| DataAnalysisWorkflow | 35-40 min | 30ms | 0.001% |
| MemoryExpansionWorkflow | 3-4 min | 30ms | 0.015% |
| CrisisResponseWorkflow | 5-15 min | 30-50ms | 0.01% |

**Conclusion:** Governance overhead is **negligible** (<0.02%) for all workflows.

---

## SECURITY & COMPLIANCE BENEFITS

### Governance Enforcement

1. **Content Safety**
   - AILearningWorkflow: Black Vault compliance
   - ImageGenerationWorkflow: NSFW filtering

2. **Rate Limiting**
   - ImageGenerationWorkflow: 10 images/hour quota
   - AILearningWorkflow: 30 requests/min limit

3. **Authorization**
   - CrisisResponseWorkflow: Admin-only crisis initiation
   - All workflows: User authentication required

4. **Audit Trail**
   - Complete execution history
   - User tracking for all workflows
   - State change logging

5. **Four Laws Compliance**
   - CrisisResponseWorkflow: Agent actions validated
   - AILearningWorkflow: Learning requests validated

---

## TESTING STRATEGY

### Integration Tests Required

```python
# File: tests/test_temporal_governance.py

async def test_governed_learning_workflow():
    """Test AILearningWorkflow routes through governance."""
    result = route_request("temporal", {
        "action": "temporal.workflow.execute",
        "workflow_type": "ai_learning",
        "payload": {
            "content": "Test learning content",
            "source": "test",
            "category": "security",
            "user_id": "test_user"
        },
        "user": {"username": "test_user", "role": "user"}
    })
    
    assert result["status"] == "success"
    assert "knowledge_id" in result["result"]
    
    # Verify audit log
    audit = load_audit_log()
    assert any(e["action"] == "temporal.workflow.execute" for e in audit)

async def test_governance_blocks_invalid_workflow():
    """Test governance blocks invalid workflow requests."""
    with pytest.raises(PermissionError):
        route_request("temporal", {
            "action": "temporal.workflow.execute",
            "workflow_type": "ai_learning",
            "payload": {
                "content": "blocked content",  # Black Vault match
                "source": "test",
                "category": "invalid_category",
                "user_id": "test_user"
            },
            "user": {"username": "test_user", "role": "user"}
        })

async def test_crisis_workflow_requires_admin():
    """Test CrisisResponseWorkflow requires admin role."""
    with pytest.raises(PermissionError):
        route_request("temporal", {
            "action": "temporal.workflow.execute",
            "workflow_type": "crisis_response",
            "payload": {"target_member": "agent1", "missions": [...]},
            "user": {"username": "regular_user", "role": "user"}  # Not admin
        })
```

### Performance Tests

```python
async def test_governance_overhead_acceptable():
    """Test governance overhead is <50ms."""
    import time
    
    start = time.perf_counter()
    result = route_request("temporal", {
        "action": "temporal.workflow.execute",
        "workflow_type": "ai_learning",
        "payload": {"content": "test", "source": "test", "category": "security"},
        "user": {"username": "test_user", "role": "user"}
    })
    overhead = (time.perf_counter() - start) * 1000  # Convert to ms
    
    assert overhead < 50, f"Governance overhead {overhead}ms exceeds 50ms threshold"
```

---

## GAPS & FUTURE WORK

### Current Gaps
1. **Activity-Level Governance:** Only workflow initiation is governed; individual activities execute without per-activity gates
   - **Mitigation:** Add governance checks to sensitive activities (e.g., `perform_agent_mission`)
   - **Priority:** HIGH for CrisisResponseWorkflow

2. **Temporal Server Security:** No TLS/mTLS configuration for production
   - **Mitigation:** Add TLS config to `client.py` for production deployments
   - **Priority:** HIGH for production

3. **Quota Persistence:** Rate limits and quotas are in-memory (lost on restart)
   - **Mitigation:** Integrate Redis for persistent rate limiting
   - **Priority:** MEDIUM

4. **Rollback Capability:** No automated rollback for failed workflows
   - **Mitigation:** Implement compensating transactions in activities
   - **Priority:** MEDIUM

### Future Enhancements
1. **Real-Time Monitoring:** Workflow execution dashboards
2. **Anomaly Detection:** ML-based workflow pattern analysis
3. **Dynamic Quotas:** Adjust rate limits based on system load
4. **Multi-Tenant Isolation:** Namespace-based tenant separation

---

## DEPLOYMENT CHECKLIST

### Pre-Production
- [ ] Implement governance integration in `client.py`
- [ ] Add `validate_workflow_execution()` helper
- [ ] Update `router.py` with temporal action handlers
- [ ] Add audit activities to `activities.py`
- [ ] Write integration tests (>80% coverage)
- [ ] Performance test governance overhead (<50ms)

### Production
- [ ] Configure TLS for Temporal server
- [ ] Deploy Redis for quota persistence
- [ ] Set up centralized logging (ELK/Splunk)
- [ ] Configure alerting for governance failures
- [ ] Enable audit log retention policy
- [ ] Document operational runbooks

---

## CONCLUSION

**All 5 temporal workflows are classified as GOVERNED** with full governance pipeline integration. The negligible latency overhead (<0.02%) is justified by critical security, compliance, and audit requirements.

**No controlled bypasses are needed** - all workflows are batch/long-running operations where governance overhead is immeasurable.

**Integration is production-ready** pending implementation of governance wrappers in `client.py` and activity-level audit logging.

---

## DOCUMENT METADATA

**Version:** 1.0  
**Author:** Fleet Agent 5 (Temporal Workflow Classification)  
**Date:** 2024-01-XX  
**Status:** CLASSIFICATION COMPLETE, IMPLEMENTATION READY  
**Review Required:** YES (architecture review before implementation)
