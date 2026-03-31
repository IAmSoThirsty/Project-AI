<!--                                        [2026-03-04 14:24]  -->
<!--                                       Productivity: Active  -->

# `temporal/` — Temporal Workflow Engine

> **Durable, fault-tolerant workflow execution.** Temporal provides long-running workflow orchestration with automatic retry, timeout handling, and state persistence.

## Overview

Project-AI uses Temporal for workflows that:

- Must survive process restarts
- Require multi-step orchestration with rollback
- Need visibility into execution state
- Have complex retry and timeout policies

## Setup

```bash
# Install Temporal CLI
python scripts/setup_temporal.py

# Or via shell
bash scripts/temporal_quickstart.sh

# Start Temporal server (dev mode)
temporal server start-dev
```

## Integration

Temporal workflows are tested in `tests/temporal/` (5 test files) and integrate with:

- `taar/` — Build automation workflows
- `governance/` — Constitutional verification workflows
- `deploy/` — Deployment orchestration

## Configuration

See `config/` for Temporal-specific settings and `scripts/setup_temporal.py` for environment setup.
