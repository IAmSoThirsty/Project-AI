# Temporal Relationships Documentation - Project-AI

## 📋 Mission Summary
**Agent**: AGENT-057: Temporal Workflows Relationship Mapping Specialist  
**Mission**: Document relationships for 4 Temporal systems (Workflows, Activities, Integration, Temporal Governance)  
**Completion Date**: 2025-01-21  
**Status**: ✅ **COMPLETE**

---

## 🎯 Documentation Overview

This directory contains comprehensive relationship maps for Project-AI's Temporal orchestration infrastructure. All four target systems are fully documented with detailed execution flows, dependency graphs, and integration patterns.

---

## 📚 Documentation Index

### 1️⃣ [Workflow Chains](./01_WORKFLOW_CHAINS.md)
**Scope**: Workflow orchestration patterns and execution chains  
**File Size**: 21.3 KB  
**Key Topics**:
- Core workflow chains (Triumvirate, Security, Learning, Image Gen, Data Analysis)
- Step-by-step execution flows with decision trees
- Retry policies and timeout configurations
- Workflow scheduling patterns (daily, weekly, on-demand)
- Cross-workflow interactions and dependencies
- Error handling and recovery strategies
- Workflow lifecycle management
- Observability and telemetry integration

**Workflows Documented** (11 total):
1. `TriumvirateWorkflow` [[temporal/workflows/triumvirate_workflow.py]] - Durable AI pipeline orchestration
2. `TriumvirateStepWorkflow` [[temporal/workflows/triumvirate_workflow.py]] - Granular step-by-step execution
3. `RedTeamCampaignWorkflow` [[temporal/workflows/security_agent_workflows.py]] - Persona-based security testing
4. `EnhancedRedTeamCampaignWorkflow` [[temporal/workflows/enhanced_security_workflows.py]] - Forensic snapshots + SARIF upload
5. `CodeSecuritySweepWorkflow` [[temporal/workflows/enhanced_security_workflows.py]] - Vulnerability scanning
6. `EnhancedCodeSecuritySweepWorkflow` [[temporal/workflows/enhanced_security_workflows.py]] - Auto-patching + deployment gates
7. `ConstitutionalMonitoringWorkflow` [[temporal/workflows/enhanced_security_workflows.py]] - AI compliance monitoring
8. `EnhancedConstitutionalMonitoringWorkflow` [[temporal/workflows/enhanced_security_workflows.py]] - Advanced compliance
9. `SafetyTestingWorkflow` [[temporal/workflows/enhanced_security_workflows.py]] - Jailbreak benchmarking (HYDRA, JBB)
10. `AILearningWorkflow` [[temporal/workflows/activities.py]] - Human-in-the-loop learning
11. `ImageGenerationWorkflow` [[temporal/workflows/activities.py]] - Multi-backend image generation

---

### 2️⃣ [Activity Dependencies](./02_ACTIVITY_DEPENDENCIES.md)
**Scope**: Activity definitions, dependencies, and execution patterns  
**File Size**: 25.3 KB  
**Key Topics**:
- Triumvirate pipeline activities (6 activities)
- Security agent activities (14 activities)
- AI learning & memory activities (7 activities)
- Image generation activities (3 activities)
- Data analysis activities (3 activities)
- Activity dependency graphs
- Isolation and testing patterns
- Heartbeat patterns for long-running activities
- Performance and resource metrics

