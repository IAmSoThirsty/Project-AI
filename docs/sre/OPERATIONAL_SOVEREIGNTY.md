# Sovereign SRE: SLO Budgets & Alerting Policies

**System**: Project-AI Sovereign Substrate

## 1. Service Level Objectives (SLOs)

| Service | Metric | Target | Error Budget (Monthly) |
|---------|--------|--------|------------------------|
| **Audit API** | Availability | 99.99% | 4.38 minutes |
| **Invariant Gate** | Latency (p99) | < 50ms | 1% of requests |
| **Shadow VM** | Verification Success | 100% | **0% (Zero Tolerance)** |

## 2. Alerting Policy (Paging)

### Critical Alerts (P1 - Immediate Page)

- **InvariantDivergenceDetected**: Primary and Shadow planes have diverged. System successfully halted. (Action: Forensic analysis required).
- **AuditChainCorruption**: Deterministic hash chain check failed. (Action: Restore from S3 Object Lock).
- **KMSKeyInaccessible**: Sovereign Master Key cannot be reached. (Action: Emergency failover to HSM).

### Warning Alerts (P2 - Ticket Created)

- **ErrorBudgetBurnRateHigh**: SLO at risk of violation.
- **CryptoRotationPending**: Algorithm rotation threshold approaching (60-day warning).

## 3. Incident Response Playbook: "Iron Path Divergence"

1. **Detection**: `ShadowAwareVM` throws `DivergenceError`.
2. **Containment**: Reflexive halt automatically locks the namespace.
3. **Investigation**: Pull `sovereign_events` DDL-validated output for the specific `event_id`.
4. **Resolution**: If benign, patch the Shadow Plane simulation; if malicious, initiate **Sovereign Quarantine**.
