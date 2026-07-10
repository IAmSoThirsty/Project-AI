# TAAR Report: workflow-injection-report-writer

Agent: workflow-injection-report-writer  
Source: workflow-injection-reader  
Run ID: 20260710T160529336463Z-af14c21d  
Source Evidence Hash: 93a0ae2132c71716d050de2770af660258a9a8eaec3a9e4559adf011491dbcdc  
Classification: RESTRICTED  
Created: 2026-07-10T16:05:29.474583+00:00

## Summary

critical: 1

## Findings

| Severity | Path | Line | Message |
|---|---|---:|---|
| critical | dangerous.yml | — | Attacker-controllable context interpolated into shell: ${{ github.event.pull_request.title }} (job build) |

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
run_id: 20260710T160529336463Z-af14c21d
writer_agent_id: workflow-injection-report-writer
source_evidence_hash: 93a0ae2132c71716d050de2770af660258a9a8eaec3a9e4559adf011491dbcdc
classification: RESTRICTED
```
