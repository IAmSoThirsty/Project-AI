# TAAR Report: workflow-artifact-report-writer

Agent: workflow-artifact-report-writer  
Source: workflow-artifact-reader  
Run ID: 20260710T160528861011Z-15c1da83  
Source Evidence Hash: 4773e9c77c74666340561ae3aee492c7e0aee651542b9dbf550a8e804852ba38  
Classification: CONTROLLED  
Created: 2026-07-10T16:05:28.989592+00:00

## Summary

high: 1, low: 2

## Findings

| Severity | Path | Line | Message |
|---|---|---:|---|
| low | ci.yaml | — | Artifact upload without retention-days in job sbom |
| high | dangerous.yml | — | Artifact upload of entire workspace in job build |
| low | dangerous.yml | — | Artifact upload without retention-days in job build |

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
run_id: 20260710T160528861011Z-15c1da83
writer_agent_id: workflow-artifact-report-writer
source_evidence_hash: 4773e9c77c74666340561ae3aee492c7e0aee651542b9dbf550a8e804852ba38
classification: CONTROLLED
```
