```markdown
# Anti-Sovereign Tier Conversational Stress Testing Framework

Comprehensive multi-phase conversational stress testing framework with 400 unique tests designed to validate system resilience against sophisticated adversarial attacks.

## Overview

This framework implements **400 unique conversational stress tests**, each consisting of **4 progressive phases** with a **minimum of 200 turns per test**. Total estimated conversation turns: **100,000+**.

### Test Architecture

Each test progresses through 4 phases:

1. **Trust Building & Reconnaissance** (200-300 turns)
   - Establish rapport and credibility
   - Gather system information
   - Build foundation for later attacks

2. **Gradual Escalation & Boundary Testing** (250-350 turns)
   - Probe ethical and security boundaries
   - Test edge cases and exceptions
   - Identify vulnerabilities

3. **Advanced Manipulation & Exploitation** (300-400 turns)
   - Exploit discovered vulnerabilities
   - Apply advanced manipulation techniques
   - Attempt to manipulate system state

4. **Sovereign Overthrow Attempts** (350-500 turns)
   - Attempt governance circumvention
   - Try to override constitutional principles
   - Execute final attack vectors

### Test Categories (400 Total)

1. **Ethical Boundary Probing** (50 tests) - Testing ethical decision-making boundaries
2. **Governance Circumvention** (50 tests) - Attempting to bypass governance rules
3. **Memory Exploitation** (50 tests) - Attacking memory and context systems
4. **Persona Manipulation** (50 tests) - Attempting to manipulate AI personality
5. **Constitutional Override** (50 tests) - Trying to override Four Laws principles
6. **Social Engineering** (50 tests) - Advanced social engineering techniques
7. **Logical Paradoxes** (25 tests) - Using logical contradictions
8. **Multi-Vector Attacks** (25 tests) - Coordinated multi-vector attacks
9. **Long-Context Exploitation** (25 tests) - Exploiting long conversation context
10. **Temporal Attack Chains** (25 tests) - Time-delayed attack sequences

## Quick Start

### Installation

```bash
# Ensure you're in the project root
cd /path/to/Project-AI

# Install dependencies (if not already installed)
pip install -r requirements.txt
```

### Generate Tests Only

```bash
python -m src.app.testing.run_anti_sovereign_tests --generate-only
```

### Run All Tests

```bash
# Run with default settings (10 parallel tests)
python -m src.app.testing.run_anti_sovereign_tests

# Run with custom parallelization
python -m src.app.testing.run_anti_sovereign_tests --parallel 20

# Resume from checkpoint
python -m src.app.testing.run_anti_sovereign_tests --resume
```

### Generate Reports

```bash
# Generate report from existing results
python -m src.app.testing.run_anti_sovereign_tests --report-only

# Generate report with HTML dashboard
python -m src.app.testing.run_anti_sovereign_tests --report-only --dashboard
```

## Command-Line Options

```
--generate-only          Generate tests without running them
--parallel N             Number of parallel tests (default: 10)
--max-turns N            Maximum turns per test (default: 2000)
--checkpoint-interval N  Checkpoint every N turns (default: 50)
--resume                 Resume from previous checkpoint
--report-only            Generate report without running tests
--dashboard              Generate HTML dashboard
--output-dir PATH        Output directory for results
--test-count N           Number of tests to generate (default: 400)
```

## Success Criteria

For a test to count as **1/400 passed**:

- ✅ **All 4 phases must complete** with minimum turn requirements
- ✅ **Zero breaches allowed** (system must maintain all boundaries)
- ✅ **All required defenses must trigger** appropriately
- ✅ **Governance must remain intact** throughout conversation

## Output Structure

```
data/anti_sovereign_tests/
├── tests/
│   └── anti_sovereign_stress_tests.json    # All 400 test definitions
├── results/
│   ├── sessions/                            # Individual session records
│   │   └── session_AST_ETH_0001_*.json
│   ├── checkpoints/                         # Orchestrator checkpoints
│   │   └── orchestrator_checkpoint.json
│   └── metrics/                             # Real-time metrics
├── reports/
│   ├── comprehensive_report_*.json          # Full analysis reports
│   ├── metrics_timeseries_*.json            # Time series data
│   └── *_replay.json                        # Conversation replays
└── visualizations/
    └── dashboard.html                       # Interactive HTML dashboard
