# Agent Build Template

*Source model: `docs/architecture/AGENT_MODEL.md`*
*Template Version: 1.0 | Status: Active*
*Use for: PACE-compatible task, coordinator, monitor, and learning agents*

## Purpose

Use this template when defining a new autonomous agent for Project-AI/PACE.

An agent is not just a script. It is a bounded computational actor with explicit capabilities, lifecycle state, communication behavior, governance constraints, and verifiable success criteria.

## 1. Agent Identity

| Field | Value |
|---|---|
| Agent name | `{{agent_name}}` |
| Agent ID pattern | `{{agent_id_pattern}}` |
| Agent type | `task | coordinator | monitor | learning` |
| Owner/system | `{{owning_system}}` |
| Runtime package | `{{runtime_package}}` |
| Source path | `{{source_path}}` |
| Status | `draft | active | deprecated` |

## 2. Role Statement

Write one sentence:

`{{agent_name}}` exists to `{{specific_operational_purpose}}`.

Keep it narrow. If the sentence needs "and" more than once, split the agent.

## 3. Agent Type

Select one primary type.

| Type | Use When |
|---|---|
| Task Agent | Executes one bounded task with clear success criteria |
| Coordinator Agent | Decomposes work, routes tasks, aggregates results |
| Monitor Agent | Watches state, detects events, escalates responses |
| Learning Agent | Refines strategy from feedback or observed patterns |

Primary type: `{{agent_type}}`

Secondary type, if any: `{{secondary_agent_type}}`

## 4. Capabilities

Capabilities are routing keys. Use `domain:verb` names.

```yaml
capabilities:
  - "{{capability_1}}"
  - "{{capability_2}}"
  - "{{capability_3}}"
```

Examples:

- `data:process`
- `workflow:orchestrate`
- `system:monitor`
- `security:validate`
- `document:curate`

## 5. Boundaries

Define what this agent is allowed and forbidden to do.

```yaml
allowed_operations:
  - "{{allowed_operation_1}}"
  - "{{allowed_operation_2}}"

forbidden_operations:
  - "{{forbidden_operation_1}}"
  - "{{forbidden_operation_2}}"

requires_approval:
  - "{{approval_required_operation}}"
```

## 6. Inputs

```yaml
input_contract:
  task_type: "{{task_type}}"
  required_fields:
    - "{{field_1}}"
    - "{{field_2}}"
  optional_fields:
    - "{{optional_field}}"
  validation_rules:
    - "{{validation_rule}}"
```

## 7. Outputs

```yaml
output_contract:
  success_shape:
    status: "success"
    output: "{{output_description}}"
  failure_shape:
    status: "failed"
    error: "{{error_description}}"
  partial_result_policy: "{{partial_result_policy}}"
```

## 8. Execution Flow

1. Validate task type and input contract.
2. Set status to `busy`.
3. Route governed actions through the kernel/coordinator where required.
4. Execute the bounded operation.
5. Emit result, audit event, and metrics.
6. Reset status to `idle` or `error`.

## 9. Communication

Select the communication pattern.

| Pattern | Use When |
|---|---|
| Request-Reply | Caller needs a direct result |
| Publish-Subscribe | Events should fan out to observers |
| Pipeline | Work must move through ordered stages |
| Scatter-Gather | Work can run in parallel and aggregate |

Pattern: `{{communication_pattern}}`

Topics/messages:

```yaml
messages:
  receives:
    - "{{incoming_message_type}}"
  emits:
    - "{{outgoing_message_type}}"
```

## 10. Lifecycle

```yaml
lifecycle:
  created_by: "{{creator_or_factory}}"
  registration: "{{registry_name}}"
  heartbeat_interval_seconds: {{heartbeat_interval}}
  timeout_seconds: {{timeout_seconds}}
  recovery_strategy: "{{recovery_strategy}}"
  deregistration_policy: "{{deregistration_policy}}"
```

Allowed states:

- `idle`
- `busy`
- `blocked`
- `error`
- `maintenance`

## 11. Governance

```yaml
governance:
  policy_layer: "{{policy_layer}}"
  risk_level: "low | medium | high | critical"
  audit_required: true
  approval_required: "{{approval_rule}}"
  data_access_scope:
    - "{{data_scope}}"
```

Minimum rule: all meaningful mutation must be auditable and must respect `Sovereign_Agent_Standard.md`.

## 12. Observability

```yaml
metrics:
  - task_count
  - success_rate
  - failure_rate
  - latency_ms
  - utilization

logs:
  - task_started
  - task_completed
  - task_failed
  - message_sent
  - message_received
```

## 13. Test Checklist

- [ ] `can_execute` returns true only for declared capabilities.
- [ ] Invalid input returns a failed task result, not an uncaught exception.
- [ ] Successful execution emits a stable result shape.
- [ ] Status returns to `idle` after success.
- [ ] Status becomes `error` or emits failure metadata after failure.
- [ ] Governed operations route through the expected kernel/coordinator path.
- [ ] Message handling preserves correlation IDs.
- [ ] Agent can be registered, queried, and deregistered.

## 14. Python Scaffold

Use `data/cerberus/agent_templates/pace_agent_template.py` as the implementation starting point.

## 15. Implementation Record

| Artifact | Path |
|---|---|
| Agent source | `{{agent_source_path}}` |
| Unit tests | `{{unit_test_path}}` |
| Integration tests | `{{integration_test_path}}` |
| Docs/wiki note | `{{wiki_note_path}}` |
| Config | `{{config_path}}` |

## 16. Done Definition

An agent is ready when it has:

- A narrow purpose.
- Declared capabilities.
- Explicit boundaries.
- Valid input and output contracts.
- Lifecycle and registry behavior.
- Audit and metrics hooks.
- Tests for success, failure, and routing.
- A wiki note linking it to the systems it touches.

