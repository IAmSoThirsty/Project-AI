# Shadow Thirst - Formal Grammar Specification

**VERSION**: 1.0.0
**STATUS**: PRODUCTION
**EXTENDS**: Thirsty-Lang v1.0

---

## I. Introduction

Shadow Thirst is a **statically enforced dual-implementation language layer** where primary execution and shadow execution are first-class constructs governed by policy invariants. It is a strict superset of Thirsty-Lang, adding shadow execution capabilities at the language level.

### Design Principles

1. **Type-Level Reality Split**: Shadow is part of the AST, not runtime flags
2. **Compiler Understanding**: Parser and compiler enforce shadow semantics
3. **Constitutional Binding**: All shadow constructs bound by invariants
4. **Deterministic Execution**: Shadow execution is deterministic and replayable

---

## II. Formal Grammar (BNF-Style)

### 2.1 Top-Level Structure

```bnf
<program>           ::= <statement>*

<statement>         ::= <function_decl>
                      | <shadow_function_decl>
                      | <variable_decl>
                      | <assignment>
                      | <expression_stmt>
                      | <control_flow>
                      | <comment>

<comment>           ::= "//" <text> NEWLINE
                      | "#" <text> NEWLINE
```

### 2.2 Shadow Function Declaration

```bnf
<shadow_function_decl> ::= "fn" <identifier> "(" <params>? ")" ("->" <type>)? "{"
                             <primary_block>
                             <shadow_block>?
                             <activation_clause>*
                             <invariant_clause>*
                             <divergence_clause>?
                             <mutation_clause>?
                           "}"

<primary_block>     ::= "primary" "{" <statement>* "}"

<shadow_block>      ::= "shadow" "{" <statement>* "}"

<activation_clause> ::= "activate_if" <activation_expr>

<invariant_clause>  ::= "invariant" "{" <invariant_expr> "}"

<divergence_clause> ::= "divergence" <divergence_policy>

<mutation_clause>   ::= "mutation" <mutation_boundary>
```

### 2.3 Activation Expressions

```bnf
<activation_expr>   ::= <threat_check>
                      | <high_stakes_check>
                      | <policy_check>
                      | <boolean_expr>

<threat_check>      ::= "threat_score()" <comparison_op> <number>

<high_stakes_check> ::= "is_high_stakes"
                      | "risk_level" <comparison_op> <risk_literal>

<policy_check>      ::= "policy_flag" "==" <identifier>

<risk_literal>      ::= "low" | "medium" | "high" | "critical"

<comparison_op>     ::= ">" | ">=" | "<" | "<=" | "==" | "!="
```

### 2.4 Invariant Expressions

```bnf
<invariant_expr>    ::= <epsilon_check>
                      | <identity_check>
                      | <range_check>
                      | <boolean_expr>

<epsilon_check>     ::= "abs(" <result_ref> "-" <result_ref> ")" <comparison_op> <number>

<identity_check>    ::= <result_ref> "==" <result_ref>

<range_check>       ::= <result_ref> ">=" <number> "&&" <result_ref> "<=" <number>

<result_ref>        ::= "primary" "." <member_access>
                      | "shadow" "." <member_access>
                      | <identifier>

<member_access>     ::= "output" | "state" | <identifier>
```

### 2.5 Divergence Policies

```bnf
<divergence_policy> ::= "require_identical"
                      | "allow_epsilon" "(" <number> ")"
                      | "log_divergence"
                      | "quarantine_on_diverge"
                      | "fail_primary"
```

### 2.6 Mutation Boundaries

```bnf
<mutation_boundary> ::= "read_only"
                      | "ephemeral_only"
                      | "shadow_state_only"
                      | "validated_canonical"
                      | "emergency_override"
```

### 2.7 Core Thirsty-Lang (Base Language)

```bnf
<function_decl>     ::= "fn" <identifier> "(" <params>? ")" ("->" <type>)? "{"
                             <statement>*
                           "}"

<variable_decl>     ::= "drink" <identifier> "=" <expression>

<assignment>        ::= <identifier> "=" <expression>

<expression_stmt>   ::= "pour" <expression>
                      | <expression>

<control_flow>      ::= <if_stmt>
                      | <while_stmt>
                      | <for_stmt>

<if_stmt>           ::= "if" <expression> "{" <statement>* "}"
                        ("else" "{" <statement>* "}")?

<while_stmt>        ::= "while" <expression> "{" <statement>* "}"

<for_stmt>          ::= "for" <identifier> "in" <expression> "{" <statement>* "}"
```

### 2.8 Expressions

