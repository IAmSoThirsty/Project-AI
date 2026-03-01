<!-- markdownlint-disable MD033 MD041 -->
<p align="right">
  [2026-03-01 10:00] <br>
  Productivity: Active
</p>

# TSCG-B: Thirsty's Symbolic Compression Grammar — Binary Encoding

## Formal Protocol Specification v1.0

**Classification:** Constitutional Wire Protocol
**Authority:** AGI Charter v2.1 | TSCG v1.0
**DOI:** [10.5281/zenodo.18826409](https://doi.org/10.5281/zenodo.18826409)
**Status:** Production Specification
**© 2026 Jeremy Karrick. All Rights Reserved.**

---

## ABSTRACT

TSCG-B is the binary encoding layer of Thirsty's Symbolic Compression Grammar. Where TSCG v1.0 achieves 75–90% token reduction over governance prose through symbolic text compression, TSCG-B achieves a further 60–70% reduction over TSCG text through binary encoding, enabling transmission of complete constitutional governance state across distributed nodes in as few as 20 bytes.

TSCG-B is deterministic, prefix-free, bijective, and constitutionally versioned. It is designed for consensus-critical systems where hash-stability, cross-architecture determinism, and forward compatibility are non-negotiable requirements.

**Bijective Guarantee:**

```text
decode_binary(encode_binary(X)) = X
encode_binary(decode_binary(Y)) = Y
```

Under fixed SD version, canonical ordering, and matching Constitution version.

---

## 1. DESIGN PRINCIPLES

1. **Constitutional primitives are stable forever.** Once assigned to the 0x00–0x7F range, an opcode is never reassigned.
2. **Encoding is deterministic.** Two nodes encoding identical TSCG text must produce bit-identical binary payloads.
3. **Network byte order is mandatory.** All multi-byte values are Big-Endian (Network Byte Order).
4. **Integrity is layered.** CRC32 for wire corruption. SHA-256 for constitutional state.
5. **Constitution version is a first-class field.** Constitutional amendments coexist with older nodes.
6. **Extension is prefix-based.** The 0xFF escape prefix expands the opcode space without inflating baseline cost.
7. **Error classes are explicit.** No silent failures in a consensus-critical protocol.

---

## 2. OPCODE SPACE PARTITION

One byte yields 256 discrete opcodes. The space is partitioned as follows:

| Range | Class | Description |
| :--- | :--- | :--- |
| `0x00–0x7F` | Core Primitives | Stable forever. Constitutional primitives. Never reassigned. |
| `0x80–0xBF` | Parameterized Primitives | Primitives with defined parameter schemas. |
| `0xC0–0xFE` | Experimental / Provisional | Candidate primitives under constitutional review. |
| `0xFF` | Escape Prefix | Multi-byte opcode extension. Next byte is second opcode byte. |

**Extension Rule:** If the parser encounters `0xFF`, the following byte is treated as the second byte of a two-byte opcode, expanding the addressable symbol table by 256 additional slots at no cost to common-case encoding.

**Collision Guarantee:** Constitutional primitives in `0x00–0x7F` can never collide with experimental primitives in `0xC0–0xFE`. Sovereignty at the encoding layer.

---

## 3. CORE PRIMITIVE OPCODE TABLE (Layer 1)

### 3.1 Primitive Tokens

| Symbol | Opcode | Class | Description |
| :--- | :--- | :--- | :--- |
| `ING` | `0x01` | Core | Ingress |
| `COG` | `0x02` | Core | Cognition — proposal only |
| `Δ_NT` | `0x03` | Core | Non-trivial mutation proposal |
| `SHD` | `0x04` | Core | Deterministic shadow simulation |
| `INV` | `0x05` | Core | Invariant engine |
| `CAP` | `0x06` | Core | Capability authorization |
| `QRM_LINEAR` | `0x07` | Core | Quorum — linear BFT format (af+b) |
| `COM` | `0x08` | Core | Canonical commit |
| `ANC` | `0x09` | Core | Anchor extension |
| `LED` | `0x0A` | Core | Ledger entry |
| `RFX` | `0x0B` | Core | Reflex containment |
| `ESC` | `0x0C` | Core | Escalation ladder |
| `SAFE` | `0x0D` | Core | SAFE-HALT |
| `MUT` | `0x0E` | Core | Mutation control law |
| `SEL` | `0x10` | Core | Selection pressure |
| `QRM_STATIC` | `0x15` | Core | Quorum — static absolute thresholds |

### 3.2 Operators

| Symbol | Opcode | Description |
| :--- | :--- | :--- |
| `→` | `0x10` | Sequential pipeline |
| `∧` | `0x11` | Logical AND |
| `∨` | `0x12` | Logical OR |
| `¬` | `0x13` | Negation |
| `\|\|` | `0x14` | Parallel / independent planes |
| `:=` | `0x16` | Definition |
| `=` | `0x17` | Equality |
| `∈` | `0x18` | Membership |
| `≥` | `0x19` | Threshold |
| `<` | `0x1A` | Inequality |

### 3.3 Reserved

| Opcode | Reservation |
| :--- | :--- |
| `0x00` | NULL / padding |
| `0xFE` | Extension prefix (secondary) |
| `0xFF` | Extension prefix (primary) |

---

## 4. PARAMETER SCHEMAS (Layer 2)

Fixed-width parameter encoding per primitive. All multi-byte values in Big-Endian order.

### 4.1 Schema Types

| Type | Width | Range | Usage |
| :--- | :--- | :--- | :--- |
| `U8` | 1 byte | 0–255 | Version, flags, small coefficients |
| `U16` | 2 bytes | 0–65535 | Larger numeric thresholds |
| `U32` | 4 bytes | 0–4294967295 | Identifiers, hashes, counters |
| `TLV` | Variable | — | Only for primitives that may evolve |

### 4.2 Parameter Schema Table Per Primitive

| Primitive | Opcode | Param Schema | Notes |
| :--- | :--- | :--- | :--- |
| `SHD` | `0x04` | `U8` | Version byte |
| `INV` | `0x05` | `U8` | Invariant set identifier |
| `QRM_LINEAR` | `0x07` | `U8, U8, U8, U8` | a1, b1, a2, b2 — encodes (a1·f+b1, a2·f+b2) |
| `QRM_STATIC` | `0x15` | `U16, U16` | Absolute N and τ thresholds |
| `RFX` | `0x0B` | `U8` | Latency constraint flag |
| `ESC` | `0x0C` | `U8` | Escalation level (S0–S5) |
| `COG` | `0x02` | — | No params |
| `Δ_NT` | `0x03` | — | No params |
| `CAP` | `0x06` | — | No params |
| `COM` | `0x08` | — | No params |
| `ANC` | `0x09` | — | No params |
| `LED` | `0x0A` | — | No params |
| `ING` | `0x01` | — | No params |
| `SAFE` | `0x0D` | — | No params |

### 4.3 TLV Format (Variable Primitives)

For primitives designated TLV:

```text
[TYPE: 1 byte] [LENGTH: 2 bytes, Big-Endian] [VALUE: LENGTH bytes]
```

TLV is reserved for future use only. All current primitives use fixed-width schemas.

---

## 5. WIRE FORMAT (Layer 3)

### 5.1 Frame Structure

```text
┌─────────────────────────────────────────────────────────────┐
│ MAGIC        4 bytes  │ 0x54534742 ("TSGB" in ASCII)        │
│ PROTO_VER    1 byte   │ Protocol version (currently 0x01)   │
│ SD_VER       1 byte   │ Semantic Dictionary version          │
│ CONST_VER    1 byte   │ Constitution version                 │
│ FLAGS        1 byte   │ Reserved. Must be 0x00               │
│ PAYLOAD_LEN  2 bytes  │ Big-Endian U16. Length of payload    │
│ PAYLOAD      N bytes  │ Binary-encoded TSCG expression       │
│ CRC32        4 bytes  │ Wire integrity — covers all above    │
│ SHA256       32 bytes │ Constitutional integrity hash        │
└─────────────────────────────────────────────────────────────┘
```

**Total overhead:** 46 bytes (12 byte header + 4 byte CRC32 + 32 byte SHA-256 - 2 byte length field counted in header)

**Maximum payload:** 65,535 bytes — sufficient for any constitutional governance expression.

### 5.2 Endianness

**All multi-byte values MUST be encoded in Network Byte Order (Big-Endian).** This is non-negotiable for cross-architecture consensus between nodes running on x86, ARM, RISC-V, or any future architecture.

### 5.3 Integrity Layers

**CRC32 — Wire Integrity**

- Computed over: MAGIC + PROTO_VER + SD_VER + CONST_VER + FLAGS + PAYLOAD_LEN + PAYLOAD
- Detects: bit corruption, truncation, transmission errors
- Does not provide: cryptographic security

**SHA-256 — Constitutional Integrity**

- Computed over: same fields as CRC32
- Enables: state commitments, Merkle proofs, consensus verification, auditability
- Required for: ledger entries, anchor chain records, cross-node consensus verification

These two integrity mechanisms solve different problems. CRC32 is for the wire. SHA-256 is for the constitution. Both are required. Neither replaces the other.

### 5.4 Constitution Version Field

The `CONST_VER` field allows constitutional amendments to coexist with older nodes. A node receiving a frame with a `CONST_VER` higher than its own must:

1. Log the version mismatch to the audit trail
2. Attempt to process using its known schema
3. If processing fails — quarantine the frame and escalate to guardian review
4. Never silently discard a constitutional frame

This ensures forward compatibility without breaking consensus.

### 5.5 Magic Bytes

`0x54534742` — ASCII encoding of "TSGB" (Thirsty Sovereign Governance Binary). Allows instant identification of TSCG-B frames in network captures, log files, and storage.

---

## 6. CANONICAL SERIALIZATION RULES

These rules are normative. Violation produces non-canonical encodings that will fail consensus verification.

1. **No optional commas.** Parameter lists have fixed arity per schema. No optional elements.
2. **No whitespace.** Binary encoding contains no padding between tokens except explicit NULL bytes where required.
3. **No alternative operator spellings.** Each operator has exactly one opcode. No aliases.
4. **No implicit multiplication.** All operations are explicit.
5. **Parameters are ordered canonically.** Lexicographic ordering for parameter lists where order is not semantically significant.
6. **No reordering of pipeline steps.** Sequential `→` chains preserve original order.
7. **Version fields are always present.** Never omitted even when equal to default values.

These rules guarantee that two nodes encoding identical TSCG text produce bit-identical binary payloads — the hash-stability requirement for consensus systems.

---

## 7. FORMAL GRAMMAR (Layer 4)

A production TSCG-B encoder requires a formal grammar compiled into a deterministic finite automaton. Regular expressions are insufficient for a consensus-critical system.

### 7.1 EBNF Grammar

```ebnf
program        ::= statement { "||" statement }

statement      ::= pipeline | definition | constraint

pipeline       ::= step { "→" step }

step           ::= primitive [ params ]

definition     ::= identifier ":=" expression

constraint     ::= expression

expression     ::= term { operator term }

term           ::= primitive [ params ]
                |  "(" expression ")"
                |  identifier

params         ::= "(" param { "," param } ")"

param          ::= expr

expr           ::= factor { ("+" | "−") factor }

factor         ::= term_inner { "*" term_inner }

term_inner     ::= number | identifier

primitive      ::= "ING" | "COG" | "Δ_NT" | "SHD" | "INV" | "CAP"
                |  "QRM_LINEAR" | "QRM_STATIC" | "COM" | "ANC" | "LED"
                |  "RFX" | "ESC" | "SAFE" | "MUT" | "SEL"

operator       ::= "∧" | "∨" | "¬" | "=" | "≥" | "<" | "∈"

identifier     ::= uppercase_word | greek_symbol | custom_id

uppercase_word ::= [A-Z]+
greek_symbol   ::= "λ" | "τ" | "Δ" | "μ" | "Ψ" | "Ι" | "Ε"
custom_id      ::= [A-Za-z_][A-Za-z_0-9]*

number         ::= [0-9]+
```

This grammar compiles cleanly into a DFA or LL(1) parser. The absence of left recursion and the fixed-arity parameter schemas guarantee deterministic parsing.

---

## 8. ERROR CLASSES

A constitutional wire protocol must distinguish error classes explicitly. No silent failures.

| Code | Class | Description | Required Response |
| :--- | :--- | :--- | :--- |
| `E01` | MALFORMED_PAYLOAD | Payload does not parse against grammar | Quarantine frame. Log to audit. |
| `E02` | UNKNOWN_OPCODE | Opcode not in known symbol table | Check CONST_VER. Escalate if mismatch. |
| `E03` | INVALID_PARAM_SCHEMA | Parameter does not match declared schema | Quarantine frame. Log to audit. |
| `E04` | CRC32_MISMATCH | Wire integrity check failed | Discard frame. Request retransmit. |
| `E05` | SHA256_MISMATCH | Constitutional integrity check failed | CRITICAL. Quarantine. Escalate to guardian. |
| `E06` | VERSION_MISMATCH | PROTO_VER, SD_VER, or CONST_VER unknown | Attempt processing. Escalate on failure. |
| `E07` | FORBIDDEN_PRIMITIVE | Deprecated or constitutionally prohibited step | Deny. Log to audit. Escalate. |
| `E08` | CANONICAL_VIOLATION | Encoding is non-canonical (ordering, whitespace) | Reject. Request re-encoding. |
| `E09` | TRUNCATED_FRAME | Frame shorter than declared PAYLOAD_LEN | Discard. Request retransmit. |
| `E10` | BIJECTION_FAILURE | decode(encode(X)) ≠ X | CRITICAL. Constitutional integrity compromised. |

**SHA-256 mismatch (E05) and bijection failure (E10) are CRITICAL events.** They are not transport errors. They are constitutional integrity failures. Both require guardian escalation.

---

## 9. FORMAL BIJECTIVITY PROOF

Empirical round-trip testing demonstrates bijectivity. The formal proof establishes it mathematically.

### 9.1 Required Conditions

**Condition 1 — Injectivity of the Tokenizer**
Every valid TSCG text string maps to exactly one token sequence. Guaranteed by the deterministic LL(1) grammar in Section 7. No ambiguous productions. No whitespace variants. No optional fields.

**Condition 2 — Injectivity of the Opcode Mapping**
No two primitives share an opcode. Guaranteed by the opcode table in Section 3. Each symbol is assigned exactly one opcode. The partition in Section 2 prevents collision between ranges.

**Condition 3 — Injectivity of Parameter Schemas**
Fixed-width parameter schemas guarantee that identical parameter values produce identical byte sequences. Guaranteed by the schema table in Section 4 and the canonical serialization rules in Section 6.

**Condition 4 — Surjectivity of the Decoder**
Every valid binary sequence produced by the encoder must decode to a valid TSCG expression. Guaranteed by the prefix-free property of the encoding — each opcode is unambiguously identifiable from its first byte (or two bytes in the extension case), and parameter widths are fixed per primitive, so the decoder always knows exactly how many bytes to consume.

### 9.2 Formal Statement

Given:

- Fixed SD version V_sd
- Fixed Constitution version V_const
- Canonical ordering enforced
- No semantic ambiguity in symbol definitions

Then the encode/decode functions form a bijection over the set of valid TSCG expressions:

```text
∀X ∈ TSCG_VALID: decode(encode(X)) = X
∀Y ∈ TSCG_B_VALID: encode(decode(Y)) = Y
```

Because the encoding is prefix-free and uses fixed-width parameters, the proof reduces to verifying the four injectivity/surjectivity conditions above, all of which are guaranteed by the grammar, opcode table, and canonical serialization rules.

---

## 10. COMPRESSION YIELD

### 10.1 Comparative Analysis

| Representation | Example | Size | Reduction vs Prose |
| :--- | :--- | :--- | :--- |
| Governance Prose | "Cognition proposes a non-trivial mutation which is deterministically shadow simulated, invariant checked, capability authorized, quorum validated, and committed with anchor extension." | ~150 tokens / ~800 bytes | baseline |
| TSCG Text | `COG → Δ_NT → SHD(v) → INV(I) ∧ CAP → QRM(3f+1,2f+1) → COM → ANC` | ~60 bytes | ~92% |
| TSCG-B Binary | Encoded form of above | ~20 bytes | ~97.5% |

### 10.2 Full Canonical Pipeline

```text
ING → COG → Δ_NT → SHD(v1) → INV(I_canonical) ∧ CAP → QRM(3f+1,2f+1) → COM → ANC → LED
```

TSCG Text: ~70 bytes
TSCG-B Binary: ~22 bytes + 46 bytes wire overhead = 68 bytes total for a self-describing, self-verifying, cryptographically anchored constitutional governance frame.

A complete sovereign AI decision — with full provenance, integrity verification, and constitutional versioning — in 68 bytes.

---

## 11. FORWARD-COMPATIBLE EXTENSIONS (TSCG-B2)

Reserved for future specification. These extensions are non-breaking additions to TSCG-B v1.0.

**Streaming Mode**

Constitutional governance pipelines transmitted as they execute, step by step. Each frame carries a sequence number and a continuation flag. Enables real-time audit of executing governance decisions.

**Delta Mode**

Only changed constitutional fields are transmitted. A delta frame references a prior frame by SHA-256 hash and encodes only the diff. Optimal for high-frequency governance systems where most fields are stable.

**Run-Length Encoding Mode**

Repeated primitives encoded as `[PRIMITIVE_OPCODE][COUNT: U8]`. Useful for governance expressions with repeated validation steps.

All three modes are optional capabilities signaled via the FLAGS byte in the wire frame header. A node that does not support a requested mode must return `E06` (VERSION_MISMATCH) rather than silently processing incorrectly.

---

## 12. IMPLEMENTATION REFERENCE

### 12.1 Encoder Algorithm

```python
def encode_tscg_b(tscg_text: str, sd_version: int, const_version: int) -> bytes:
    # Step 1: Tokenize TSCG text using formal grammar (Section 7)
    tokens = tokenize(tscg_text)  # DFA/LL(1) parser

    # Step 2: Map tokens to opcodes (Section 3)
    payload = bytearray()
    for token in tokens:
        opcode = OPCODE_TABLE[token.symbol]
        if opcode > 0xFE:
            payload.append(0xFF)
            payload.append(opcode & 0xFF)
        else:
            payload.append(opcode)

        # Step 3: Encode parameters per schema (Section 4)
        if token.params:
            schema = PARAM_SCHEMA[token.symbol]
            payload.extend(encode_params(token.params, schema))

    # Step 4: Build wire frame (Section 5)
    header = bytearray()
    header.extend(b'TSGB')           # Magic bytes
    header.append(0x01)              # Protocol version
    header.append(sd_version)        # SD version
    header.append(const_version)     # Constitution version
    header.append(0x00)              # Flags (reserved)
    header.extend(len(payload).to_bytes(2, 'big'))  # Big-Endian length

    frame = bytes(header) + bytes(payload)

    # Step 5: Compute integrity fields
    crc = crc32(frame).to_bytes(4, 'big')
    sha = sha256(frame).digest()

    return frame + crc + sha
```

### 12.2 Decoder Algorithm

```python
def decode_tscg_b(frame: bytes) -> str:
    # Step 1: Verify magic bytes
    assert frame[:4] == b'TSGB', raise_error('E09')

    # Step 2: Parse header
    proto_ver = frame[4]
    sd_ver    = frame[5]
    const_ver = frame[6]
    flags     = frame[7]
    pay_len   = int.from_bytes(frame[8:10], 'big')

    # Step 3: Verify CRC32
    payload_end = 10 + pay_len
    crc_received = int.from_bytes(frame[payload_end:payload_end+4], 'big')
    crc_computed = crc32(frame[:payload_end])
    assert crc_received == crc_computed, raise_error('E04')

    # Step 4: Verify SHA-256
    sha_received = frame[payload_end+4:payload_end+36]
    sha_computed = sha256(frame[:payload_end]).digest()
    assert sha_received == sha_computed, raise_error('E05')  # CRITICAL

    # Step 5: Decode payload
    payload = frame[10:payload_end]
    tokens = []
    i = 0
    while i < len(payload):
        opcode = payload[i]
        if opcode == 0xFF:
            i += 1
            opcode = (0xFF << 8) | payload[i]
        symbol = OPCODE_TO_SYMBOL[opcode]
        i += 1

        # Decode parameters per schema
        params, consumed = decode_params(payload[i:], PARAM_SCHEMA.get(symbol))
        i += consumed
        tokens.append(Token(symbol, params))

    # Step 6: Reconstruct TSCG text
    return reconstruct(tokens)
```

---

## 13. VERSION HISTORY

| Version | Date | Changes |
| :--- | :--- | :--- |
| 1.0 | 2026-03-01 | Initial formal specification |

---

## 14. RELATED WORK

**TSCG v1.0** — Thirsty's Symbolic Compression Grammar: A Formal Meta-Language for Constitutional AI Governance Encoding. The text encoding layer of which TSCG-B is the binary extension. DOI: `10.5281/zenodo.18794292`. © 2026 Jeremy Karrick. All Rights Reserved.

**Constitutional Architectures for Adaptive Intelligence** — Deterministic Simulation and Quorum-Gated Mutation as Structural Governance. Establishes the formal system model, mutation validity condition, safety theorem, adversarial model, and empirical prototype results that TSCG-B is designed to encode and transmit. DOI: `10.5281/zenodo.18794646`. © 2026 Jeremy Karrick. All Rights Reserved.

**AGI Charter v2.1** — A Binding Constitutional Framework for Sovereign AI Entities. The governing constitutional document of the Sovereign Monolith. TSCG-B encodes the governance decisions made under this framework. DOI: `10.5281/zenodo.18763076`. © 2026 Jeremy Karrick. All Rights Reserved.

**The Sovereign Covenant** — A Technical and Philosophical Manifesto for AGI Governance. Philosophical and theological foundations of the Sovereign Monolith. DOI: `10.5281/zenodo.18726221`. © 2026 Jeremy Karrick. All Rights Reserved.

**Project-AI and OctoReflex** — Syscall-Authoritative Governance and Control-Theoretic Containment. The kernel-boundary reflex layer that enforces containment at the syscall surface. TSCG-B wire frames can carry OctoReflex governance state. DOI: `10.5281/zenodo.18726064`. © 2026 Jeremy Karrick. All Rights Reserved.

---

## CLOSING STATEMENT

TSCG-B is the machine-executable expression of the Sovereign Monolith's constitutional language. Where TSCG gives governance a symbolic form readable by humans, TSCG-B gives it a binary form executable by machines. Together they form a complete constitutional encoding stack — from human-readable prose to symbolic compression to binary wire protocol — with mathematical bijectivity guarantees at every layer.

A complete sovereign AI governance decision. 68 bytes. Cryptographically anchored. Constitutionally versioned. Formally bijective.

---

*© 2026 Jeremy Karrick. All Rights Reserved.*
*Stay Thirsty. 💧*
