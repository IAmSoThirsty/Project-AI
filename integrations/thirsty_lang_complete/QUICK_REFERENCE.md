# Thirsty-lang Complete - Quick Reference

**Version:** 2.0.0 | **Last Updated:** 2026-01-28

---

## Installation

```bash
# Clone/copy integration package
cp -r integrations/thirsty_lang_complete /path/to/thirsty-lang/

# Or use automated script
cd integrations/thirsty_lang_complete
./copy_to_thirsty_lang.sh /path/to/thirsty-lang-repo

# Install dependencies
npm install
pip install -r requirements.txt
```

---

## Basic Usage

### JavaScript

```javascript
const { ThirstyInterpreter } = require('./src/secure-interpreter');

const interpreter = new ThirstyInterpreter({ security: true });

const code = `
shield myApp {
  drink name = "World"
  pour "Hello, " + name
}
`;

interpreter.execute(code);
```

### Python

```python
from thirsty_interpreter import ThirstyInterpreter

interpreter = ThirstyInterpreter(security=True)

code = """
shield myApp {
  drink name = "World"
  pour "Hello, " + name
}
"""

interpreter.execute(code)
```

---

## Language Syntax

### Variables
```thirsty
drink name = "value"        // Variable declaration
name = "new value"          // Reassignment
```

### Output
```thirsty
pour "Hello, World!"        // Print to console
pour variable               // Print variable
```

### Input
```thirsty
drink input = sip "Enter name: "
```

### Conditionals
```thirsty
thirsty condition {
  // If block
} hydrated {
  // Else block
}
```

### Loops
```thirsty
refill count < 10 {
  pour count
  count = count + 1
}
```

### Functions
```thirsty
glass greet(name) {
  pour "Hello, " + name
}

greet("World")
```

---

## Security Features

### Basic Protection
```thirsty
shield myApp {
  // Protected code block
  drink data = sip "Enter data: "
  pour data
}
```

### Threat Detection
```thirsty
detect attacks {
  morph on: ["injection", "overflow", "timing"]
  defend with: "aggressive"
}
```

### Input Sanitization
```thirsty
drink userData = sip "Enter name: "
sanitize userData              // Remove dangerous characters
armor userData                 // Protect from tampering
```

### TARL Policy Enforcement
```thirsty
tarl_policy {
  mutation_allowed: false
  unknown_agent_action: "escalate"
  threat_level: "high"
}
```

---

## TARL Runtime (Python)

### Basic Usage

```python
from tarl import TARLRuntime
from tarl.policies.default import DEFAULT_POLICIES

runtime = TARLRuntime(DEFAULT_POLICIES)

context = {
    "agent": "user_123",
    "mutation": False,
    "mutation_allowed": False
}

decision = runtime.evaluate(context)
print(decision.verdict)  # TarlVerdict.ALLOW
```

### Custom Policy

```python
from tarl.policy import TarlPolicy
from tarl.spec import TarlDecision, TarlVerdict

def rate_limit_policy(ctx):
    if ctx.get("requests_per_minute", 0) > 100:
        return TarlDecision(
            verdict=TarlVerdict.DENY,
            reason="Rate limit exceeded"
        )
    return TarlDecision(TarlVerdict.ALLOW, "OK")

policy = TarlPolicy("rate_limit", rate_limit_policy)
```

---

## Bridge Integration

### JavaScript + TARL

```javascript
const { TARLBridge } = require('./bridge/tarl-bridge');

const bridge = new TARLBridge();
await bridge.initialize();

const decision = await bridge.evaluatePolicy({
  agent: 'user_123',
  mutation: false
});

console.log(decision.verdict);  // 'ALLOW'
```

### Python Unified Security

```python
from bridge.unified_security import UnifiedSecurityManager

manager = UnifiedSecurityManager()
await manager.initialize()

context = {
    "agent": "user_123",
    "mutation": False,
    "code": "drink x = 5"
}

result = await manager.evaluate_unified(context)
print(result['allowed'])  # True/False
```

---

## Configuration

### Environment Variables

```bash
# Thirsty-lang
export THIRSTY_SECURITY_MODE=aggressive
export THIRSTY_ENABLE_TARL=true

# TARL
export TARL_ENABLED=1
export TARL_RUNTIME_ENABLE_JIT=true
export CODEX_ESCALATION_ENABLED=1
```

### Config Files

**tarl/config/tarl.toml**
```toml
[runtime]
enable_jit = true
stack_size = 1048576

[security]
enable_sandbox = true
max_execution_time = 30.0
```

**thirsty.config.json**
```json
{
  "securityMode": "aggressive",
  "enableMorphing": true,
  "enableTARL": true,
  "tarlContext": {
    "agent": "default_user",
    "mutation_allowed": false
  }
}
```

---

## Development Tools

### REPL

