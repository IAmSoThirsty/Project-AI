# TAAR Report: workflow-dag-report-writer

Agent: workflow-dag-report-writer  
Source: workflow-dag-reader  
Run ID: 20260710T160529013599Z-d9c44acc  
Source Evidence Hash: 8b862b5048696f8219add83683753cfc80a503adb16b8b7abdc8edae30571e1c  
Classification: OPEN  
Created: 2026-07-10T16:05:29.182802+00:00

## Summary

info: 24

## Findings

| Severity | Path | Line | Message |
|---|---|---:|---|
| info | ci.yaml | — | triggers: pull_request, push |
| info | ci.yaml | — | job python: needs=['-'] runs-on=ubuntu-latest permissions=inherited secrets=['-'] steps=10 |
| info | ci.yaml | — | job rust: needs=['-'] runs-on=ubuntu-latest permissions=inherited secrets=['-'] steps=5 |
| info | ci.yaml | — | job node: needs=['-'] runs-on=ubuntu-latest permissions=inherited secrets=['-'] steps=7 |
| info | ci.yaml | — | job android: needs=['-'] runs-on=ubuntu-latest permissions=inherited secrets=['-'] steps=5 |
| info | ci.yaml | — | job desktop: needs=['-'] runs-on=ubuntu-latest permissions=inherited secrets=['-'] steps=6 |
| info | ci.yaml | — | job compose: needs=['-'] runs-on=ubuntu-latest permissions=inherited secrets=['-'] steps=6 |
| info | ci.yaml | — | job kubernetes: needs=['-'] runs-on=ubuntu-latest permissions=inherited secrets=['-'] steps=6 |
| info | ci.yaml | — | job sbom: needs=['-'] runs-on=ubuntu-latest permissions=inherited secrets=['-'] steps=5 |
| info | dangerous.yml | — | triggers: pull_request_target |
| info | dangerous.yml | — | job build: needs=['-'] runs-on=self-hosted permissions=inherited secrets=['DEPLOY_TOKEN'] steps=5 |
| info | dangerous.yml | — | job deploy: needs=['-'] runs-on=ubuntu-latest permissions=inherited secrets=['-'] steps=1 |
| info | hardened.yml | — | triggers: pull_request |
| info | hardened.yml | — | job test: needs=['-'] runs-on=ubuntu-latest permissions=inherited secrets=['-'] steps=3 |
| info | hardened.yml | — | job deploy: needs=['test'] runs-on=ubuntu-latest permissions=inherited secrets=['-'] steps=1 |
| info | publish.yaml | — | triggers: push, workflow_dispatch |
| info | publish.yaml | — | job image-metadata: needs=['-'] runs-on=ubuntu-latest permissions=inherited secrets=['-'] steps=3 |
| info | publish.yaml | — | job build-api: needs=['image-metadata'] runs-on=ubuntu-latest permissions=declared secrets=['GITHUB_TOKEN'] steps=4 |
| info | publish.yaml | — | job build-web: needs=['image-metadata'] runs-on=ubuntu-latest permissions=declared secrets=['GITHUB_TOKEN'] steps=4 |
| info | publish.yaml | — | job build-adapters: needs=['image-metadata'] runs-on=ubuntu-latest permissions=declared secrets=['GITHUB_TOKEN'] steps=4 |
| info | publish.yaml | — | job build-genesis: needs=['image-metadata'] runs-on=ubuntu-latest permissions=declared secrets=['GITHUB_TOKEN'] steps=4 |
| info | publish.yaml | — | job publish-sbom: needs=['build-api', 'build-web', 'build-adapters', 'build-genesis'] runs-on=ubuntu-latest permissions=declared secrets=['-'] steps=2 |
| info | publish.yaml | — | job verify-images: needs=['image-metadata', 'build-api', 'build-web', 'build-adapters', 'build-genesis'] runs-on=ubuntu-latest permissions=declared secrets=['GITHUB_TOKEN'] steps=5 |
| info | publish.yaml | — | job publish-release-notes: needs=['image-metadata', 'verify-images'] runs-on=ubuntu-latest permissions=declared secrets=['-'] steps=3 |

## Ignored

| Path | Reason |
|---|---|
| — | — |

## Uncertainty

- None recorded

## Human Action Required

No

## Output Record

```yaml
run_id: 20260710T160529013599Z-d9c44acc
writer_agent_id: workflow-dag-report-writer
source_evidence_hash: 8b862b5048696f8219add83683753cfc80a503adb16b8b7abdc8edae30571e1c
classification: OPEN
```
