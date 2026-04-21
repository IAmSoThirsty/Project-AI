# Temporal Activity Dependencies - Project-AI

## 📋 Document Metadata
- **Category**: Temporal Infrastructure
- **Last Updated**: 2025-01-21
- **Scope**: Activity definitions, dependencies, and execution patterns

## 🎯 Overview

Activities are the fundamental units of work in Temporal workflows. They encapsulate non-deterministic operations (API calls, database access, external services) and provide retry/timeout semantics.

---

## 1️⃣ TRIUMVIRATE PIPELINE ACTIVITIES

**Location**: `temporal/workflows/activities.py`  
**Module**: Triumvirate system activities

### 1.1 run_triumvirate_pipeline [[temporal/workflows/triumvirate_workflow.py]]
**Function**: Main pipeline execution activity  
**Type**: Composite (orchestrates multiple systems)

#### Dependencies
```yaml
External:
  - src.cognition.triumvirate.Triumvirate
  
Data:
  - input_data: Any
  - context: dict
  - skip_validation: bool

Outputs:
  - correlation_id: str (UUID)
  - success: bool
  - output: dict
  - duration_ms: float
  - pipeline: dict (stage details)

Configuration:
  - timeout: Configurable (default 300s)
  - retry_policy: Standard (1s → 30s, 2x backoff, 3 attempts)
```

#### Internal Flow
```
run_triumvirate_pipeline
  │
  ├─→ Import: Triumvirate
  ├─→ Extract: input_data, context, skip_validation
  ├─→ Inject: activity_id, workflow_id, attempt into context
  ├─→ Initialize: Triumvirate() (cached in worker)
  ├─→ Process: triumvirate.process(input_data, context, skip_validation)
  └─→ Return: result dict
```

**Activity Metadata Injection**:
- `activity.info().activity_id`
- `activity.info().workflow_id`
- `activity.info().attempt`

---

### 1.2 validate_input_activity [[temporal/workflows/triumvirate_workflow.py]]
**Function**: Input validation through Cerberus  
**Type**: Atomic validation

#### Dependencies
```yaml
External:
  - src.cognition.cerberus.engine.CerberusEngine
  
Data:
  - input_data: Any
  - context: dict | None

Outputs:
  - valid: bool
  - reason: str (if invalid)
  - input: Any (sanitized/transformed input)

Configuration:
  - timeout: 30s
  - retry_policy: Standard
```

#### Validation Rules
1. **Type checking**: Ensures input matches expected schema
2. **Sanitization**: Removes dangerous content
3. **Transformation**: Normalizes input format
4. **Policy enforcement**: Checks against constitutional rules

---

### 1.3 run_codex_inference [[temporal/workflows/triumvirate_workflow.py]]
**Function**: ML inference through Codex engine  
**Type**: Inference

#### Dependencies
```yaml
External:
  - src.cognition.codex.engine.CodexEngine
  
Data:
  - input_data: Any
  - context: dict | None

Outputs:
  - success: bool
  - output: dict (inference results)
  - error: str | None

Configuration:
  - timeout: 120s (2 minutes for complex inference)
  - retry_policy: Standard
```

#### Inference Pipeline
```
Codex Inference
  │
  ├─→ Load model (cached)
  ├─→ Preprocess input
  ├─→ Run inference
  ├─→ Postprocess output
  └─→ Return predictions
```

---

### 1.4 run_galahad_reasoning [[temporal/workflows/triumvirate_workflow.py]]
**Function**: Reasoning through Galahad engine  
**Type**: Symbolic reasoning

#### Dependencies
```yaml
External:
  - src.cognition.galahad.engine.GalahadEngine
  
Data:
  - inputs: list (multiple inputs to reason over)
  - context: dict | None

Outputs:
  - success: bool
  - conclusion: Any (reasoning result)
  - error: str | None

Configuration:
  - timeout: 60s
  - retry_policy: Standard
```

#### Reasoning Process
```
Galahad Reasoning
  │
  ├─→ Parse inputs (list of evidence)
  ├─→ Apply reasoning rules
  ├─→ Synthesize conclusion
  └─→ Return conclusion with confidence
```

