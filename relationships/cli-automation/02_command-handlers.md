---
title: Command Handlers Relationships
description: Command routing, execution patterns, and handler architecture
tags:
  - relationships
  - command-handlers
  - routing
  - execution
created: 2025-02-08
agent: AGENT-063
---

# Command Handlers Relationships

## Overview

Command handlers form the **middle layer** between CLI interfaces and core business logic, providing routing, validation, and execution orchestration.

## 🎯 Handler Architecture

### Handler Pattern
```
CLI Entry Point
    ↓
Argument Parser (argparse/typer)
    ↓
Command Router (main function)
    ↓
Command Handler Function (cmd_*)
    ↓
Core Business Logic
    ↓
Output Formatter
    ↓
Exit Code Return
```

---

## 📋 Primary Command Handlers

### 1. Sovereign Runtime Handlers (`project_ai_cli.py`)

#### Handler: `cmd_run(args)`
**Purpose**: Execute sovereign governance pipeline

**Flow**:
```python
def cmd_run(args):
    1. Log execution start
    2. Create IronPathExecutor(pipeline_path=args.pipeline)
    3. Execute: result = executor.execute()
    4. Check result["status"]
       ├─ "completed" → Log success, show artifacts, exit(0)
       └─ "failed" → Log error, exit(1)
```

**Dependencies**:
- `governance.iron_path.IronPathExecutor`
- Pipeline YAML file

**Input**: `args.pipeline` (path to YAML)

**Output**:
- Execution artifacts
- Compliance bundle
- Exit code: 0/1

**Relationships**:
- **Calls**: `IronPathExecutor.execute()`
- **Generates**: Artifacts in `governance/sovereign_data/artifacts/`
- **Logs**: Structured execution logs

---

#### Handler: `cmd_sovereign_verify(args)`
**Purpose**: Comprehensive third-party verification

**Flow**:
```python
def cmd_sovereign_verify(args):
    1. Create SovereignVerifier(bundle_path=args.bundle)
    2. Run: report = verifier.verify()
    3. Display verification results
       ├─ Hash chain validation
       ├─ Signature authority mapping
       ├─ Policy resolution trace
       └─ Timestamped attestation
    4. Save report if --output specified
    5. Exit with status-based code (0/1/2)
```

**Dependencies**:
- `governance.sovereign_verifier.SovereignVerifier`

**Input**: 
- `args.bundle` (compliance bundle path)
- `args.output` (optional report path)

**Output**:
- Verification report (JSON)
- Exit code: 0 (pass), 1 (fail), 2 (warning)

**Relationships**:
- **Calls**: `SovereignVerifier.verify()`
- **Generates**: Verification reports
- **Validates**: Compliance bundles

---

#### Handler: `cmd_verify_audit(args)`
**Purpose**: Verify audit trail integrity

**Flow**:
```python
def cmd_verify_audit(args):
    1. Extract data_dir from audit_log path
    2. Create SovereignRuntime(data_dir=data_dir)
    3. Verify: is_valid, issues = sovereign.verify_audit_trail_integrity()
    4. Display results
       ├─ Valid → Show success, exit(0)
       └─ Invalid → Show issues, exit(1)
```

**Dependencies**:
- `governance.sovereign_runtime.SovereignRuntime`

**Input**: `args.audit_log` (JSONL path)

**Output**:
- Validation status
- Issue list (if invalid)
- Exit code: 0/1

**Relationships**:
- **Calls**: `SovereignRuntime.verify_audit_trail_integrity()`
- **Validates**: Audit log files

---

#### Handler: `cmd_verify_bundle(args)`
**Purpose**: Verify compliance bundle

**Flow**:
```python
def cmd_verify_bundle(args):
    1. Load bundle JSON
    2. Extract integrity_verification section
    3. Check is_valid flag
       ├─ True → Show success, exit(0)
       └─ False → Show issues, exit(1)
```

**Dependencies**: JSON parsing

**Input**: `args.bundle` (JSON path)

**Output**:
- Bundle validity status
- Exit code: 0/1

**Relationships**:
- **Validates**: Compliance bundles
- **Independent**: No external module calls

---

### 2. Inspection Handlers (`inspection_cli.py`)

#### Handler: `main()`
**Purpose**: Route to inspection CLI

**Flow**:
```python
def main():
    1. Add src/ to Python path
    2. Import app.inspection.cli.main
    3. Delegate to inspection system
```

**Dependencies**:
- `app.inspection.cli.main`

**Input**: Command-line arguments (via delegated parser)

**Output**: Inspection results

**Relationships**:
- **Wrapper**: Delegates to `app.inspection.cli`
- **Path Setup**: Modifies sys.path for imports

---

### 3. DeepSeek Inference Handlers (`scripts/deepseek_v32_cli.py`)

#### Handler: `print_result(result, mode)`
**Purpose**: Format and display inference results

