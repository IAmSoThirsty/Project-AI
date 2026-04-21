# Infrastructure Dashboard

**Purpose:** Monitor Docker deployment, CI/CD pipelines, dependency management, and deployment health

**Core Systems:** Docker, GitHub Actions, npm/pip dependencies, web version architecture

**Last Updated:** `= dateformat(this.file.mtime, "yyyy-MM-dd HH:mm")`

---

## Infrastructure Status

```dataview
TABLE WITHOUT ID
  component-name as "Component",
  status as "Status",
  version as "Version",
  health as "Health",
  last-check as "Last Check"
FROM "docs/infrastructure"
WHERE component-type = "infrastructure"
SORT health ASC, component-name ASC
```

---

## Docker Deployment

```dataview
TABLE WITHOUT ID
  container-name as "Container",
  image as "Image",
  status as "Status",
  ports as "Ports",
  volumes as "Volumes",
  health-check as "Health"
FROM "docs/infrastructure/docker"
WHERE deployment-type = "docker"
SORT container-name ASC
```

---

## CI/CD Pipeline Status

```dataview
TABLE WITHOUT ID
  workflow-name as "Workflow",
  trigger as "Trigger",
  last-run as "Last Run",
  status as "Status",
  duration as "Duration",
  success-rate as "Success %"
FROM "docs/infrastructure/cicd"
WHERE pipeline-type = "github-actions"
SORT last-run DESC
```

---

## GitHub Actions Workflows

```dataview
TABLE WITHOUT ID
  file.link as "Workflow",
  workflow-type as "Type",
  schedule as "Schedule",
  active as "Active",
  description as "Description"
FROM ".github/workflows"
WHERE contains(file.ext, "yml") OR contains(file.ext, "yaml")
SORT workflow-type ASC, file.name ASC
```

---

## Dependency Status

```dataview
TABLE WITHOUT ID
  dependency-name as "Dependency",
  current-version as "Current",
  latest-version as "Latest",
  update-type as "Update",
  security-issues as "Security",
  auto-update as "Auto"
FROM "docs/infrastructure/dependencies"
WHERE dependency-category = "production"
SORT length(security-issues) DESC, update-type ASC
```

---

## Python Dependencies

```dataview
TABLE WITHOUT ID
  package as "Package",
  version as "Version",
  purpose as "Purpose",
  security-rating as "Security",
  update-available as "Update"
FROM "docs/infrastructure/python-deps"
WHERE ecosystem = "python"
SORT package ASC
```

---

## Node.js Dependencies

```dataview
TABLE WITHOUT ID
  package as "Package",
  version as "Version",
  dev-dependency as "Dev",
  security-rating as "Security",
  update-available as "Update"
FROM "docs/infrastructure/node-deps"
WHERE ecosystem = "nodejs"
SORT dev-dependency ASC, package ASC
```

---

## Deployment Environments

```dataview
TABLE WITHOUT ID
  environment as "Environment",
  deployment-type as "Type",
  url as "URL",
  status as "Status",
  last-deployed as "Last Deploy",
  version as "Version"
FROM "docs/infrastructure/environments"
WHERE environment-category = "deployment"
SORT environment ASC
```

---

## Build Status

```dataview
TABLE WITHOUT ID
  build-id as "Build",
  environment as "Environment",
  commit-sha as "Commit",
  status as "Status",
  duration as "Duration",
  timestamp as "Timestamp"
FROM "docs/infrastructure/builds"
WHERE build-type = "automated"
SORT timestamp DESC
LIMIT 20
```

---

## Automated Workflows

```dataview
TABLE WITHOUT ID
  workflow-name as "Workflow",
  trigger-type as "Trigger",
  last-run as "Last Run",
  next-run as "Next Run",
  success-count as "Successes",
  failure-count as "Failures"
FROM "docs/infrastructure/automation"
WHERE automation-type = "workflow"
SORT next-run ASC
```

---

## Security Automation

```dataview
TABLE WITHOUT ID
  scanner-name as "Scanner",
  scan-type as "Type",
  schedule as "Schedule",
  last-scan as "Last Scan",
  issues-found as "Issues",
  status as "Status"
FROM "docs/infrastructure/security-scans"
WHERE scanner-category = "security"
SORT last-scan DESC
```