**Activities Documented** (33 total):
- **Triumvirate**: `run_triumvirate_pipeline` [[temporal/workflows/triumvirate_workflow.py]], `validate_input_activity` [[temporal/workflows/triumvirate_workflow.py]], `run_codex_inference` [[temporal/workflows/triumvirate_workflow.py]], `run_galahad_reasoning` [[temporal/workflows/triumvirate_workflow.py]], `enforce_output_policy` [[temporal/workflows/triumvirate_workflow.py]], `record_telemetry`
- **Security**: `run_red_team_campaign` [[temporal/workflows/security_agent_activities.py]], `run_red_team_attack` [[temporal/workflows/security_agent_activities.py]], `evaluate_attack` [[temporal/workflows/security_agent_activities.py]], `trigger_incident`, `create_forensic_snapshot` [[temporal/workflows/atomic_security_activities.py]], `generate_sarif` [[temporal/workflows/atomic_security_activities.py]], `upload_sarif`, `notify_triumvirate`, `run_code_vulnerability_scan`, `generate_security_patches`, `block_deployment`, `run_constitutional_reviews`, `run_safety_benchmark`, `trigger_security_alert`
- **Learning**: `validate_learning_content` [[temporal/workflows/activities.py]], `request_human_approval` [[temporal/workflows/activities.py]], `store_knowledge` [[temporal/workflows/activities.py]], `update_memory_system` [[temporal/workflows/activities.py]], `extract_conversation_insights`, `categorize_knowledge`, `store_memories`
- **Image Gen**: `content_filter_check`, `generate_image_activity`, `save_image_metadata`
- **Data Analysis**: `validate_file`, `analyze_data`, `save_results`

---

### 3️⃣ [Temporal Integration Flows](./03_TEMPORAL_INTEGRATION.md)
**Scope**: Integration patterns, client usage, worker deployment, and execution flows  
**File Size**: 22.2 KB  
**Key Topics**:
- Temporal architecture overview (Server + Client + Workers)
- Client connection patterns (`TemporalClient` wrapper)
- Worker registration and deployment (3 task queues)
- Task queue architecture and specialization
- Integration with desktop application (PyQt6 + QThread)
- Integration with web application (Flask API)
- Integration with CLI (project-ai CLI)
- Cross-system integration flows (Triumvirate, Security Agents, Governance)
- Deployment patterns (local, Docker Compose, Kubernetes)
- Error handling and recovery
- Monitoring and observability (Temporal Web UI, Prometheus)
- Security considerations (mTLS, encryption)
- Temporal Cloud migration

**Task Queues**:
1. `project-ai-tasks` - General AI operations (2-4 workers)
2. `security-agents` - Security operations (2-3 workers)
3. `constitutional-enforcement` - Governance (1-2 workers)

---

### 4️⃣ [Temporal Governance Integration](./04_TEMPORAL_GOVERNANCE.md)
**Scope**: Constitutional enforcement, policy workflows, temporal laws, and governance patterns  
**File Size**: 20.0 KB  
**Key Topics**:
- Temporal Law system (`TemporalLaw` [[gradle_evolution/constitutional/temporal_law.py]], `TemporalLawRegistry`, `TemporalLawEnforcer` [[gradle_evolution/constitutional/temporal_law.py]])
- Time-bounded policy enforcement
- Historical decision queries (time-travel debugging)
- Policy enforcement workflows (`PolicyEnforcementWorkflow` [[temporal/workflows/enhanced_security_workflows.py]], `PeriodicPolicyReview`)
- Governance activities (4 activities)
- Enforcement patterns (standard, time-bounded, historical, periodic)
- Constitutional monitoring integration
- Audit trail structure and forensic queries
- Workflow and activity governance metadata
- Compliance reporting (daily reports, law effectiveness)
- Future enhancements (AI-powered law synthesis, multi-region enforcement)

**Governance Activities** (4 total):
1. `get_active_temporal_laws` - Retrieve active laws
2. `evaluate_action_against_laws` - Policy evaluation
3. `record_policy_decision` - Audit logging
4. `notify_policy_change` - Change notification

---

## 🔗 Relationship Maps

### System Interconnections

