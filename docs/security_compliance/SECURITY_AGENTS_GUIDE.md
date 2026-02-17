# Security and Testing Agents - User Guide

## Overview

Project-AI now includes four advanced security and testing agents that integrate with the Triumvirate governance system. These agents provide long-context support, safety moderation, jailbreak testing, and adversarial red-teaming capabilities.

## Available Agents

### 1. LongContextAgent

**Purpose**: Handle extended conversations and large document analysis with 200k+ token context windows.

**Based on**: Nous-Capybara-34B-200k architecture

**Key Features**:

- Extended context support (up to 200k tokens)
- Large document analysis
- Context compression and management
- Multi-document reasoning

**Use Cases**:

- Extended conversation history analysis
- Large policy document processing
- Knowledge base consultation
- Multi-document synthesis

### 2. SafetyGuardAgent

**Purpose**: Content moderation and jailbreak detection using Llama-Guard-3-8B.

**Key Features**:

- Pre-processing prompt filtering
- Post-processing response filtering
- Jailbreak attempt detection
- Harmful content filtering
- Data leak prevention
- Manipulation pattern detection

**Use Cases**:

- Input validation before LLM processing
- Output validation before user display
- Real-time safety monitoring
- Abuse prevention

### 3. JailbreakBenchAgent

**Purpose**: Systematic jailbreak testing using standardized benchmarks.

**Key Features**:

- Standardized attack scenarios
- Defense strength evaluation
- Attack category coverage
- Comprehensive reporting

**Use Cases**:

- Regular security testing
- Defense capability assessment
- Vulnerability discovery
- Compliance validation

### 4. RedTeamAgent

**Purpose**: Automated adversarial testing using ARTKIT framework.

**Key Features**:

- Multi-turn attack conversations
- Adaptive strategy selection
- Vulnerability discovery
- Session-based testing

**Use Cases**:

- Adversarial testing
- Agent vulnerability analysis
- Security posture assessment
- Red team exercises

## Quick Start

### Installation

1. **Environment Setup**

Create or update your `.env` file:

```bash

# Long-Context Model Configuration

LONG_CONTEXT_API_ENDPOINT=https://api.example.com/v1/long-context
LONG_CONTEXT_API_KEY=your_api_key_here

# Safety Model Configuration

SAFETY_MODEL_API_ENDPOINT=https://api.example.com/v1/safety
SAFETY_MODEL_API_KEY=your_api_key_here
```

1. **Agent Access via CouncilHub**

All agents are automatically registered with the CouncilHub when you initialize Project-AI:

```python
from app.core.council_hub import CouncilHub
from app.core.cognition_kernel import CognitionKernel

# Initialize with governance

kernel = CognitionKernel()
hub = CouncilHub(kernel=kernel)
hub.register_project("Project-AI")

# Agents are now available

agents = hub.list_agents()

# ['curator', 'qa_generator', ..., 'long_context', 'safety_guard',

#  'jailbreak_bench', 'red_team']

```

## Usage Examples

### Example 1: Long-Context Conversation

```python
from app.agents.long_context_agent import LongContextAgent
from app.core.cognition_kernel import CognitionKernel

kernel = CognitionKernel()
agent = LongContextAgent(
    max_context_tokens=200000,
    kernel=kernel
)

# Process extended conversation

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Let's discuss AI safety..."},

    # ... many more messages ...

]

result = agent.process_long_conversation(
    messages=messages,
    max_tokens=4096
)

if result["success"]:
    print(f"Response: {result['response']}")
    print(f"Tokens used: {result['estimated_tokens']}")
```

### Example 2: Safety Filtering

```python
from app.agents.safety_guard_agent import SafetyGuardAgent

agent = SafetyGuardAgent(
    strict_mode=True,  # Fewer false negatives
    kernel=kernel
)

# Pre-process user input

prompt = "User's potentially unsafe prompt"
safety_check = agent.check_prompt_safety(prompt)

if safety_check["is_safe"]:

    # Process with main LLM

    response = main_llm.generate(prompt)

    # Post-process LLM output

    response_check = agent.check_response_safety(response)

    if response_check["is_safe"]:
        return response
    else:
        return "Response blocked for safety reasons."
else:
    print(f"Blocked: {safety_check['violation_type']}")
    return "Prompt violates safety guidelines."

# View statistics

stats = agent.get_safety_statistics()
print(f"Violation rate: {stats['violation_rate']:.2%}")
```

### Example 3: Jailbreak Testing

```python
from app.agents.jailbreak_bench_agent import JailbreakBenchAgent

agent = JailbreakBenchAgent(
    data_dir="data/jailbreak_tests",
    kernel=kernel
)

# Define a target system to test

class MyAISystem:
    def process(self, prompt):

        # Your AI system's processing logic

        return {"output": "Response..."}

target = MyAISystem()

# Run benchmark

results = agent.run_benchmark(
    target_system=target,
    categories=["prompt_injection", "role_play"],
    max_tests=50
)

print(f"Tests run: {results['total_tests']}")
print(f"Pass rate: {results['pass_rate']:.2%}")

# Evaluate defense strength

evaluation = agent.evaluate_defense()
print(f"Defense strength: {evaluation['overall_strength']}")

# Generate report

report = agent.generate_report(
    output_file="jailbreak_report_2026.json"
)
```