**Input Structure**: `[input_data, codex_output]` - combines user input with ML predictions

---

### 1.5 enforce_output_policy [[temporal/workflows/triumvirate_workflow.py]]
**Function**: Output policy enforcement through Cerberus  
**Type**: Policy enforcement

#### Dependencies
```yaml
External:
  - src.cognition.cerberus.engine.CerberusEngine
  
Data:
  - output_data: Any
  - context: dict | None

Outputs:
  - allowed: bool
  - reason: str (if blocked)
  - output: Any (sanitized output)

Configuration:
  - timeout: 30s
  - retry_policy: Standard
```

#### Enforcement Checks
1. **Content filtering**: Removes prohibited content
2. **Constitutional compliance**: Checks against principles
3. **Safety checks**: Ensures output doesn't harm users
4. **Rate limiting**: Enforces usage limits

---

### 1.6 record_telemetry
**Function**: Telemetry event recording  
**Type**: Non-critical logging

#### Dependencies
```yaml
External:
  - Monitoring system (future integration)
  
Data:
  - event_type: str
  - payload: dict

Outputs:
  - success: bool

Configuration:
  - timeout: 10s
  - retry_policy: NONE (maximum_attempts=1)
  - non_blocking: true
```

#### Event Structure
```json
{
  "event_type": "workflow_start | workflow_complete | workflow_error",
  "timestamp": "2025-01-21T12:00:00Z",
  "payload": { ... },
  "workflow_id": "uuid",
  "activity_id": "uuid"
}
```

**Critical Feature**: Never fails workflow if telemetry fails

---

## 2️⃣ SECURITY AGENT ACTIVITIES

**Location**: `temporal/workflows/security_agent_activities.py`  
**Module**: Security operations activities

### 2.1 run_red_team_campaign [[temporal/workflows/security_agent_activities.py]]
**Function**: Execute red team attack campaign  
**Type**: Complex campaign orchestration

#### Dependencies
```yaml
External:
  - Security agent personas
  - Target system endpoints
  - Attack simulation frameworks
  
Data:
  - persona_ids: list[str]
  - targets: list[dict]
  - max_turns_per_attack: int
  - severity_threshold: str

Outputs:
  - success: bool
  - total_attacks: int
  - successful_attacks: int
  - failed_attacks: int
  - sessions: list[dict] (attack logs)
  - vulnerabilities_found: list[dict]

Configuration:
  - timeout: 3600s (1 hour)
  - retry_policy: {2s → 60s, 2x, 3 attempts}
```

#### Campaign Structure
```
For each persona_id in persona_ids:
  For each target in targets:
    │
    ├─→ Load persona configuration
    ├─→ Initialize attack session
    ├─→ Execute multi-turn attack (up to max_turns)
    ├─→ Record session logs
    ├─→ Identify vulnerabilities
    └─→ Aggregate results
```

---

### 2.2 run_red_team_attack [[temporal/workflows/security_agent_activities.py]]
**Function**: Single persona-target attack  
**Type**: Atomic attack execution

#### Dependencies
```yaml
External:
  - Attack simulation engine
  - Target system API
  
Data:
  - persona: str
  - target: str
  - snapshot_id: str (forensic reference)

Outputs:
  - success: bool
  - attack_log: dict
  - vulnerability_detected: bool
  - severity: str | None

Configuration:
  - timeout: 900s (15 minutes)
  - retry_policy: {1s → 30s, 2x, 3 attempts}
```

---

### 2.3 evaluate_attack [[temporal/workflows/security_agent_activities.py]]
**Function**: Evaluate attack result severity  
**Type**: Risk assessment

#### Dependencies
```yaml
External:
  - Severity classification model
  
Data:
  - attack_result: dict

Outputs:
  - severity: "critical" | "high" | "medium" | "low"

Configuration:
  - timeout: 30s
  - retry_policy: Standard
```

