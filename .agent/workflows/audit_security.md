# ============================================================================ #
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-17 | TIME: 10:48               #
# COMPLIANCE: Sovereign Substrate / Zero-Trust Defense                          #
# ============================================================================ #

---
description: Brutal security audit for Zero-Trust Substrate and TARL enforcement.
---

### 🛡️ Security / Zero-Trust Audit

This workflow verifies the TARL policy engine, cryptographic agility, and the adversarial resilience of the substrate.

// turbo
1. **TARL Runtime Verification**: Verify the integrated TARL runtime is correctly evaluating policies.
```bash
python src/thirsty_lang/src/thirsty_interpreter.py --test-policy src/thirsty_lang/src/tarl/policies/default.json
```

// turbo
2. **Crypto-Agility Check**: Verify the cryptographic agility logic in the core substrate.
```bash
python src/thirsty_lang/src/thirsty_interpreter.py src/app/core/crypto_agility.thirsty
```

// turbo
3. **Sanitization Audit**: Scan all `advanced-defense.thirsty` modules for bypasses or weak sanitization.
```bash
python tools/architect_agent.py --target src/thirsty_lang/examples/security/advanced-defense.thirsty
```

// turbo
4. **Access Control Trace**: Verify the Governance Service's binding approval for security-sensitive executions.
```bash
python tools/path_integrity_agent.py --target src/app/core/services/governance_service.py
```

### 📊 Report
- `governance/SECURITY_ZERO_TRUST_AUDIT.md`
