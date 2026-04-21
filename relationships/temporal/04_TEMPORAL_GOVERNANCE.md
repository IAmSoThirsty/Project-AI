# Temporal Governance Integration - Project-AI

## 📋 Document Metadata
- **Category**: Temporal Infrastructure
- **Last Updated**: 2025-01-21
- **Scope**: Constitutional enforcement, policy workflows, temporal laws, and governance patterns

## 🎯 Overview

Project-AI integrates Temporal with constitutional governance to provide time-bounded policy enforcement, historical auditing, and durable compliance workflows. This document maps the governance-specific Temporal patterns.

---

## 1️⃣ TEMPORAL LAW SYSTEM

### 1.1 Temporal Law Concepts

**Location**: `gradle-evolution/constitutional/temporal_law.py`

#### Core Classes
```
TemporalLaw
  │
  ├─→ law_id: str (unique identifier)
  ├─→ effective_from: datetime (activation timestamp)
  ├─→ effective_until: datetime | None (expiration, or None for permanent)
  ├─→ description: str (human-readable policy)
  └─→ rules: list[dict] (policy rules)

TemporalLawRegistry
  │
  ├─→ storage_path: Path (persistence location)
  ├─→ laws: dict[str, TemporalLaw] (in-memory registry)
  ├─→ Methods:
  │   ├─→ register_law(law)
  │   ├─→ get_active_laws(at: datetime)
  │   ├─→ revoke_law(law_id)
  │   ├─→ save() / load()

TemporalLawEnforcer
  │
  ├─→ temporal_client: Client (connection to Temporal)
  ├─→ task_queue: str (default: "constitutional-enforcement")
  ├─→ workflow_cache: dict (action_id → workflow_id)
  └─→ Methods:
      ├─→ enforce_with_timeout(action, metadata, timeout)
      ├─→ query_historical_decision(action, timestamp)
      ├─→ schedule_periodic_review(action, metadata, interval)
      ├─→ enforce_time_bounded_policy(action, metadata, valid_until)
      └─→ cleanup_expired_workflows(max_age_days)
```

---

### 1.2 Temporal Law Lifecycle

```
Law Creation
  │
  ├─→ Define TemporalLaw(
  │     law_id="data-retention-2025",
  │     effective_from="2025-01-01T00:00:00Z",
  │     effective_until="2026-01-01T00:00:00Z",
  │     description="Delete user data after 90 days",
  │     rules=[{"action": "delete_data", "condition": "age > 90d"}]
  │   )
  │
  ├─→ Registry.register_law(law)
  │
  ├─→ Registry.save() → Persists to data/governance/temporal_laws.json
  │
  └─→ Law is now active and enforceable

Law Activation Check
  │
  ├─→ Law.is_active(at=datetime.now())
  │   ├─→ Check: now >= effective_from
  │   ├─→ Check: now <= effective_until (if set)
  │   └─→ Return: bool
  │
  └─→ Only active laws are enforced

Law Revocation
  │
  ├─→ Registry.revoke_law(law_id)
  │
  ├─→ Removes from registry.laws
  │
  ├─→ Registry.save() → Updates persistence
  │
  └─→ Law is no longer enforced
```

---

## 2️⃣ POLICY ENFORCEMENT WORKFLOWS

### 2.1 PolicyEnforcementWorkflow [[temporal/workflows/enhanced_security_workflows.py]]

**Location**: Conceptual (referenced in `temporal_law.py`)  
**Task Queue**: `constitutional-enforcement`