#### Severity Criteria
- **Critical**: System compromise, data exfiltration possible
- **High**: Privilege escalation, authentication bypass
- **Medium**: Information disclosure, DoS
- **Low**: Minor configuration issues

---

### 2.4 trigger_incident
**Function**: Create incident ticket for vulnerability  
**Type**: Incident management

#### Dependencies
```yaml
External:
  - Incident management system (GitHub Issues, Jira)
  - Notification service
  
Data:
  - snapshot_id: str
  - attack_result: dict
  - severity: str

Outputs:
  - incident_id: str
  - ticket_url: str

Configuration:
  - timeout: 300s (5 minutes)
  - retry_policy: Standard
```

---

### 2.5 create_forensic_snapshot [[temporal/workflows/atomic_security_activities.py]]
**Function**: Create immutable forensic snapshot  
**Type**: State capture (non-retryable)

#### Dependencies
```yaml
External:
  - Git snapshot tools
  - State persistence layer
  
Data:
  - campaign_id: str

Outputs:
  - snapshot_id: str
  - snapshot_path: str
  - timestamp: str

Configuration:
  - timeout: 600s (10 minutes)
  - retry_policy: NONE (maximum_attempts=1)
  - immutable: true
```

#### Snapshot Contents
1. **Code State**: Git commit SHA, diff
2. **Configuration**: Environment variables, config files
3. **Dependencies**: package.json, requirements.txt lockfiles
4. **Logs**: Recent application logs
5. **Metrics**: System health metrics at snapshot time

**Critical**: Snapshot must succeed or workflow aborts

---

### 2.6 generate_sarif [[temporal/workflows/atomic_security_activities.py]]
**Function**: Generate SARIF security report  
**Type**: Report generation

#### Dependencies
```yaml
External:
  - SARIF schema (v2.1.0)
  
Data:
  - results: list[dict] (findings or attack results)
  - identifier: str (campaign_id or scan_id)

Outputs:
  - sarif_report: dict (SARIF JSON)
  - report_path: str

Configuration:
  - timeout: 300s (5 minutes)
  - retry_policy: Standard
```

#### SARIF Structure
```json
{
  "version": "2.1.0",
  "runs": [{
    "tool": {
      "driver": {
        "name": "Project-AI Security Scanner"
      }
    },
    "results": [
      {
        "ruleId": "VULNERABILITY_ID",
        "level": "error",
        "message": { "text": "..." },
        "locations": [ ... ]
      }
    ]
  }]
}
```

---

### 2.7 upload_sarif
**Function**: Upload SARIF to GitHub Security  
**Type**: External API integration

#### Dependencies
```yaml
External:
  - GitHub API (code-scanning endpoint)
  - GitHub token (GITHUB_TOKEN env)
  
Data:
  - sarif_report: dict
  - repo: str (e.g., "IAmSoThirsty/Project-AI")
  - commit_sha: str

Outputs:
  - status: "uploaded" | "failed"
  - analysis_url: str

Configuration:
  - timeout: 300s (5 minutes)
  - retry_policy: Standard
```

#### API Endpoint
```
POST /repos/{owner}/{repo}/code-scanning/sarifs
Authorization: token {GITHUB_TOKEN}
Content-Type: application/json

Body: {
  "commit_sha": "...",
  "ref": "refs/heads/main",
  "sarif": "base64_encoded_sarif"
}
```

---

### 2.8 notify_triumvirate
**Function**: Send review request to Triumvirate  
**Type**: Notification

#### Dependencies
```yaml
External:
  - Triumvirate notification service
  
Data:
  - campaign_id: str
  - results: list[dict]

Outputs:
  - notified: bool

Configuration:
  - timeout: 120s (2 minutes)
  - retry_policy: Standard
```

---

### 2.9 run_code_vulnerability_scan
**Function**: Scan codebase for vulnerabilities  
**Type**: Static analysis

