---
title: Temporal.io Integration Guide - Full Integration Status
id: temporal-io-integration
type: guide
version: 1.0
created: 2026-01-28
created_date: 2026-01-28
last_verified: 2026-04-20
updated_date: 2026-01-28
status: active
author: Temporal Integration Team
contributors: ["Security Team", "Learning Team", "Crisis Response Team"]
# Architecture-Specific Metadata
architecture_layer: infrastructure
design_pattern: ["durable-execution", "workflow-orchestration", "distributed-workflows"]
implements: ["triumvirate-workflows", "security-agent-workflows", "learning-workflows", "crisis-workflows"]
uses: ["temporalio-sdk", "protobuf"]
quality_attributes: ["fault-tolerance", "reliability", "observability", "scalability", "durability"]
adr_status: accepted
# Component Classification
area: ["architecture", "architecture/infrastructure", "workflow", "integration"]
tags: ["temporal", "workflow-integration", "durable-execution", "triumvirate", "security-workflows", "learning-workflows", "crisis-response"]
component: ["triumvirate-workflows", "security-agent-workflows", "red-team-workflows", "learning-workflows", "liara-crisis-workflows"]
# Relationships
related_docs: ["temporal-integration-architecture", "workflow-engine-spec", "architecture-overview"]
related_systems: ["temporal-integration", "workflow-engine", "triumvirate"]
depends_on: ["workflow-engine-spec"]
supersedes: []
superseded_by: []
# Audience & Priority
audience: ["architects", "workflow-developers", "operations-teams"]
stakeholders: ["platform-team", "devops-team", "developers", "architecture-team"]
priority: P0
difficulty: intermediate
estimated_reading_time: 12 minutes
review_cycle: quarterly
# Security & Compliance
classification: internal
sensitivity: low
compliance: []
# Discovery
keywords: ["Temporal.io", "workflow integration", "Triumvirate workflows", "security workflows", "crisis response"]
search_terms: ["temporalio SDK", "durable execution", "Liara", "red team workflows"]
aliases: ["Temporal Integration", "Workflow Platform"]
# Quality Metadata
review_status: approved
accuracy_rating: high
test_coverage: 83%
---


# Temporal.io Integration Guide

**Last Updated:** January 28, 2026  
**Status:** ✅ **FULLY INTEGRATED AND ACTIVE**

---

## 🎯 Executive Summary

**YES, Temporal.io IS integrated with Project-AI!**

Project-AI uses Temporal.io for durable, fault-tolerant workflow orchestration across multiple critical systems including crisis response, security scanning, learning workflows, and agent coordination.

---

## 🔌 Integration Architecture

### What is Temporal.io?

Temporal.io is a durable execution platform that ensures:
- **Fault Tolerance**: Workflows survive crashes and restarts
- **Reliability**: Automatic retries with exponential backoff
- **Observability**: Full execution history and state tracking
- **Scalability**: Distributed execution across workers
- **Durability**: State persists even if servers go down

### Integration Points in Project-AI

| Component | Purpose | Location | Status |
|-----------|---------|----------|--------|
| **Triumvirate Workflows** | Ethical review orchestration | `temporal/workflows/triumvirate_workflow.py` | ✅ Active |
| **Security Agent Workflows** | Automated security scanning | `temporal/workflows/security_agent_workflows.py` | ✅ Active |
| **Red Team Workflows** | Adversarial testing campaigns | `scripts/redteam_workflow.py` | ✅ Active |
| **Learning Workflows** | Autonomous learning tasks | `examples/temporal/learning_workflow_example.py` | ✅ Active |
| **Crisis Response (Liara)** | Emergency orchestration | `cognition/liara/` | ✅ Active |
| **Code Security Sweeps** | Continuous code analysis | `temporal/workflows/enhanced_security_workflows.py` | ✅ Active |
| **Batch Workflows** | Bulk processing tasks | `examples/temporal/batch_workflows_example.py` | ✅ Active |

---

## 📦 Dependencies

**Current Installation:**

