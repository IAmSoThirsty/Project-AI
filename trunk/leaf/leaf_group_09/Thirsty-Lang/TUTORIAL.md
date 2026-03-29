<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / TUTORIAL.md # -->
<!-- # ============================================================================ # -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / TUTORIAL.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
# Thirsty-lang Tutorial: Complete Walkthrough

Welcome to Thirsty-lang - an enterprise-grade programming language with built-in defensive security features!

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Concepts](#basic-concepts)
3. [Control Flow](#control-flow)
4. [Loops](#loops)
5. [Security Features](#security-features)
6. [Advanced Examples](#advanced-examples)
7. [Best Practices](#best-practices)

---

## Getting Started

### Installation

```bash
git clone https://github.com/IAmSoThirsty/Thirsty-lang.git
cd Thirsty-lang
npm install
```

### Running Your First Program

Create a file called `hello.thirsty`:

```thirsty
drink message = "Hello, World!"
pour message
```

Run it:

```bash
npm start hello.thirsty
```

Output:
```
Hello, World!
```

---

## Basic Concepts

### 1. Variables (drink)

Variables in Thirsty-lang are declared using the `drink` keyword:

```thirsty
drink name = "Alice"
drink age = 25
drink temperature = 98.6
drink isThirsty = true
```

**Example Program:** `variables.thirsty`
```thirsty
drink water = "H2O"
drink volume = 250
drink quality = 99.9

pour water
pour volume
pour quality
```

Run: `npm start variables.thirsty`

### 2. Output (pour)

Use `pour` to display values:

```thirsty
pour "Direct string"
pour 42
pour true

drink message = "Stored value"
pour message
```

### 3. Comments

Comments start with `//`:

```thirsty
// This is a comment
drink x = 10  // Inline comment
```

### 4. Arithmetic Operations

Thirsty-lang supports full arithmetic with proper operator precedence:

```thirsty
drink a = 10
drink b = 5

pour a + b    // 15
pour a - b    // 5
pour a * b    // 50
pour a / b    // 2

// Operator precedence: * and / before + and -
pour 2 + 3 * 4    // 14 (not 20)
pour 10 - 8 / 2   // 6 (not 1)
```

**Example Program:** `arithmetic.thirsty`
```thirsty
drink x = 100
drink y = 25

pour "Addition:"
pour x + y

pour "Subtraction:"
pour x - y

pour "Multiplication:"
pour x * y

pour "Division:"
pour x / y

pour "Complex:"
pour x + y * 2
```

### 5. String Operations

```thirsty
drink first = "Hello"
drink second = "World"
drink space = " "

pour first + space + second  // "Hello World"

// String and number concatenation
drink name = "Alice"
drink age = 30
pour name + " is " + age + " years old"
```

---

## Control Flow

### Conditionals: thirsty and hydrated

Use `thirsty` for if statements and `hydrated` for else:

```thirsty
drink temperature = 75

thirsty temperature > 80 {
  pour "It's hot! Drink more water!"
}
hydrated {
  pour "Temperature is comfortable"
}
```

**Example Program:** `control-flow.thirsty`
```thirsty
drink age = 25
drink hasID = true

thirsty age >= 21 {
  thirsty hasID == true {
    pour "Access granted"
  }
  hydrated {
    pour "Need ID"
  }
}
hydrated {
  pour "Too young"
}
```

### Comparison Operators

Thirsty-lang supports all standard comparison operators:

```thirsty
drink a = 10
drink b = 20

thirsty a < b {
  pour "a is less than b"
}

thirsty a == 10 {
  pour "a equals 10"
}

thirsty a != b {
  pour "a is not equal to b"
}

thirsty b >= 20 {
  pour "b is 20 or more"
}
```

---

## Loops

### The refill Loop

Use `refill` for loops that continue while a condition is true:

```thirsty
drink counter = 1

refill counter <= 5 {
  pour counter
  drink counter = counter + 1
}
```

Output:
```
1
2
3
4
5
```

**Example: Countdown**
```thirsty
drink countdown = 10

refill countdown > 0 {
  pour countdown
  drink countdown = countdown - 1
}

pour "Liftoff!"
```

**Example: Sum calculation**
```thirsty
drink total = 0
drink i = 1

refill i <= 10 {
  drink total = total + i
  drink i = i + 1
}

pour "Sum of 1 to 10:"
pour total  // 55
```

**Example: Loop with complex condition**
```thirsty
drink x = 2
drink limit = 100

refill x < limit {
  pour x
  drink x = x * 2  // Double each time
}
```

Output:
```
2
4
8
16
32
64
```

### Safety Features

Loops have built-in protection against infinite loops:

```thirsty
// This will throw an error after 10,000 iterations
drink i = 0
refill i >= 0 {
  drink i = i + 1
}
// Error: Loop exceeded maximum iterations (10000)
```

---

## Security Features

Thirsty-lang is designed for defensive programming with enterprise-grade security features.

### 1. Shield Blocks

Use `shield` to create protected execution contexts:

```thirsty
shield secureZone {
  drink sensitiveData = "confidential"
  pour "Processing in secure context"
}
```

### 2. Sanitization (sanitize)

Protect against XSS, SQL injection, and other attacks:

```thirsty
drink userInput = "<script>alert('XSS')</script>"
sanitize userInput

pour userInput  // &lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;
```

**Example: SQL Injection Protection**
```thirsty
shield databaseQuery {
  drink query = "'; DROP TABLE users; --"
  sanitize query

  pour "Safe query:"
  pour query  // &#x27;; DROP TABLE users; --
}
```

### 3. Variable Protection (armor)

Protect variables from modification:

```thirsty
drink apiKey = "secret-key-12345"
armor apiKey

// Attempt to modify
drink apiKey = "hacked"  // Warning: blocked!

pour apiKey  // Still: "secret-key-12345"
```

### 4. Threat Morphing (morph)

Enable code obfuscation against specific threats:

```thirsty
shield protectedApp {
  morph on: ["injection", "overflow", "timing"]

  drink data = "sensitive information"
  sanitize data
  armor data

  pour "Data is protected"
}
```

### 5. Defense Configuration (defend)

Set your security strategy:

```thirsty
shield highSecurity {
  defend with: "aggressive"

  drink password = "user_password"
  sanitize password
  armor password
}
```

### Complete Security Example

**File:** `secure-app.thirsty`
```thirsty
shield applicationSecurity {
  // Configure defenses
  morph on: ["injection", "xss", "overflow"]
  defend with: "paranoid"

  // User authentication
  drink username = "admin'--"
  drink password = "<script>steal()</script>"

  // Sanitize all inputs
  sanitize username
  sanitize password

  // Protect credentials
  armor username
  armor password

  // Process safely
  drink credentials = username + ":" + password
  armor credentials

  pour "Secure authentication complete"
  pour "Username: " + username
  pour "All threats neutralized"
}
```

Run: `npm start secure-app.thirsty`

---

## Advanced Examples

### Example 1: Fibonacci Sequence

```thirsty
drink n = 10
drink a = 0
drink b = 1
drink i = 0

pour "Fibonacci sequence:"

refill i < n {
  pour a
  drink temp = a
  drink a = b
  drink b = temp + b
  drink i = i + 1
}
```

### Example 2: Prime Number Checker

```thirsty
drink number = 17
drink isPrime = true
drink i = 2

thirsty number <= 1 {
  drink isPrime = false
}
hydrated {
  refill i * i <= number {
    drink remainder = number / i * i
    thirsty remainder == number {
      drink isPrime = false
    }
    drink i = i + 1
  }
}

thirsty isPrime == true {
  pour number + " is prime"
}
hydrated {
  pour number + " is not prime"
}
```

### Example 3: Secure Data Processing

```thirsty
shield dataProcessor {
  morph on: ["injection", "overflow"]
  defend with: "aggressive"

  // Simulate user data
  drink records = 5
  drink processed = 0

  refill processed < records {
    drink dataItem = "Record " + processed
    sanitize dataItem
    armor dataItem

    pour "Processing: " + dataItem
    drink processed = processed + 1
  }

  pour "All records processed securely"
  pour "Total: " + processed
}
```

---

## Best Practices

### 1. Always Sanitize User Input

```thirsty
shield userInterface {
  drink userEmail = "<user@example.com>"
  sanitize userEmail  // Always sanitize before use

  drink userName = "admin' OR '1'='1"
  sanitize userName  // Protect against SQL injection
}
```

### 2. Use Armor for Sensitive Data

```thirsty
drink apiSecret = "prod-key-xyz"
drink dbPassword = "secure123"

armor apiSecret
armor dbPassword

// These are now protected from modification
```

### 3. Use Shield Blocks for Critical Operations

```thirsty
shield criticalOperation {
  defend with: "paranoid"
  morph on: ["injection", "timing", "overflow"]

  // Your critical code here
}
```

### 4. Check Bounds and Conditions

```thirsty
drink denominator = 5

thirsty denominator == 0 {
  pour "Error: Cannot divide by zero"
}
hydrated {
  drink result = 100 / denominator
  pour result
}
```

### 5. Use Descriptive Variable Names

```thirsty
// Good
drink userAge = 25
drink maxAttempts = 3
drink isAuthenticated = true

// Avoid
drink x = 25
drink n = 3
drink f = true
```

---

## Testing Your Code

Run the test suite to verify all functionality:

```bash
npm test
```

Expected output:
```
Running Thirsty-lang Tests...

✓ Variable declaration with string
✓ Variable declaration with number
✓ Pour statement with literal
✓ Pour statement with variable
✓ Multiple statements
✓ Comments are ignored
✓ String concatenation
✓ Arithmetic expression evaluation
✓ Operator precedence
✓ Conditional statements (thirsty)
✓ Conditional with hydrated (else) block
✓ Comparison operators
✓ Loop (refill) functionality
✓ Loop: Simple countdown
✓ Loop: Counter with multiplication
✓ Loop: Nested variable updates
✓ Loop: Zero iterations when condition false
✓ Loop: Complex condition with multiple variables
✓ Error: Division by zero
✓ Error: Division by zero in expression
✓ Error: Unmatched opening brace in thirsty
✓ Error: Unmatched opening brace in refill
✓ Error: Unmatched opening brace in shield
✓ Error: Invalid thirsty statement
✓ Error: Invalid refill statement
✓ Error: Unknown variable reference
✓ Error: Unknown variable in expression
✓ Error: Invalid drink statement
✓ Error: Invalid shield statement
✓ Error: Invalid sanitize statement
✓ Error: Sanitize undefined variable
✓ Error: Armor undefined variable
✓ Error: Unknown statement
✓ Error: Loop iteration safety limit
✓ Security: Shield block execution
✓ Security: Sanitize removes XSS
✓ Security: Armor protects variables

37 tests, 37 passed, 0 failed
```

---

## Error Handling

Thirsty-lang provides clear error messages:

### Division by Zero

```thirsty
pour 10 / 0
// Error: Division by zero in expression
```

### Unmatched Braces

```thirsty
thirsty true {
  pour "missing closing brace"
// Error: Unmatched opening brace for thirsty statement at line 1
```

### Unknown Variables

```thirsty
pour undefinedVar
// Error: Unknown expression: undefinedVar
```

### Invalid Statements

```thirsty
unknownKeyword test
// Error: Unknown statement: unknownKeyword test
```

---

## Next Steps

1. **Explore Examples**: Check the `examples/` directory for more sample programs
2. **Write Your Own Programs**: Start with simple scripts and gradually add complexity
3. **Use Security Features**: Always use `shield`, `sanitize`, and `armor` for production code
4. **Run Tests**: Verify your installation with `npm test`
5. **Read Documentation**: Check `README.md` and `FEATURE_STATUS.md` for detailed information

---

## Support and Resources

- **Repository**: https://github.com/IAmSoThirsty/Thirsty-lang
- **Issues**: Report bugs or request features on GitHub
- **Examples**: See `examples/` directory for more code samples
- **Tests**: See `src/test/runner.js` for comprehensive test examples

---

**Stay hydrated and code securely!** 💧🔒
