# Agent Systems Dashboard

**Purpose:** Monitor the four specialized AI agents (Oversight, Planner, Validator, Explainability)

**Core Systems:** src/app/agents/ (oversight.py, planner.py, validator.py, explainability.py)

**Last Updated:** `= dateformat(this.file.mtime, "yyyy-MM-dd HH:mm")`

---

## Agent Status Overview

```dataview
TABLE WITHOUT ID
  agent-name as "Agent",
  status as "Status",
  specialization as "Specialization",
  invocation-count as "Invocations",
  success-rate as "Success %"
FROM "docs/agents"
WHERE agent-type = "specialized"
SORT agent-name ASC
```

---

## Agent Capabilities Matrix

```dataview
TABLE WITHOUT ID
  file.link as "Agent",
  primary-function as "Primary Function",
  secondary-functions as "Secondary",
  integration-points as "Integrations",
  complexity as "Complexity"
FROM "docs/agents"
WHERE contains(tags, "agent-system")
SORT complexity DESC
```

---

## Oversight Agent

```dataview
TABLE WITHOUT ID
  validation-type as "Validation Type",
  rules-count as "Rules",
  override-capability as "Override",
  escalation-path as "Escalation",
  audit-logging as "Audit"
FROM "docs/agents/oversight"
WHERE agent = "oversight"
SORT validation-type ASC
```

---

## Planner Agent

```dataview
TABLE WITHOUT ID
  planning-mode as "Mode",
  decomposition-depth as "Max Depth",
  optimization-strategy as "Strategy",
  task-complexity as "Complexity",
  success-rate as "Success %"
FROM "docs/agents/planner"
WHERE agent = "planner"
SORT task-complexity DESC
```

---

## Validator Agent

```dataview
TABLE WITHOUT ID
  validation-category as "Category",
  validation-rules as "Rules",
  failure-handling as "On Failure",
  retry-strategy as "Retry",
  confidence-threshold as "Threshold"
FROM "docs/agents/validator"
WHERE agent = "validator"
SORT validation-category ASC
```

---

## Explainability Agent

```dataview
TABLE WITHOUT ID
  explanation-type as "Type",
  detail-level as "Detail Level",
  target-audience as "Audience",
  format as "Format",
  examples-count as "Examples"
FROM "docs/agents/explainability"
WHERE agent = "explainability"
SORT detail-level ASC
```

---

## Agent Interaction Flow

```dataview
TABLE WITHOUT ID
  interaction-id as "ID",
  agent-chain as "Agent Chain",
  trigger as "Trigger",
  data-flow as "Data Flow",
  coordination-method as "Coordination"
FROM "docs/agents/interactions"
WHERE interaction-type = "multi-agent"
SORT interaction-id ASC
```

---

## Recent Agent Activity

```dataview
TABLE WITHOUT ID
  timestamp as "Timestamp",
  agent as "Agent",
  action-type as "Action",
  input-summary as "Input",
  output-summary as "Output",
  duration as "Duration (ms)"
FROM "docs/agents/activity"
WHERE contains(tags, "agent-activity")
SORT timestamp DESC
LIMIT 25
```

---

## Agent Performance Metrics

```dataview
TABLE WITHOUT ID
  agent as "Agent",
  avg-response-time as "Avg Time (ms)",
  max-response-time as "Max Time (ms)",
  error-rate as "Error %",
  throughput as "Throughput/min"
FROM "docs/agents/performance"
WHERE metric-type = "agent-performance"
SORT avg-response-time ASC
```

---

## Agent Decision History

```dataview
TABLE WITHOUT ID
  decision-id as "ID",
  agent as "Agent",
  decision-type as "Type",
  input as "Input",
  output as "Output",
  confidence as "Confidence",
  timestamp as "Timestamp"
FROM "docs/agents/decisions"
WHERE contains(tags, "agent-decision")
SORT timestamp DESC
LIMIT 20
```

---

## Error Handling Strategies