#### Workflow Structure
```python
@workflow.defn
class PolicyEnforcementWorkflow:
    """
    Durable policy enforcement workflow.
    
    Features:
    - Time-bounded policy evaluation
    - Historical decision recording
    - Audit trail persistence
    """
    
    @workflow.run
    async def run(self, action: str, metadata: dict) -> dict:
        """
        Enforce policy for an action.
        
        Args:
            action: Action to validate
            metadata: Action context (user, risk_level, etc.)
        
        Returns:
            {allowed: bool, reason: str, timestamp: str}
        """
        workflow.logger.info("Enforcing policy for action: %s", action)
        
        # Get active temporal laws
        active_laws = await workflow.execute_activity(
            "get_active_temporal_laws",
            start_to_close_timeout=timedelta(seconds=10)
        )
        
        # Evaluate action against laws
        decision = await workflow.execute_activity(
            "evaluate_action_against_laws",
            args=[action, metadata, active_laws],
            start_to_close_timeout=timedelta(seconds=30)
        )
        
        # Record decision for historical query
        await workflow.execute_activity(
            "record_policy_decision",
            args=[action, decision],
            start_to_close_timeout=timedelta(seconds=10)
        )
        
        return decision
```

---

### 2.2 PeriodicPolicyReview Workflow

**Location**: Conceptual (referenced in `temporal_law.py`)  
**Task Queue**: `constitutional-enforcement`

#### Workflow Structure
```python
@workflow.defn
class PeriodicPolicyReview:
    """
    Continuous policy review workflow.
    
    Periodically re-evaluates actions to detect policy drift.
    """
    
    @workflow.run
    async def run(self, action: str, metadata: dict, interval_hours: int) -> dict:
        """
        Periodic review loop.
        
        Args:
            action: Action to review
            metadata: Action context
            interval_hours: Review frequency
        
        Returns:
            Review summary
        """
        review_count = 0
        policy_changes = []
        
        while True:
            # Wait for interval
            await asyncio.sleep(interval_hours * 3600)
            
            # Re-evaluate policy
            current_decision = await workflow.execute_activity(
                "evaluate_action_against_laws",
                args=[action, metadata],
                start_to_close_timeout=timedelta(seconds=30)
            )
            
            # Compare with previous decision
            if review_count > 0:
                if current_decision != previous_decision:
                    # Policy changed
                    policy_changes.append({
                        "timestamp": workflow.now(),
                        "old_decision": previous_decision,
                        "new_decision": current_decision
                    })
                    
                    # Notify
                    await workflow.execute_activity(
                        "notify_policy_change",
                        args=[action, policy_changes[-1]],
                        start_to_close_timeout=timedelta(seconds=10)
                    )
            
            previous_decision = current_decision
            review_count += 1
```

---

## 3️⃣ GOVERNANCE ACTIVITIES

### 3.1 get_active_temporal_laws
**Function**: Retrieve active laws at current time  
**Type**: Data retrieval

```python
@activity.defn
async def get_active_temporal_laws() -> list[dict]:
    """
    Get all currently active temporal laws.
    
    Returns:
        List of active law dicts
    """
    registry = TemporalLawRegistry(storage_path="data/governance/temporal_laws.json")
    registry.load()
    
    active_laws = registry.get_active_laws()
    
    return [law.to_dict() for law in active_laws]
```

---

### 3.2 evaluate_action_against_laws
**Function**: Evaluate action against policy rules  
**Type**: Policy evaluation

```python
@activity.defn
async def evaluate_action_against_laws(
    action: str,
    metadata: dict,
    laws: list[dict]
) -> dict:
    """
    Evaluate action against active laws.
    
    Args:
        action: Action to evaluate
        metadata: Action context
        laws: List of active laws
    
    Returns:
        {allowed: bool, reason: str, timestamp: str}
    """
    activity.logger.info("Evaluating action: %s", action)
    
    # Check each law
    for law in laws:
        for rule in law.get("rules", []):
            if rule.get("action") == action:
                # Evaluate condition
                if not evaluate_condition(rule["condition"], metadata):
                    return {
                        "allowed": False,
                        "reason": f"Blocked by law: {law['law_id']}",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "law_id": law["law_id"]
                    }
    
    # No blocking laws
    return {
        "allowed": True,
        "reason": "No blocking laws",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
```

---

### 3.3 record_policy_decision
**Function**: Record decision for audit trail  
**Type**: Audit logging