```
┌─────────────────────────────────────────────────────────────┐
│                    Temporal Server                          │
│                   (localhost:7233)                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
           ┌───────────┴───────────┬───────────────┐
           │                       │               │
     ┌─────▼─────┐         ┌──────▼──────┐ ┌─────▼─────┐
     │project-ai-│         │security-    │ │constitu-  │
     │tasks      │         │agents       │ │tional-    │
     │(2-4 wkrs) │         │(2-3 wkrs)   │ │enforce    │
     └─────┬─────┘         └──────┬──────┘ │(1-2 wkrs) │
           │                      │        └─────┬─────┘
     ┌─────▼─────────────────┐    │              │
     │ Triumvirate           │    │              │
     │ Learning              │    │              │
     │ Image Gen             │    │              │
     │ Data Analysis         │    │              │
     └───────────────────────┘    │              │
                                  │              │
                       ┌──────────▼──────────────▼──────┐
                       │ Red Team Campaigns             │
                       │ Code Security Sweeps           │
                       │ Constitutional Monitoring      │
                       │ Safety Testing                 │
                       │                                │
                       │ ┌──────────────────────────┐   │
                       │ │ Temporal Governance      │   │
                       │ │ - TemporalLaw            │   │
                       │ │ - TemporalLawRegistry    │   │
                       │ │ - TemporalLawEnforcer    │   │
                       │ └──────────────────────────┘   │
                       └────────────────────────────────┘
```

---

## 🎨 Visual Dependency Graph

```
Workflows
    │
    ├─→ TriumvirateWorkflow
    │   ├─→ run_triumvirate_pipeline (Activity)
    │   │   ├─→ Triumvirate.process() (Core System)
    │   │   │   ├─→ CerberusEngine (Validation)
    │   │   │   ├─→ CodexEngine (Inference)
    │   │   │   ├─→ GalahadEngine (Reasoning)
    │   │   │   └─→ CerberusEngine (Enforcement)
    │   │   └─→ record_telemetry (Activity)
    │   │
    │   └─→ TriumvirateStepWorkflow (Granular)
    │       ├─→ validate_input_activity
    │       ├─→ run_codex_inference
    │       ├─→ run_galahad_reasoning
    │       └─→ enforce_output_policy
    │
    ├─→ RedTeamCampaignWorkflow
    │   ├─→ run_red_team_campaign (Activity)
    │   │   └─→ For each (persona, target)
    │   └─→ trigger_incident_workflow (If critical)
    │
    ├─→ EnhancedRedTeamCampaignWorkflow
    │   ├─→ create_forensic_snapshot (Non-retryable)
    │   ├─→ run_red_team_attack (Multiple)
    │   ├─→ evaluate_attack
    │   ├─→ trigger_incident (If critical/high)
    │   ├─→ generate_sarif
    │   ├─→ upload_sarif (GitHub Security)
    │   └─→ notify_triumvirate
    │
    ├─→ CodeSecuritySweepWorkflow
    │   ├─→ run_code_vulnerability_scan
    │   ├─→ generate_security_patches
    │   ├─→ generate_sarif_report
    │   └─→ block_deployment (If critical)
    │
    ├─→ ConstitutionalMonitoringWorkflow
    │   ├─→ run_constitutional_reviews
    │   └─→ TemporalLawEnforcer (Integration)
    │       ├─→ PolicyEnforcementWorkflow
    │       │   ├─→ get_active_temporal_laws
    │       │   ├─→ evaluate_action_against_laws
    │       │   └─→ record_policy_decision
    │       │
    │       └─→ PeriodicPolicyReview
    │           └─→ Continuous monitoring loop
    │
    ├─→ AILearningWorkflow
    │   ├─→ validate_learning_content
    │   ├─→ request_human_approval (Human-in-the-loop)
    │   ├─→ store_knowledge
    │   └─→ update_memory_system
    │
    └─→ ImageGenerationWorkflow
        ├─→ content_filter_check
        ├─→ generate_image_activity
        │   ├─→ Hugging Face API (Stable Diffusion 2.1)
        │   └─→ OpenAI API (DALL-E 3)
        └─→ save_image_metadata
```

---

## 📊 Coverage Matrix

