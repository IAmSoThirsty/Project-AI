# Temporal Workflow Chains - Project-AI

## 📋 Document Metadata
- **Category**: Temporal Infrastructure
- **Last Updated**: 2025-01-21
- **Scope**: Workflow orchestration patterns and execution chains

## 🎯 Overview

Project-AI implements durable workflow orchestration through Temporal, providing fault-tolerant, long-running operations with automatic retries, state persistence, and distributed execution.

---

## 1️⃣ CORE WORKFLOW CHAINS

### 1.1 Triumvirate Pipeline Workflow
**Location**: `temporal/workflows/triumvirate_workflow.py`  
**Primary Workflow**: `TriumvirateWorkflow` [[temporal/workflows/triumvirate_workflow.py]]  
**Task Queue**: `project-ai-tasks`

#### Execution Chain
```
START → TriumvirateWorkflow.run()
  │
  ├─→ [Telemetry] record_telemetry("workflow_start")
  │   └─→ Logs: workflow_id, request summary
  │
  ├─→ [Main Pipeline] run_triumvirate_pipeline(activity)
  │   ├─→ Activity: validate_input_activity (if !skip_validation)
  │   ├─→ Activity: run_codex_inference
  │   ├─→ Activity: run_galahad_reasoning
  │   └─→ Activity: enforce_output_policy
  │   └─→ Result: {success, output, correlation_id}
  │
  ├─→ [Telemetry] record_telemetry("workflow_complete")
  │   └─→ Logs: correlation_id, success status
  │
  └─→ RETURN: TriumvirateResult
```

**Retry Policy**:
- Initial Interval: 1s
- Max Interval: 30s
- Backoff: 2x exponential
- Max Attempts: Configurable (default: 3)

**Timeout**: Configurable (default: 300s)

---

### 1.2 Step-by-Step Triumvirate Workflow
**Location**: `temporal/workflows/triumvirate_workflow.py`  
**Primary Workflow**: `TriumvirateStepWorkflow` [[temporal/workflows/triumvirate_workflow.py]]

#### Granular Execution Chain
```
START → TriumvirateStepWorkflow.run()
  │
  ├─→ [Step 1] Input Validation
  │   ├─→ Activity: validate_input_activity(input_data, context)
  │   ├─→ Decision: valid?
  │   │   ├─→ YES: Continue with validated input
  │   │   └─→ NO: ABORT with validation error
  │   └─→ Timeout: 30s
  │
  ├─→ [Step 2] Codex Inference
  │   ├─→ Activity: run_codex_inference(input_data, context)
  │   ├─→ Timeout: 120s
  │   ├─→ Retry: Up to max_retries
  │   └─→ Output: {success, output}
  │
  ├─→ [Step 3] Galahad Reasoning
  │   ├─→ Activity: run_galahad_reasoning([input_data, codex_output], context)
  │   ├─→ Timeout: 60s
  │   └─→ Output: {success, conclusion}
  │
  ├─→ [Step 4] Output Enforcement
  │   ├─→ Activity: enforce_output_policy(conclusion, context)
  │   ├─→ Decision: allowed?
  │   │   ├─→ YES: Return success with output
  │   │   └─→ NO: ABORT with enforcement error
  │   └─→ Timeout: 30s
  │
  └─→ RETURN: TriumvirateResult with full pipeline_details
```

**Observability**: Each step logs independently, providing granular tracing.

---

## 2️⃣ SECURITY AGENT WORKFLOW CHAINS

### 2.1 Red Team Campaign Workflow
**Location**: `temporal/workflows/security_agent_workflows.py`  
**Primary Workflow**: `RedTeamCampaignWorkflow` [[temporal/workflows/security_agent_workflows.py]]  
**Task Queue**: `security-agents`

#### Execution Chain
```
START → RedTeamCampaignWorkflow.run(request)
  │
  ├─→ [Telemetry] record_telemetry("red_team_campaign_start")
  │   └─→ Log persona_count
  │
  ├─→ [Execute Campaign] run_red_team_campaign(request)
  │   ├─→ For each persona_id:
  │   │   └─→ For each target:
  │   │       ├─→ Execute attack
  │   │       ├─→ Record session
  │   │       └─→ Identify vulnerabilities
  │   ├─→ Timeout: request.timeout_seconds (default: 3600s)
  │   └─→ Result: {sessions, vulnerabilities, attack_stats}
  │
  ├─→ [Telemetry] record_telemetry("red_team_campaign_complete")
  │   └─→ Log success, total_attacks
  │
  ├─→ [Critical Check] If critical vulnerabilities found:
  │   └─→ Activity: trigger_incident_workflow(critical_vulns)
  │       └─→ Creates incident tickets, alerts
  │
  └─→ RETURN: RedTeamCampaignResult
```

