<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / SECURITY_API.md # -->
<!-- # ============================================================================ # -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / SECURITY_API.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
# Thirsty-lang Security API Reference

## Core Modules

### SecurityManager

Main security interface with T.A.R.L. integration.

#### Constructor

```javascript
new SecurityManager(options)
```

**Options**:

- `enabled` (boolean): Enable security features (default: true)
- `mode` (string): Security mode - 'defensive', 'strict', 'permissive' (default: 'defensive')
- `useTarl` (boolean): Enable T.A.R.L. integration (default: true)

#### Methods

##### `async initialize()`

Initialize T.A.R.L. runtime and security bridge.

**Returns**: `Promise<void>`

**Throws**: Error if initialization fails

**Example**:
```javascript
const security = new SecurityManager();
await security.initialize();
```

##### `secureInput(input, context)`

Sanitize input using HTML encoding.

**Parameters**:

- `input` (string): Input to sanitize
- `context` (object): Optional context information

**Returns**: Object with `original`, `sanitized`, and `modified` properties

**Example**:
```javascript
const result = security.secureInput('<script>alert("xss")</script>');
console.log(result.sanitized); // &lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;
```

##### `async detectThreats(input, context)`

Detect security threats in input.

**Parameters**:

- `input` (string): Input to analyze
- `context` (object): Context for threat detection

**Returns**: `Promise<ThreatResult>`

**ThreatResult**:
```typescript
{
  detected: boolean,
  threats: Array<{
    type: string,
    severity: 'low' | 'medium' | 'high' | 'critical',
    pattern: string,
    input: string
  }>,
  action: 'allow' | 'warn' | 'blocked' | 'escalate',
  reason: string
}
```

**Example**:
```javascript
const result = await security.detectThreats(userInput, { source: 'form' });
if (result.detected) {
  console.log('Threats:', result.threats);
}
```

##### `async compileSecure(code, options)`

Compile code with defensive measures.

**Parameters**:

- `code` (string): Source code to compile
- `options` (object): Compilation options
  - `source` (string): Source identifier
  - `mode` (string): Compilation mode
  - `morph` (boolean): Enable code morphing (default: true)
  - `addGuards` (boolean): Add runtime guards (default: true)

**Returns**: `Promise<CompileResult>`

**CompileResult**:
```typescript
{
  code: string,
  original: string,
  threats: Array<Threat>,
  transformations: Array<string>,
  metrics: object
}
```

**Example**:
```javascript
const result = await security.compileSecure(code, {
  source: 'user',
  mode: 'production'
});
```

##### `async loadPolicies(policyPath)`

Load security policies from file.

**Parameters**:

- `policyPath` (string): Path to policy file (JSON or YAML)

**Returns**: `Promise<LoadResult>`

**LoadResult**:
```typescript
{
  loaded: number,
  policies: Array<string>
}
```

**Example**:
```javascript
await security.loadPolicies('./tarl/policies/default.json');
```

##### `async shutdown()`

Shutdown security bridge and cleanup resources.

**Returns**: `Promise<void>`

---

### SecurityBridge

Bi-directional bridge between JavaScript and Python T.A.R.L. runtime.

#### Constructor

```javascript
new SecurityBridge(options)
```

**Options**:

- `pythonPath` (string): Path to Python executable (default: 'python3')
- `tarlPath` (string): Path to T.A.R.L. directory

#### Methods

##### `async initialize()`

Start Python bridge server.

**Returns**: `Promise<void>`

**Throws**: Error if initialization fails or times out

##### `async evaluatePolicy(context)`

Evaluate policy against context.

**Parameters**:

- `context` (object): Evaluation context

**Returns**: `Promise<PolicyDecision>`

**PolicyDecision**:
```typescript
{
  verdict: 'allow' | 'deny' | 'escalate',
  reason: string,
  metadata?: object
}
```

**Example**:
```javascript
const decision = await bridge.evaluatePolicy({
  action: 'compile',
  mode: 'production'
});
if (decision.verdict === 'deny') {
  throw new Error(decision.reason);
}
```

##### `async loadPolicies(policyPath)`

Load policies into T.A.R.L. runtime.

**Returns**: `Promise<object>`