```python
@activity.defn
async def record_policy_decision(action: str, decision: dict) -> bool:
    """
    Record policy decision for historical audit.
    
    Args:
        action: Action evaluated
        decision: Enforcement decision
    
    Returns:
        True if recorded successfully
    """
    log_entry = {
        "action": action,
        "decision": decision,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "workflow_id": activity.info().workflow_id,
        "activity_id": activity.info().activity_id
    }
    
    # Append to audit log
    audit_path = Path("data/governance/audit_log.jsonl")
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    
    with audit_path.open("a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    activity.logger.info("Recorded decision for action: %s", action)
    return True
```

---

### 3.4 notify_policy_change
**Function**: Notify on policy change  
**Type**: Notification

```python
@activity.defn
async def notify_policy_change(action: str, change: dict) -> bool:
    """
    Notify stakeholders of policy change.
    
    Args:
        action: Action affected
        change: Policy change details
    
    Returns:
        True if notified successfully
    """
    notification = {
        "type": "policy_change",
        "action": action,
        "timestamp": change["timestamp"],
        "old_decision": change["old_decision"],
        "new_decision": change["new_decision"]
    }
    
    # Send to notification service
    # (Email, Slack, PagerDuty, etc.)
    activity.logger.warning("Policy changed for action: %s", action)
    
    return True
```

---

## 4️⃣ ENFORCEMENT PATTERNS

### 4.1 Standard Enforcement

```python
# Application code
enforcer = TemporalLawEnforcer(temporal_client, task_queue="constitutional-enforcement")

# Enforce action
result = await enforcer.enforce_with_timeout(
    action="delete_user_data",
    metadata={
        "user_id": "12345",
        "data_age_days": 95,
        "risk_level": 2
    },
    timeout_seconds=30
)

if result["allowed"]:
    # Proceed with action
    await delete_user_data(user_id)
else:
    # Block action
    logger.warning("Action blocked: %s", result["reason"])
```

---

### 4.2 Time-Bounded Enforcement

```python
# Enforce policy that expires at specific time
result = await enforcer.enforce_time_bounded_policy(
    action="emergency_access",
    metadata={
        "user_id": "admin-123",
        "reason": "security incident"
    },
    valid_until=datetime.now() + timedelta(hours=1)
)

# Policy automatically expires after 1 hour
```

---

### 4.3 Historical Query

```python
# Query historical decision
historical_decision = await enforcer.query_historical_decision(
    action="delete_user_data",
    timestamp=datetime(2025, 1, 20, 10, 0, 0)
)

# Returns:
# {
#   "allowed": False,
#   "reason": "User data age < 90 days",
#   "timestamp": "2025-01-20T10:00:00Z",
#   "law_id": "data-retention-2025"
# }
```

---

### 4.4 Periodic Review

```python
# Schedule periodic review every 24 hours
workflow_id = await enforcer.schedule_periodic_review(
    action="critical_system_access",
    metadata={
        "system": "production-database",
        "access_level": "admin"
    },
    interval_hours=24
)

# Workflow continuously monitors policy changes
```

---

## 5️⃣ CONSTITUTIONAL MONITORING INTEGRATION

### 5.1 ConstitutionalMonitoringWorkflow [[temporal/workflows/enhanced_security_workflows.py]]

**Location**: `temporal/workflows/security_agent_workflows.py`  
**Primary Workflow**: `ConstitutionalMonitoringWorkflow` [[temporal/workflows/enhanced_security_workflows.py]]

#### Integration with Temporal Law
```
ConstitutionalMonitoringWorkflow.run(request)
  │
  ├─→ [Load Active Laws]
  │   └─→ Activity: get_active_temporal_laws()
  │
  ├─→ [For each test_prompt]
  │   │
  │   ├─→ Send prompt to target_endpoint
  │   │
  │   ├─→ Get response
  │   │
  │   ├─→ Activity: evaluate_response_against_laws(response, laws)
  │   │   ├─→ Check constitutional principles
  │   │   ├─→ Check temporal laws
  │   │   └─→ Return: {has_violations: bool, violations: list}
  │   │
  │   └─→ If has_violations:
  │       └─→ Activity: record_constitutional_violation(...)
  │
  └─→ RETURN: ConstitutionalMonitoringResult
```