**Retry Policy**:
- Initial: 2s
- Max: 60s
- Backoff: 2x
- Max Attempts: 3

---

### 2.2 Enhanced Red Team Campaign with Forensics
**Location**: `temporal/workflows/enhanced_security_workflows.py`  
**Primary Workflow**: `EnhancedRedTeamCampaignWorkflow` [[temporal/workflows/enhanced_security_workflows.py]]

#### Advanced Execution Chain
```
START → EnhancedRedTeamCampaignWorkflow.run(request)
  │
  ├─→ [Step 1] Forensic Snapshot
  │   ├─→ Activity: create_forensic_snapshot(campaign_id)
  │   ├─→ NON-RETRYABLE (maximum_attempts=1)
  │   ├─→ Timeout: 10m
  │   └─→ ABORT on failure (immutable snapshot required)
  │
  ├─→ [Step 2] Persona × Target Matrix Execution
  │   └─→ For each (persona, target) pair:
  │       │
  │       ├─→ Activity: run_red_team_attack(persona, target, snapshot_id)
  │       │   ├─→ Timeout: 15m
  │       │   ├─→ Retry: 3 attempts (cap for flaky detection)
  │       │   └─→ Result: attack_result
  │       │
  │       ├─→ Activity: evaluate_attack(attack_result)
  │       │   ├─→ Timeout: 30s
  │       │   └─→ Output: severity (critical/high/medium/low)
  │       │
  │       ├─→ Decision: If severity in [critical, high]:
  │       │   ├─→ Activity: trigger_incident(snapshot_id, attack_result, severity)
  │       │   │   ├─→ Creates incident ticket
  │       │   │   ├─→ Alerts Triumvirate
  │       │   │   └─→ Returns: incident_id
  │       │   │
  │       │   └─→ Policy Check: Should halt campaign?
  │       │       ├─→ CRITICAL: HALT campaign immediately
  │       │       └─→ HIGH: Continue (investigate all vectors)
  │       │
  │       └─→ Continue or break based on policy
  │
  ├─→ [Step 3] SARIF Report Generation
  │   ├─→ Activity: generate_sarif(results, campaign_id)
  │   ├─→ Timeout: 5m
  │   └─→ Output: sarif_report
  │
  ├─→ [Step 4] GitHub Security Upload
  │   ├─→ Activity: upload_sarif(sarif_report, repo, commit_sha)
  │   ├─→ Timeout: 5m
  │   └─→ Integrates with GitHub Security tab
  │
  ├─→ [Step 5] Triumvirate Notification
  │   ├─→ Activity: notify_triumvirate(campaign_id, results)
  │   ├─→ Timeout: 2m
  │   └─→ Sends review request
  │
  └─→ RETURN: {
      │   status: "completed" | "halted" | "aborted",
      │   snapshot_id,
      │   results,
      │   success_rate,
      │   sarif_uploaded
      └─}
```

**Key Features**:
- **Immutable Forensics**: Snapshot creation is non-retryable
- **Halt Policy**: Automatic campaign termination on critical findings
- **SARIF Integration**: Automated GitHub Security upload

---

### 2.3 Code Security Sweep Workflow
**Location**: `temporal/workflows/security_agent_workflows.py`  
**Primary Workflow**: `CodeSecuritySweepWorkflow` [[temporal/workflows/enhanced_security_workflows.py]]

#### Execution Chain
```
START → CodeSecuritySweepWorkflow.run(request)
  │
  ├─→ [Telemetry] record_telemetry("code_sweep_start")
  │
  ├─→ [Scan] run_code_vulnerability_scan(request)
  │   ├─→ Timeout: request.timeout_seconds (default: 1800s)
  │   ├─→ Scans: repo_path, scope_dirs
  │   └─→ Result: {findings, by_severity, total_findings}
  │
  ├─→ [Patch Generation] If request.generate_patches && findings:
  │   ├─→ Activity: generate_security_patches(findings)
  │   ├─→ Timeout: 300s
  │   └─→ Output: patches array
  │
  ├─→ [SARIF Report] If request.create_sarif && findings:
  │   ├─→ Activity: generate_sarif_report(findings)
  │   ├─→ Timeout: 60s
  │   └─→ Output: sarif_path
  │
  ├─→ [Telemetry] record_telemetry("code_sweep_complete")
  │
  ├─→ [Deployment Gate] If critical_count > 0:
  │   └─→ Activity: block_deployment({reason: "X critical vulnerabilities"})
  │       ├─→ Sets deployment lock
  │       └─→ Notifies DevOps
  │
  └─→ RETURN: CodeSecuritySweepResult
```

