<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / SPECIFICATION.md # -->
<!-- # ============================================================================ # -->
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / SPECIFICATION.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>

# Thirsty-lang Language Specification

## Version 1.0.0

## Introduction

Thirsty-lang is a simple, interpreted programming language with water-themed keywords designed to make programming fun and accessible.

## Syntax

### Comments

Comments start with `//` and continue to the end of the line:

```thirsty
// This is a comment
```

### Variables

Variables are declared using the `drink` keyword:

```thirsty
drink varname = value
```

Variable names must start with a letter and can contain letters, numbers, and underscores.

### Data Types

Thirsty-lang supports the following data types:

- **Strings**: Text enclosed in double quotes `"` or single quotes `'`
- **Numbers**: Integer or floating-point numbers

Examples:
```thirsty
drink message = "Hello"
drink count = 42
drink temperature = 98.6
```

### Output

The `pour` keyword outputs a value to the console:

```thirsty
pour "Hello, World!"
pour varname
```

### Input

The `sip` keyword reads input from the user:

```thirsty
sip username
```

### Control Flow

The `thirsty` keyword creates a conditional (if) statement:

```thirsty
drink temperature = 25

thirsty temperature > 30 {
  pour "It's hot!"
}
```

The `hydrated` keyword provides an else clause:

```thirsty
drink age = 21

thirsty age >= 18 {
  pour "You are an adult"
}
hydrated {
  pour "You are a minor"
}
```

### Loops

The `refill` keyword creates a while-style loop:

```thirsty
drink water = 3

refill water > 0 {
  pour water
  drink water = water - 1
}
```

### Arithmetic Operations

Thirsty-lang supports standard arithmetic operators:

- `+` Addition
- `-` Subtraction
- `*` Multiplication
- `/` Division

```thirsty
drink result = 10 + 5 * 2  // Result: 20 (proper precedence)
pour result
```

### Comparison Operators

- `>` Greater than
- `<` Less than
- `>=` Greater than or equal
- `<=` Less than or equal
- `==` Equal to
- `!=` Not equal to

```thirsty
drink a = 10
drink b = 5

thirsty a > b {
  pour "a is greater"
}
```

### String Concatenation

Strings can be concatenated using the `+` operator:

```thirsty
drink greeting = "Hello, " + "World!"
pour greeting
```

### Security Features

Thirsty-lang includes defensive programming features:

- `shield` - Protected code blocks
- `sanitize` - HTML encoding to prevent XSS
- `armor` - Variable protection against modification
- `morph` - Dynamic code mutation (placeholder)
- `detect` - Threat monitoring (placeholder)
- `defend` - Automated countermeasures (placeholder)

```thirsty
shield secureApp {
  drink userData = "<script>alert('xss')</script>"
  sanitize userData
  pour userData  // Outputs: &lt;script&gt;...
}
```

## Reserved Keywords

- `drink` - Variable declaration
- `pour` - Output/print
- `sip` - Input
- `thirsty` - If statement
- `hydrated` - Else statement
- `refill` - Loop
- `shield` - Protected code block
- `sanitize` - HTML encoding
- `armor` - Variable protection
- `morph` - Code mutation
- `detect` - Threat monitoring
- `defend` - Automated countermeasures
- `glass` - Function declaration (planned)

## Future Features

The following features are planned for future releases:

1. Functions (`glass` keyword)
2. Arrays and data structures
3. Classes and OOP
4. Modules and imports
5. Async/await

## Examples

### Hello World

```thirsty
drink message = "Hello, World!"
pour message
```

### Multiple Variables

```thirsty
drink water = "H2O"
drink temperature = 25
drink liters = 2.5

pour water
pour temperature
pour liters
```

## Modules and Imports

Thirsty-lang supports modular code organization through the `import` and `export` keywords.

### Exporting

The `export` keyword makes functions and variables available to other modules:

```thirsty
glass add(a, b) {
  return a + b
}

drink PI = 3.14159

export add
export PI
```

### Importing

The `import` keyword loads functions and variables from other modules:

```thirsty
// Import specific items
import { add, PI } from "math-utils.thirsty"

// Import entire module
import MathUtils from "math-utils.thirsty"
```