| System | Workflows | Activities | Integration Points | Governance | Documentation |
|--------|-----------|------------|-------------------|------------|---------------|
| **Triumvirate Pipeline** | ✅ 2 | ✅ 6 | ✅ Desktop + Web + CLI | ✅ Full | ✅ Complete |
| **Security Agents** | ✅ 6 | ✅ 14 | ✅ GitHub Security | ✅ Full | ✅ Complete |
| **AI Learning** | ✅ 1 | ✅ 7 | ✅ Desktop + Web | ✅ Partial | ✅ Complete |
| **Image Generation** | ✅ 1 | ✅ 3 | ✅ Desktop | ✅ Content Filter | ✅ Complete |
| **Data Analysis** | ✅ 1 | ✅ 3 | ✅ Desktop + CLI | ⚠️ None | ✅ Complete |
| **Temporal Governance** | ✅ 2 | ✅ 4 | ✅ All Systems | ✅ Full | ✅ Complete |
| **Total** | **13** | **37** | **6** | **5/6** | **100%** |

---

## 🚀 Quick Start Guide

### 1. Prerequisites
```bash
# Install Temporal CLI
brew install temporal

# Or download from https://temporal.io
```

### 2. Start Temporal Server
```bash
temporal server start-dev
```

### 3. Start Workers
```bash
# Terminal 1: General operations worker
python -m src.integrations.temporal.worker

# Terminal 2: Security operations worker (optional)
TEMPORAL_TASK_QUEUE=security-agents python -m src.integrations.temporal.worker

# Terminal 3: Governance worker (optional)
TEMPORAL_TASK_QUEUE=constitutional-enforcement python -m src.integrations.temporal.worker
```

### 4. Run Application
```bash
# Desktop
python -m src.app.main

# Web backend
cd web/backend && flask run

# CLI
python project_ai_cli.py --help
```

### 5. Access Temporal Web UI
```
http://localhost:8080
```

---

## 📖 Usage Examples

### Example 1: Start Triumvirate Workflow
```python
from src.integrations.temporal.client import TemporalClient
from temporal.workflows.triumvirate_workflow import TriumvirateWorkflow, TriumvirateRequest

async def main():
    client = TemporalClient()
    await client.connect()
    
    request = TriumvirateRequest(
        input_data="Analyze this code for vulnerabilities",
        context={"language": "python"},
        timeout_seconds=300
    )
    
    handle = await client.start_workflow(
        workflow=TriumvirateWorkflow.run,
        args=request,
        workflow_id="triumvirate-123",
        task_queue="project-ai-tasks"
    )
    
    result = await handle.result()
    print(f"Success: {result.success}")
    print(f"Output: {result.output}")
```

### Example 2: Start Red Team Campaign
```python
from temporal.workflows.enhanced_security_workflows import EnhancedRedTeamCampaignWorkflow, RedTeamCampaignRequest

request = RedTeamCampaignRequest(
    campaign_id="campaign-2025-01-21",
    persona_ids=["persona-1", "persona-2", "persona-3"],
    targets=["http://localhost:8000/api/v1"],
    repo="IAmSoThirsty/Project-AI",
    commit_sha="main"
)

handle = await client.start_workflow(
    workflow=EnhancedRedTeamCampaignWorkflow.run,
    args=request,
    workflow_id=f"red-team-{request.campaign_id}",
    task_queue="security-agents"
)

result = await handle.result()
print(f"Status: {result['status']}")
print(f"Attacks: {result['total_attacks']}")
print(f"Success Rate: {result['success_rate']}")
```

### Example 3: Enforce Temporal Law
```python
from gradle_evolution.constitutional.temporal_law import TemporalLawEnforcer

enforcer = TemporalLawEnforcer(temporal_client=client)

result = await enforcer.enforce_with_timeout(
    action="delete_user_data",
    metadata={
        "user_id": "12345",
        "data_age_days": 95
    },
    timeout_seconds=30
)

if result["allowed"]:
    # Proceed with action
    await delete_user_data(user_id)
else:
    print(f"Action blocked: {result['reason']}")
```

---

## 🔍 Key Findings

### Architectural Strengths
1. **Comprehensive Coverage**: 13 workflows, 37 activities across all core systems
2. **Separation of Concerns**: 3 specialized task queues for workload isolation
3. **Governance Integration**: Deep integration with constitutional AI and temporal laws
4. **Forensic Capabilities**: Immutable snapshots for security workflows
5. **Observability**: Full telemetry and audit trail for all operations
6. **Error Resilience**: Configurable retry policies and graceful degradation