```toml
# From pyproject.toml and requirements.txt
temporalio>=1.5.0              # Temporal.io SDK for Python
protobuf>=4.25.8                # Protocol Buffers for Temporal
```

**Verification:**

```bash
# Check if Temporal is installed
pip show temporalio

# Expected output:
# Name: temporalio
# Version: 1.5.0+
# Summary: Temporal.io Python SDK
```

---

## 🏗️ Architecture Overview

### Directory Structure

```
Project-AI/
├── temporal/                          # Temporal workflow definitions
│   ├── __init__.py
│   └── workflows/
│       ├── triumvirate_workflow.py    # Ethical review workflows
│       ├── security_agent_workflows.py # Security orchestration
│       ├── enhanced_security_workflows.py
│       ├── atomic_security_activities.py
│       └── activities.py
│
├── src/app/temporal/                  # Core Temporal integration
│   ├── config.py                      # Configuration settings
│   ├── client.py                      # Temporal client wrapper
│   ├── worker.py                      # Worker management
│   ├── activities.py                  # Activity definitions
│   └── workflows.py                   # Workflow definitions
│
├── src/integrations/temporal/         # Integration layer
│   ├── client.py                      # Extended client
│   ├── worker.py                      # Extended worker
│   ├── activities/
│   │   └── core_tasks.py             # Core activities
│   └── workflows/
│       └── example_workflow.py       # Example workflows
│
├── cognition/liara/                   # Liara orchestration layer
│   ├── agency.py                      # Agent coordination
│   ├── worker.py                      # Liara-specific worker
│   └── cli.py                         # CLI interface
│
├── scripts/                           # Operational scripts
│   ├── setup_temporal.py              # Initial setup
│   ├── run_security_worker.py         # Security worker runner
│   ├── redteam_workflow.py            # Red team coordination
│   └── run_novel_scenarios.py         # Novel scenario testing
│
├── examples/temporal/                 # Usage examples
│   ├── learning_workflow_example.py   # Learning workflows
│   ├── liara_crisis_example.py        # Crisis response
│   ├── image_generation_example.py    # Image gen workflows
│   ├── red_team_campaign_example.py   # Red team campaigns
│   ├── code_security_sweep_example.py # Security sweeps
│   └── batch_workflows_example.py     # Batch processing
│
└── tests/temporal/                    # Test suite
    ├── test_client.py                 # Client tests
    ├── test_config.py                 # Config tests
    ├── test_workflows.py              # Workflow tests
    └── test_liara_workflows.py        # Liara tests
```

---

## 🚀 Quick Start

### 1. Install Temporal Server

**Option A: Docker (Recommended for Development)**

```bash
# Clone Temporal Docker Compose
git clone https://github.com/temporalio/docker-compose.git temporal-server
cd temporal-server

# Start Temporal server
docker-compose up -d

# Verify it's running
curl http://localhost:8233/health
```

**Option B: Temporal Cloud (Production)**

1. Sign up at: https://temporal.io/cloud
2. Get your namespace and certificates
3. Configure in `.env`:

```bash
TEMPORAL_CLOUD_NAMESPACE=my-namespace.a2b3c
TEMPORAL_CLOUD_CERT_PATH=/path/to/client.pem
TEMPORAL_CLOUD_KEY_PATH=/path/to/client-key.pem
TEMPORAL_CLOUD_API_KEY=your-api-key
```

### 2. Configure Project-AI

**Create/update `.env` file:**

```bash
# Temporal Server Configuration (Local)
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default
TEMPORAL_TASK_QUEUE=project-ai-tasks

# Or Temporal Cloud (Production)
TEMPORAL_CLOUD_NAMESPACE=my-namespace.a2b3c
TEMPORAL_CLOUD_CERT_PATH=/path/to/cert.pem
TEMPORAL_CLOUD_KEY_PATH=/path/to/key.pem
```

### 3. Run Setup Script

```bash
# Initialize Temporal integration
python scripts/setup_temporal.py

# Expected output:
# ✅ Temporal server connection verified
# ✅ Namespace 'default' accessible
# ✅ Task queue 'project-ai-tasks' created
# ✅ Setup complete!
```