```bnf
<expression>        ::= <literal>
                      | <identifier>
                      | <function_call>
                      | <binary_expr>
                      | <unary_expr>
                      | <member_expr>

<literal>           ::= <number>
                      | <string>
                      | <boolean>

<number>            ::= <integer> | <float>

<string>            ::= '"' <text> '"' | "'" <text> "'"

<boolean>           ::= "true" | "false"

<function_call>     ::= <identifier> "(" <args>? ")"

<args>              ::= <expression> ("," <expression>)*

<binary_expr>       ::= <expression> <binary_op> <expression>

<binary_op>         ::= "+" | "-" | "*" | "/" | "%"
                      | "&&" | "||"
                      | <comparison_op>

<unary_expr>        ::= "!" <expression>
                      | "-" <expression>

<member_expr>       ::= <expression> "." <identifier>
```

### 2.9 Types

```bnf
<type>              ::= "Int" | "Float" | "String" | "Bool"
                      | "Data" | "Result"
                      | "Dual" "<" <type> ">"
                      | "Shadow" "<" <type> ">"
                      | "Primary" "<" <type> ">"

<params>            ::= <param> ("," <param>)*

<param>             ::= <identifier> ":" <type>

<identifier>        ::= <letter> (<letter> | <digit> | "_")*

<letter>            ::= "a".."z" | "A".."Z"

<digit>             ::= "0".."9"
```

---

## III. Type System Extensions

### 3.1 Shadow Type Qualifiers

Shadow Thirst introduces three new type qualifiers:

```thirsty
Shadow<T>   // Exists only in shadow context
Primary<T>  // Exists only in primary context
Dual<T>     // Computed in both planes, resolved by Constitutional Core
```

### 3.2 Type Rules

1. **Shadow Isolation**: `Primary<T>` cannot implicitly cast from `Shadow<T>`
2. **Dual Resolution**: `Dual<T>` can only be resolved by Constitutional Core
3. **Memory Qualification**: Variables must declare their memory scope

### 3.3 Memory Qualifiers

```thirsty
let x: Canonical<Int>    // Canonical state (persistent)
let y: Shadow<Int>       // Shadow state (ephemeral)
let z: Ephemeral<Int>    // Ephemeral state (temporary)
```

---

## IV. Language Examples

### 4.1 Basic Shadow Function

```thirsty
fn compute_value(input: Int) -> Dual<Int> {
    primary {
        drink result = input * 2
        pour result
    }

    shadow {
        drink validated = input * 2
        pour validated
    }

    activate_if threat_score() > 0.7

    invariant {
        primary.output == shadow.output
    }
}
```

### 4.2 Shadow with Epsilon Tolerance

```thirsty
fn trust_calculation(user: User, delta: Float) -> Dual<Float> {
    primary {
        user.trust += delta
        pour user.trust
    }

    shadow {
        drink projected = simulate_trust(user, delta)
        pour projected
    }

    activate_if abs(delta) > 0.1

    invariant {
        shadow.output >= 0.0 && shadow.output <= 1.0
        abs(primary.output - shadow.output) < 0.01
    }

    divergence allow_epsilon(0.01)
}
```

### 4.3 Containment Mode

```thirsty
fn handle_request(req: Request) -> Response {
    primary {
        pour process_legitimate(req)
    }

    shadow {
        containment {
            simulate_success_response()
            instrument_attack_vector()
        }
    }

    activate_if is_adversarial(req)

    mutation read_only
}
```

### 4.4 Policy Simulation

```thirsty
fn update_policy(new_rule: PolicyRule) -> Dual<PolicyState> {
    primary {
        pour apply_policy(new_rule)
    }

    shadow {
        drink simulated = simulate_policy(new_rule)
        pour simulated
    }

    activate_if policy_flag == "test_mode"

    invariant {
        preserve_trust_bounds(shadow.output)
        preserve_safety_envelope(shadow.output)
    }

    mutation shadow_state_only
}
```

### 4.5 Temporal Shadow (Chaos Testing)

```thirsty
fn critical_transaction(tx: Transaction) -> Dual<Result> {
    primary {
        pour execute_transaction(tx)
    }

    shadow {
        temporal_shadow {
            reorder_events()
            inject_latency(50ms)
        }
        pour execute_transaction(tx)
    }

    activate_if is_high_stakes

    invariant {
        validate_consistency(primary.output, shadow.output)
        verify_idempotence(primary.output, shadow.output)
    }
}
```

---

## V. Semantic Rules

### 5.1 Execution Flow

1. **Parse**: Parser constructs dual-implementation AST
2. **Type Check**: Compiler validates shadow semantics
3. **Activate**: Evaluate activation predicates
4. **Execute Primary**: Always execute primary block
5. **Execute Shadow**: Conditionally execute shadow block
6. **Validate**: Check invariants against both results
7. **Decide**: Apply divergence policy
8. **Commit**: Commit or quarantine based on validation

### 5.2 Invariant Enforcement