##### `async reloadPolicies()`

Reload policies from previously loaded path.

**Returns**: `Promise<object>`

##### `async getRuntimeMetrics()`

Get T.A.R.L. runtime performance metrics.

**Returns**: `Promise<RuntimeMetrics>`

**RuntimeMetrics**:
```typescript
{
  total_evaluations: number,
  cache_enabled: boolean,
  cache_hit_rate_percent: number,
  productivity_improvement_percent: number,
  policy_stats: object
}
```

##### `getBridgeMetrics()`

Get bridge communication metrics.

**Returns**: `BridgeMetrics`

**BridgeMetrics**:
```typescript
{
  requests: number,
  successes: number,
  failures: number,
  avgResponseTime: number
}
```

---

### ThreatDetector

Advanced threat detection with pattern matching.

#### Constructor

```javascript
new ThreatDetector(securityBridge)
```

#### Methods

##### `async detect(input, context)`

Detect threats in input.

**Parameters**:

- `input` (string): Input to analyze
- `context` (object): Detection context

**Returns**: `Promise<ThreatResult>`

##### `addPattern(threatType, pattern)`

Add custom threat pattern.

**Parameters**:

- `threatType` (string): Type of threat
- `pattern` (RegExp): Pattern to match

**Example**:
```javascript
detector.addPattern('customThreat', /malicious_pattern/gi);
```

##### `getMetrics()`

Get detection metrics.

**Returns**: `DetectionMetrics`

```typescript
{
  threatsDetected: number,
  falsePositives: number,
  policyEnforced: number
}
```

---

### CodeMorpher

Dynamic code transformation for defense.

#### Constructor

```javascript
new CodeMorpher(securityBridge)
```

#### Methods

##### `async morph(code, context)`

Transform code using configured strategies.

**Parameters**:

- `code` (string): Code to morph
- `context` (object): Morphing context

**Returns**: `Promise<MorphResult>`

**MorphResult**:
```typescript
{
  code: string,
  original: string,
  transformations: Array<string>,
  metrics: object
}
```

##### `setStrategy(strategy, enabled)`

Configure morphing strategy.

**Parameters**:

- `strategy` (string): Strategy name ('rename', 'shuffle', 'obfuscate', 'encrypt')
- `enabled` (boolean): Enable or disable strategy

**Example**:
```javascript
morpher.setStrategy('obfuscate', true);
morpher.setStrategy('rename', false);
```

---

### DefenseCompiler

Compile code with defensive transformations.

#### Constructor

```javascript
new DefenseCompiler(securityBridge)
```

#### Methods

##### `async compile(code, options)`

Compile with defensive measures.

**Parameters**:

- `code` (string): Source code
- `options` (object): Compilation options

**Returns**: `Promise<CompileResult>`

##### `getMetrics()`

Get compilation metrics.

**Returns**: `CompilerMetrics`

```typescript
{
  compilations: number,
  threatsBlocked: number,
  transformations: number,
  threatDetector: object,
  codeMorpher: object
}
```

---

### PolicyEngine

Manage and enforce security policies.

#### Constructor

```javascript
new PolicyEngine(securityBridge)
```

#### Methods

##### `async loadPolicies(policyPath)`

Load policies from file.

**Returns**: `Promise<LoadResult>`

##### `enableHotReload()`

Enable automatic policy reloading on file changes.

**Example**:
```javascript
policyEngine.enableHotReload();
policyEngine.on('policies_reloaded', () => {
  console.log('Policies updated!');
});
```

##### `disableHotReload()`

Disable automatic policy reloading.

##### `async reloadPolicies()`

Manually reload policies from disk.

**Returns**: `Promise<LoadResult>`

##### `async evaluate(action, context)`

Evaluate action against loaded policies.

**Parameters**:

- `action` (string): Action to evaluate
- `context` (object): Evaluation context

**Returns**: `Promise<PolicyDecision>`

##### `getPolicies()`

Get all loaded policies.

**Returns**: `Array<Policy>`

##### `getMetrics()`

Get policy engine metrics.

**Returns**: `PolicyMetrics`

```typescript
{
  policyEvaluations: number,
  policyReloads: number,
  lastReload: string
}
```

