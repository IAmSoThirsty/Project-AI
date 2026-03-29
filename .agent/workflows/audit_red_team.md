# ============================================================================ #
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-17 | TIME: 10:50               #
# COMPLIANCE: Sovereign Substrate / Red Team Adversarial Logic                  #
# ============================================================================ #

---
description: Relentless Red Team audit for adversarial simulation and defense.
---

### 🧨 Red Team / Adversarial Audit

This workflow verifies the adversary generator, attack surface, and the system's ability to self-morph under attack.

// turbo
1. **Adversary Simulation**: Trigger the adversary generator to simulate hierarchical attack vectors.
```bash
python src/thirsty_lang/src/thirsty_interpreter.py src/app/core/adversary_generator.thirsty
```

// turbo
2. **Morphing Defense Verification**: Verify that the `advanced-defense.thirsty` rules correctly trigger polymorphic code morphing.
```bash
python tools/stub_hunter_agent.py --target src/thirsty_lang/examples/security/advanced-defense.thirsty
```

// turbo
3. **Attack Surface Map**: Map all reachable entrypoints from external substrate harnesses.
```bash
python tools/dependency_agent.py --target src/app/core/battery_harness.py
```

// turbo
4. **Resilience Stress**: Run total system stress tests while the Red Team engine is active.
```bash
python tools/boot_verification_agent.py --adversarial
```

### 📊 Report
- `governance/RED_TEAM_ADVERSARIAL_AUDIT.md`