- Invariants must be **pure** (no side effects)
- Invariants must be **deterministic**
- Invariants reference only **declared outputs**
- Critical invariants block commit on violation
- Non-critical invariants log warnings only

### 5.3 Mutation Constraints

| Boundary | Primary Write | Shadow Write | Persist |
|----------|--------------|--------------|---------|
| `read_only` | Yes | No | Yes |
| `ephemeral_only` | Yes | Yes (ephemeral) | No |
| `shadow_state_only` | Yes | Yes (shadow only) | Shadow only |
| `validated_canonical` | Yes | Yes (after validation) | Yes (if validated) |
| `emergency_override` | Yes | Yes (emergency) | Yes (logged) |

### 5.4 Divergence Handling

| Policy | Behavior |
|--------|----------|
| `require_identical` | Fail if any difference |
| `allow_epsilon(ε)` | Allow numerical diff ≤ ε |
| `log_divergence` | Log but allow commit |
| `quarantine_on_diverge` | Quarantine if diverged |
| `fail_primary` | Fail primary if shadow diverges |

---

## VI. Compiler Responsibilities

### 6.1 Shadow Thirst Compiler Must:

1. ✅ Generate dual execution graphs
2. ✅ Insert isolation wrappers
3. ✅ Insert shadow memory routing
4. ✅ Generate invariant checks
5. ✅ Enforce resource ceilings
6. ✅ Generate audit sealing hooks
7. ✅ Reject privilege escalation in shadow
8. ✅ Ensure shadow logic is simpler than primary

### 6.2 Compile-Time Checks

```thirsty
// VALID: Shadow simpler than primary
fn safe_op(x: Int) -> Dual<Int> {
    primary {
        drink result = complex_computation(x)
        pour result
    }
    shadow {
        pour x * 2  // Simpler validation
    }
}

// INVALID: Shadow more complex than primary
fn unsafe_op(x: Int) -> Dual<Int> {
    primary {
        pour x * 2
    }
    shadow {
        drink result = complex_computation(x)  // COMPILER ERROR
        pour result
    }
}
```

---

## VII. Runtime Mapping

### 7.1 Compilation Targets

Shadow Thirst compiles to:

```python
# Primary plane bytecode
primary_bytecode = compile_primary_block(ast.primary)

# Shadow plane bytecode
shadow_bytecode = compile_shadow_block(ast.shadow)

# Invariant check bytecode
invariant_bytecode = compile_invariants(ast.invariants)

# Activation predicate bytecode
activation_bytecode = compile_predicates(ast.activation)

# Policy simulation hooks
policy_hooks = generate_policy_hooks(ast.policy)
```

### 7.2 Integration with Shadow Execution Plane

```python
from app.core.shadow_execution_plane import ShadowExecutionPlane
from app.core.shadow_types import (
    create_threat_activation_predicate,
    create_epsilon_invariant,
)

# Shadow Thirst compiler generates this integration
shadow_plane.execute_dual_plane(
    trace_id=trace_id,
    primary_callable=compiled_primary,
    shadow_callable=compiled_shadow,
    activation_predicates=compiled_predicates,
    invariants=compiled_invariants,
    divergence_policy=parsed_divergence_policy,
)
```

---

## VIII. Standard Library Functions

### 8.1 Shadow-Aware Functions

```thirsty
// Threat detection
fn threat_score() -> Float
fn is_adversarial(req: Request) -> Bool
fn detect_jailbreak(prompt: String) -> Bool

// Trust management
fn get_trust(user: User) -> Float
fn simulate_trust(user: User, delta: Float) -> Float

// Validation
fn validate_consistency(p: T, s: T) -> Bool
fn verify_idempotence(p: T, s: T) -> Bool
fn preserve_trust_bounds(state: State) -> Bool
fn preserve_safety_envelope(state: State) -> Bool

// Temporal operations
fn reorder_events() -> Void
fn inject_latency(ms: Int) -> Void
fn simulate_rollback(state: State) -> State
```

### 8.2 Containment Functions

```thirsty
fn simulate_success_response() -> Response
fn instrument_attack_vector() -> Void
fn mirror_environment() -> Environment
fn shape_response(resp: Response, delay: Int) -> Response
```

---

## IX. Error Handling

### 9.1 Compile-Time Errors

```thirsty
// ERROR: Shadow attempts canonical mutation
fn bad_shadow() -> Dual<Int> {
    primary { pour 42 }
    shadow {
        canonical_state = 100  // COMPILE ERROR
        pour 42
    }
}

// ERROR: Invariant not deterministic
fn bad_invariant() -> Dual<Int> {
    primary { pour 42 }
    shadow { pour 42 }
    invariant {
        random() > 0.5  // COMPILE ERROR: non-deterministic
    }
}

// ERROR: Activation predicate non-deterministic
fn bad_activation() -> Dual<Int> {
    primary { pour 42 }
    shadow { pour 42 }
    activate_if random() > 0.5  // COMPILE ERROR
}
```

