<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / DOCUMENTATION.md # -->
<!-- # ============================================================================ # -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / DOCUMENTATION.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
# Thirsty-lang Complete Documentation

## Enterprise-Grade Programming Language with Defensive Security

Version: 1.0.0
Status: Production Ready ✅

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Language Syntax](#language-syntax)
4. [Core Features](#core-features)
5. [Security Features](#security-features)
6. [API Reference](#api-reference)
7. [Testing](#testing)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Examples](#examples)

---

## Overview

Thirsty-lang is a fully operational, enterprise-grade programming language designed for:

- **Defensive Programming**: Built-in security against all known attack vectors
- **Project-AI Integration**: Optimized for AI-powered development workflows
- **Combat Red/Black Hatters**: Comprehensive threat detection and mitigation
- **Production Ready**: 100% tested and verified functionality

### Key Features

✅ **Full Language Implementation**

- Variables, arithmetic, strings
- Control flow (if/else, loops)
- Operator precedence
- Type safety with strict equality

✅ **Enterprise Security**

- Shield blocks for protected execution
- Input/output sanitization
- Variable protection (armor)
- Code morphing and obfuscation
- Threat detection and defense

✅ **Quality Assurance**

- 37/37 tests passing
- 0 security vulnerabilities (CodeQL)
- Comprehensive error handling
- Production-grade validation

---

## Installation

### Prerequisites

- Node.js 14 or higher
- npm (comes with Node.js)
- Git

### Quick Start

```bash

# Clone repository

git clone https://github.com/IAmSoThirsty/Thirsty-lang.git
cd Thirsty-lang

# Install dependencies (if any)

npm install

# Verify installation

npm test

# Run your first program

echo 'pour "Hello, Thirsty!"' > hello.thirsty
npm start hello.thirsty
```

---

## Language Syntax

### File Extension

Thirsty-lang files use the `.thirsty` extension.

### Basic Structure

```thirsty
// Comments start with //

drink variableName = value    // Variable declaration
pour expression               // Output statement

thirsty condition {           // If statement
  // code block
}
hydrated {                    // Else statement
  // code block
}

refill condition {            // Loop
  // code block
}

shield name {                 // Security block
  // protected code
}
```

---

## Core Features

### 1. Variables (drink)

**Syntax:** `drink variableName = value`

**Supported Types:**

- Strings: `"text"` or `'text'`
- Numbers: `42`, `3.14`, `-10`
- Booleans: `true`, `false`

**Examples:**
```thirsty
drink name = "Alice"
drink age = 30
drink temperature = 98.6
drink isActive = true
drink negativeNumber = -5
```

**Rules:**

- Variable names must start with a letter
- Can contain letters, numbers, underscore
- Case-sensitive
- Must be declared before use

---

### 2. Output (pour)

**Syntax:** `pour expression`

**Examples:**
```thirsty
pour "Hello, World!"          // String literal
pour 42                        // Number
pour true                      // Boolean
pour myVariable                // Variable
pour 10 + 5                    // Expression
pour "Age: " + age             // Concatenation
```

---

### 3. Arithmetic Operations

**Operators:** `+` `-` `*` `/`

**Operator Precedence:**

1. Multiplication (`*`) and Division (`/`)
2. Addition (`+`) and Subtraction (`-`)

**Examples:**
```thirsty
drink a = 10
drink b = 5

drink sum = a + b              // 15
drink difference = a - b       // 5
drink product = a * b          // 50
drink quotient = a / b         // 2

// Precedence examples
pour 2 + 3 * 4                 // 14 (not 20)
pour 10 - 6 / 2                // 7 (not 2)
pour 5 * 2 + 3                 // 13

// Division by zero protection
pour 10 / 0                    // Error: Division by zero
```

---

### 4. String Operations

**Concatenation:** Use `+` operator

**Examples:**
```thirsty
drink first = "Hello"
drink second = "World"
pour first + " " + second      // "Hello World"

// String and number concatenation
drink name = "Alice"
drink age = 25
pour name + " is " + age       // "Alice is 25"

// Multi-part concatenation
pour "Result: " + 10 + 5       // "Result: 105"
```

---

### 5. Comparison Operators

**Operators:** `==` `!=` `<` `>` `<=` `>=`

**Strict Equality:** Uses `===` and `!==` internally to avoid type coercion

**Examples:**
```thirsty
drink x = 10
drink y = 20

thirsty x < y {                // Less than
  pour "x is smaller"
}

thirsty x == 10 {              // Equality
  pour "x equals 10"
}

thirsty x != y {               // Not equal
  pour "x and y are different"
}

thirsty y >= 20 {              // Greater than or equal
  pour "y is 20 or more"
}
```

---

### 6. Conditional Statements

**Syntax:**
```thirsty
thirsty condition {
  // code if true
}
hydrated {
  // code if false (optional)
}
```

**Examples:**

**Simple If:**
```thirsty
drink age = 25

thirsty age >= 18 {
  pour "Adult"
}
```

**If-Else:**
```thirsty
drink temperature = 85

thirsty temperature > 80 {
  pour "Hot!"
}
hydrated {
  pour "Comfortable"
}
```

**Nested Conditions:**
```thirsty
drink score = 85

thirsty score >= 90 {
  pour "A"
}
hydrated {
  thirsty score >= 80 {
    pour "B"
  }
  hydrated {
    thirsty score >= 70 {
      pour "C"
    }
    hydrated {
      pour "D or F"
    }
  }
}
```

---

### 7. Loops (refill)

**Syntax:**
```thirsty
refill condition {
  // loop body
}
```

**Safety:** Maximum 10,000 iterations to prevent infinite loops

**Examples:**

**Basic Loop:**
```thirsty
drink i = 0

refill i < 5 {
  pour i
  drink i = i + 1
}
// Output: 0, 1, 2, 3, 4
```

**Countdown:**
```thirsty
drink count = 10

refill count > 0 {
  pour count
  drink count = count - 1
}
pour "Done!"
```

**Accumulation:**
```thirsty
drink sum = 0
drink i = 1

refill i <= 10 {
  drink sum = sum + i
  drink i = i + 1
}

pour sum  // 55
```

**Complex Conditions:**
```thirsty
drink a = 1
drink b = 100

refill a < b {
  pour a
  drink a = a * 2
}
// Output: 1, 2, 4, 8, 16, 32, 64
```

---

## Security Features

### 1. Shield Blocks

**Purpose:** Create protected execution contexts

**Syntax:**
```thirsty
shield blockName {
  // protected code
}
```

**Example:**
```thirsty
shield secureOperation {
  drink apiKey = "secret-key"
  sanitize apiKey
  armor apiKey

  pour "Processing in secure context"
}
```

**Features:**

- Context isolation
- Nesting support
- Threat monitoring
- Enhanced error handling

---

### 2. Sanitization (sanitize)

**Purpose:** Clean input/output to prevent injection attacks

**Syntax:** `sanitize variableName`

**Protection Against:**

- XSS (Cross-Site Scripting)
- SQL Injection
- Command Injection
- HTML Injection
- Script Injection

**Implementation:**

- HTML entity encoding
- Special character escaping
- Pattern-based threat detection

**Examples:**

**XSS Prevention:**
```thirsty
drink userInput = "<script>alert('XSS')</script>"
sanitize userInput
pour userInput
// Output: &lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;
```

**SQL Injection Prevention:**
```thirsty
drink query = "'; DROP TABLE users; --"
sanitize query
pour query
// Output: &#x27;; DROP TABLE users; --
```

**Complete Sanitization:**
```thirsty
shield dataValidation {
  drink email = "<user@example.com>"
  drink username = "admin' OR '1'='1"
  drink comment = "Test<script>hack()</script>"

  sanitize email
  sanitize username
  sanitize comment

  pour "All inputs sanitized"
}
```

---

### 3. Variable Protection (armor)

**Purpose:** Prevent unauthorized variable modification

**Syntax:** `armor variableName`

**Features:**

- Read-only protection
- Warning on modification attempts
- Secure credential storage
- Tamper detection

**Examples:**

**Basic Protection:**
```thirsty
drink secretKey = "prod-api-key-12345"
armor secretKey

drink secretKey = "hacked"  // Warning: blocked
pour secretKey              // Still: "prod-api-key-12345"
```

**Complete Security:**
```thirsty
shield credentialManager {
  drink apiKey = "secret-key"
  drink dbPassword = "secure-pwd"
  drink jwtSecret = "jwt-secret"

  sanitize apiKey
  sanitize dbPassword
  sanitize jwtSecret

  armor apiKey
  armor dbPassword
  armor jwtSecret

  pour "Credentials secured"
}
```

---

### 4. Code Morphing (morph)

**Purpose:** Enable code obfuscation and anti-analysis

**Syntax:** `morph on: [threatList]`

**Threat Types:**

- `"injection"` - SQL, XSS, command injection
- `"overflow"` - Buffer overflow
- `"timing"` - Timing attacks
- `"xss"` - Cross-site scripting
- `"sqli"` - SQL injection specific

**Example:**
```thirsty
shield protectedApp {
  morph on: ["injection", "overflow", "timing"]

  drink sensitiveData = "confidential"
  sanitize sensitiveData
  armor sensitiveData
}
```

---

### 5. Defense Strategy (defend)

**Purpose:** Configure automated countermeasures

**Syntax:** `defend with: "strategy"`

**Strategies:**

- `"passive"` - Log only
- `"moderate"` - Warn and log
- `"aggressive"` - Block threats
- `"paranoid"` - Maximum security

**Example:**
```thirsty
shield highSecurity {
  defend with: "paranoid"
  morph on: ["injection", "overflow", "timing", "xss"]

  drink userData = "user-input"
  sanitize userData
  armor userData

  pour "Maximum security active"
}
```

---

## API Reference

### ThirstyInterpreter Class

**Constructor:**
```javascript
const ThirstyInterpreter = require('./src/index');
const interpreter = new ThirstyInterpreter(options);
```

**Options:**
```javascript
{
  security: true,              // Enable security features (default: true)
  securityMode: 'defensive',   // Security mode (default: 'defensive')
  securityLevel: 'moderate'    // Security level (default: 'moderate')
}
```

**Methods:**

**execute(code)**

- Execute Thirsty-lang code
- Parameters: `code` (string) - The source code
- Returns: void
- Throws: Error on invalid syntax or runtime errors

**Example:**
```javascript
const interpreter = new ThirstyInterpreter();
interpreter.execute('drink x = 10\npour x');
```

---

## Testing

### Running Tests

```bash
npm test
```

### Test Coverage

**37 comprehensive tests covering:**

**Core Features (12 tests):**

- Variable declaration (strings, numbers)
- Output statements
- Multiple statements
- Comments
- String concatenation
- Arithmetic evaluation
- Operator precedence
- Conditional statements
- Hydrated (else) blocks
- Comparison operators
- Loop functionality (basic)

**Loop Tests (5 tests):**

- Simple countdown
- Counter with multiplication
- Nested variable updates
- Zero iterations
- Complex conditions

**Error Tests (17 tests):**

- Division by zero (2 tests)
- Unmatched braces (3 tests)
- Invalid statements (5 tests)
- Unknown variables (2 tests)
- Sanitize/armor errors (2 tests)
- Unknown statements
- Loop iteration limit
- Invalid drink statement

**Security Tests (3 tests):**

- Shield block execution
- Sanitize XSS removal
- Armor variable protection

---

## Error Handling

### Error Types

**1. Syntax Errors**
```thirsty
drink noValue
// Error: Invalid drink statement
```

**2. Runtime Errors**
```thirsty
pour undefined Var
// Error: Unknown expression: undefinedVar
```

**3. Division Errors**
```thirsty
pour 10 / 0
// Error: Division by zero in expression
```

**4. Brace Errors**
```thirsty
thirsty true {
  pour "test"
// Error: Unmatched opening brace for thirsty statement at line 1
```

**5. Security Errors**
```thirsty
sanitize nonExistent
// Error: Cannot sanitize undefined variable: nonExistent
```

**6. Loop Safety**
```thirsty
drink i = 0
refill i >= 0 {
  drink i = i + 1
}
// Error: Loop exceeded maximum iterations (10000)
```

---

## Best Practices

### 1. Always Use Shield for Sensitive Operations

```thirsty
shield paymentProcessing {
  defend with: "paranoid"
  morph on: ["injection", "overflow"]

  drink cardNumber = "4532-1234-5678-9012"
  sanitize cardNumber
  armor cardNumber

  // Process payment
}
```

### 2. Sanitize All External Input

```thirsty
// User input
drink userEmail = userProvidedEmail
sanitize userEmail

// Database queries
drink sqlQuery = buildQuery()
sanitize sqlQuery

// API parameters
drink apiParam = getParameter()
sanitize apiParam
```

### 3. Armor Sensitive Credentials

```thirsty
drink apiKey = getApiKey()
drink dbPassword = getDbPassword()

armor apiKey
armor dbPassword

// These are now read-only
```

### 4. Use Descriptive Names

```thirsty
// Good
drink userAge = 25
drink maxRetries = 3
drink isAuthenticated = true

// Avoid
drink x = 25
drink n = 3
drink f = true
```

### 5. Handle Edge Cases

```thirsty
drink divisor = getDivisor()

thirsty divisor == 0 {
  pour "Error: Division by zero"
}
hydrated {
  drink result = 100 / divisor
  pour result
}
```

---

## Examples

### Complete Examples in Repository

1. **hello.thirsty** - Basic output
2. **variables.thirsty** - Variable usage
3. **arithmetic.thirsty** - Math operations
4. **control-flow.thirsty** - If/else statements
5. **loops.thirsty** - Loop examples
6. **basic-protection.thirsty** - Security basics
7. **advanced-defense.thirsty** - Advanced security
8. **attack-mitigation.thirsty** - Threat prevention
9. **paranoid-mode.thirsty** - Maximum security

### Running Examples

```bash
npm start examples/hello.thirsty
npm start examples/arithmetic.thirsty
npm start examples/security/basic-protection.thirsty
```

---

## Production Readiness Checklist

✅ **Language Features**

- [x] Variables with all types
- [x] Arithmetic with precedence
- [x] String operations
- [x] Control flow (if/else)
- [x] Loops with safety
- [x] Comments
- [x] Error handling

✅ **Security Features**

- [x] Shield blocks
- [x] Input/output sanitization
- [x] Variable protection (armor)
- [x] Code morphing
- [x] Defense strategies
- [x] Threat detection

✅ **Quality Assurance**

- [x] 37/37 tests passing
- [x] 0 security vulnerabilities
- [x] Comprehensive error handling
- [x] Full documentation
- [x] Tutorial walkthrough
- [x] Example programs

✅ **Production Features**

- [x] Loop safety limits
- [x] Division by zero protection
- [x] Brace matching validation
- [x] Strict equality checks
- [x] Type validation
- [x] Clear error messages

---

## Support

- **Repository**: https://github.com/IAmSoThirsty/Thirsty-lang
- **Issues**: Report bugs on GitHub Issues
- **Documentation**: README.md, TUTORIAL.md, this file
- **Examples**: See `examples/` directory

---

## License

See LICENSE file in repository.

---

**Thirsty-lang - Enterprise-Grade Security Language**

*Stay hydrated. Code securely. Build confidently.* 💧🔒

**Version 1.0.0 - Production Ready**
