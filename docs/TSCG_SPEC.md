# Thirsty Symbolic Compression Grammar (TSCG) Specification

## Overview

TSCG is a symbolic grammar designed for 85%+ token reduction of complex architectural descriptions and governance invariants within the Thirsty-Lang ecosystem. It enables high-fidelity, verifiable, and recursively defined system states using a compact set of glyphs and operators.

## The Core Symbols

| Symbol | Semantic (Noun) | Technical Role |
| :--- | :--- | :--- |
| **SEL** | Selection pressure | Genetic/Evolutionary optimization target |
| **COG** | Cognition | Proposal-only authority (no write access) |
| **Δ** | Mutation proposal | Action or state change request |
| **Δ_NT** | Non-trivial mutation | Governance-impacting change |
| **SHD** | Deterministic shadow | Simulation-based verification |
| **INV** | Invariant engine | Continuous solvability/validity check |
| **CAP** | Capability auth | Authorization and identity layer |
| **QRM** | Quorum | Byzantine Fault Tolerant agreement |
| **COM** | Commit canonical | State finalization |
| **ANC** | Anchor extension | Cryptographic ledger anchoring |
| **RFX** | Reflex containment | Automated incident response |
| **ESC** | Escalation ladder | Manual or high-tier intervention |
| **SAFE** | SAFE-HALT | Immediate system suspension |
| **MUT** | Mutation control law | Hard-coded governance constraints |
| **LED** | Ledger | Audit trail and history |
| **ING** | Ingress | Data/Input entry point |

## Operators & Flow

| Operator | Semantic | Meaning |
| :--- | :--- | :--- |
| **→** | Sequential flow | Step A leads to Step B |
| **∧** | Parallel constraint | Both A and B must be true/active |
| **∨** | Choice | Either A or B must be true |
| **\|\|** | Async parallel | A and B run independently |
| **¬** | Negation | NOT A |
| **:=** | Recursive definition | Definition of a complex macro |

## Grammar Rules

### 1. Simple Term

A term consists of a Symbol optionally followed by Classes in brackets `[]` and Parameters in parentheses `()`.

- Example: `SHD(v1.0)` - Simulation using version 1.0.
- Example: `QRM[admin](3f+1)` - Admin-class quorum requiring 3f+1 agreement.

### 2. Composition (The Stack)

Terms are composed using operators to describe a pipeline.

- Example: `ING → COG → Δ_NT → SHD(v) → INV(I) ∧ CAP → QRM → COM → ANC`

### 3. Recursive Macro Definition

Complex pipelines can be named and reused.

- Example: `GOV_LOOP := SHD → INV ∧ CAP → QRM → COM`
- Usage: `Δ_NT → GOV_LOOP`

### 4. Parallel Enclosure

Use `||` to indicate independent jurisdictional planes.

- Example: `RFX(Lr<Lc) || COG → GOV_LOOP`

## Token Reduction Yield

| Description Mode | Word/Token Count (Approx) | TSCG Symbol Count | Yield |
| :--- | :--- | :--- | :--- |
| Natural Language | 160-200 | N/A | 0% |
| JSON/YAML | 80-120 | N/A | 40-50% |
| **TSCG** | **15-25** | **10-15** | **85-90%** |

## Implementation

TSCG is implemented via `TSCGEncoder` and `TSCGDecoder` in `Thirsty-Lang/src/core/tscg/tscg.thirsty`.
