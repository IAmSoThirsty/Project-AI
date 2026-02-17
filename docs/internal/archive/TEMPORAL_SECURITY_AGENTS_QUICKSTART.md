# Security Agent Temporal Integration - Quick Start

## Prerequisites

```bash

# Install Temporal SDK

pip install temporalio

# Or add to requirements.txt

echo "temporalio>=1.5.0" >> requirements.txt
pip install -r requirements.txt
```

## Start Temporal Server

### Option 1: Docker Compose (Recommended)

```bash

# Start Temporal with PostgreSQL

docker-compose up -d temporal temporal-postgresql

# Verify it's running

curl http://localhost:7233/health

# Access UI

open http://localhost:8233
```

### Option 2: Temporal CLI

```bash

# Install Temporal CLI

brew install temporal

# Or download from https://github.com/temporalio/cli

# Start dev server

temporal server start-dev
```

## Start Security Worker

```bash

# Start the worker (listens for workflow tasks)

python scripts/run_security_worker.py
```

You should see:

```
🔌 Connecting to Temporal server at localhost:7233
✅ Connected to Temporal server
🛡️ Creating security agent worker on queue: security-agents
✅ Worker created successfully
📋 Registered workflows:
   • RedTeamCampaignWorkflow
   • CodeSecuritySweepWorkflow
   • ConstitutionalMonitoringWorkflow
   • SafetyTestingWorkflow
📋 Registered activities: 10
🚀 Starting worker (task queue: security-agents)
Press Ctrl+C to stop
```

## Run Workflows

### Red Team Campaign

```bash

# High-priority daily campaign

python examples/temporal/red_team_campaign_example.py --type high-priority

# Comprehensive weekly campaign

python examples/temporal/red_team_campaign_example.py --type comprehensive
```

### Code Security Sweep

```bash
python examples/temporal/code_security_sweep_example.py
```

## View Results

### Temporal UI

- Open <http://localhost:8233>
- Navigate to "Workflows"
- Click on your workflow ID to see:
  - Execution timeline
  - Activity results
  - Error logs (if any)
  - Event history

### Command Line

```bash

# List workflows

temporal workflow list --task-queue security-agents

# Describe specific workflow

temporal workflow describe --workflow-id red-team-campaign-high-priority-...

# View workflow history

temporal workflow show --workflow-id red-team-campaign-high-priority-...
```

## Schedule Workflows

Create automated schedules:

```python
from temporalio.client import Client, Schedule, ScheduleActionStartWorkflow, ScheduleSpec

async def setup_schedules():
    client = await Client.connect("localhost:7233")

    # Daily at 2 AM

    await client.create_schedule(
        "red-team-daily",
        Schedule(
            action=ScheduleActionStartWorkflow(
                RedTeamCampaignWorkflow.run,
                request,
                id="red-team-daily",
                task_queue="security-agents",
            ),
            spec=ScheduleSpec(cron_expressions=["0 2 * * *"]),
        ),
    )
```

## Troubleshooting

### Worker won't start

- Check Temporal server is running: `curl <http://localhost:7233/health`>
- Check port 7233 is not blocked
- Verify temporalio is installed: `pip show temporalio`

### Workflows fail

- Check worker logs for errors
- View workflow details in Temporal UI
- Ensure all imports are working: `python -c "from temporal.workflows import *"`

### Can't connect to Temporal

- Ensure Docker containers are running: `docker ps | grep temporal`
- Check logs: `docker logs temporal`
- Try restarting: `docker-compose restart temporal`

## Files Created

- `temporal/workflows/security_agent_workflows.py` - 4 workflow definitions
- `temporal/workflows/security_agent_activities.py` - 9 activity implementations
- `scripts/run_security_worker.py` - Worker process
- `examples/temporal/red_team_campaign_example.py` - Campaign example
- `examples/temporal/code_security_sweep_example.py` - Sweep example
- `docs/SECURITY_AGENTS_TEMPORAL_LLM_GUIDE.md` - Complete guide

## Next Steps

1. Configure LLM endpoints in `.env` (see docs/SECURITY_AGENTS_TEMPORAL_LLM_GUIDE.md)
1. Set up scheduled campaigns
1. Integrate with CI/CD
1. Configure monitoring and alerting

For complete documentation, see `docs/SECURITY_AGENTS_TEMPORAL_LLM_GUIDE.md`.