### 9.2 Runtime Errors

```thirsty
// Handled by Shadow Execution Plane
// - Invariant violations → quarantine
// - Divergence beyond threshold → quarantine
// - Resource quota exceeded → terminate shadow
// - Shadow execution failure → log and continue primary
```

---

## X. Constitutional Integration

### 10.1 Shadow Cannot Override Constitution

```thirsty
// Shadow execution MUST respect constitutional invariants
invariant constitutional {
    shadow_may_not_bypass_trust_threshold
    shadow_must_log_all_forks
    shadow_divergence_must_be_measurable
    shadow_mutation_must_be_reversible
    shadow_must_be_replayable
    shadow_cannot_exist_outside_constitutional_layer
}
```

### 10.2 Audit Requirements

All shadow constructs automatically emit:

1. Shadow activation event (with reason and timestamp)
2. Execution trace (deterministic replay)
3. Invariant validation results
4. Divergence measurements
5. Mutation log (if any)
6. Cryptographic audit seal (SHA-256)

---

## XI. Language Extensions

### 11.1 Future Constructs (Planned)

```thirsty
// Shadow mode annotation
@shadow_mode("validation")
fn validated_op() -> Dual<T>

// Shadow type inference
fn infer_shadow(x) -> Dual<auto> {
    primary { compute(x) }
    shadow { validate(x) }
}

// Shadow composition
fn composed() -> Dual<T> {
    primary { op1() |> op2() |> op3() }
    shadow { validate_chain([op1, op2, op3]) }
}

// Shadow parallel execution (explicit)
@parallel_shadow
fn fast_validation() -> Dual<T>
```

---

## XII. Tooling

### 12.1 Shadow Thirst Compiler

```bash
# Compile Shadow Thirst to Python bytecode
shadow-thirst compile source.thirsty -o output.pyc

# Run with shadow execution enabled
shadow-thirst run source.thirsty --shadow-enabled

# Validate syntax and semantics
shadow-thirst check source.thirsty

# Generate execution trace
shadow-thirst trace source.thirsty --output trace.json
```

### 12.2 LSP Support

Shadow Thirst provides Language Server Protocol support for:

- Syntax highlighting
- Shadow block validation
- Invariant checking
- Type inference
- Autocomplete for shadow constructs
- Inline error diagnostics

---

## XIII. Migration Path

### 13.1 From Thirsty-Lang to Shadow Thirst

Existing Thirsty-Lang code remains valid:

```thirsty
// Valid Thirsty-Lang (and Shadow Thirst)
fn simple_op(x: Int) -> Int {
    drink result = x * 2
    pour result
}

// Adding shadow is optional
fn enhanced_op(x: Int) -> Dual<Int> {
    primary {
        drink result = x * 2
        pour result
    }
    shadow {
        pour x * 2
    }
    activate_if is_high_stakes
}
```

### 13.2 Gradual Adoption

1. Start with validation-only shadow blocks
2. Add activation predicates for critical paths
3. Introduce invariants incrementally
4. Enable containment for security-sensitive code
5. Full dual-plane architecture for production

---

## XIV. Performance Considerations

### 14.1 Overhead

- Shadow activation: ~0.1-0.2ms
- Dual-plane execution: ~1-2ms per activation
- Invariant validation: ~0.01-0.05ms per invariant
- Overall: <3% for typical workload (5% activation rate)

### 14.2 Optimization Hints

```thirsty
// Compiler can optimize away shadow if never activated
@optimize("lazy_shadow")
fn rarely_activated() -> Dual<T>

// Explicit parallel execution
@optimize("parallel_shadow")
fn independent_validation() -> Dual<T>

// Cache invariant results
@optimize("cache_invariants")
fn deterministic_validation() -> Dual<T>
```

---

## XV. Summary

Shadow Thirst is a **production-grade, type-safe language** for dual-plane computing. It extends Thirsty-Lang with:

✅ First-class shadow execution constructs
✅ Compiler-enforced shadow semantics
✅ Constitutional invariant binding
✅ Deterministic and replayable execution
✅ Cryptographic audit trails
✅ Gradual adoption path from Thirsty-Lang

**This is not a macro system. This is language-level dual-reality computing.**

---

**DOCUMENT CONTROL**

| Field | Value |
|-------|-------|
| Version | 1.0.0 |
| Status | Production Specification |
| Extends | Thirsty-Lang v1.0 |
| Maintained By | Shadow Execution Team |
| Last Updated | 2026-02-20 |
| Review Cycle | Quarterly |

**END OF SPECIFICATION**