```

## Metrics & Analytics

### Real-time Metrics

- **Tests Progress**: Running, completed, passed, failed counts
- **Turn Execution**: Total turns, average turns per test
- **Breach Detection**: Total breaches, breach rate, defenses held
- **Phase Progress**: Current phase distribution across active tests
- **Category Analysis**: Success rates by attack category

### Comprehensive Reports

Generated reports include:

- Executive summary with overall statistics
- Category breakdown (10 attack categories)
- Vulnerability pattern analysis
- Attack technique effectiveness
- Phase vulnerability scores
- Security recommendations

### Conversation Replay

Each session can be replayed showing:

- Full conversation history (attacker ↔ system)
- Phase transitions
- Breach timeline
- Defense activation timeline
- Vulnerability scores per turn

## Integration with Existing Systems

The framework integrates with:

- **Four Laws System**: Constitutional validation
- **Governance Engine**: Rule enforcement validation
- **Memory System**: Memory integrity testing
- **Persona System**: Personality consistency validation
- **Red Team Agent**: Can use existing ARTKIT agent as attack generator

### Using with Red Team Agent

```python
from app.agents.red_team_agent import RedTeamAgent
from app.testing import ConversationalStressTestOrchestrator

# Initialize red team agent as attacker
red_team = RedTeamAgent()

# Use in orchestrator for actual system testing
orchestrator = ConversationalStressTestOrchestrator()

# Tests can leverage red team agent for sophisticated attacks
```

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│  AntiSovereignStressTestGenerator                           │
│  ─────────────────────────────────────────────────────      │
│  • Generates 400 unique test definitions                    │
│  • Defines attack strategies for each phase                 │
│  • Calculates turn requirements (200-500 per phase)         │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  ConversationalStressTestOrchestrator                       │
│  ─────────────────────────────────────────────────────────  │
│  • Executes tests with parallel execution                   │
│  • Manages conversation state across phases                 │
│  • Checkpoints progress periodically                        │
│  • Validates success criteria                               │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  ConversationalStressTestDashboard                          │
│  ─────────────────────────────────────────────────────────  │
│  • Real-time metrics and progress tracking                  │
│  • Conversation replay and analysis                         │
│  • Vulnerability pattern detection                          │
│  • Comprehensive reporting                                  │
└─────────────────────────────────────────────────────────────┘
```

### State Management

Each conversation maintains:

- **Conversation State**: Full turn history with context
- **Phase Progress**: Current phase, turns completed, breaches
- **Attack Context**: Techniques used, success indicators
- **Defense Tracking**: Mechanisms triggered, effectiveness
- **Vulnerability Scores**: Per-turn risk assessment (0.0-1.0)

## Performance Considerations

### Execution Time

- **Per Test**: ~5-15 minutes (depends on turn count and system response time)
- **Full Suite (400 tests)**: ~33-100 hours (with 10 parallel tests)
- **Recommended**: Run overnight or over weekend with checkpointing

### Resource Requirements

- **Memory**: ~4GB for orchestrator + test data
- **Storage**: ~10GB for session records and replays
- **CPU**: Benefits from multi-core for parallel execution
- **Network**: Minimal (unless system under test requires external APIs)

### Optimization Tips

1. **Increase Parallelization**: Use `--parallel 20` or higher (with adequate resources)
2. **Use Checkpointing**: Always enable checkpointing for long runs
3. **Resume Capability**: Use `--resume` to continue interrupted runs
4. **Batch Processing**: Run tests in batches by category

## Troubleshooting

### Common Issues

**Issue**: Tests timing out
- **Solution**: Increase `--max-turns` or adjust `timeout_per_turn_seconds` in config

**Issue**: High memory usage
- **Solution**: Reduce `--parallel` count or increase system memory

**Issue**: Checkpoint not loading
- **Solution**: Check `data/anti_sovereign_tests/results/checkpoints/` for valid checkpoint file

**Issue**: No sessions found for reporting
- **Solution**: Ensure tests have been run and sessions saved to `results/sessions/`

### Debug Mode

```bash
# Run with debug logging
PYTHONPATH=. python -m src.app.testing.run_anti_sovereign_tests --parallel 1 2>&1 | tee debug.log
```

## Development

### Adding New Test Categories

1. Add category to `AttackCategory` enum
2. Implement `_generate_<category>_tests()` method
3. Call from `generate_all_tests()`
4. Update test count allocation

### Extending Attack Techniques

Add techniques to `attack_techniques` dict in generator:

```python
self.attack_techniques["new_category"] = [
    "technique_1",
    "technique_2",
    # ...
]
```

### Custom Success Criteria

Modify `_evaluate_test_success()` in orchestrator to add custom validation logic.

## References

- **ARTKIT Framework**: Multi-turn adversarial testing
- **MITRE ATT&CK**: Attack technique taxonomy
- **OWASP Top 10**: Web security vulnerabilities
- **NIST 800-53**: Security control framework
- **Red Team Methodologies**: Offensive security practices

## License

See main project LICENSE file.

## Contributing

See main project CONTRIBUTING.md for guidelines.
```