```bash
# JavaScript REPL
npm run repl

# Python REPL
python src/thirsty_repl.py
```

### Debugger

```bash
npm run debug examples/hello.thirsty
```

### Profiler

```bash
npm run profile examples/hello.thirsty
```

### Linter

```bash
npm run lint examples/hello.thirsty
```

### Formatter

```bash
npm run format examples/hello.thirsty
```

### Transpiler

```bash
node src/transpiler.js examples/hello.thirsty --target python
node src/transpiler.js examples/hello.thirsty --target go
```

---

## Testing

```bash
# Thirsty-lang tests
npm test

# TARL tests
pytest tarl/tests/ -v

# Integration tests
python test_integration.py

# Security tests
node src/test/security-tests.js

# Fuzz tests
python -m tarl.fuzz.fuzz_tarl
```

---

## Common Patterns

### Secure User Input

```thirsty
shield inputHandler {
  detect attacks { defend with: "aggressive" }
  
  drink userInput = sip "Enter data: "
  sanitize userInput
  armor userInput
  
  thirsty userInput != "" {
    pour "You entered: " + userInput
  } hydrated {
    pour "No input received"
  }
}
```

### Authenticated Operations

```javascript
const { UnifiedSecurityManager } = require('./bridge/unified-security');

const manager = new UnifiedSecurityManager();
await manager.initialize();

const context = {
  agent: "admin_user",
  mutation: true,
  mutation_allowed: true,
  code: "drink x = 5"
};

const result = await manager.evaluateUnified(context);
if (result.allowed) {
  // Execute protected operation
}
```

### Error Handling

```javascript
const { ThirstyInterpreter } = require('./src/secure-interpreter');
const { TARLBridge } = require('./bridge/tarl-bridge');

const bridge = new TARLBridge();
const interpreter = new ThirstyInterpreter({
  security: true,
  tarlBridge: bridge
});

try {
  const result = await interpreter.execute(code);
  console.log('Success:', result);
} catch (error) {
  if (error.name === 'SecurityError') {
    console.error('Security violation:', error.message);
  } else if (error.name === 'TARLEnforcementError') {
    console.error('TARL blocked:', error.message);
  } else {
    console.error('Runtime error:', error);
  }
}
```

---

## Performance Tips

1. **Enable JIT Compilation**
   ```bash
   export TARL_RUNTIME_ENABLE_JIT=true
   ```

2. **Use Code Caching**
   ```javascript
   const interpreter = new ThirstyInterpreter({
     cache: true,
     cacheDir: './cache'
   });
   ```

3. **Optimize Policy Checks**
   ```python
   # Use cached decisions
   runtime = TARLRuntime(DEFAULT_POLICIES, cache_size=1000)
   ```

4. **Reduce Security Overhead**
   ```thirsty
   // Only use security where needed
   shield criticalSection {
     // Protected code
   }
   
   // Regular code (no overhead)
   drink x = 5
   pour x
   ```

---

## Troubleshooting

### Issue: TARL not starting

```bash
# Check Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/thirsty-lang"

# Verify TARL installation
python -c "import tarl; print(tarl.__version__)"
```

### Issue: Bridge connection failed

```bash
# Test bridge manually
node bridge/tarl-bridge.js test

# Check Python dependencies
pip install -r requirements.txt
```

### Issue: Security tests failing

```bash
# Run with verbose output
npm test -- --verbose
pytest tarl/tests/ -v -s
```

---

## API Quick Reference

### Thirsty-lang (JavaScript)

```javascript
const interpreter = new ThirstyInterpreter(options)
interpreter.execute(code)
interpreter.executeFile(path)
interpreter.evaluate(expression)
interpreter.reset()
```

### TARL (Python)

```python
runtime = TARLRuntime(policies)
decision = runtime.evaluate(context)
runtime.add_policy(policy)
runtime.remove_policy(name)
```

### Bridge (JavaScript)

```javascript
bridge = new TARLBridge()
await bridge.initialize()
decision = await bridge.evaluatePolicy(context)
await bridge.shutdown()
```

---

## Resources

- **Full Documentation**: `INTEGRATION_COMPLETE.md`
- **Migration Guide**: `MIGRATION_CHECKLIST.md`
- **Features List**: `FEATURES.md`
- **Bridge Docs**: `bridge/README.md`
- **Language Spec**: `../src/thirsty_lang/docs/SPECIFICATION.md`
- **TARL Docs**: `../tarl/docs/ARCHITECTURE.md`

---

## Support

- **Issues**: https://github.com/IAmSoThirsty/Thirsty-lang/issues
- **Project-AI**: https://github.com/IAmSoThirsty/Project-AI
- **Documentation**: https://iamsothirsty.github.io/Thirsty-lang

---

**Built with ❤️ for defensive programming**

Stay hydrated and secure! 💧🔒
