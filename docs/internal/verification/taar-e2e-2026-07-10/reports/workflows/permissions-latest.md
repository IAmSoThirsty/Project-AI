# TAAR Report: workflow-permission-report-writer

Agent: workflow-permission-report-writer  
Source: workflow-permission-reader  
Run ID: 20260710T160529490626Z-b57933d2  
Source Evidence Hash: 4001835b3ffab5eb308e083ddb981e0e0c18b76fa4bb749cb3c05dad62eb92fb  
Classification: RESTRICTED  
Created: 2026-07-10T16:05:29.647699+00:00

## Summary

critical: 1, high: 6, medium: 1

## Findings

| Severity | Path | Line | Message |
|---|---|---:|---|
| medium | ci.yaml | — | No permissions block declared: GITHUB_TOKEN falls back to repository default |
| critical | dangerous.yml | — | workflow: permissions set to write-all |
| high | publish.yaml | — | job build-api: broad permission packages: write |
| high | publish.yaml | — | job build-web: broad permission packages: write |
| high | publish.yaml | — | job build-adapters: broad permission packages: write |
| high | publish.yaml | — | job build-genesis: broad permission packages: write |
| high | publish.yaml | — | job publish-sbom: broad permission packages: write |
| high | publish.yaml | — | job publish-release-notes: broad permission contents: write |

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
run_id: 20260710T160529490626Z-b57933d2
writer_agent_id: workflow-permission-report-writer
source_evidence_hash: 4001835b3ffab5eb308e083ddb981e0e0c18b76fa4bb749cb3c05dad62eb92fb
classification: RESTRICTED
```