**Flow**:
```python
def print_result(result, mode):
    1. Check result["success"]
    2. If failed → print error, return
    3. Format output based on mode:
       ├─ completion → Show prompt + generated text
       └─ chat → Show assistant response
    4. Display metadata (model, tokens)
```

**Dependencies**: None (pure formatting)

**Input**: 
- `result` dict (from DeepSeekV32)
- `mode` string (completion/chat)

**Output**: Formatted text to stdout

**Relationships**:
- **Formats**: DeepSeekV32 results
- **Displays**: User-friendly output

---

#### Handler: `interactive_chat(deepseek, args)`
**Purpose**: Manage interactive chat sessions

**Flow**:
```python
def interactive_chat(deepseek, args):
    1. Display welcome message
    2. Initialize messages list
    3. Loop:
       a. Get user input
       b. Handle special commands (exit, clear, info)
       c. Add user message to history
       d. Generate response via deepseek.generate_chat()
       e. Display assistant response
       f. Add assistant message to history
    4. Handle errors and interrupts
```

**Dependencies**:
- `DeepSeekV32` instance

**Input**: 
- `deepseek` (initialized model)
- `args` (CLI arguments)

**Output**: Interactive chat session

**Relationships**:
- **Calls**: `deepseek.generate_chat()`
- **Manages**: Conversation state
- **Handles**: User input loop

---

#### Handler: `main()`
**Purpose**: DeepSeek CLI entry point

**Flow**:
```python
def main():
    1. Parse arguments (argparse)
    2. Validate arguments
       ├─ Require prompt or --interactive
       └─ Check mode compatibility
    3. Initialize DeepSeekV32
    4. Route to mode:
       ├─ interactive → interactive_chat()
       ├─ completion → generate_completion()
       └─ chat → generate_chat()
    5. Output results (JSON or formatted)
    6. Exit with status code
```

**Dependencies**:
- `app.core.deepseek_v32_inference.DeepSeekV32`
- `app.core.runtime.router.route_request` (governance)

**Input**: Command-line arguments

**Output**: 
- Generated text
- JSON results (optional)
- Exit code: 0/1/130

**Relationships**:
- **Initializes**: DeepSeekV32 model
- **Routes**: To appropriate generation mode
- **Applies**: Governance routing
- **Handles**: Keyboard interrupts

---

## 🔄 Handler Routing Patterns

### 1. Argument-Based Routing
```python
# project_ai_cli.py
if args.command == "run":
    cmd_run(args)
elif args.command == "sovereign-verify":
    cmd_sovereign_verify(args)
elif args.command == "verify-audit":
    cmd_verify_audit(args)
elif args.command == "verify-bundle":
    cmd_verify_bundle(args)
```

**Pattern**: Direct command name matching

**Characteristics**:
- Simple, explicit routing
- One handler per command
- Clear separation of concerns

---

### 2. Delegation Pattern
```python
# inspection_cli.py
from app.inspection.cli import main
if __name__ == "__main__":
    main()
```

**Pattern**: Thin wrapper delegates to module

**Characteristics**:
- Minimal CLI script
- Logic in module
- Path setup only

---

### 3. Conditional Routing
```python
# deepseek_v32_cli.py
if args.interactive:
    interactive_chat(deepseek, args)
elif args.mode == "completion":
    result = deepseek.generate_completion(...)
else:  # chat mode
    result = deepseek.generate_chat(...)
```

**Pattern**: Mode-based branching

**Characteristics**:
- Multiple execution paths
- Flag-based routing
- Shared initialization

---

## 🔗 Handler Integration Points

### CLI → Handler → Core

```
project_ai_cli.py
    ├─ cmd_run()
    │   └─ IronPathExecutor.execute()
    │       ├─ Load pipeline YAML
    │       ├─ Execute stages
    │       └─ Generate artifacts
    │
    ├─ cmd_sovereign_verify()
    │   └─ SovereignVerifier.verify()
    │       ├─ Validate hash chain
    │       ├─ Check signatures
    │       └─ Generate report
    │
    ├─ cmd_verify_audit()
    │   └─ SovereignRuntime.verify_audit_trail_integrity()
    │       ├─ Load audit log
    │       ├─ Validate hashes
    │       └─ Check integrity
    │
    └─ cmd_verify_bundle()
        └─ JSON validation (internal)
            ├─ Load bundle
            ├─ Extract integrity data
            └─ Validate structure
```

---

### Handler → Output Formatter

```
Handler Execution Result
    ↓
Output Decision
    ├─ Success → Format success output
    │   ├─ Structured logging
    │   ├─ Artifact paths
    │   └─ Summary metrics
    │
    └─ Failure → Format error output
        ├─ Error message
        ├─ Issue details
        └─ Exit code
```

---

## 📊 Handler Characteristics

### Error Handling Patterns

#### Try-Except with Logging
```python
# project_ai_cli.py cmd_run()
if result["status"] == "completed":
    logger.info("✅ EXECUTION SUCCESSFUL")
    # ... success output
    sys.exit(0)
else:
    logger.error("❌ EXECUTION FAILED")
    logger.error("Error: %s", result.get("error", "Unknown error"))
    sys.exit(1)
```

