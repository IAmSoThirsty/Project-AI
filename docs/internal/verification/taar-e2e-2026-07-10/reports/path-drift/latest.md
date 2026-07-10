# TAAR Path Drift Report

Agent: path-drift-report-writer  
Source: path-drift-reader  
Run ID: 20260710T160527617153Z-c846f167  
Source Evidence Hash: f2b260df61aa45a7d2859b775c8ad9679b0463aede08f97e89d259f43dc2ecf3  
Classification: OPEN  
Created: 2026-07-10T16:05:27.772713+00:00

## Summary

high: 4, low: 1

## Findings

| Severity | Path | Line | Message |
|---|---|---:|---|
| low | NOTES.md | 1 | Stale path pattern 'T:/Project-AI-Beginnings' found; canonical root is T:\Temp\claude\scratch\taar-e2e |
| high | taar.toml | 22 | Stale path pattern 'T:/Project-AI-Beginnings' found; canonical root is T:\Temp\claude\scratch\taar-e2e |
| high | taar.toml | 23 | Stale path pattern 'Project-AI-main' found; canonical root is T:\Temp\claude\scratch\taar-e2e |
| high | taar.toml | 24 | Stale path pattern 'T:/Project-AI-main' found; canonical root is T:\Temp\claude\scratch\taar-e2e |
| high | taar.toml | 25 | Stale path pattern 'Project-AI-main' found; canonical root is T:\Temp\claude\scratch\taar-e2e |

## Ignored

| Path | Reason |
|---|---|
| T:\Temp\claude\scratch\taar-e2e\.project-ai\automation\evidence\git-status-reader\20260710T160521653061Z-05b83266\evidence.yaml | automation output history |
| T:\Temp\claude\scratch\taar-e2e\.project-ai\automation\evidence\git-status-reader\20260710T160521653061Z-05b83266\stderr.txt | automation output history |
| T:\Temp\claude\scratch\taar-e2e\.project-ai\automation\evidence\git-status-reader\20260710T160521653061Z-05b83266\stdout.txt | automation output history |
| T:\Temp\claude\scratch\taar-e2e\.project-ai\automation\evidence\governance-reader\20260710T160521957480Z-28335853\evidence.yaml | automation output history |
| T:\Temp\claude\scratch\taar-e2e\.project-ai\automation\evidence\governance-reader\20260710T160521957480Z-28335853\stderr.txt | automation output history |
| T:\Temp\claude\scratch\taar-e2e\.project-ai\automation\evidence\governance-reader\20260710T160521957480Z-28335853\stdout.txt | automation output history |
| T:\Temp\claude\scratch\taar-e2e\.project-ai\automation\evidence\heartbeat-reader\20260710T160522081544Z-a4602e83\evidence.yaml | automation output history |
| T:\Temp\claude\scratch\taar-e2e\.project-ai\automation\evidence\heartbeat-reader\20260710T160522081544Z-a4602e83\stderr.txt | automation output history |
| T:\Temp\claude\scratch\taar-e2e\.project-ai\automation\evidence\heartbeat-reader\20260710T160522081544Z-a4602e83\stdout.txt | automation output history |
| T:\Temp\claude\scratch\taar-e2e\.project-ai\automation\evidence\lock-reader\20260710T160522350656Z-6d8993f4\evidence.yaml | automation output history |
| T:\Temp\claude\scratch\taar-e2e\.project-ai\automation\evidence\lock-reader\20260710T160522350656Z-6d8993f4\stderr.txt | automation output history |
| T:\Temp\claude\scratch\taar-e2e\.project-ai\automation\evidence\lock-reader\20260710T160522350656Z-6d8993f4\stdout.txt | automation output history |
| T:\Temp\claude\scratch\taar-e2e\.project-ai\automation\evidence\mypy-reader\20260710T160522614593Z-31ad3e7a\evidence.yaml | automation output history |
| T:\Temp\claude\scratch\taar-e2e\.project-ai\automation\evidence\mypy-reader\20260710T160522614593Z-31ad3e7a\stderr.txt | automation output history |
| T:\Temp\claude\scratch\taar-e2e\.project-ai\automation\evidence\mypy-reader\20260710T160522614593Z-31ad3e7a\stdout.txt | automation output history |
| T:\Temp\claude\scratch\taar-e2e\.project-ai\automation\evidence\overnight-reader\20260710T160523019484Z-358fb8d7\evidence.yaml | automation output history |
| T:\Temp\claude\scratch\taar-e2e\.project-ai\automation\evidence\overnight-reader\20260710T160523019484Z-358fb8d7\stderr.txt | automation output history |
| T:\Temp\claude\scratch\taar-e2e\.project-ai\automation\evidence\overnight-reader\20260710T160523019484Z-358fb8d7\stdout.txt | automation output history |
| T:\Temp\claude\scratch\taar-e2e\.project-ai\automation\locks\path-drift-reader.lock.json | automation output history |

## Uncertainty

- None recorded

## Human Action Required

No

## Output Record

```yaml
run_id: 20260710T160527617153Z-c846f167
writer_agent_id: path-drift-report-writer
source_evidence_hash: f2b260df61aa45a7d2859b775c8ad9679b0463aede08f97e89d259f43dc2ecf3
classification: OPEN
```