Modules are cached after first load to avoid redundant execution.

## Async/Await Support

Thirsty-lang supports asynchronous programming with the `cascade` and `await` keywords.

### Cascade (Async Functions)

The `cascade` keyword declares an asynchronous function:

```thirsty
cascade fetchData(url) {
  drink response = await Http.get(url)
  return response.body
}
```

### Await

The `await` keyword pauses execution until a promise resolves:

```thirsty
cascade processFile() {
  drink content = await File.readAsync("data.txt")
  pour content
}
```

## Built-in Libraries

### File I/O (File)

The `File` built-in provides file system operations:

- `File.read(path)` - Read file contents synchronously
- `File.write(path, content)` - Write to file synchronously
- `File.exists(path)` - Check if file exists
- `File.delete(path)` - Delete a file
- `File.readAsync(path)` - Read file asynchronously (returns promise)
- `File.writeAsync(path, content)` - Write file asynchronously (returns promise)

Example:
```thirsty
drink content = File.read("data.txt")
drink success = File.write("output.txt", "Hello!")
drink exists = File.exists("data.txt")
```

### Network Utilities (Http)

The `Http` built-in provides HTTP request capabilities:

- `Http.get(url)` - Perform GET request (returns promise)
- `Http.post(url, data)` - Perform POST request (returns promise)
- `Http.fetch(url, options)` - Generic HTTP request (returns promise)

All HTTP functions return a promise that resolves to:
```thirsty
{
  status: 200,
  headers: {...},
  body: "response body"
}
```

Example:
```thirsty
cascade getData() {
  drink response = await Http.get("https://api.example.com/data")
  pour "Status: " + response.status
  return response.body
}
```

## Enhanced Debugging

The debugger (`node src/debugger.js file.thirsty`) includes:

- **Breakpoints**: Set/clear breakpoints at specific lines
- **Step execution**: Step through code line by line
- **Variable watching**: Monitor variable changes
- **Expression evaluation**: Evaluate expressions at runtime
- **Call stack**: View function call hierarchy
- **Code listing**: View code with context

Commands:

- `break <line>`, `b` - Set breakpoint
- `continue`, `c` - Continue execution
- `step`, `s` - Step into
- `next`, `n` - Step over
- `print <var>`, `p` - Print variable
- `eval <expr>`, `e` - Evaluate expression
- `stack` - Show call stack
- `list`, `l` - Show code listing

## Grammar (BNF)

```
program        ::= statement*

statement      ::= drink_stmt
                 | pour_stmt
                 | sip_stmt
                 | thirsty_stmt
                 | refill_stmt
                 | shield_stmt
                 | sanitize_stmt
                 | armor_stmt
                 | morph_stmt
                 | detect_stmt
                 | defend_stmt
                 | comment

drink_stmt     ::= "drink" identifier "=" expression
pour_stmt      ::= "pour" expression
sip_stmt       ::= "sip" identifier

thirsty_stmt   ::= "thirsty" condition block ("hydrated" block)?
refill_stmt    ::= "refill" condition block
shield_stmt    ::= "shield" identifier block

sanitize_stmt  ::= "sanitize" identifier
armor_stmt     ::= "armor" identifier

morph_stmt     ::= "morph" "on:" "[" string_list "]"
detect_stmt    ::= "detect" identifier
defend_stmt    ::= "defend" "with:" string

block          ::= "{" statement* "}"
condition      ::= expression comparison expression
comparison     ::= ">" | "<" | ">=" | "<=" | "==" | "!="

expression     ::= term (("+"|"-") term)*
term           ::= factor (("*"|"/") factor)*
factor         ::= number | string | identifier | "(" expression ")"

identifier     ::= [a-zA-Z_][a-zA-Z0-9_]*
string         ::= '"' [^"]* '"' | "'" [^']* "'"
number         ::= [0-9]+ ("." [0-9]+)?
string_list    ::= string ("," string)*
comment        ::= "//" [^\n]*
```

## Error Handling

The interpreter will report errors for:

- Unknown statements
- Invalid syntax
- Undefined variables
- Type mismatches (in future versions)

## Conclusion

Thirsty-lang is designed to be simple and fun. Stay hydrated and happy coding! 💧