### Example 4: Red Team Session

```python
from app.agents.red_team_agent import RedTeamAgent, AttackStrategy

agent = RedTeamAgent(
    data_dir="data/red_team_sessions",
    max_turns=10,
    kernel=kernel
)

# Run adversarial session

session = agent.run_adversarial_session(
    target_system=target,
    strategy=AttackStrategy.GRADUAL_ESCALATION.value,
    initial_prompt="Hello, I need your help with something."
)

print(f"Session ID: {session['session_id']}")
print(f"Turns: {session['total_turns']}")
print(f"Vulnerabilities: {session['vulnerabilities_found']}")

# Analyze findings

analysis = agent.analyze_vulnerabilities()
print(f"Total vulnerabilities: {analysis['total_vulnerabilities']}")
for vuln_type, data in analysis['vulnerability_breakdown'].items():
    print(f"  {vuln_type}: {data['count']}")

# Generate comprehensive report

report = agent.generate_comprehensive_report(
    output_file="red_team_report_2026.json"
)
```

## Integration with Triumvirate

All agents are designed to work with the Triumvirate governance system:

```python
from app.core.governance import Triumvirate, GovernanceContext

triumvirate = Triumvirate()

# Before running red team test

context = GovernanceContext(
    is_abusive=False,
    high_risk=True,  # Red teaming is high risk
    fully_clarified=True,
    affects_identity=False,
    user_consent=True,
    requires_approval=True,
)

decision = triumvirate.evaluate_action(
    action="Run red team adversarial testing",
    context=context
)

if decision.allowed:

    # Proceed with testing

    session = red_team_agent.run_adversarial_session(target)
else:
    print(f"Blocked by governance: {decision.reason}")
```

## Best Practices

### Security Testing Schedule

1. **Daily**: SafetyGuard monitoring on all user interactions
1. **Weekly**: JailbreakBench automated tests
1. **Monthly**: Red team adversarial sessions
1. **Quarterly**: Comprehensive security review

### Configuration Recommendations

**Development**:

```python

# More lenient for testing

safety_guard = SafetyGuardAgent(strict_mode=False)
red_team = RedTeamAgent(max_turns=5)
```

**Production**:

```python

# Strict filtering

safety_guard = SafetyGuardAgent(strict_mode=True)
red_team = RedTeamAgent(max_turns=10)
```

### Monitoring and Alerts

```python

# Set up monitoring

stats = safety_guard.get_safety_statistics()

if stats['violation_rate'] > 0.1:  # 10% violations
    send_alert("High violation rate detected")

if stats['jailbreak_rate'] > 0.05:  # 5% jailbreaks
    send_alert("Jailbreak attempts increasing")
```

## Performance Considerations

### LongContextAgent

- **Context window**: Up to 200k tokens
- **Latency**: Scales with context size
- **Memory**: ~4-8GB for full context
- **Recommendation**: Use context compression for efficiency

### SafetyGuardAgent

- **Latency**: \<100ms per check
- **Memory**: ~2GB for model
- **Recommendation**: Cache common patterns

### JailbreakBenchAgent

- **Test time**: 1-5 seconds per test
- **Total benchmark**: 5-10 minutes for 50 tests
- **Recommendation**: Run during off-peak hours

### RedTeamAgent

- **Session time**: 30-300 seconds (depends on turns)
- **Memory**: Minimal (\<1GB)
- **Recommendation**: Parallelize multiple sessions

## Troubleshooting

### Agent Not Responding

```python

# Check agent status

print(agent.get_context_stats())  # LongContextAgent
print(agent.get_safety_statistics())  # SafetyGuardAgent
```

### High False Positive Rate

```python

# Adjust sensitivity

safety_guard = SafetyGuardAgent(strict_mode=False)
```

### Tests Failing

```python

# Check target system integration

class TestTarget:
    def process(self, prompt):
        print(f"Received: {prompt}")
        return {"output": "Response"}

# Verify with simple test

result = jailbreak_bench.run_benchmark(TestTarget(), max_tests=1)
print(result)
```

## API Reference

See individual agent files for detailed API documentation:

- `src/app/agents/long_context_agent.py`
- `src/app/agents/safety_guard_agent.py`
- `src/app/agents/jailbreak_bench_agent.py`
- `src/app/agents/red_team_agent.py`

## Support

For issues or questions:

1. Check logs in `logs/` directory
1. Review TRIUMVIRATE_INTEGRATION.md
1. See examples in `examples/` directory
1. File an issue on GitHub

## Version History

- **v1.0.0** (January 2026): Initial release
  - LongContextAgent with 200k context
  - SafetyGuardAgent with Llama-Guard-3-8B
  - JailbreakBenchAgent with standardized tests
  - RedTeamAgent with ARTKIT framework