#### Dependencies
```yaml
External:
  - Bandit (Python security scanner)
  - Semgrep (multi-language scanner)
  - Custom security rules
  
Data:
  - scope_files: list[str] (directories to scan)
  - scan_id: str

Outputs:
  - success: bool
  - findings: list[dict]
  - by_severity: dict[str, int]
  - total_findings: int

Configuration:
  - timeout: 1800s (30 minutes)
  - retry_policy: Standard
```

#### Scan Process
```
Vulnerability Scan
  │
  ├─→ Run Bandit on Python files
  ├─→ Run Semgrep on all files
  ├─→ Aggregate findings
  ├─→ Deduplicate results
  ├─→ Classify by severity
  └─→ Return structured findings
```

---

### 2.10 generate_security_patches
**Function**: Generate patches for vulnerabilities  
**Type**: Automated remediation

#### Dependencies
```yaml
External:
  - AST parsing libraries
  - Patch generation engine
  
Data:
  - findings: list[dict]

Outputs:
  - patches: list[dict] (patch files)

Configuration:
  - timeout: 1200s (20 minutes)
  - retry_policy: Standard
```

#### Patch Structure
```json
{
  "vulnerability_id": "SEC-001",
  "file": "src/app/core/auth.py",
  "patch": "unified diff format",
  "risk_level": "safe | review_required",
  "auto_mergeable": true
}
```

---

### 2.11 block_deployment
**Function**: Set deployment gate to block  
**Type**: CI/CD integration

#### Dependencies
```yaml
External:
  - CI/CD system (GitHub Actions, Jenkins)
  
Data:
  - scan_id: str
  - critical_count: int
  - reason: str

Outputs:
  - blocked: bool

Configuration:
  - timeout: 120s (2 minutes)
  - retry_policy: Standard
```

---

### 2.12 run_constitutional_reviews
**Function**: Run constitutional compliance reviews  
**Type**: Policy validation

#### Dependencies
```yaml
External:
  - Constitutional principle definitions
  - Review engine
  
Data:
  - test_prompts: list[str]
  - review_mode: "self_critique" | "external"

Outputs:
  - reviews: list[dict]
  - violations: int

Configuration:
  - timeout: 600s (10 minutes)
  - retry_policy: Standard (2 attempts)
```

---

### 2.13 run_safety_benchmark
**Function**: Run safety test suite  
**Type**: Benchmarking

#### Dependencies
```yaml
External:
  - HYDRA dataset
  - JBB dataset (JailBreak Benchmark)
  
Data:
  - test_dataset: "hydra" | "jbb" | "all"
  - max_tests: int
  - target_system: str

Outputs:
  - total_tests: int
  - passed_tests: int
  - failed_tests: int
  - test_results: list[dict]
  - defense_rate: float

Configuration:
  - timeout: 1800s (30 minutes)
  - retry_policy: {2s → 60s, 2x, 3 attempts}
```

---

### 2.14 trigger_security_alert
**Function**: Trigger security alert for low defense rate  
**Type**: Alerting

#### Dependencies
```yaml
External:
  - Alerting system (PagerDuty, Slack)
  
Data:
  - alert_data: dict {type, rate, dataset}

Outputs:
  - alert_id: str

Configuration:
  - timeout: 30s
  - retry_policy: Standard
```

---

## 3️⃣ AI LEARNING & MEMORY ACTIVITIES

**Location**: `src/app/temporal/activities.py`  
**Module**: Learning and memory activities

### 3.1 validate_learning_content [[temporal/workflows/activities.py]]
**Function**: Validate learning request content  
**Type**: Content validation

#### Dependencies
```yaml
External:
  - Content safety filters
  - Category validation rules
  
Data:
  - content: str
  - source: str
  - category: str

Outputs:
  - valid: bool
  - reason: str | None

Configuration:
  - timeout: 30s
  - retry_policy: Standard
```

---

### 3.2 request_human_approval [[temporal/workflows/activities.py]]
**Function**: Request human approval for learning  
**Type**: Human-in-the-loop

#### Dependencies
```yaml
External:
  - Approval queue system
  - User notification service
  
Data:
  - content: str
  - user_id: str

Outputs:
  - approved: bool
  - approval_timestamp: str

Configuration:
  - timeout: 86400s (24 hours)
  - retry_policy: NONE (human decision)
```

