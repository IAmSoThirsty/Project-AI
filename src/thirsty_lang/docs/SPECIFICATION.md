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
pour "Hello, " + username
```

## Reserved Keywords

- `drink` - Variable declaration
- `pour` - Output/print
- `sip` - Input from user
- `thirsty` - If statement (conditional execution)
- `hydrated` - Else statement
- `refill` - Loop iteration
- `glass` / `endglass` - Function declaration
- `fountain` / `endfountain` - Class definition

## Control Flow

### If Statements

The `thirsty` keyword provides conditional execution:

```thirsty
thirsty age > 18
  pour "Adult"
```

### Else Statements

The `hydrated` keyword provides alternative execution paths:

```thirsty
thirsty age > 18
  pour "Adult"
hydrated
  pour "Minor"
```

## Functions

Define reusable code blocks with the `glass` keyword:

```thirsty
glass greet(name)
  pour "Hello, " + name
endglass

greet("World")
```

## Classes

Define object blueprints with the `fountain` keyword:

```thirsty
fountain Person
  drink name
  drink age
endfountain

new Person
```

## Loops

The `refill` keyword enables iteration:

```thirsty
refill 5
  pour "Iteration"
```

## Future Features

The following features are planned for future releases:

1. Advanced error handling
1. Module system and imports
1. Functions (`glass` keyword)
1. Arithmetic operations
1. String concatenation
1. Comparison operators
1. Boolean logic

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

## Grammar (BNF)

```
program     ::= statement*
statement   ::= drink_stmt | pour_stmt | comment
drink_stmt  ::= "drink" identifier "=" expression
pour_stmt   ::= "pour" expression
expression  ::= string | number | identifier
identifier  ::= [a-zA-Z_][a-zA-Z0-9_]*
string      ::= '"' [^"]* '"' | "'" [^']* "'"
number      ::= [0-9]+ ("." [0-9]+)?
comment     ::= "//" [^\n]*
```

## Error Handling

The interpreter will report errors for:

- Unknown statements
- Invalid syntax
- Undefined variables
- Type mismatches (in future versions)

## Conclusion

Thirsty-lang is designed to be simple and fun. Stay hydrated and happy coding! 💧