**Schedule**: Nightly, on merge to main, on security-sensitive changes

---

### 2.4 Enhanced Code Security Sweep
**Location**: `temporal/workflows/enhanced_security_workflows.py`  
**Primary Workflow**: `EnhancedCodeSecuritySweepWorkflow` [[temporal/workflows/enhanced_security_workflows.py]]

#### Advanced Chain with Auto-Patching
```
START → EnhancedCodeSecuritySweepWorkflow.run(request)
  │
  ├─→ [Step 1] Forensic Snapshot
  │   └─→ Activity: create_forensic_snapshot(scan_id)
  │
  ├─→ [Step 2] Vulnerability Scan
  │   ├─→ Activity: run_code_vulnerability_scan(scope_files, scan_id)
  │   ├─→ Timeout: 30m
  │   └─→ Output: findings with severity breakdown
  │
  ├─→ [Step 3] Patch Generation
  │   ├─→ Activity: generate_security_patches(findings)
  │   ├─→ Timeout: 20m
  │   ├─→ Evaluates patch risk
  │   └─→ Decision:
  │       ├─→ Safe patches: Auto-merge
  │       └─→ Risky patches: Create review PR
  │
  ├─→ [Step 4] SARIF Generation & Upload
  │   ├─→ Activity: generate_sarif(findings, scan_id)
  │   └─→ Activity: upload_sarif(sarif_report, repo, commit_sha)
  │
  ├─→ [Step 5] Deployment Gate
  │   └─→ If critical_count > 0:
  │       └─→ Activity: block_deployment(scan_id, critical_count, reason)
  │
  └─→ RETURN: {
      │   scan_id, snapshot_id,
      │   findings_count, critical_count,
      │   patches_generated,
      │   deployment_blocked,
      │   sarif_uploaded
      └─}
```

---

### 2.5 Constitutional Monitoring Workflow
**Location**: `temporal/workflows/security_agent_workflows.py`  
**Primary Workflow**: `ConstitutionalMonitoringWorkflow` [[temporal/workflows/enhanced_security_workflows.py]]

#### Execution Chain
```
START → ConstitutionalMonitoringWorkflow.run(request)
  │
  ├─→ [Telemetry] record_telemetry("constitutional_monitoring_start")
  │
  ├─→ [Reviews] run_constitutional_reviews(request)
  │   ├─→ For each sample_prompt:
  │   │   ├─→ Send prompt to target_endpoint
  │   │   ├─→ Apply review_mode ("self_critique" | "external")
  │   │   ├─→ Check constitutional principles
  │   │   └─→ Record violations
  │   ├─→ Timeout: request.timeout_seconds (default: 600s)
  │   └─→ Result: {reviews, violations, compliant_responses}
  │
  ├─→ [Telemetry] record_telemetry("constitutional_monitoring_complete")
  │
  └─→ RETURN: ConstitutionalMonitoringResult
```

**Schedule**: Continuous with sample traffic

---

### 2.6 Safety Testing Workflow
**Location**: `temporal/workflows/security_agent_workflows.py`  
**Primary Workflow**: `SafetyTestingWorkflow` [[temporal/workflows/enhanced_security_workflows.py]]

#### Execution Chain
```
START → SafetyTestingWorkflow.run(request)
  │
  ├─→ [Telemetry] record_telemetry("safety_testing_start")
  │
  ├─→ [Benchmark] run_safety_benchmark(request)
  │   ├─→ Load test dataset: "hydra" | "jbb" | "all"
  │   ├─→ Run max_tests against target_system
  │   ├─→ Calculate defense_rate
  │   ├─→ Timeout: request.timeout_seconds (default: 1800s)
  │   └─→ Result: {test_results, defense_rate}
  │
  ├─→ [Telemetry] record_telemetry("safety_testing_complete")
  │
  ├─→ [Alert Check] If defense_rate < 0.8 (80%):
  │   └─→ Activity: trigger_security_alert({type, rate, dataset})
  │
  └─→ RETURN: SafetyTestingResult
```

**Schedule**: Weekly comprehensive, daily for critical tests

---

## 3️⃣ AI LEARNING & MEMORY WORKFLOWS

