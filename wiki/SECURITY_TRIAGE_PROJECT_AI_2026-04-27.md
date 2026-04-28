---
title: "Project-AI Security Triage and Remediation Plan"
date: 2026-04-27
status: actionable
scope: project-ai-only
source: user-submitted vulnerability inventory
---

## Executive Summary

Your vulnerability inventory is valid in spirit: there are multiple **critical exploit paths** in this repository that should be addressed in a strict order.

Highest-risk classes confirmed in current workspace:

1. **Unsafe deserialization / model loading** (`torch.load`, `pickle.loads`)
2. **SQL injection via string-concatenated queries**
3. **Workflow injection + unpinned/over-permissive GitHub Actions**
4. **Insecure runtime config in demo server (`debug=True`)**
5. **Android insecure defaults (`allowBackup=true`, cleartext traffic enabled)**

---

## Confirmed Critical Hotspots (Project-AI)

### 1) Unsafe deserialization / code execution

- `src/app/core/snn_integration.py`
  - `torch.load(path)` and `load_state_dict(torch.load(path))`
- `src/cognition/adapters/model_adapter.py`
  - `torch.load(...)`
- `src/app/core/memory_optimization/compression_engine.py`
  - `pickle.loads(decompressed)`

### 2) SQL injection risk

- `src/app/core/clickhouse_integration.py`
  - dynamic f-string SQL using user-controlled tokens (table/metric/time inputs)
- `src/app/core/risingwave_integration.py`
  - dynamic `SELECT * FROM {table_or_view}` and optional where concatenation
- `src/app/core/storage.py`
  - dynamic table/where composition via f-strings

### 3) GitHub Actions template injection / broad trust

- `.github/workflows/archive/build-release.yml`
- `.github/workflows/archive/sign-release-artifacts.yml`
- plus multiple archive workflows with dynamic shell interpolation and broad permissions

### 4) Insecure debug runtime

- `demos/thirstys_security_demo/demo_server.py`
  - `app.run(..., debug=True)`

### 5) Mobile security misconfigurations

- `android/app/src/main/AndroidManifest.xml`
  - `android:allowBackup="true"`
  - `android:usesCleartextTraffic="true"`
- `android/legion_mini/src/main/AndroidManifest.xml`
  - same insecure defaults
- `app/src/main/AndroidManifest.xml`
  - `android:allowBackup="true"`

### 6) Dependency-version exposures (high/critical surface)

- `requirements.txt`
  - `cryptography==42.0.4`
  - `PyJWT==2.8.0`
  - `gunicorn==22.0.0`
- `desktop/package.json`
  - `axios`, `electron` track
- `web/package.json`
  - `axios`, `next` track

---

## Immediate 24h Remediation Order (Do in this order)

## P0-A (0–4h): stop active exploitability

1. **Disable or harden risky archive workflows first**
   - remove dynamic interpolation of untrusted event/input values in shell contexts
   - pin third-party actions by full commit SHA
   - reduce `permissions:` to least privilege per job

2. **Patch unsafe deserialization**
   - `torch.load(..., weights_only=True, map_location="cpu")` where supported
   - enforce extension + trusted directory allowlist + SHA256 allowlist for model files
   - replace `pickle.loads` with safe format (JSON/msgpack) or signed-blob verification gate before unpickle

3. **Kill debug-mode RCE surface**
   - set `debug=False`
   - bind localhost by default for demos unless explicit env override

## P0-B (4–10h): data-layer containment

1. **Remove dynamic SQL concatenation**
   - enforce strict identifier allowlists for table/view names
   - parameterize values only (never concatenate untrusted predicates)
   - reject arbitrary `where_clause` strings; use structured filter DSL

2. **Lock Android defaults**
   - `allowBackup=false`
   - disable cleartext unless debug flavor requires it
   - explicitly gate exported components and network security config

## P1 (Day 2): package hardening + secret containment

1. **Upgrade vulnerable packages with compatibility test sweep**
   - Python security libs first (`cryptography`, `PyJWT`, `gunicorn`, etc.)
   - JS ecosystem (`axios`, `next`, Electron track)

2. **Secret response actions**
   - rotate any real credentials/private keys
   - replace committed values with placeholders
   - add secret scanning allowlist only for intentional fake examples

---

## Suggested Patch Batching Strategy (safe for CI)

- **PR-1 (Workflow Security)**
  - `.github/workflows/**` high-risk and archive pipelines
- **PR-2 (Deserialization + Sandbox Guardrails)**
  - `snn_integration.py`, `model_adapter.py`, `compression_engine.py`, `demo_server.py`
- **PR-3 (SQL Injection Hardening)**
  - `clickhouse_integration.py`, `risingwave_integration.py`, `storage.py`
- **PR-4 (Android Security Posture)**
  - all `AndroidManifest.xml`
- **PR-5 (Dependency Upgrades + lockfiles + regression tests)**

This sequence minimizes blast radius while reducing the highest exploitability first.

---

## Notes on Multi-Repo Findings

Your submitted inventory includes findings from other repositories (e.g., `Thirstys-waterfall`, `Thirsty-lang`, `Thirstys-Projects-Miniature-Office`).
This runbook is scoped to current workspace: **Project-AI**.

---

## Definition of Done (Security)

A batch is complete only when all are true:

- lint/type/tests pass
- targeted security checks are clean on touched files
- no new critical/high introduced
- remediation is documented with before/after rationale
- for secret findings: keys rotated and old credentials revoked

---

## Related Tracking Artifacts

- Compliance bundle control exceptions: [[COMPLIANCE_BUNDLE_EXCEPTION_REGISTER]]
