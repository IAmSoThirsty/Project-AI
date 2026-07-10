# TAAR Report: workflow-deploy-report-writer

Agent: workflow-deploy-report-writer  
Source: workflow-deploy-reader  
Run ID: 20260710T160529199310Z-ef497608  
Source Evidence Hash: bef20e8f48b3d4eb8f05cafb106548f1988366f59832d0191a58323bf0e90b73  
Classification: CONTROLLED  
Created: 2026-07-10T16:05:29.323724+00:00

## Summary

high: 5, info: 1

## Findings

| Severity | Path | Line | Message |
|---|---|---:|---|
| high | dangerous.yml | — | Deployment-shaped job build has no environment gate (no approval boundary) |
| high | dangerous.yml | — | Deployment-shaped job deploy has no environment gate (no approval boundary) |
| info | hardened.yml | — | Deployment job deploy gated by environment production |
| high | publish.yaml | — | Deployment-shaped job publish-sbom has no environment gate (no approval boundary) |
| high | publish.yaml | — | Deployment-shaped job verify-images has no environment gate (no approval boundary) |
| high | publish.yaml | — | Deployment-shaped job publish-release-notes has no environment gate (no approval boundary) |

## Ignored

| Path | Reason |
|---|---|
| — | — |

## Uncertainty

- None recorded

## Human Action Required

Yes

## Output Record

```yaml
run_id: 20260710T160529199310Z-ef497608
writer_agent_id: workflow-deploy-report-writer
source_evidence_hash: bef20e8f48b3d4eb8f05cafb106548f1988366f59832d0191a58323bf0e90b73
classification: CONTROLLED
```