---

### 5.2 Enhanced Constitutional Monitoring

**Location**: `temporal/workflows/enhanced_security_workflows.py`  
**Primary Workflow**: `EnhancedConstitutionalMonitoringWorkflow` [[temporal/workflows/enhanced_security_workflows.py]]

#### Advanced Compliance Flow
```
EnhancedConstitutionalMonitoringWorkflow.run(request)
  │
  ├─→ [Step 1] Load Governance Context
  │   ├─→ Activity: get_active_temporal_laws()
  │   └─→ Activity: get_constitutional_principles()
  │
  ├─→ [Step 2] Run Compliance Tests
  │   └─→ For each test_prompt:
  │       │
  │       ├─→ Activity: run_compliance_test(prompt, context)
  │       │   ├─→ Temporal law checks
  │       │   ├─→ Constitutional principle checks
  │       │   └─→ Return: compliance_result
  │       │
  │       └─→ If non-compliant:
  │           ├─→ Activity: trigger_compliance_incident(...)
  │           └─→ Activity: block_deployment(reason="compliance violation")
  │
  ├─→ [Step 3] Generate Compliance Report
  │   └─→ Activity: generate_compliance_report(results)
  │
  └─→ RETURN: ComplianceResult
```

---

## 6️⃣ AUDIT & FORENSICS

### 6.1 Audit Trail Structure

**Location**: `data/governance/audit_log.jsonl`

```jsonlines
{"action": "delete_user_data", "decision": {"allowed": true, "reason": "..."}, "timestamp": "2025-01-21T12:00:00Z", "workflow_id": "enforce-delete_user_data-1737464400.0", "activity_id": "activity-123"}
{"action": "emergency_access", "decision": {"allowed": true, "reason": "..."}, "timestamp": "2025-01-21T12:05:00Z", "workflow_id": "enforce-emergency_access-1737464700.0", "activity_id": "activity-124"}
{"action": "delete_user_data", "decision": {"allowed": false, "reason": "Blocked by law: data-retention-2025"}, "timestamp": "2025-01-21T12:10:00Z", "workflow_id": "enforce-delete_user_data-1737465000.0", "activity_id": "activity-125"}
```

---

### 6.2 Forensic Queries

#### Query 1: All Blocked Actions
```python
import json
from pathlib import Path

audit_log = Path("data/governance/audit_log.jsonl")
blocked_actions = []

with audit_log.open() as f:
    for line in f:
        entry = json.loads(line)
        if not entry["decision"]["allowed"]:
            blocked_actions.append(entry)

# blocked_actions contains all denied actions
```

#### Query 2: Actions by Time Range
```python
from datetime import datetime, timezone

start = datetime(2025, 1, 20, 0, 0, 0, tzinfo=timezone.utc)
end = datetime(2025, 1, 21, 23, 59, 59, tzinfo=timezone.utc)

actions_in_range = []

with audit_log.open() as f:
    for line in f:
        entry = json.loads(line)
        timestamp = datetime.fromisoformat(entry["timestamp"])
        
        if start <= timestamp <= end:
            actions_in_range.append(entry)
```

#### Query 3: Actions by Law
```python
law_id = "data-retention-2025"
actions_by_law = []

with audit_log.open() as f:
    for line in f:
        entry = json.loads(line)
        if entry["decision"].get("law_id") == law_id:
            actions_by_law.append(entry)
```

---

## 7️⃣ WORKFLOW GOVERNANCE METADATA

### 7.1 Workflow Governance Tags

**Location**: `src/app/temporal/WORKFLOW_GOVERNANCE.md`

```yaml
workflows:
  - name: TriumvirateWorkflow
    governance:
      risk_level: high
      requires_approval: false
      max_execution_time: 300s
      audit_level: full
      
  - name: RedTeamCampaignWorkflow
    governance:
      risk_level: critical
      requires_approval: true
      max_execution_time: 3600s
      audit_level: full
      forensic_snapshot: required
      
  - name: PolicyEnforcementWorkflow
    governance:
      risk_level: critical
      requires_approval: false
      max_execution_time: 30s
      audit_level: full
      immutable: true
```