---

## Dependabot Configuration

```dataview
TABLE WITHOUT ID
  ecosystem as "Ecosystem",
  update-frequency as "Frequency",
  open-pr-limit as "PR Limit",
  auto-merge as "Auto-merge",
  reviewers as "Reviewers"
FROM "docs/infrastructure/dependabot"
WHERE automation-type = "dependabot"
SORT ecosystem ASC
```

---

## Container Images

```dataview
TABLE WITHOUT ID
  image-name as "Image",
  tag as "Tag",
  size as "Size (MB)",
  last-built as "Built",
  registry as "Registry",
  scan-status as "Scanned"
FROM "docs/infrastructure/images"
WHERE image-type = "docker"
SORT last-built DESC
```

---

## Health Check Endpoints

```dataview
TABLE WITHOUT ID
  endpoint as "Endpoint",
  service as "Service",
  interval as "Interval",
  timeout as "Timeout",
  last-check as "Last Check",
  status as "Status"
FROM "docs/infrastructure/health-checks"
WHERE check-type = "automated"
SORT status ASC, service ASC
```

---

## Environment Variables

```dataview
TABLE WITHOUT ID
  var-name as "Variable",
  required-by as "Required By",
  configured as "Configured",
  sensitive as "Sensitive",
  documentation as "Docs"
FROM "docs/infrastructure/env-vars"
WHERE var-category = "environment"
SORT required-by ASC, var-name ASC
```

---

## Web Version Architecture

```dataview
TABLE WITHOUT ID
  component as "Component",
  layer as "Layer",
  technology as "Technology",
  port as "Port",
  status as "Status"
FROM "docs/infrastructure/web-version"
WHERE architecture-type = "web"
SORT layer ASC, component ASC
```

---

## Deployment Scripts

```dataview
LIST
FROM "scripts" OR "."
WHERE contains(file.ext, "sh") OR contains(file.ext, "ps1") OR contains(file.ext, "bat")
SORT file.name ASC
```

---

## Infrastructure Costs

```dataview
TABLE WITHOUT ID
  service as "Service",
  cost-category as "Category",
  monthly-cost as "Cost/Month",
  usage as "Usage",
  optimization as "Optimize"
FROM "docs/infrastructure/costs"
WHERE cost-tracking = true
SORT monthly-cost DESC
```

---

## Open Infrastructure Issues

```dataview
TABLE WITHOUT ID
  issue-id as "ID",
  issue-type as "Type",
  component as "Component",
  severity as "Severity",
  status as "Status",
  assigned-to as "Assigned"
FROM "docs/issues"
WHERE issue-category = "infrastructure" AND status != "closed"
SORT severity DESC, component ASC
```

---

## Infrastructure Tasks

```dataview
TASK
FROM "docs/tasks"
WHERE contains(tags, "infrastructure") OR contains(tags, "deployment") OR contains(tags, "cicd") AND !completed
SORT priority DESC, due ASC
```

---

## Related Documentation

```dataview
TABLE WITHOUT ID
  file.link as "Document",
  infrastructure-area as "Area",
  doc-type as "Type",
  dateformat(file.mtime, "yyyy-MM-dd") as "Updated"
FROM "docs/infrastructure" OR "docs" OR "web"
WHERE contains(tags, "infrastructure") OR contains(tags, "deployment") OR contains(file.name, "DEPLOYMENT") OR contains(file.name, "DOCKER")
SORT file.mtime DESC
LIMIT 15
```

---

## Quick Actions

- 🐳 [[Docker Setup|View Docker Configuration]]
- 🔄 [[CI/CD Pipelines|View GitHub Actions]]
- 📦 [[Dependencies|View Dependency Status]]
- 🌐 [[Web Deployment|View Web Architecture]]
- 🔒 [[Security Scans|View Security Automation]]
- 📊 [[Build Status|View Recent Builds]]

---

**Query Performance:** Target <1s | **Data Sources:** .github/workflows, docker-compose.yml, package.json, pyproject.toml | **Refresh:** Real-time
