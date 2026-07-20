# Monitoring and Alerting Plan — v0.0.3 Successor

> The v0.0.2 references below identify the superseded baseline only; all
> current deployment evidence and target-environment acceptance belong to the
> v0.0.3 successor CAB record.

**Status:** CAB plan defined; deployed signal, query, dashboard, receiver, and
page-delivery evidence pending.

## Current repository surfaces

- API liveness/readiness probe: `/health/live`.
- Prometheus `/metrics` endpoint with `project_ai_build_info`, bounded
  `project_ai_http_requests_total`, and request-duration histogram series.
- Release-namespaced `ServiceMonitor`, `PrometheusRule`, and Grafana dashboard
  discovery ConfigMap for an externally operated monitoring stack.
- Rules cover missing metrics, API availability, 5xx ratio, p99 latency, PVC
  utilization, restart rate, and operational verifier failures.
- NetworkPolicy permits only the configured monitoring namespace/pod selector
  to scrape the API.
- Working performance targets exist in `docs/operations/PERFORMANCE_SLOS.md`.

These are configuration surfaces, not proof that signals or paging work.

## Local remediation status

Resolved locally:

1. Monitoring resources now use `.Release.Namespace`; the production render
   was verified for `project-ai-prod`.
2. Alert/dashboard queries use the actual API metric names, and the rebuilt
   Compose API exposed those series live.
3. The chart no longer deploys an incomplete embedded Prometheus/Grafana/Loki
   stack. It declares the contract for an externally operated stack.
4. The production render passed 1,123 Checkov Kubernetes checks with zero
   failures or skips.

Still required from the target environment:

1. Confirm Prometheus Operator and kube-state-metrics availability and labels.
2. Provide real Prometheus, Grafana, Alertmanager, and log-search endpoints.
3. Configure primary/secondary receivers and prove alert delivery and
   acknowledgement.
4. Import the dashboard and prove every required query against live cluster
   data.

## Required signals and provisional thresholds

Thresholds below are CAB starting criteria, not measured SLO guarantees.

| Signal | Trigger | Severity | Required action |
|---|---|---:|---|
| API workload unavailable | Required API pod not Running/Ready for 5m | Critical | Page; evaluate rollback |
| Liveness | Two consecutive non-200 `/health/live` checks 1m apart | Critical | Page; rollback if release-caused |
| Authentication/governance denial | Any expected denial accepts an unauthorized request | Critical | Stop traffic and rollback |
| Audit integrity | Any chain verification failure or audit write failure | Critical | Stop traffic; preserve evidence; rollback |
| 5xx ratio | >5% for 5m with real request denominator | High | Investigate; rollback if release-caused |
| API latency | p99 >1s for 5m | High | Investigate; rollback if sustained/release-caused |
| PVC capacity | >80% for 5m | High | Page storage owner; protect audit continuity |
| Restart rate | Confirmed repeated restarts over 5m | High | Investigate; rollback if release-caused |
| Backup | Scheduled backup missing/failed | High | Do not exit observation window |

## Ownership and routing

| Role/route | Value |
|---|---|
| Monitoring owner | TBD — named person/rota required |
| Primary page receiver | TBD |
| Secondary/escalation receiver | TBD |
| Incident commander | TBD |
| Dashboard URL | TBD |
| Prometheus URL/query access | TBD |
| Log search URL | TBD |
| Status/change channel | TBD |

## Pre-change validation

- Confirm Prometheus Operator, kube-state-metrics, ingress metrics, and storage.
- Render resources in the real namespace and confirm the configured monitoring
  namespace/pod selectors match the operated stack.
- Capture `/metrics`; map every alert and dashboard query to an emitted series.
- Run `promtool check rules` against rendered rules.
- Import dashboards and prove every required panel returns data.
- Configure Alertmanager routing and send a test alert through primary and
  secondary receivers; record acknowledgement time.
- Establish a pre-change baseline for traffic, errors, latency, restarts, PVC
  usage, governance outcomes, and audit integrity.

## Change observation

Proposed observation period: 30 minutes after all workloads become Ready. CAB
must approve the actual period.

- Minutes 0–10: continuous workload, health, error, latency, log, audit, and
  ingress observation.
- Minutes 10–30: five-minute checks plus core-flow and protected-route smoke.
- Support owner monitors user reports for the entire window.
- Any critical trigger invokes the rollback runbook immediately.

## Post-change checklist

- [ ] All required workloads Ready; image digests match approved evidence.
- [ ] `/health/live` returns 200 and the approved successor version.
- [ ] Prometheus target is Up and `/metrics` contains the approved series.
- [ ] Every required alert query evaluates without missing-series ambiguity.
- [ ] Test alert reached primary and secondary routes and was acknowledged.
- [ ] Dashboards show current traffic, error, latency, capacity, restart,
      governance, and audit information.
- [ ] Audit-chain verification and persistence checks pass.
- [ ] Backup job/target is healthy.
- [ ] Observation period closes without rollback trigger.
- [ ] Monitoring owner and acceptance authority sign off.
