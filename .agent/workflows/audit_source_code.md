# ============================================================================ #
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-17 | TIME: 11:02               #
# COMPLIANCE: Sovereign Substrate / Source Code Integrity                       #
# ============================================================================ #

---
description: Comprehensive audit for everything that isn't documentation.
---

### 💻 Source Code Audit (Non-Docs)

This workflow verifies every source file in the repository for technical validity, lint compliance, and security grounding.

// turbo
1. **Global Lint Sweep**: Run a comprehensive lint check across all Python source files.
```bash
ruff check src/
```

// turbo
2. **Path Resolution Check**: Verify that all relative imports in the `src/` directory are resolvable.
```bash
python tools/path_integrity_agent.py --target src
```

// turbo
3. **Stub Hunter (Global)**: Identify every unimplemented function across the entire source tree.
```bash
python tools/stub_hunter_agent.py --target . --exclude docs/
```

// turbo
4. **Dead Code (Global)**: Detect all unreachable logic and orphaned modules in the repository.
```bash
python tools/dead_code_agent.py --target . --exclude docs/
```

### 📊 Report
- `governance/SOURCE_CODE_AUDIT.md`