#### Exception Catching with Context
```python
# cmd_verify_bundle()
try:
    with open(args.bundle) as f:
        bundle = json.load(f)
    # ... validation logic
except Exception as e:
    logger.error("Failed to verify bundle: %s", e)
    sys.exit(1)
```

#### Keyboard Interrupt Handling
```python
# deepseek_v32_cli.py
try:
    # ... main logic
except KeyboardInterrupt:
    print("\n\n⚠️  Interrupted by user")
    sys.exit(130)
except Exception as e:
    logger.exception("Fatal error")
    sys.exit(1)
```

---

### Logging Patterns

#### Structured Execution Logging
```python
logger.info("=" * 80)
logger.info("PROJECT-AI SOVEREIGN RUNTIME")
logger.info("=" * 80)
logger.info("Pipeline: %s", args.pipeline)
logger.info("=" * 80)
```

#### Result Detail Logging
```python
logger.info("Execution ID: %s", result["execution_id"])
logger.info("Stages Completed: %d", len(result["stages_completed"]))
logger.info("Artifacts Directory: %s", executor.artifacts_dir)
```

#### Error Logging
```python
logger.error("❌ EXECUTION FAILED")
logger.error("Error: %s", result.get("error", "Unknown error"))
```

---

### Exit Code Conventions

| Code | Meaning | Usage |
|------|---------|-------|
| 0 | Success | Operation completed successfully |
| 1 | Failure | Operation failed with error |
| 2 | Warning | Operation completed with warnings |
| 130 | Interrupted | User interrupted (Ctrl+C) |

**Examples**:
- `cmd_run()`: 0 (success), 1 (failure)
- `cmd_sovereign_verify()`: 0 (pass), 1 (fail), 2 (warning)
- `main()` (deepseek): 0 (success), 1 (error), 130 (interrupt)

---

## 🛡️ Validation & Security

### Input Validation
```python
# Argument validation
if not args.command:
    parser.print_help()
    sys.exit(1)

# Mode compatibility check
if args.interactive and args.mode != "chat":
    parser.error("--interactive can only be used with --mode chat")

# Prompt requirement
if not args.interactive and not args.prompt:
    parser.error("Prompt is required unless --interactive is specified")
```

### Path Validation
```python
# cmd_verify_bundle()
try:
    with open(args.bundle) as f:
        bundle = json.load(f)
except Exception as e:
    logger.error("Failed to verify bundle: %s", e)
    sys.exit(1)
```

### Governance Integration
```python
# deepseek_v32_cli.py
from app.core.runtime.router import route_request

# Content filtering
if args.no_filter:
    deepseek.content_filter_enabled = False
```

---

## 📈 Handler Performance

### Execution Timing
- **cmd_run()**: Depends on pipeline complexity (seconds to minutes)
- **cmd_verify_audit()**: O(n) in audit log size
- **cmd_sovereign_verify()**: O(n) in bundle size
- **interactive_chat()**: Real-time, per-turn generation

### Resource Usage
- **Memory**: Minimal for routing, high for model inference
- **I/O**: File reads (YAML, JSON, JSONL), artifact writes
- **CPU**: Negligible for routing, intensive for inference

---

## 🔍 Handler Dependencies

### Module Dependencies
```
project_ai_cli.py
    └─ governance
        ├─ iron_path.IronPathExecutor
        ├─ sovereign_runtime.SovereignRuntime
        └─ sovereign_verifier.SovereignVerifier

inspection_cli.py
    └─ app.inspection.cli

deepseek_v32_cli.py
    └─ app.core
        ├─ deepseek_v32_inference.DeepSeekV32
        └─ runtime.router.route_request
```

### External Dependencies
- argparse (stdlib)
- json (stdlib)
- logging (stdlib)
- sys (stdlib)
- pathlib (stdlib)

---

## 🔄 Handler Lifecycle

### Initialization → Execution → Cleanup

```
1. Parse Arguments
   ├─ Create ArgumentParser
   ├─ Define subcommands
   └─ Parse sys.argv

2. Validate Input
   ├─ Check required args
   ├─ Validate paths
   └─ Check mode compatibility

3. Initialize Resources
   ├─ Setup logging
   ├─ Load configuration
   └─ Create service instances

4. Execute Handler
   ├─ Route to handler function
   ├─ Execute business logic
   └─ Generate results

5. Format Output
   ├─ Log execution details
   ├─ Display results
   └─ Save artifacts

6. Cleanup & Exit
   ├─ Close resources
   ├─ Flush logs
   └─ Exit with status code
```

---

## 🔗 Related Documentation

- **CLI Interface**: See `01_cli-interface.md`
- **Scripts**: See `03_scripts.md`
- **Core Modules**: See core system documentation

---

**Version**: 1.0.0  
**Last Updated**: 2025-02-08  
**Maintainer**: AGENT-063  
