# REFACTOR NOTICE: polyglot_execution.py

## Status: MARKED FOR FULL REFACTOR

This file (`src/app/core/polyglot_execution.py`) contains complex legacy AI execution code with direct OpenAI/HuggingFace calls.

### Current State
- **Direct AI calls**: Uses OpenAI and HuggingFace APIs directly
- **Complex orchestration**: Has its own routing, caching, rate limiting
- **NOT governance-compliant**: Bypasses governance pipeline

### Required Action
This file needs a **comprehensive refactor** to:
1. Use AI orchestrator instead of direct calls
2. Route through governance pipeline
3. Preserve existing features (caching, rate limiting, streaming)
4. Maintain backward compatibility

### Recommended Approach
Given the complexity (500+ lines), this should be refactored as a **separate focused task** to:
1. Understand all current features and callers
2. Design migration strategy preserving behavior
3. Implement with full test coverage
4. Gradual rollout with fallback

### Temporary Mitigation
For Level 2 minimal compliance:
- Mark file as "legacy bypass" in documentation
- Add warning log when used
- Document all callers for future migration

### Future Work
Create dedicated task: "Refactor polyglot_execution.py to governance-compliant orchestration"

---
**Created**: 2026-04-13  
**Priority**: Medium (not blocking Level 2 minimal, but required for full compliance)