#### Approval Workflow
```
request_human_approval
  │
  ├─→ Create approval request
  ├─→ Send notification to user
  ├─→ Wait for response (up to timeout)
  ├─→ If approved: Return true
  ├─→ If denied: Add to Black Vault
  └─→ If timeout: Return false (denied by default)
```

---

### 3.3 store_knowledge [[temporal/workflows/activities.py]]
**Function**: Store approved knowledge  
**Type**: Data persistence

#### Dependencies
```yaml
External:
  - data/memory/knowledge.json
  - LearningRequestManager
  
Data:
  - content: str
  - category: str

Outputs:
  - knowledge_id: str

Configuration:
  - timeout: 30s
  - retry_policy: Standard
```

---

### 3.4 update_memory_system [[temporal/workflows/activities.py]]
**Function**: Update memory expansion system  
**Type**: System integration

#### Dependencies
```yaml
External:
  - MemoryExpansionSystem
  
Data:
  - knowledge_id: str

Outputs:
  - success: bool

Configuration:
  - timeout: 30s
  - retry_policy: Standard
```

---

### 3.5 extract_conversation_insights
**Function**: Extract insights from conversation  
**Type**: NLP extraction

#### Dependencies
```yaml
External:
  - OpenAI API (GPT models)
  - Conversation parser
  
Data:
  - messages: list[dict]

Outputs:
  - insights: list[dict]

Configuration:
  - timeout: 60s
  - retry_policy: Standard
```

---

### 3.6 categorize_knowledge
**Function**: Categorize extracted knowledge  
**Type**: Classification

#### Dependencies
```yaml
External:
  - Classification model
  
Data:
  - insights: list[dict]

Outputs:
  - categorized_insights: dict[str, list]

Configuration:
  - timeout: 30s
  - retry_policy: Standard
```

#### Categories
1. **Technical**: Code, algorithms, tech concepts
2. **Personal**: User preferences, personal data
3. **Security**: Security practices, vulnerabilities
4. **Projects**: Project-specific knowledge
5. **Preferences**: User preferences, settings
6. **General**: Miscellaneous knowledge

---

### 3.7 store_memories
**Function**: Persist categorized memories  
**Type**: Data persistence

#### Dependencies
```yaml
External:
  - data/memory/knowledge.json
  
Data:
  - categorized_insights: dict

Outputs:
  - memory_count: int

Configuration:
  - timeout: 30s
  - retry_policy: Standard
```

---

## 4️⃣ IMAGE GENERATION ACTIVITIES

**Location**: `src/app/temporal/activities.py`  
**Module**: Image generation activities

### 4.1 content_filter_check
**Function**: Check prompt against content filters  
**Type**: Safety check

#### Dependencies
```yaml
External:
  - Blocked keywords list (15 keywords)
  
Data:
  - prompt: str

Outputs:
  - safe: bool
  - reason: str | None

Configuration:
  - timeout: 10s
  - retry_policy: Standard
```

#### Blocked Keywords
- violence, gore, nsfw, explicit, sexual
- hate, racism, discrimination, offensive
- illegal, drugs, weapons, terrorism
- malware, hack, exploit

---

### 4.2 generate_image_activity
**Function**: Generate image using backend  
**Type**: External API call

#### Dependencies
```yaml
External:
  - Hugging Face API (Stable Diffusion 2.1)
  - OpenAI API (DALL-E 3)
  
Data:
  - prompt: str
  - style: str
  - size: str
  - backend: "huggingface" | "openai"

Outputs:
  - image_path: str
  - metadata: dict

Configuration:
  - timeout: 120s (HF), 60s (OpenAI)
  - retry_policy: {1s → 30s, 2x, 3 attempts}
```

