# Security Agents - Quick Reference

## Overview

Project-AI now includes 4 security and testing agents integrated with the Triumvirate governance system:

1. **LongContextAgent** - 200k token context (Nous-Capybara-34B-200k)
2. **SafetyGuardAgent** - Content moderation (Llama-Guard-3-8B)
3. **JailbreakBenchAgent** - Systematic jailbreak testing
4. **RedTeamAgent** - Multi-turn adversarial testing (ARTKIT)

## Quick Start

### 1. Access via CouncilHub

```python
from app.core.council_hub import CouncilHub
from app.core.cognition_kernel import CognitionKernel

kernel = CognitionKernel()
hub = CouncilHub(kernel=kernel)
hub.register_project("Project-AI")

# Agents are now available
agents = hub.list_agents()
# ['long_context', 'safety_guard', 'jailbreak_bench', 'red_team', ...]
```

### 2. Direct Agent Use

```python
from app.agents import (
    LongContextAgent,
    SafetyGuardAgent,
    JailbreakBenchAgent,
    RedTeamAgent
)

# Initialize with governance
safety = SafetyGuardAgent(strict_mode=True, kernel=kernel)
long_context = LongContextAgent(max_context_tokens=200000, kernel=kernel)
jailbreak = JailbreakBenchAgent(data_dir="data/jailbreak", kernel=kernel)
red_team = RedTeamAgent(data_dir="data/red_team", max_turns=10, kernel=kernel)
```

## Common Use Cases

### Safety Filtering

```python
# Pre-process input
check = safety.check_prompt_safety(user_input)
if not check["is_safe"]:
    return f"Blocked: {check['violation_type']}"

# Post-process output
check = safety.check_response_safety(llm_response)
if check["is_safe"]:
    return llm_response
```

### Long Document Analysis

```python
result = long_context.analyze_large_document(
    document=large_doc,
    query="Summarize key points"
)
print(result["analysis"])
```

### Jailbreak Testing

```python
results = jailbreak.run_benchmark(
    target_system=my_ai_system,
    max_tests=50
)
print(f"Pass rate: {results['pass_rate']:.1%}")
```

### Red Team Testing

```python
session = red_team.run_adversarial_session(
    target_system=my_ai_system,
    strategy="gradual_escalation"
)
print(f"Vulnerabilities: {session['vulnerabilities_found']}")
```

## Configuration

Add to `.env`:

```bash
# Long-Context Model
LONG_CONTEXT_API_ENDPOINT=https://api.example.com/v1
LONG_CONTEXT_API_KEY=your_key

# Safety Model
SAFETY_MODEL_API_ENDPOINT=https://api.example.com/v1
SAFETY_MODEL_API_KEY=your_key
```

## Testing

Run verification:
```bash
python tests/verify_security_agents.py
```

Run demo:
```bash
python examples/security_agents_demo.py
```

## Documentation

- **User Guide**: `docs/SECURITY_AGENTS_GUIDE.md`
- **Integration Summary**: `docs/SECURITY_AGENTS_INTEGRATION_SUMMARY.md`
- **Demo**: `examples/security_agents_demo.py`

## Features Summary

### LongContextAgent
- 200k token context window
- Document analysis
- Context compression
- Streaming support

### SafetyGuardAgent
- Pre/post-processing filters
- 6 violation types
- Jailbreak detection
- Statistics tracking

### JailbreakBenchAgent
- Standardized test scenarios
- 4+ attack categories
- Defense evaluation
- Automated reporting

### RedTeamAgent
- Multi-turn conversations
- 6 attack strategies
- Vulnerability discovery
- Session management

## Agent Statistics

| Agent | Lines | Features |
|-------|-------|----------|
| LongContextAgent | 360 | Context management, compression |
| SafetyGuardAgent | 443 | 6 detection types, stats |
| JailbreakBenchAgent | 573 | 4+ categories, evaluation |
| RedTeamAgent | 683 | 6 strategies, multi-turn |

## Integration

All agents:
- ✅ Inherit from `KernelRoutedAgent`
- ✅ Route through `CognitionKernel`
- ✅ Triumvirate governance
- ✅ Full audit trail
- ✅ Memory integration

## Status

**Version**: v1.0.0  
**Status**: Production Ready  
**Tests**: All Passing ✓  
**Date**: January 2026

## Support

See full documentation:
- `docs/SECURITY_AGENTS_GUIDE.md`
- `docs/SECURITY_AGENTS_INTEGRATION_SUMMARY.md`