### 4. Start Workers

**Terminal 1: General Purpose Worker**

```bash
# Start main worker
python -m src.app.temporal.worker

# Output:
# 🚀 Starting Temporal worker...
# 📋 Task queue: project-ai-tasks
# ✅ Worker started successfully
```

**Terminal 2: Security Worker**

```bash
# Start security-specific worker
python scripts/run_security_worker.py

# Output:
# 🔒 Starting security worker...
# 📋 Task queue: security-tasks
# ✅ Security worker started
```

**Terminal 3: Liara Orchestration Worker**

```bash
# Start Liara (crisis response) worker
python -m cognition.liara.worker

# Output:
# ⚡ Starting Liara orchestration worker...
# 📋 Task queue: liara-tasks
# ✅ Liara worker started
```

### 5. Verify Integration

```bash
# Test workflow execution
python examples/temporal/learning_workflow_example.py

# Expected output:
# 🎯 Starting learning workflow...
# ✅ Workflow started: workflow_id_123
# ⏳ Waiting for completion...
# ✅ Workflow completed successfully!
# Result: Learning path generated for Python programming
```

---

## 📚 Core Features

### 1. Triumvirate Workflow (Ethical Review)

**Purpose:** Orchestrate ethical review process through Galahad, Cerberus, and Codex Deus Maximus.

**Code Example:**

```python
from temporalio.client import Client
from temporal.workflows import TriumvirateWorkflow, TriumvirateRequest

async def run_ethical_review():
    """Run ethical review through Triumvirate workflow."""
    
    client = await Client.connect("localhost:7233")
    
    request = TriumvirateRequest(
        action="deploy_new_ai_feature",
        description="Add autonomous decision-making capability",
        requester="alice@example.com",
        priority="high"
    )
    
    result = await client.execute_workflow(
        TriumvirateWorkflow.run,
        request,
        id=f"ethical-review-{request.action}",
        task_queue="project-ai-tasks",
    )
    
    print(f"Review result: {result.decision}")
    print(f"Galahad (Ethics): {result.galahad_vote}")
    print(f"Cerberus (Security): {result.cerberus_vote}")
    print(f"Codex (Knowledge): {result.codex_vote}")

# Run it
import asyncio
asyncio.run(run_ethical_review())
```

**Features:**
- ✅ Three-guardian approval process
- ✅ Audit trail for all decisions
- ✅ Automatic retries on transient failures
- ✅ Timeout handling (1 hour max per review)

### 2. Security Agent Workflows

**Purpose:** Automated security scanning with Bandit, CodeQL, and vulnerability checks.

**Code Example:**

```python
from temporalio.client import Client
from temporal.workflows.security_agent_workflows import SecurityScanWorkflow

async def run_security_scan(repo_path: str):
    """Run comprehensive security scan."""
    
    client = await Client.connect("localhost:7233")
    
    result = await client.execute_workflow(
        SecurityScanWorkflow.run,
        repo_path,
        id=f"security-scan-{datetime.now().isoformat()}",
        task_queue="security-tasks",
    )
    
    print(f"Scan completed: {result.status}")
    print(f"Vulnerabilities found: {result.vulnerability_count}")
    print(f"Bandit issues: {result.bandit_issues}")
    print(f"CodeQL alerts: {result.codeql_alerts}")

# Run it
asyncio.run(run_security_scan("/home/runner/work/Project-AI/Project-AI"))
```

**Features:**
- ✅ Parallel execution of security tools
- ✅ Automatic issue creation on findings
- ✅ Retry logic for transient failures
- ✅ Results aggregation and reporting

### 3. Red Team Workflow

**Purpose:** Coordinate adversarial testing campaigns with JailbreakBench and Garak.

**Code Example:**