```dataview
TABLE WITHOUT ID
  agent as "Agent",
  error-type as "Error Type",
  handling-strategy as "Strategy",
  fallback-behavior as "Fallback",
  recovery-steps as "Recovery"
FROM "docs/agents/error-handling"
WHERE contains(tags, "error-strategy")
SORT agent ASC, error-type ASC
```

---

## Agent Integration Points

```dataview
TABLE WITHOUT ID
  agent as "Agent",
  integrates-with as "Integrates With",
  communication-method as "Method",
  data-contract as "Data Contract",
  coupling-level as "Coupling"
FROM "docs/agents/integration"
WHERE integration-type = "agent-system"
SORT coupling-level DESC
```

---

## Agent Configuration

```dataview
TABLE WITHOUT ID
  agent as "Agent",
  config-file as "Config File",
  configurable-params as "Parameters",
  default-mode as "Default Mode",
  override-capability as "Override"
FROM "docs/agents/configuration"
WHERE contains(tags, "agent-config")
SORT agent ASC
```

---

## Agent vs Plugin Comparison

```dataview
TABLE WITHOUT ID
  component-name as "Component",
  component-type as "Type",
  purpose as "Purpose",
  extensibility as "Extensible",
  enable-disable as "Enable/Disable"
FROM "docs/architecture"
WHERE component-type = "agent" OR component-type = "plugin"
SORT component-type ASC, component-name ASC
```

---

## Agent Test Coverage

```dataview
TABLE WITHOUT ID
  agent as "Agent",
  test-count as "Tests",
  coverage as "Coverage %",
  integration-tests as "Integration",
  last-test-run as "Last Run"
FROM "docs/testing/agents"
WHERE test-category = "agent"
SORT coverage ASC
```

---

## Agent Enhancement Roadmap

```dataview
TABLE WITHOUT ID
  enhancement-id as "ID",
  agent as "Agent",
  enhancement-type as "Type",
  priority as "Priority",
  status as "Status",
  target-release as "Target"
FROM "docs/roadmap"
WHERE roadmap-category = "agents"
SORT priority ASC, target-release ASC
```

---

## Agent Dependencies

```dataview
TABLE WITHOUT ID
  agent as "Agent",
  depends-on as "Dependencies",
  core-systems as "Core Systems",
  external-services as "External",
  coupling-score as "Coupling"
FROM "docs/agents/dependencies"
WHERE dependency-type = "agent"
SORT coupling-score DESC
```

---

## Open Agent Issues

```dataview
TABLE WITHOUT ID
  issue-id as "ID",
  agent as "Agent",
  issue-type as "Type",
  severity as "Severity",
  status as "Status",
  assigned-to as "Assigned"
FROM "docs/issues"
WHERE issue-category = "agent" AND status != "closed"
SORT severity DESC, agent ASC
```

---

## Agent Tasks

```dataview
TASK
FROM "docs/tasks"
WHERE contains(tags, "agent") OR contains(tags, "agent-system") AND !completed
SORT priority DESC, due ASC
```

---

## Related Documentation

```dataview
TABLE WITHOUT ID
  file.link as "Document",
  agent-focus as "Agent Focus",
  doc-type as "Type",
  dateformat(file.mtime, "yyyy-MM-dd") as "Updated"
FROM "docs/agents" OR "src/app/agents" OR "docs"
WHERE contains(tags, "agent") OR contains(file.path, "agents")
SORT file.mtime DESC
LIMIT 15
```

---

## Quick Actions

- 👁️ [[Oversight Agent|View Oversight System]]
- 📋 [[Planner Agent|View Planning System]]
- ✅ [[Validator Agent|View Validation System]]
- 💡 [[Explainability Agent|View Explanation System]]
- 🔗 [[Agent Integration|View Integration Flow]]
- 📊 [[Agent Performance|View Metrics]]

---

**Query Performance:** Target <1s | **Data Sources:** src/app/agents, docs/agents | **Refresh:** Real-time