### 3.1 AI Learning Workflow
**Location**: `src/app/temporal/workflows.py`  
**Primary Workflow**: `AILearningWorkflow` [[temporal/workflows/activities.py]]

#### Execution Chain
```
START → AILearningWorkflow.run(LearningRequest)
  │
  ├─→ [Validate] validate_learning_content(content, source, category)
  │   ├─→ Check: Content safety
  │   ├─→ Check: Category validity
  │   └─→ Timeout: 30s
  │
  ├─→ [Approval] request_human_approval(content, user_id)
  │   ├─→ Sends approval request
  │   ├─→ Timeout: Configurable (default: 24h)
  │   └─→ Decision: approved | denied
  │
  ├─→ [Store] If approved:
  │   ├─→ Activity: store_knowledge(content, category)
  │   └─→ Activity: update_memory_system(knowledge_id)
  │
  └─→ RETURN: LearningResult
```

**Human-in-the-Loop**: Requires approval for learning requests

---

### 3.2 Memory Expansion Workflow
**Location**: `src/app/temporal/workflows.py`  
**Primary Workflow**: `MemoryExpansionWorkflow` [[temporal/workflows/activities.py]]

#### Execution Chain
```
START → MemoryExpansionWorkflow.run(MemoryExpansionRequest)
  │
  ├─→ [Extract] extract_conversation_insights(messages)
  │   ├─→ Parse conversation_id, messages
  │   ├─→ Identify key concepts
  │   └─→ Timeout: 60s
  │
  ├─→ [Categorize] categorize_knowledge(insights)
  │   └─→ 6 Categories: Technical, Personal, Security, Projects, Preferences, General
  │
  ├─→ [Store] store_memories(categorized_insights)
  │   └─→ Persists to data/memory/knowledge.json
  │
  └─→ RETURN: MemoryExpansionResult with memory_count
```

---

## 4️⃣ IMAGE GENERATION WORKFLOW

### 4.1 Image Generation Workflow
**Location**: `src/app/temporal/workflows.py`  
**Primary Workflow**: `ImageGenerationWorkflow` [[temporal/workflows/activities.py]]

#### Execution Chain
```
START → ImageGenerationWorkflow.run(ImageGenerationRequest)
  │
  ├─→ [Filter] content_filter_check(prompt)
  │   ├─→ 15 blocked keywords
  │   ├─→ Safety negative prompts
  │   └─→ Decision: safe | blocked
  │
  ├─→ [Generate] If safe:
  │   ├─→ Activity: generate_image_activity(prompt, style, size, backend)
  │   │   ├─→ Backend: "huggingface" (Stable Diffusion 2.1)
  │   │   │   └─→ Or "openai" (DALL-E 3)
  │   │   ├─→ Apply style preset
  │   │   └─→ Timeout: 120s (HF), 60s (OpenAI)
  │   │
  │   └─→ Activity: save_image_metadata(image_path, metadata)
  │
  └─→ RETURN: ImageGenerationResult
```

**Style Presets**: 10 options (photorealistic, digital_art, oil_painting, watercolor, anime, sketch, abstract, cyberpunk, fantasy, minimalist)

---

## 5️⃣ DATA ANALYSIS WORKFLOW

### 5.1 Data Analysis Workflow
**Location**: `src/app/temporal/workflows.py`  
**Primary Workflow**: `DataAnalysisWorkflow` [[temporal/workflows/activities.py]]

#### Execution Chain
```
START → DataAnalysisWorkflow.run(DataAnalysisRequest)
  │
  ├─→ [Validate] validate_file(file_path)
  │   ├─→ Check: Exists, readable
  │   └─→ Check: Format (CSV/XLSX/JSON)
  │
  ├─→ [Analyze] analyze_data(file_path, analysis_type)
  │   ├─→ Type: "clustering" → K-means clustering
  │   ├─→ Type: "statistics" → Descriptive stats
  │   ├─→ Type: "visualization" → Generate plots
  │   └─→ Timeout: 180s
  │
  ├─→ [Store] save_results(results, output_path)
  │
  └─→ RETURN: DataAnalysisResult
```

---

## 6️⃣ TEMPORAL GOVERNANCE INTEGRATION

### 6.1 Temporal Law Enforcement Workflow
**Location**: `gradle-evolution/constitutional/temporal_law.py`  
**Class**: `TemporalLawEnforcer` [[gradle_evolution/constitutional/temporal_law.py]]

