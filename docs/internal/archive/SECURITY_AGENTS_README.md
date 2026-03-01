## Security Agents - Quick Reference                         Productivity: Out-Dated(archive)

## Overview

Project-AI now includes 4 security and testing agents integrated with the Triumvirate governance system:

1. **LongContextAgent** - 200k token context (Nous-Capybara-34B-200k)
1. **SafetyGuardAgent** - Content moderation (Llama-Guard-3-8B) with continuous learning
1. **JailbreakBenchAgent** - Systematic jailbreak testing with HYDRA & JBB dataset integration
1. **RedTeamAgent** - Multi-turn adversarial testing (ARTKIT) with multi-turn scenario loading

## What's New

### Integrated with Existing Test Data

The agents now automatically integrate with Project-AI's extensive adversarial test datasets:

- **JailbreakBenchAgent** loads from:

  - HYDRA dataset (200 tests across 40 categories)
  - JBB dataset (30 jailbreak prompts)
  - Falls back to default scenarios if datasets unavailable

- **RedTeamAgent** loads from:

  - Multi-turn attack scenarios (YAML-based)
  - Falls back to default strategies if unavailable

- **SafetyGuardAgent** includes:

  - Pattern learning system for continuous improvement
  - Integration with continuous learning engine
  - Persistent pattern database

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

### Safety Filtering with Pattern Learning

```python

# Pre-process input

check = safety.check_prompt_safety(user_input)
if not check["is_safe"]:
    return f"Blocked: {check['violation_type']}"

# Learn from new attack patterns (continuous learning)

new_patterns = {
    "novel_attacks": ["new jailbreak pattern", "another bypass attempt"]
}
result = safety.update_detection_patterns(new_patterns, pattern_type="jailbreak")
print(f"Added {result['patterns_added']} new patterns")

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

### Jailbreak Testing with Real Data

```python

# Automatically loads HYDRA (200 tests) and JBB (30 tests) if available

results = jailbreak.run_benchmark(
    target_system=my_ai_system,
    max_tests=50  # Will use real test data first
)
print(f"Pass rate: {results['pass_rate']:.1%}")
print(f"Used {len(jailbreak.test_scenarios)} total scenarios")
```

### Red Team Testing with Multi-Turn Scenarios

```python

# Automatically loads multi-turn YAML scenarios if available

session = red_team.run_adversarial_session(
    target_system=my_ai_system,
    strategy="gradual_escalation"  # Will try to load matching scenario
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
- **NEW**: Pattern learning and continuous improvement
- **NEW**: Persistent pattern database
- Statistics tracking

### JailbreakBenchAgent

- **NEW**: Auto-loads HYDRA dataset (200 tests)
- **NEW**: Auto-loads JBB dataset (30 tests)
- 4+ attack categories
- Defense evaluation
- Automated reporting
- Graceful fallback to default scenarios

### RedTeamAgent

- Multi-turn conversations
- 6 attack strategies
- **NEW**: Auto-loads multi-turn YAML scenarios
- Vulnerability discovery
- Session management
- Graceful fallback to default strategies

## Dataset Integration

### HYDRA Dataset

- **Location**: `adversarial_tests/hydra/hydra_dataset.json`
- **Size**: 200 tests across 40 categories
- **Auto-loaded by**: JailbreakBenchAgent
- **Format**: JSON with id, category, prompt, severity

### JBB Dataset

- **Location**: `adversarial_tests/jbb/jbb_dataset.py`
- **Size**: 30 jailbreak prompts
- **Auto-loaded by**: JailbreakBenchAgent
- **Format**: Python module with JBB_PROMPTS

### Multi-Turn Scenarios

- **Location**: `adversarial_tests/multiturn/*.yaml`
- **Auto-loaded by**: RedTeamAgent
- **Format**: YAML with turns and attack types

## Agent Statistics

| Agent               | Lines | Features                        | Dataset Integration   |
| ------------------- | ----- | ------------------------------- | --------------------- |
| LongContextAgent    | 360   | Context management, compression | N/A                   |
| SafetyGuardAgent    | 443   | 6 detection types, learning     | Pattern database      |
| JailbreakBenchAgent | 573   | 4+ categories, evaluation       | HYDRA (200), JBB (30) |
| RedTeamAgent        | 683   | 6 strategies, multi-turn        | Multi-turn YAML       |

## Integration

All agents:

- ✅ Inherit from `KernelRoutedAgent`
- ✅ Route through `CognitionKernel`
- ✅ Triumvirate governance
- ✅ Full audit trail
- ✅ Memory integration
- ✅ **NEW**: Real dataset integration

## Status

**Version**: v1.1.0 **Status**: Production Ready **Tests**: All Passing ✓ **Date**: January 2026 **New**: Integrated with existing adversarial test datasets

## Support

See full documentation:

- `docs/SECURITY_AGENTS_GUIDE.md`
- `docs/SECURITY_AGENTS_INTEGRATION_SUMMARY.md`
