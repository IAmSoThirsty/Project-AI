# ============================================================================ #
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-17 | TIME: 10:42               #
# COMPLIANCE: Sovereign Substrate / Level 1 Defense Dept                       #
# ============================================================================ #

---
description: Relentless audit for Galahad (Defense Dept), Ethics, and Four Laws enforcement.
---

### 🛡️ Galahad / Defense Dept Audit

This workflow verifies the ethical boundaries, defense resilience, and the integrity of the Four Laws enforcement substrate.

// turbo
1. **Four Laws Validation**: Audit the Governance Service's core Law enforcement logic.
```bash
python tools/stub_hunter_agent.py --target src/app/core/services/governance_service.py
```

// turbo
2. **Constitutional Scenario Stress**: Run the Constitutional Scenario Engine against adversarial edge cases.
```bash
python src/app/governance/constitutional_scenario_engine.py --stress --depth 5
```

// turbo
3. **Defense Harness Verification**: Verify the Collective Defense Harness's threat propagation logic.
```bash
python tools/path_integrity_agent.py --target src/app/core/collective_defense_harness.py
```

// turbo
4. **Ethics Compliance Trace**: Scan `trunk/mid/Defense_Dept` for alignment with UTF-8 ethical standards.
```bash
python tools/architect_agent.py --target trunk/mid/Defense_Dept
```

### 📊 Report
- `governance/GALAHAD_DEFENSE_AUDIT.md`