---

## Python T.A.R.L. API

### TarlRuntime

```python
from tarl import TarlRuntime, TarlPolicy, TarlDecision, TarlVerdict

# Create runtime with policies

policies = [
    TarlPolicy("policy_name", lambda ctx: TarlDecision(
        TarlVerdict.ALLOW,
        "reason"
    ))
]

runtime = TarlRuntime(
    policies,
    enable_cache=True,
    enable_parallel=True,
    cache_size=128
)

# Evaluate

decision = runtime.evaluate({"action": "compile"})

# Get metrics

metrics = runtime.get_performance_metrics()
```

### TarlPolicy

```python
from tarl import TarlPolicy, TarlDecision, TarlVerdict

def policy_rule(context):
    if context.get("action") == "dangerous":
        return TarlDecision(TarlVerdict.DENY, "Dangerous action")
    return TarlDecision(TarlVerdict.ALLOW, "Safe")

policy = TarlPolicy("my_policy", policy_rule)
```

### TarlDecision & TarlVerdict

```python
from tarl import TarlDecision, TarlVerdict

# Create decision

decision = TarlDecision(
    TarlVerdict.ALLOW,
    "Operation permitted",
    metadata={"user": "admin"}
)

# Check if terminal

if decision.is_terminal():
    print("Decision terminates evaluation")
```

---

## Events

### PolicyEngine Events

- `policies_loaded`: Fired when policies are loaded

  ```javascript
  policyEngine.on('policies_loaded', ({ count, path }) => {
    console.log(`Loaded ${count} policies from ${path}`);
  });
  ```

- `policies_reloaded`: Fired when policies are hot-reloaded

  ```javascript
  policyEngine.on('policies_reloaded', () => {
    console.log('Policies updated');
  });
  ```

- `reload_error`: Fired when hot-reload fails

  ```javascript
  policyEngine.on('reload_error', (error) => {
    console.error('Reload failed:', error);
  });
  ```

### SecurityBridge Events

- `disconnected`: Fired when Python bridge disconnects

  ```javascript
  bridge.on('disconnected', (code) => {
    console.error('Bridge disconnected with code', code);
  });
  ```

---

## Type Definitions

For TypeScript users, type definitions are available:

```typescript
interface SecurityManager {
  initialize(): Promise<void>;
  secureInput(input: string, context?: object): object;
  detectThreats(input: string, context?: object): Promise<ThreatResult>;
  compileSecure(code: string, options?: CompileOptions): Promise<CompileResult>;
  loadPolicies(policyPath: string): Promise<LoadResult>;
  shutdown(): Promise<void>;
}

interface ThreatResult {
  detected: boolean;
  threats: Threat[];
  action: 'allow' | 'warn' | 'blocked' | 'escalate';
  reason: string;
}

interface Threat {
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  pattern: string;
  input: string;
}

interface CompileOptions {
  source?: string;
  mode?: string;
  morph?: boolean;
  addGuards?: boolean;
}

interface CompileResult {
  code: string;
  original: string;
  threats: Threat[];
  transformations: string[];
  metrics: object;
}

interface PolicyDecision {
  verdict: 'allow' | 'deny' | 'escalate';
  reason: string;
  metadata?: object;
}
```

---

## Error Handling

All async methods may throw errors. Always use try-catch:

```javascript
try {
  await security.initialize();
  await security.loadPolicies('./policies.json');
  const result = await security.compileSecure(code);
} catch (err) {
  console.error('Security operation failed:', err.message);
  // Handle error
} finally {
  await security.shutdown();
}
```

## Performance Considerations

- **Bridge Overhead**: ~10-15ms per policy evaluation
- **Caching**: Reduces evaluation time by 40% for repeated contexts
- **Parallel Evaluation**: 15% improvement with multiple policies
- **Hot-Reload**: <1ms impact on normal operations

## See Also

- [T.A.R.L. Integration Guide](./TARL_INTEGRATION.md)
- [Policy Authoring Guide](./POLICY_AUTHORING.md)
- [Security Best Practices](./SECURITY_BEST_PRACTICES.md)
- [Project-AI Documentation](https://github.com/IAmSoThirsty/Project-AI)