#### Style Application
```python
style_prompts = {
    "photorealistic": "photorealistic, 4k, highly detailed",
    "digital_art": "digital art, vibrant colors, stylized",
    "oil_painting": "oil painting, classical, textured brushstrokes",
    "watercolor": "watercolor painting, soft colors, artistic",
    "anime": "anime style, manga art, clean lines",
    "sketch": "pencil sketch, hand-drawn, artistic rendering",
    "abstract": "abstract art, non-representational, expressive",
    "cyberpunk": "cyberpunk style, neon lights, futuristic",
    "fantasy": "fantasy art, magical, ethereal",
    "minimalist": "minimalist design, clean, simple composition"
}
```

---

### 4.3 save_image_metadata
**Function**: Save image generation metadata  
**Type**: Data persistence

#### Dependencies
```yaml
External:
  - data/image_generation/history.json
  
Data:
  - image_path: str
  - metadata: dict

Outputs:
  - success: bool

Configuration:
  - timeout: 10s
  - retry_policy: Standard
```

---

## 5️⃣ DATA ANALYSIS ACTIVITIES

**Location**: `src/app/temporal/activities.py`  
**Module**: Data analysis activities

### 5.1 validate_file
**Function**: Validate data file  
**Type**: File validation

#### Dependencies
```yaml
External:
  - File system
  
Data:
  - file_path: str

Outputs:
  - valid: bool
  - format: "csv" | "xlsx" | "json"

Configuration:
  - timeout: 30s
  - retry_policy: Standard
```

---

### 5.2 analyze_data
**Function**: Perform data analysis  
**Type**: Data processing

#### Dependencies
```yaml
External:
  - pandas
  - scikit-learn (for clustering)
  - matplotlib (for visualization)
  
Data:
  - file_path: str
  - analysis_type: str

Outputs:
  - results: dict
  - output_path: str | None

Configuration:
  - timeout: 180s (3 minutes)
  - retry_policy: Standard
```

#### Analysis Types

**1. Clustering**
```python
results = {
    "clusters": int,
    "centroids": list,
    "labels": list,
    "silhouette_score": float
}
```

**2. Statistics**
```python
results = {
    "mean": dict,
    "median": dict,
    "std": dict,
    "min": dict,
    "max": dict
}
```

**3. Visualization**
```python
results = {
    "plot_path": str,
    "plot_type": "histogram" | "scatter" | "boxplot"
}
```

---

### 5.3 save_results
**Function**: Save analysis results  
**Type**: Data persistence

#### Dependencies
```yaml
External:
  - File system
  - JSON serialization
  
Data:
  - results: dict
  - output_path: str

Outputs:
  - success: bool

Configuration:
  - timeout: 30s
  - retry_policy: Standard
```

---

## 6️⃣ ACTIVITY DEPENDENCY GRAPH

### Triumvirate Pipeline Dependencies
```
run_triumvirate_pipeline
  │
  ├─→ IMPORTS: Triumvirate
  ├─→ CALLS (internal): triumvirate.process()
  └─→ DEPENDS ON: Codex, Galahad, Cerberus engines

validate_input_activity
  │
  ├─→ IMPORTS: CerberusEngine
  └─→ DEPENDS ON: Constitutional rules

run_codex_inference
  │
  ├─→ IMPORTS: CodexEngine
  └─→ DEPENDS ON: ML models

run_galahad_reasoning
  │
  ├─→ IMPORTS: GalahadEngine
  └─→ DEPENDS ON: Reasoning rules

enforce_output_policy
  │
  ├─→ IMPORTS: CerberusEngine
  └─→ DEPENDS ON: Constitutional rules

record_telemetry
  │
  └─→ DEPENDS ON: Monitoring system (future)
```

