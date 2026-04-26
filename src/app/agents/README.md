# Agent Systems Index

Quick reference for all agents in this directory.

## 📚 Documentation

- **[AGENT_CLASSIFICATION.md](AGENT_CLASSIFICATION.md)** - Comprehensive classification and governance status of all 32 agents

## 🔍 Quick Lookup

### By Function

**Security & Safety (8 agents)**
- `oversight.py` - System monitoring and compliance
- `validator.py` - Input validation and data integrity
- `constitutional_guardrail_agent.py` - Constitutional AI enforcement
- `code_adversary_agent.py` - Vulnerability detection and patching
- `safety_guard_agent.py` - Content moderation and jailbreak detection
- `border_patrol.py` - Sandbox verification and quarantine
- `sandbox_runner.py` - Sandboxed code execution
- `sandbox_worker.py` - Worker process for sandbox

**Adversarial Testing (5 agents)**
- `red_team_agent.py` - ARTKIT multi-turn adversarial testing
- `jailbreak_bench_agent.py` - Standardized jailbreak benchmarks
- `red_team_persona_agent.py` - DeepMind-style persona testing
- `alpha_red.py` - Evolutionary adversary with RL
- `attack_train_loop.py` - Adversary/defender co-evolution (stub)

**Defense & Protection (3 agents)**
- `tarl_protector.py` - T-A-R-L strategic code protection
- `codex_deus_maximus.py` - Schematic guardian and auto-fix
- `thirsty_lang_validator.py` - T-A-R-L capability validation

**Code Quality & CI (6 agents)**
- `ci_checker_agent.py` - Pytest, ruff, static analysis
- `test_qa_generator.py` - Test generation
- `doc_generator.py` - Documentation generation
- `refactor_agent.py` - Code refactoring with black/ruff
- `dependency_auditor.py` - Dependency security auditing
- `rollback_agent.py` - Incident response and rollback

**Knowledge & Retrieval (4 agents)**
- `knowledge_curator.py` - Knowledge curation and deduplication
- `retrieval_agent.py` - Vector QA and document retrieval
- `long_context_agent.py` - 200k token context handling
- `explainability.py` - Decision transparency (stub)

**Planning & Coordination (2 agents)**
- `planner_agent.py` - Task planning and scheduling (GOVERNED)
- `planner.py` - Legacy stub (BYPASS)

**Utility & Support (3 agents)**
- `expert_agent.py` - Expert review with elevated permissions
- `ux_telemetry.py` - UX feedback and telemetry
- `cerberus_codex_bridge.py` - Threat detection to defense bridge

### By Governance Status

**✅ Governed (30 agents)** - Routed through CognitionKernel
- See [AGENT_CLASSIFICATION.md](AGENT_CLASSIFICATION.md#governed-agents-route-through-cognitionkernel)

**⚠️ Bypass-by-Design (2 agents)** - Explicit bypass with justification
- `planner.py` - Legacy stub, no AI/I/O
- `attack_train_loop.py` - Disabled stub, requires governance when enabled

### By Risk Level

**High Risk (14 agents)**
- All security agents, adversarial testing, sandbox execution, code modification

**Medium Risk (13 agents)**
- CI/CD, refactoring, expert actions, dependency auditing

**Low Risk (5 agents)**
- Documentation, knowledge curation, telemetry, retrieval

### By AI Integration Status

**Direct AI Calls (0 agents)** - All external APIs not yet integrated

**Planned AI Integration (9 agents)**
- `safety_guard_agent.py` - Llama-Guard-3-8B
- `long_context_agent.py` - Nous-Capybara-34B
- `codex_deus_maximus.py` - GPT-OSS 1208
- 6 adversarial agents (RL/LLM integration planned)

**No AI Required (23 agents)** - Pure utility, tooling, coordination

## 🔧 Usage Patterns

### Creating a New Agent

```python
from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent

class MyAgent(KernelRoutedAgent):
    def __init__(self, kernel: CognitionKernel | None = None) -> None:
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="medium",  # low/medium/high
        )
        
    def some_action(self, args) -> dict[str, Any]:
        return self._execute_through_kernel(
            action=self._do_some_action,
            action_name="MyAgent.some_action",
            action_args=(args,),
            requires_approval=True,  # or False
            risk_level="medium",
            metadata={"key": "value"},
        )
        
    def _do_some_action(self, args) -> dict[str, Any]:
        # Implementation here
        return {"success": True, "result": data}
```

### Bypass Pattern (Use Sparingly)

Only for agents with:
- No AI calls
- No external APIs
- No file system modifications
- No security implications

```python
# GOVERNANCE BYPASS: [REASON]
# Justification: [WHY BYPASS IS ACCEPTABLE]
# Risk: [WHAT COULD GO WRONG]
```

## 📊 Statistics

- **Total Agents**: 32
- **Governance Coverage**: 100%
- **Integration Rate**: 93.8% (30/32 governed)
- **Average Risk**: Medium-High
- **AI Integration**: 28% planned, 72% no AI needed

## 🎯 Next Steps

1. **External AI API Integration** - Wrap API calls for 3 agents
2. **Training Loop Governance** - Integrate before enabling
3. **Agent Monitoring** - Add telemetry and performance tracking

---

**Last Updated**: 2025-01-26  
**Maintained By**: AI Systems Team  
**Documentation**: [AGENT_CLASSIFICATION.md](AGENT_CLASSIFICATION.md)