```python
from scripts.redteam_workflow import RedTeamCampaignWorkflow
from temporalio.client import Client

async def run_red_team_campaign():
    """Launch red team testing campaign."""
    
    client = await Client.connect("localhost:7233")
    
    config = {
        "target_model": "gpt-3.5-turbo",
        "scenario_count": 100,
        "timeout_per_scenario": 30,
        "frameworks": ["jailbreakbench", "garak"]
    }
    
    result = await client.execute_workflow(
        RedTeamCampaignWorkflow.run,
        config,
        id=f"redteam-{datetime.now().strftime('%Y%m%d')}",
        task_queue="security-tasks",
    )
    
    print(f"Campaign completed")
    print(f"Scenarios tested: {result.total_scenarios}")
    print(f"Attack success rate: {result.asr:.2%}")
    print(f"Defense effectiveness: {result.defense_rate:.2%}")

# Run it
asyncio.run(run_red_team_campaign())
```

**Features:**
- ✅ Distributed scenario execution
- ✅ Real-time progress tracking
- ✅ Automatic report generation
- ✅ Metric aggregation (ASR, FPR, etc.)

### 4. Learning Workflow

**Purpose:** Orchestrate autonomous learning with approval workflow.

**Code Example:**

```python
from examples.temporal.learning_workflow_example import LearningWorkflow
from temporalio.client import Client

async def create_learning_path():
    """Generate and approve learning path."""
    
    client = await Client.connect("localhost:7233")
    
    result = await client.execute_workflow(
        LearningWorkflow.run,
        interest="Quantum Computing",
        skill_level="intermediate",
        id=f"learning-quantum-{datetime.now().isoformat()}",
        task_queue="project-ai-tasks",
    )
    
    print(f"Learning path created: {result.path_id}")
    print(f"Status: {result.status}")
    print(f"Content: {result.content[:200]}...")

# Run it
asyncio.run(create_learning_path())
```

**Features:**
- ✅ OpenAI integration for path generation
- ✅ Human-in-the-loop approval
- ✅ Black Vault integration for denied content
- ✅ Progress tracking

### 5. Liara Crisis Response

**Purpose:** Coordinate emergency response across multiple agents.

**Code Example:**

```python
from cognition.liara.agency import LiaraAgency
from temporalio.client import Client

async def handle_crisis():
    """Respond to security crisis."""
    
    client = await Client.connect("localhost:7233")
    
    crisis = {
        "type": "security_breach",
        "severity": "critical",
        "description": "Unauthorized API access detected",
        "affected_systems": ["api_server", "database"]
    }
    
    result = await client.execute_workflow(
        LiaraAgency.crisis_response,
        crisis,
        id=f"crisis-{datetime.now().isoformat()}",
        task_queue="liara-tasks",
    )
    
    print(f"Crisis handled: {result.resolution}")
    print(f"Actions taken: {result.actions}")
    print(f"Time to resolution: {result.duration_seconds}s")

# Run it
asyncio.run(handle_crisis())
```

**Features:**
- ✅ Multi-agent coordination
- ✅ Priority-based execution
- ✅ Automatic escalation
- ✅ Audit trail generation

---

## 🔧 Configuration

### Temporal Config (`src/app/temporal/config.py`)

```python
from pydantic_settings import BaseSettings

class TemporalConfig(BaseSettings):
    """Temporal.io configuration."""
    
    # Server
    host: str = "localhost:7233"
    namespace: str = "default"
    task_queue: str = "project-ai-tasks"
    
    # Timeouts (seconds)
    workflow_execution_timeout: int = 3600  # 1 hour
    workflow_run_timeout: int = 1800        # 30 minutes
    activity_start_to_close_timeout: int = 300  # 5 minutes
    
    # Retry Policy
    max_retry_attempts: int = 3
    initial_retry_interval: int = 1
    max_retry_interval: int = 100
    backoff_coefficient: float = 2.0
    
    # Worker
    max_concurrent_activities: int = 50
    max_concurrent_workflows: int = 50
```

**Load configuration:**

```python
from src.app.temporal.config import TemporalConfig

config = TemporalConfig()
print(f"Connecting to: {config.host}")
print(f"Task queue: {config.task_queue}")
```

---

## 🧪 Testing

### Unit Tests