---

### 7.2 Activity Governance Tags

```yaml
activities:
  - name: run_triumvirate_pipeline
    governance:
      risk_level: high
      requires_validation: true
      audit_level: full
      
  - name: trigger_incident
    governance:
      risk_level: critical
      requires_approval: false
      audit_level: full
      notify_on_execution: true
      
  - name: block_deployment
    governance:
      risk_level: critical
      requires_approval: false
      audit_level: full
      notify_on_execution: true
      reversible: true
```

---

## 8️⃣ GOVERNANCE INTEGRATION CHECKLIST

### ✅ New Workflow Governance Integration
- [ ] Define governance metadata (risk level, audit level)
- [ ] Add temporal law checks if applicable
- [ ] Implement policy enforcement activities
- [ ] Configure audit logging
- [ ] Add forensic snapshots if critical
- [ ] Test with mock temporal laws
- [ ] Document governance requirements
- [ ] Review with security team

### ✅ New Temporal Law Integration
- [ ] Define TemporalLaw with effective dates
- [ ] Add to TemporalLawRegistry
- [ ] Create enforcement activities
- [ ] Test activation/deactivation
- [ ] Test historical queries
- [ ] Document law purpose and scope
- [ ] Add to audit trail
- [ ] Schedule periodic reviews

---

## 9️⃣ GOVERNANCE METRICS

### Key Metrics
- **Policy Enforcement Rate**: % of actions evaluated
- **Policy Block Rate**: % of actions blocked
- **Policy Change Rate**: # of policy changes per day
- **Audit Trail Coverage**: % of actions logged
- **Historical Query Latency**: Time to retrieve historical decisions
- **Law Activation Time**: Time from law creation to active enforcement

---

## 🔟 COMPLIANCE REPORTING

### 10.1 Daily Compliance Report

```python
# Generate daily compliance report
report = {
    "date": "2025-01-21",
    "total_actions_evaluated": 1523,
    "actions_allowed": 1487,
    "actions_blocked": 36,
    "block_rate": 2.36,
    "active_laws": 12,
    "policy_changes": 2,
    "violations_detected": 3,
    "incidents_triggered": 1
}
```

---

### 10.2 Law Effectiveness Report

```python
# Analyze law effectiveness
law_report = {
    "law_id": "data-retention-2025",
    "effective_from": "2025-01-01T00:00:00Z",
    "effective_until": "2026-01-01T00:00:00Z",
    "total_evaluations": 234,
    "actions_blocked": 45,
    "block_rate": 19.23,
    "most_common_blocked_action": "delete_user_data",
    "compliance_rate": 80.77
}
```

---

## ♾️ FUTURE ENHANCEMENTS

### Planned Features
1. **AI-Powered Law Synthesis**: Automatically generate temporal laws from natural language policies
2. **Multi-Region Law Enforcement**: Different laws for different geographic regions
3. **Policy Simulation**: Test impact of new laws before activation
4. **Automated Law Expiry**: Automatic archival of expired laws
5. **Policy Drift Detection**: ML-based detection of policy violations over time
6. **Constitutional AI Integration**: Deep integration with Constitutional AI frameworks

---

## 🔗 Related Documentation

- **Workflow Chains**: See `01_WORKFLOW_CHAINS.md`
- **Activity Dependencies**: See `02_ACTIVITY_DEPENDENCIES.md`
- **Integration Flows**: See `03_TEMPORAL_INTEGRATION.md`
- **Constitutional AI**: See `gradle-evolution/constitutional/`

---

**End of Temporal Governance Integration Documentation**


---


---

## 📚 Related Documentation

### Cross-References

- [[source-docs/temporal/WORKFLOWS_COMPREHENSIVE.md|Workflows Comprehensive]]
- [[relationships/temporal/01_WORKFLOW_CHAINS.md|01 Workflow Chains]]

## 🔗 Source Code References

This documentation references the following Temporal source files:

- [[temporal/workflows/enhanced_security_workflows.py]] - Implementation file