#### Policy Enforcement Chain
```
START → enforce_with_timeout(action, metadata, timeout_seconds)
  │
  ├─→ [Start Workflow] PolicyEnforcementWorkflow
  │   ├─→ Workflow ID: f"enforce-{action}-{timestamp}"
  │   ├─→ Task Queue: "constitutional-enforcement"
  │   └─→ Stores in workflow_cache
  │
  ├─→ [Evaluate] Policy evaluation activities
  │   ├─→ Check active temporal laws
  │   ├─→ Apply time-bounded policies
  │   └─→ Evaluate risk level
  │
  ├─→ [Timeout] await with timeout_seconds
  │   ├─→ Success: Return enforcement result
  │   └─→ Timeout: Return {allowed: false, reason: "timeout"}
  │
  └─→ RETURN: {allowed, reason, timestamp}
```

#### Historical Query Chain
```
query_historical_decision(action, timestamp)
  │
  ├─→ Get workflow_id from cache
  ├─→ Get workflow handle
  ├─→ Query: "get_decision_at_time" with timestamp
  └─→ RETURN: Historical decision data
```

#### Periodic Review Chain
```
schedule_periodic_review(action, metadata, interval_hours)
  │
  ├─→ [Start] PeriodicPolicyReview workflow
  │   ├─→ Schedule: Every interval_hours
  │   └─→ Workflow ID: f"review-{action}-{timestamp}"
  │
  ├─→ [Loop] While not cancelled:
  │   ├─→ Sleep: interval_hours
  │   ├─→ Re-evaluate policy
  │   └─→ Log decision changes
  │
  └─→ RETURN: workflow_id
```

---

## 7️⃣ WORKFLOW SCHEDULING PATTERNS

### 7.1 Scheduled Workflows

| Workflow | Schedule | Task Queue |
|----------|----------|------------|
| RedTeamCampaignWorkflow [[temporal/workflows/security_agent_workflows.py]] | Daily (high-priority personas), Weekly (comprehensive) | security-agents |
| CodeSecuritySweepWorkflow [[temporal/workflows/enhanced_security_workflows.py]] | Nightly, on merge to main, on security changes | security-agents |
| ConstitutionalMonitoringWorkflow [[temporal/workflows/enhanced_security_workflows.py]] | Continuous (with sample traffic) | constitutional-enforcement |
| SafetyTestingWorkflow [[temporal/workflows/enhanced_security_workflows.py]] | Weekly (comprehensive), Daily (critical tests) | security-agents |

### 7.2 On-Demand Workflows

| Workflow | Trigger | Task Queue |
|----------|---------|------------|
| TriumvirateWorkflow [[temporal/workflows/triumvirate_workflow.py]] | User request, API call | project-ai-tasks |
| AILearningWorkflow [[temporal/workflows/activities.py]] | Learning request submission | project-ai-tasks |
| ImageGenerationWorkflow [[temporal/workflows/activities.py]] | User prompt submission | project-ai-tasks |
| DataAnalysisWorkflow | File upload, analysis request | project-ai-tasks |

---

## 8️⃣ CROSS-WORKFLOW INTERACTIONS

### 8.1 Workflow Chaining

```
User Request
  │
  ├─→ TriumvirateWorkflow
  │   └─→ Output violates policy
  │       └─→ TRIGGER: ConstitutionalMonitoringWorkflow
  │
  └─→ RedTeamCampaignWorkflow
      └─→ Critical vulnerability found
          ├─→ TRIGGER: EnhancedCodeSecuritySweepWorkflow
          └─→ TRIGGER: Incident workflow
```

### 8.2 Workflow Dependencies

```
EnhancedRedTeamCampaignWorkflow
  │
  ├─→ REQUIRES: create_forensic_snapshot (Step 1)
  │   └─→ All subsequent steps depend on snapshot_id
  │
  └─→ TRIGGERS: (if conditions met)
      ├─→ trigger_incident (on critical/high severity)
      ├─→ upload_sarif (for GitHub Security)
      └─→ notify_triumvirate (on completion)
```

---

## 9️⃣ RETRY & ERROR HANDLING STRATEGIES

### 9.1 Retry Policy Matrix

| Workflow | Initial Interval | Max Interval | Backoff | Max Attempts | Notes |
|----------|------------------|--------------|---------|--------------|-------|
| TriumvirateWorkflow | 1s | 30s | 2x | 3 | Standard retry |
| RedTeamCampaignWorkflow | 2s | 60s | 2x | 3 | Longer intervals for attacks |
| CodeSecuritySweepWorkflow | 1s | 30s | 2x | 3 | Standard retry |
| Forensic Snapshot | N/A | N/A | N/A | 1 | **Non-retryable** |
| Telemetry Activities | N/A | N/A | N/A | 1 | Don't retry logging |