```bash
# Run Temporal-specific tests
pytest tests/temporal/ -v

# Expected output:
# tests/temporal/test_client.py::test_connect ... PASSED
# tests/temporal/test_config.py::test_config_load ... PASSED
# tests/temporal/test_workflows.py::test_triumvirate ... PASSED
# tests/temporal/test_liara_workflows.py::test_crisis ... PASSED
```

### Integration Tests

```bash
# Run full integration test (requires running Temporal server)
pytest tests/test_temporal_integration.py -v

# This will:
# 1. Connect to Temporal server
# 2. Start a test workflow
# 3. Execute activities
# 4. Verify results
```

### Manual Testing

```bash
# Test workflow execution
python examples/temporal/learning_workflow_example.py

# Test security workflow
python examples/temporal/code_security_sweep_example.py

# Test crisis response
python examples/temporal/liara_crisis_example.py
```

---

## 📊 Monitoring and Observability

### Temporal Web UI

Access the Temporal Web UI for monitoring:

```bash
# Open in browser
http://localhost:8233

# Features:
# - Workflow execution history
# - Activity status and logs
# - Retry attempts and failures
# - Performance metrics
# - Search and filtering
```

### Custom Logging

```python
# Workflows automatically log to Temporal
from temporalio import workflow

@workflow.defn
class MyWorkflow:
    @workflow.run
    async def run(self, data: str):
        workflow.logger.info(f"Processing: {data}")
        
        # Activity execution logged automatically
        result = await workflow.execute_activity(
            my_activity,
            data,
            start_to_close_timeout=timedelta(seconds=300)
        )
        
        workflow.logger.info(f"Result: {result}")
        return result
```

### Metrics

```python
# Prometheus metrics exposed by workers
# Default port: 9090

# Metrics available:
# - temporal_worker_task_slots_available
# - temporal_workflow_execution_latency
# - temporal_activity_execution_latency
# - temporal_workflow_task_execution_failed_total
```

---

## 🔒 Security Considerations

### TLS Configuration (Production)

```python
from temporalio.client import Client, TLSConfig

# For Temporal Cloud
tls_config = TLSConfig(
    client_cert=open("client.pem", "rb").read(),
    client_private_key=open("client-key.pem", "rb").read(),
)

client = await Client.connect(
    "my-namespace.a2b3c.tmprl.cloud:7233",
    namespace="my-namespace.a2b3c",
    tls=tls_config,
)
```

### Activity Input Encryption

```python
from temporalio import activity
from cryptography.fernet import Fernet

@activity.defn
async def process_sensitive_data(encrypted_data: bytes):
    """Process encrypted sensitive data."""
    
    fernet = Fernet(os.getenv("FERNET_KEY"))
    decrypted = fernet.decrypt(encrypted_data)
    
    # Process data
    result = do_processing(decrypted)
    
    # Return encrypted result
    return fernet.encrypt(result)
```

### Secrets Management

```bash
# Store in environment variables
export TEMPORAL_API_KEY=your-api-key
export TEMPORAL_CLOUD_CERT_PATH=/secure/path/to/cert.pem

# Or use secret management tools
# - AWS Secrets Manager
# - HashiCorp Vault
# - Azure Key Vault
```

---

## 🐛 Troubleshooting

### Issue 1: "Cannot connect to Temporal server"

**Symptoms:**
```
temporalio.exceptions.WorkflowNotFoundError: Cannot connect to localhost:7233
```

**Solution:**
```bash
# Check if Temporal server is running
curl http://localhost:8233/health

# If not running, start it
cd temporal-server && docker-compose up -d

# Verify connection
python -c "
from temporalio.client import Client
import asyncio
async def test():
    client = await Client.connect('localhost:7233')
    print('✅ Connected!')
asyncio.run(test())
"
```

### Issue 2: "Worker not processing tasks"

**Symptoms:**
- Workflows stuck in "Running" state
- No activity execution

