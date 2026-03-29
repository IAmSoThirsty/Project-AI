<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / TARL_INTEGRATION.md # -->
<!-- # ============================================================================ # -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / TARL_INTEGRATION.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
# T.A.R.L. Integration Guide

## Overview

Thirsty-lang now integrates with T.A.R.L. (Thirsty's Active Resistance Language) runtime from Project-AI, providing production-grade security enforcement, policy management, and threat detection.

## Architecture

### Dual Runtime

Thirsty-lang operates with a dual runtime architecture:

1. **JavaScript/Node.js Runtime**: Primary interpreter for Thirsty-lang code
2. **Python T.A.R.L. Runtime**: Policy enforcement and security core

These runtimes communicate via a **Security Bridge** that provides bi-directional, async communication.

```
┌──────────────────────────────────────────┐
│     JavaScript/Node.js Runtime           │
│  ┌────────────────────────────────────┐  │
│  │  Thirsty-lang Interpreter          │  │
│  │  - Parser                          │  │
│  │  - Evaluator                       │  │
│  │  - Security Manager                │  │
│  └────────────┬───────────────────────┘  │
│               │                           │
│  ┌────────────▼───────────────────────┐  │
│  │  Security Bridge                   │  │
│  │  - Async communication             │  │
│  │  - Metrics tracking                │  │
│  │  - Error propagation               │  │
│  └────────────┬───────────────────────┘  │
└───────────────┼───────────────────────────┘
                │ JSON over stdio
┌───────────────▼───────────────────────────┐
│     Python T.A.R.L. Runtime               │
│  ┌────────────────────────────────────┐  │
│  │  Policy Engine                     │  │
│  │  - Policy evaluation               │  │
│  │  - Decision caching                │  │
│  │  - Performance optimization        │  │
│  └────────────────────────────────────┘  │
│                                           │
│  Security Modules:                        │
│  - Threat Detection                       │
│  - Code Morphing                          │
│  - Defense Compilation                    │
│  - Audit Logging                          │
└───────────────────────────────────────────┘
```

## Quick Start

### Installation

```bash

# Install dependencies

npm install

# Install Python requirements

pip install pyyaml  # For YAML policy support
```

### Basic Usage

```javascript
const { SecurityManager } = require('./src/security');

// Create security manager with T.A.R.L. integration
const security = new SecurityManager({ useTarl: true });

// Initialize (starts Python bridge)
await security.initialize();

// Load policies
await security.loadPolicies('./tarl/policies/default.json');

// Detect threats
const threatResult = await security.detectThreats(userInput);
if (threatResult.detected) {
  console.log('Threats found:', threatResult.threats);
}

// Compile with defensive measures
const compiled = await security.compileSecure(code);

// Shutdown when done
await security.shutdown();
```

### Using the Interpreter with Security

```javascript
const ThirstyInterpreter = require('./src/index');
const { SecurityManager } = require('./src/security');

// Create interpreter with enhanced security
const security = new SecurityManager({ useTarl: true });
await security.initialize();
await security.loadPolicies('./tarl/policies/default.json');

const interpreter = new ThirstyInterpreter({ security });

// Execute code
interpreter.run(code);
```

## Security Modules

### 1. Threat Detector

Detects security threats using pattern matching and policy evaluation.

```javascript
const { ThreatDetector } = require('./src/security/threat-detector');

const detector = new ThreatDetector(securityBridge);

// Detect threats
const result = await detector.detect(input, { source: 'user' });

if (result.detected) {
  console.log('Threats:', result.threats);
  console.log('Action:', result.action); // 'allow', 'warn', 'blocked', 'escalate'
}
```

**Threat Types**:

- XSS (Cross-Site Scripting)
- SQL Injection
- Command Injection
- Path Traversal

### 2. Code Morpher

Transforms code for security through obfuscation and mutation.

```javascript
const { CodeMorpher } = require('./src/security/code-morpher');

const morpher = new CodeMorpher(securityBridge);

// Configure strategies
morpher.setStrategy('obfuscate', true);
morpher.setStrategy('rename', true);

// Morph code
const result = await morpher.morph(code);
console.log('Morphed code:', result.code);
```

**Strategies**:

- `rename`: Variable renaming
- `shuffle`: Statement reordering
- `obfuscate`: String obfuscation
- `encrypt`: Code encryption

### 3. Defense Compiler

Compiles code with defensive measures and security checks.

```javascript
const { DefenseCompiler } = require('./src/security/defense-compiler');

const compiler = new DefenseCompiler(securityBridge);

// Compile with options
const result = await compiler.compile(code, {
  source: 'user_input',
  mode: 'defensive',
  morph: true,
  addGuards: true
});

console.log('Compiled code:', result.code);
console.log('Threats blocked:', result.threats.length);
```

### 4. Policy Engine

Manages security policies with hot-reload support.

```javascript
const { PolicyEngine } = require('./src/security/policy-engine');

const policyEngine = new PolicyEngine(securityBridge);

// Load policies
await policyEngine.loadPolicies('./tarl/policies/default.json');

// Enable hot-reload
policyEngine.enableHotReload();

// Listen for reload events
policyEngine.on('policies_reloaded', () => {
  console.log('Policies updated');
});

// Evaluate policy
const decision = await policyEngine.evaluate('compile', {
  mode: 'production'
});
```

## Policy Authoring

### Policy File Format

Policies can be defined in JSON or YAML format.

#### JSON Format

```json
{
  "policies": [
    {
      "name": "threat_policy",
      "description": "Block detected threats",
      "rules": [
        {
          "condition": {
            "action": "threat_detected"
          },
          "verdict": "DENY",
          "reason": "Threats detected in input"
        }
      ]
    }
  ]
}
```

#### YAML Format

```yaml
policies:

  - name: threat_policy

    description: Block detected threats
    rules:

      - condition:

          action: threat_detected
        verdict: DENY
        reason: Threats detected in input
```

### Policy Verdicts

- `ALLOW`: Operation is permitted
- `DENY`: Operation is blocked
- `ESCALATE`: Operation requires additional review

### Policy Conditions

Conditions are key-value pairs that must match the evaluation context:

```json
{
  "condition": {
    "action": "compile",
    "mode": "production",
    "source": "external"
  },
  "verdict": "ESCALATE",
  "reason": "External code requires review"
}
```

## Hot-Reload

Policies support live reloading without restarting the application:

```javascript
// Enable hot-reload
policyEngine.enableHotReload();

// Edit policy file...
// Policies are automatically reloaded

// Or manually reload
await policyEngine.reloadPolicies();
```

## Metrics and Monitoring

### Bridge Metrics

```javascript
const metrics = bridge.getBridgeMetrics();
console.log(metrics);
// {
//   requests: 150,
//   successes: 148,
//   failures: 2,
//   avgResponseTime: 12.5
// }
```

### Runtime Metrics

```javascript
const metrics = await bridge.getRuntimeMetrics();
console.log(metrics);
// {
//   total_evaluations: 150,
//   cache_hit_rate_percent: 65.5,
//   productivity_improvement_percent: 45.2,
//   ...
// }
```

### Security Metrics

```javascript
const metrics = threatDetector.getMetrics();
console.log(metrics);
// {
//   threatsDetected: 25,
//   falsePositives: 3,
//   policyEnforced: 22
// }
```

## Configuration

T.A.R.L. configuration is in `tarl/config/tarl.toml`:

```toml
[security]
enable_sandbox = true
max_execution_time = 30.0
max_memory = 67108864  # 64MB
disable_file_io = false
disable_network_io = false

[compiler]
debug_mode = false
optimization_level = 2

[runtime]
stack_size = 1048576  # 1MB
enable_jit = true
```

Override with environment variables:

```bash
export TARL_SECURITY_MAX_EXECUTION_TIME=60.0
export TARL_COMPILER_DEBUG_MODE=true
```

## Testing

Run security integration tests:

```bash

# Bridge tests

node src/test/bridge-tests.js

# Security module tests

node src/test/security-integration-tests.js

# All tests

npm test
```

## Troubleshooting

### Bridge Fails to Initialize

**Problem**: `Bridge initialization timeout`

**Solution**: Ensure Python 3.8+ is installed and accessible:
```bash
python3 --version
which python3
```

### Policy Loading Fails

**Problem**: `Policy file not found`

**Solution**: Use absolute paths or verify relative paths:
```javascript
const path = require('path');
const policyPath = path.join(__dirname, 'tarl', 'policies', 'default.json');
```

### High Memory Usage

**Solution**: Adjust cache size in bridge initialization:
```javascript
const bridge = new SecurityBridge({
  cacheSize: 64  // Reduce from default 128
});
```

## Best Practices

1. **Initialize Once**: Create SecurityManager at application startup
2. **Shutdown Cleanly**: Always call `security.shutdown()` on exit
3. **Policy Versioning**: Version your policy files
4. **Metric Monitoring**: Track metrics in production
5. **Error Handling**: Always catch and handle policy errors
6. **Testing**: Test policy changes before deployment

## Examples

See `examples/security/` for complete examples:

- `basic-threat-detection.js`
- `policy-enforcement.js`
- `defensive-compilation.js`
- `hot-reload-demo.js`

## Project-AI Compatibility

This integration is fully compatible with Project-AI's T.A.R.L. runtime. Policy files can be shared between Thirsty-lang and Project-AI.

For more information, see the [Project-AI Documentation](https://github.com/IAmSoThirsty/Project-AI).

## License

See LICENSE file for details.