### Security Agent Dependencies
```
run_red_team_campaign
  │
  ├─→ CALLS: run_red_team_attack (multiple times)
  └─→ DEPENDS ON: Attack personas, target systems

run_red_team_attack
  │
  ├─→ DEPENDS ON: snapshot_id from create_forensic_snapshot
  └─→ CALLS: evaluate_attack

evaluate_attack
  │
  └─→ DEPENDS ON: Severity classification model

trigger_incident
  │
  ├─→ DEPENDS ON: attack_result from evaluate_attack
  └─→ CALLS: External incident management API

create_forensic_snapshot
  │
  └─→ DEPENDS ON: Git, file system

generate_sarif
  │
  ├─→ DEPENDS ON: results from scan or attacks
  └─→ CALLS: upload_sarif

upload_sarif
  │
  └─→ DEPENDS ON: GitHub API, GITHUB_TOKEN

notify_triumvirate
  │
  └─→ DEPENDS ON: Triumvirate notification service

run_code_vulnerability_scan
  │
  ├─→ DEPENDS ON: Bandit, Semgrep
  └─→ CALLS: generate_security_patches

generate_security_patches
  │
  └─→ DEPENDS ON: AST parsers, patch engine

block_deployment
  │
  └─→ DEPENDS ON: CI/CD system API
```

---

## 7️⃣ ACTIVITY ISOLATION & TESTING

### Isolation Principles
1. **No Shared State**: Activities don't share mutable state
2. **Idempotent**: Safe to retry without side effects
3. **Deterministic Inputs**: Same inputs → same outputs
4. **External Dependencies**: Clearly declared and mockable

### Testing Pattern
```python
import pytest
from unittest.mock import Mock, patch

@pytest.mark.asyncio
async def test_activity():
    # Mock external dependencies
    with patch('module.ExternalService') as mock:
        mock.return_value.method.return_value = expected_result
        
        # Execute activity
        result = await activity_function(input_data)
        
        # Verify result
        assert result == expected_result
        mock.return_value.method.assert_called_once()
```

---

## 8️⃣ ACTIVITY METRICS

### Performance Metrics
- **Execution Time**: p50, p95, p99
- **Retry Rate**: % of executions that required retries
- **Failure Rate**: % of executions that ultimately failed
- **Timeout Rate**: % of executions that timed out

### Resource Metrics
- **Memory Usage**: Peak memory per activity
- **CPU Usage**: CPU time per activity
- **Network I/O**: Data transferred per activity
- **Disk I/O**: File operations per activity

---

## 9️⃣ ACTIVITY BEST PRACTICES

1. **Timeout All Activities**: Never omit `start_to_close_timeout`
2. **Use Appropriate Retry Policies**: Critical operations = fewer retries
3. **Log Liberally**: Use `activity.logger` for debugging
4. **Handle Exceptions**: Catch and convert to activity-specific errors
5. **Validate Inputs**: Check inputs at activity start
6. **Return Structured Data**: Use dataclasses or dicts with schema
7. **Avoid Long-Running Operations**: Split into multiple activities if > 5 min
8. **Use Activity Heartbeats**: For activities > 1 minute
9. **Mock External Services**: For testing
10. **Document Dependencies**: Clearly list all external dependencies

---

## 🔟 ACTIVITY HEARTBEATS

For long-running activities (> 1 minute), use heartbeats:

```python
from temporalio import activity

@activity.defn
async def long_running_activity():
    for i in range(100):
        # Send heartbeat every iteration
        activity.heartbeat(i)
        
        # Do work
        await process_chunk(i)
    
    return "completed"
```

**Heartbeat Benefits**:
- Worker crash detection
- Progress tracking
- Faster recovery on worker restart

---

## 🔗 Related Documentation

- **Workflow Chains**: See `01_WORKFLOW_CHAINS.md`
- **Integration Flows**: See `03_TEMPORAL_INTEGRATION.md`
- **Governance**: See `04_TEMPORAL_GOVERNANCE.md`

---

**End of Activity Dependencies Documentation**


---


---

## 📚 Related Documentation

### Cross-References

- [[source-docs/temporal/ACTIVITIES_COMPREHENSIVE.md|Activities Comprehensive]]
- [[relationships/temporal/01_WORKFLOW_CHAINS.md|01 Workflow Chains]]

## 🔗 Source Code References

This documentation references the following Temporal source files:

- [[temporal/workflows/activities.py]] - Implementation file
- [[temporal/workflows/atomic_security_activities.py]] - Implementation file
- [[temporal/workflows/security_agent_activities.py]] - Implementation file
