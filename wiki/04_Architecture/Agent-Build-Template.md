---
type: template
priority: canonical
layer: architecture
status: active
aliases:
  - agent build template
  - agent-build-template
  - Agent Build Template
domain:
  - architecture
  - systems
tags:
  - project-ai
  - type/template
  - priority/canonical
  - layer/architecture
  - domain/architecture
  - domain/systems
  - bridge/architecture-systems
  - system/pace
  - concept/agent-model
---

# Agent Build Template

This is the practical template for building Project-AI/PACE agents.

## Source
- Repo template: `docs/templates/AGENT_BUILD_TEMPLATE.md`
- Python scaffold: `data/cerberus/agent_templates/pace_agent_template.py`
- Source model: `docs/architecture/AGENT_MODEL.md`

## Use When
- Creating a new task agent.
- Creating a coordinator agent.
- Creating a monitor agent.
- Creating a learning agent.
- Reviewing whether an existing agent has enough boundaries, contracts, and audit behavior.

## Required Shape
- Narrow purpose.
- Declared capabilities.
- Explicit allowed and forbidden operations.
- Stable input and output contracts.
- Lifecycle status.
- Registry/coordinator compatibility.
- Audit and metrics hooks.
- Tests for routing, success, failure, and cleanup.

## Connects
- [[Agent Instance Template]]
- [[Workflow-Engine]]
- [[State-Model]]
- [[Sovereign-Orchestration]]
- [[Repository-Maturity]]
- [[Constitutional-Audit]]

