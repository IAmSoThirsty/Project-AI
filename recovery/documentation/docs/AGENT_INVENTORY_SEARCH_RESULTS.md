# Search Results: "1134 AI Agents" Query

**Date:** 2026-04-10  
**Query:** Location of list containing 1134 AI Agents

---

## Finding: No 1134 Agent List Found

After comprehensive search across the repository, **no file contains a list of 1134 AI agents**.

### What Was Found

#### 1. **Test Count Confusion (Most Likely)**

- Current pytest collection shows **1114 tests** (not 1134)
- Historical test counts vary:
  - `baseline_coverage.txt`: 3735 items
  - `COGNITION_TEST_SUMMARY.md`: 156 items  
  - `coverage_run_final.log`: 3772 items
  - Latest run: **1114 tests collected** (8780 total with deselected)

**Hypothesis:** 1134 might be a misremembered test count (actual: 1114)

#### 2. **Agent Implementation Files Found (NOT Lists)**

**Individual Agent Implementations:**
```
src/app/agents/
├── safety_guard_agent.py
├── rollback_agent.py
├── retrieval_agent.py
├── refactor_agent.py
├── red_team_persona_agent.py
├── red_team_agent.py
├── planner_agent.py
├── long_context_agent.py
├── jailbreak_bench_agent.py
├── expert_agent.py
├── constitutional_guardrail_agent.py
├── code_adversary_agent.py
├── ci_checker_agent.py
├── attack_train_loop.py
├── alpha_red.py
├── oversight.py
├── explainability.py
├── validator.py
├── ux_telemetry.py
└── border_patrol.py
```

**Agent System Infrastructure:**

- `src/app/miniature_office/agents/agent.py` - Base Agent class
- `src/app/miniature_office/core/global_registry.py` - Agent registry system
- `src/app/miniature_office/agent_lounge.py` - Agent coordination
- `src/app/core/council_hub.py` - Multi-agent orchestration
- `src/app/agents/planner.py` - Planning agent

**Total Individual Agent Files:** ~25-30 discrete agent implementations

#### 3. **Agent Documentation Found**

**Architecture Docs:**

- `docs/architecture/AGENT_MODEL.md` - Agent specification
- `docs/security_compliance/SECURITY_AGENTS_GUIDE.md`
- `docs/security_compliance/SECURITY_AGENTS_TEMPORAL_LLM_GUIDE.md`
- `docs/project_ai_god_tier_diagrams/data_flow/agent_execution_flow.md`

**None of these contain a list of 1134 agents.**

#### 4. **Agent System Capabilities**

**Agent Registry System:**

- `GlobalRegistry` class in `src/app/miniature_office/core/global_registry.py`
- Tracks agents dynamically at runtime
- No pre-defined list of 1134 agents in source

**Agent Roles Defined (Codex 3.1):**

1. ARCHITECT - Design authority
2. BUILDER - Implementation
3. VERIFIER - Correctness
4. SECURITY - Threat modeling
5. DOC_AGENT - Communication
6. MANAGER - Meta-agent for consensus

---

## Possible Explanations

### 1. **Misremembered Test Count** ⭐ Most Likely

- Current test suite: **1114 tests** (close to 1134)
- User may have seen "1114 tests collected" and remembered as 1134

### 2. **Deleted/Archived File**

- File may have existed in `archive/` directories
- Could have been moved during cleanup operations
- No trace found in git history for recent commits

### 3. **Planned Feature (Not Yet Implemented)**

- May refer to a planned agent library/catalog
- Specification exists but implementation pending
- Design docs mention multi-agent systems but no 1134 count

### 4. **External Data File**

- Could be in a data file not committed to git
- Might be in `.gitignore`d directory
- Could be in external database/service

### 5. **Confused with Another Metric**

- 1134 might refer to:
  - Lines of code in a specific file
  - Configuration parameters
  - Test assertions
  - Function/class count

---

## Recommendations

### If You're Looking For:

**1. All Agent Implementations:**

- See `src/app/agents/` directory (25+ agents)
- See `src/app/miniature_office/agents/` for base classes

**2. Agent Registry/Inventory:**

- Runtime registry: `src/app/miniature_office/core/global_registry.py`
- No static pre-populated list of 1134 agents exists

**3. Test Count:**

- Run: `python -m pytest --collect-only` to see all tests
- Current count: 1114 tests (8780 total items with deselected)

**4. Agent Capabilities:**

- See: `docs/architecture/AGENT_MODEL.md`
- See: `src/app/miniature_office/agents/agent.py` (CapabilityProfile class)

### Next Steps

**To Locate the 1134 List:**

1. Check if this was mentioned in external documentation
2. Check if it's in a database (not flat file)
3. Check if it's dynamically generated at runtime
4. Check if the number 1134 refers to something else entirely

**To Create a 1134 Agent List:**
If this list needs to be created, consider:

- Defining agent types/roles in `docs/architecture/`
- Creating JSON/YAML manifest in `data/agents/`
- Adding to global registry system

---

## File Search Summary

**Searches Performed:**

- [x] Grep for "1134" across all files
- [x] Grep for "agent" + "list", "inventory", "catalog"
- [x] Glob for all agent-related files
- [x] Search JSON/YAML for agent data
- [x] Check pytest collection counts
- [x] Review agent architecture docs

**Result:** No file containing 1134 agents found.

---

## Agent Count Breakdown

| Category | Count | Location |
|----------|-------|----------|
| Individual Agent Files | ~25 | `src/app/agents/` |
| Agent Base Classes | 2-3 | `src/app/miniature_office/` |
| Agent Roles (Enum) | 6 | `AgentRole` enum |
| Tests Collected | 1114 | pytest |
| Total Test Items | 8780 | pytest (with deselected) |

**Closest Match to 1134:** pytest test count of 1114 tests

---

**Conclusion:** The "1134 AI Agents" list does not exist in the current repository state. Most likely explanation is confusion with the test count (1114 tests).