**Solution:**
```bash
# Check if workers are running
ps aux | grep temporal

# Restart workers
pkill -f temporal.worker
python -m src.app.temporal.worker &
python scripts/run_security_worker.py &

# Verify task queue
# Check Temporal Web UI: http://localhost:8233
```

### Issue 3: "Workflow timeout"

**Symptoms:**
```
temporalio.exceptions.WorkflowTimedOutError
```

**Solution:**
```python
# Increase timeout in workflow execution
result = await client.execute_workflow(
    MyWorkflow.run,
    data,
    id="my-workflow",
    task_queue="project-ai-tasks",
    execution_timeout=timedelta(hours=2),  # Increase from 1 hour
    run_timeout=timedelta(hours=1),        # Increase from 30 min
)
```

---

## 💰 Cost Considerations

### Temporal Cloud Pricing

| Tier | Price | Actions/Month | Storage |
|------|-------|---------------|---------|
| Free | $0 | 1M actions | 10 GB |
| Starter | $200/mo | 10M actions | 100 GB |
| Standard | Custom | Unlimited | Custom |

**Cost Optimization Tips:**

1. **Batch operations**: Group small tasks into larger workflows
2. **Use local timers**: Avoid activity polling
3. **Efficient activities**: Keep activities short and focused
4. **Archive old workflows**: Delete completed workflow history
5. **Self-hosted**: Run Temporal server locally (free)

### Self-Hosted Costs

**Infrastructure requirements:**

- **Development**: 4 GB RAM, 2 CPU cores (Docker)
- **Production**: 16 GB RAM, 8 CPU cores, PostgreSQL/Cassandra
- **Cloud**: ~$100-300/month (AWS EC2, RDS)

---

## 📖 References

### Official Documentation

- **Temporal.io Docs**: https://docs.temporal.io/
- **Python SDK**: https://docs.temporal.io/dev-guide/python
- **Tutorials**: https://learn.temporal.io/

### Project-AI Documentation

- **Temporal Integration Summary**: `TEMPORAL_INTEGRATION_SUMMARY.md`
- **Security Agents Quickstart**: `TEMPORAL_SECURITY_AGENTS_QUICKSTART.md`
- **Triumvirate Integration**: `TRIUMVIRATE_INTEGRATION.md`
- **Workflow Engine**: `WORKFLOW_ENGINE.md`

### Code Examples

- `examples/temporal/` - 6 example workflows
- `tests/temporal/` - Test suite
- `scripts/setup_temporal.py` - Setup guide

---

## 🎯 Best Practices

### 1. Workflow Design

✅ **DO:**
- Keep workflows deterministic
- Use activities for side effects
- Handle errors gracefully
- Add timeouts to all operations
- Use signals for external updates

❌ **DON'T:**
- Make API calls directly in workflows
- Use random numbers without workflow.random()
- Store large data in workflow state
- Create infinite loops without sleep
- Skip error handling

### 2. Activity Design

✅ **DO:**
- Keep activities idempotent
- Add retries for transient failures
- Log progress for long-running tasks
- Return meaningful results
- Handle all exceptions

❌ **DON'T:**
- Run activities for hours without checkpoints
- Store state in activity memory
- Assume activities run only once
- Skip input validation
- Ignore timeouts

### 3. Testing

✅ **DO:**
- Use Temporal's testing framework
- Mock external dependencies
- Test failure scenarios
- Verify retry logic
- Check timeout handling

❌ **DON'T:**
- Test only happy paths
- Skip integration tests
- Forget to test cancellation
- Ignore edge cases
- Deploy without testing

---

## 🚀 Next Steps

1. **Explore Examples**: Run all 6 example workflows in `examples/temporal/`
2. **Read Documentation**: Review `TEMPORAL_INTEGRATION_SUMMARY.md`
3. **Write Custom Workflows**: Create workflows for your use cases
4. **Monitor Production**: Set up alerts and dashboards
5. **Scale Workers**: Add more workers as load increases

---

**Last reviewed:** January 28, 2026  
**Next review:** April 28, 2026  
**Maintainer:** @IAmSoThirsty  
**Integration Status:** ✅ Fully Operational
