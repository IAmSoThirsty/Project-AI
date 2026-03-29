# ============================================================================ #
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-17 | TIME: 10:45               #
# COMPLIANCE: Sovereign Substrate / Level 1-2 Memory Dept                      #
# ============================================================================ #

---
description: Relentless audit for Liara (Memory Dept), Registry, and Persistence logic.
---

### 📚 Liara / Memory Dept Audit

This workflow verifies the Registry integrity, memory logging services, and the persistence of the Sovereign state.

// turbo
1. **Registry Integrity Sweep**: Verify the Registry Dept's state consistency and CID resolution.
```bash
python tools/dependency_agent.py --target trunk/mid/Registry_Dept
```

// turbo
2. **Memory Service Verification**: Audit the memory logging service for secure serialization of Sovereign engrams.
```bash
python tools/stub_hunter_agent.py --target src/app/core/services/memory_logging_service.py
```

// turbo
3. **State Migration Resilience**: Verify the State Migration Manager's cross-substrate migration logic.
```bash
python tools/path_integrity_agent.py --target src/app/core/state_migration_manager.py
```

// turbo
4. **Persistence Audit**: Scan `trunk/mid/Memory_Dept` for unencrypted engram leaks or stale registries.
```bash
python tools/dead_code_agent.py --target trunk/mid/Memory_Dept
```

### 📊 Report
- `governance/LIARA_MEMORY_AUDIT.md`