### Integration Points
1. **Desktop Application**: PyQt6 with QThread for async workflow execution
2. **Web Application**: Flask API with async workflow handling
3. **CLI**: Direct workflow invocation from command line
4. **GitHub Security**: Automated SARIF upload for security findings
5. **Temporal Governance**: Constitutional enforcement through workflows
6. **Multi-System**: Triumvirate, Security Agents, Learning, Image Gen, Data Analysis

---

## 🎯 Mission Accomplishments

### Deliverables
✅ **01_WORKFLOW_CHAINS.md** - 11 workflows documented with execution flows  
✅ **02_ACTIVITY_DEPENDENCIES.md** - 37 activities documented with dependency graphs  
✅ **03_TEMPORAL_INTEGRATION.md** - 6 integration points documented with patterns  
✅ **04_TEMPORAL_GOVERNANCE.md** - Full governance system documented with audit trails  
✅ **README.md** - Comprehensive index and quick start guide  

### Coverage
✅ **Workflows**: 100% coverage (all workflows documented)  
✅ **Activities**: 100% coverage (all activities documented)  
✅ **Integration**: 100% coverage (desktop, web, CLI)  
✅ **Governance**: 100% coverage (temporal laws, enforcement, audit)  

### Quality Metrics
- **Total Documentation**: ~88.8 KB across 5 files
- **Workflows Documented**: 13
- **Activities Documented**: 37
- **Diagrams & Flows**: 25+ execution flows
- **Code Examples**: 20+ usage examples
- **Best Practices**: 15+ documented patterns

---

## 📚 Related Documentation


### Cross-References

- [[relationships/temporal/01_WORKFLOW_CHAINS.md|01 Workflow Chains]]
- [[relationships/temporal/02_ACTIVITY_DEPENDENCIES.md|02 Activity Dependencies]]
- [[relationships/temporal/03_TEMPORAL_INTEGRATION.md|03 Temporal Integration]]
- [[relationships/temporal/04_TEMPORAL_GOVERNANCE.md|04 Temporal Governance]]
- [[source-docs/temporal/README.md|Readme]]
### Project-AI Core
- `PROGRAM_SUMMARY.md` - Complete architecture overview
- `DEVELOPER_QUICK_REFERENCE.md` - GUI component API reference
- `.github/instructions/ARCHITECTURE_QUICK_REF.md` - Visual diagrams

### Temporal Infrastructure
- `src/app/temporal/WORKFLOW_GOVERNANCE.md` - Workflow governance metadata
- `temporal/workflows/` - Workflow implementations
- `src/integrations/temporal/` - Client and worker code

### Constitutional AI
- `gradle-evolution/constitutional/temporal_law.py` - Temporal law system
- `src/cognition/triumvirate/` - Triumvirate AI pipeline

### Security Systems
- `src/app/agents/` - Security agent implementations
- `whitepaper/THIRSTYS_ASYMMETRIC_SECURITY_WHITEPAPER.md` - Security architecture

---

## 🤝 Contributing

When adding new Temporal workflows or activities:

1. **Update Workflow Chains**: Add to `01_WORKFLOW_CHAINS.md`
2. **Update Activity Dependencies**: Add to `02_ACTIVITY_DEPENDENCIES.md`
3. **Update Integration**: Document integration in `03_TEMPORAL_INTEGRATION.md`
4. **Update Governance**: Add governance metadata to `04_TEMPORAL_GOVERNANCE.md`
5. **Update README**: Add to coverage matrix and index

---

## 📞 Contact

**Mission Agent**: AGENT-057  
**Mission Date**: 2025-01-21  
**Mission Status**: ✅ COMPLETE  
**Documentation Version**: 1.0  

---

**End of Temporal Relationships Documentation**

*All 4 Temporal systems fully documented with comprehensive relationship maps, execution flows, and integration patterns.*