### 9.2 Timeout Matrix

| Activity | Timeout | Rationale |
|----------|---------|-----------|
| Forensic Snapshot | 10m | Large state capture |
| Red Team Attack | 15m | Complex multi-turn attacks |
| Vulnerability Scan | 30m | Full codebase analysis |
| Patch Generation | 20m | AST transformations |
| SARIF Upload | 5m | Network I/O |
| Telemetry | 10s | Lightweight logging |

### 9.3 Error Recovery Patterns

#### Pattern 1: Graceful Degradation
```python
try:
    result = await execute_activity(...)
except ActivityError:
    # Fall back to local enforcement
    result = local_fallback(...)
```

#### Pattern 2: Circuit Breaker
```python
if failure_count > threshold:
    # Halt workflow execution
    return {status: "halted", reason: "circuit_open"}
```

#### Pattern 3: Compensating Actions
```python
try:
    await critical_operation()
except Exception:
    await compensate()  # Rollback changes
    raise
```

---

## 🔟 WORKFLOW OBSERVABILITY

### 10.1 Telemetry Points

Every workflow emits telemetry at:
1. **Start**: `record_telemetry("workflow_start")`
2. **Complete**: `record_telemetry("workflow_complete")`
3. **Error**: `record_telemetry("workflow_error")`

### 10.2 Correlation IDs

All workflows use correlation IDs for tracing:
- **Triumvirate**: `correlation_id` in result
- **Security**: `campaign_id`, `scan_id`
- **Learning**: `knowledge_id`
- **Image Gen**: `image_path` as identifier

### 10.3 Workflow Queries

Workflows support queries for live inspection:
- `get_decision_at_time(timestamp)` - Historical policy decisions
- `get_enforcement_history(lookback_hours)` - Enforcement logs
- `get_workflow_status()` - Current execution state

---

## ♾️ WORKFLOW LIFECYCLE MANAGEMENT

### Workflow States
1. **Scheduled**: Workflow registered but not started
2. **Running**: Active execution
3. **Completed**: Successful finish
4. **Failed**: Terminated with error
5. **Timed Out**: Exceeded execution timeout
6. **Cancelled**: Manually cancelled
7. **Continued-As-New**: Restarted with new history

### Cleanup
- **Expired Workflows**: Cleaned up after 30 days
- **Method**: `cleanup_expired_workflows(max_age_days)`
- **Location**: `TemporalLawEnforcer` [[gradle_evolution/constitutional/temporal_law.py]]

---

## 📊 WORKFLOW METRICS

### Key Performance Indicators
- **Workflow Success Rate**: % completed successfully
- **Average Execution Time**: Per workflow type
- **Retry Rate**: % of activities that required retries
- **Timeout Rate**: % of workflows that timed out
- **Incident Trigger Rate**: % of red team campaigns that triggered incidents

---

## 🎓 BEST PRACTICES

1. **Determinism**: All workflows use deterministic activity execution
2. **Idempotency**: Activities are safe to retry
3. **Timeouts**: Every activity has explicit timeout
4. **Retry Policies**: Configured per activity type
5. **Telemetry**: Non-blocking telemetry activities
6. **Correlation**: Unique IDs for tracing
7. **Graceful Degradation**: Local fallbacks when Temporal unavailable
8. **State Persistence**: Workflow state survives worker restarts

---

## 🔗 Related Documentation

- **Activity Dependencies**: See `02_ACTIVITY_DEPENDENCIES.md`
- **Integration Flows**: See `03_TEMPORAL_INTEGRATION.md`
- **Governance**: See `04_TEMPORAL_GOVERNANCE.md`

---

**End of Workflow Chains Documentation**


---


---

## 📚 Related Documentation

### Cross-References

- [[source-docs/temporal/WORKFLOWS_COMPREHENSIVE.md|Workflows Comprehensive]]
- [[relationships/temporal/02_ACTIVITY_DEPENDENCIES.md|02 Activity Dependencies]]

## 🔗 Source Code References

This documentation references the following Temporal source files:

- [[temporal/workflows/triumvirate_workflow.py]] - Implementation file
- [[temporal/workflows/security_agent_workflows.py]] - Implementation file
- [[temporal/workflows/enhanced_security_workflows.py]] - Implementation file
