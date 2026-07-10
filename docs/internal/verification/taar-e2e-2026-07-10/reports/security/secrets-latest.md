# TAAR Secret Scan Report

Agent: secret-report-writer  
Source: secret-reader  
Run ID: 20260710T160528252513Z-9f8f09ec  
Source Evidence Hash: 4c449e7b56f19eee1be243588398471d78d8dd9926b59d36ac4bf5e904367533  
Classification: SECRET  
Created: 2026-07-10T16:05:28.544091+00:00

## Summary

critical: 1, high: 1

## Findings

| Severity | Path | Line | Message |
|---|---|---:|---|
| critical | config_backup.py | 1 | Possible github_token: ghp_...7Ii8 |
| high | config_backup.py | 1 | Possible env_secret: API_...Ii8" |

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
run_id: 20260710T160528252513Z-9f8f09ec
writer_agent_id: secret-report-writer
source_evidence_hash: 4c449e7b56f19eee1be243588398471d78d8dd9926b59d36ac4bf5e904367533
classification: SECRET
```
