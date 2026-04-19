---
type: template
priority: canonical
layer: architecture
status: active
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
---

# {{title}}

Created: {{date}}

## Agent Identity

| Field | Value |
|---|---|
| Agent name |  |
| Agent ID pattern |  |
| Agent type | task / coordinator / monitor / learning |
| Owner/system |  |
| Source path |  |
| Status | draft |

## Role Statement

This agent exists to:

## Capabilities

```yaml
capabilities:
  - domain:verb
```

## Boundaries

```yaml
allowed_operations:
  -
forbidden_operations:
  -
requires_approval:
  -
```

## Input Contract

```yaml
task_type:
required_fields:
  -
optional_fields:
  -
validation_rules:
  -
```

## Output Contract

```yaml
success_shape:
  status: success
  output:
failure_shape:
  status: failed
  error:
partial_result_policy:
```

## Execution Flow

1. Validate task type and input contract.
2. Set status to `busy`.
3. Route governed actions through the kernel/coordinator where required.
4. Execute the bounded operation.
5. Emit result, audit event, and metrics.
6. Reset status to `idle` or `error`.

## Communication

Pattern: request-reply / publish-subscribe / pipeline / scatter-gather

```yaml
receives:
  -
emits:
  -
```

## Lifecycle

```yaml
registry:
heartbeat_interval_seconds:
timeout_seconds:
recovery_strategy:
deregistration_policy:
```

## Governance

```yaml
policy_layer:
risk_level: low
audit_required: true
approval_required:
data_access_scope:
  -
```

## Observability

- task_count
- success_rate
- failure_rate
- latency_ms
- utilization

## Tests

- [ ] `can_execute` only accepts declared capabilities.
- [ ] Invalid input returns a failed result.
- [ ] Successful execution emits the expected result shape.
- [ ] Status resets after success.
- [ ] Failure preserves error metadata.
- [ ] Governed operations route correctly.
- [ ] Agent registers and deregisters cleanly.

## Connects

- [[Agent-Build-Template]]
- [[Workflow-Engine]]
- [[State-Model]]
- [[Sovereign-Orchestration]]
